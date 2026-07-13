"""Flexible Data Placement (FDP) engine, aligned to the FEMU/WARP FDP FTL model.

Mirrors the mechanisms in FEMU's bbssd/ftl.c so results can be validated against
FEMU:

  * Reclaim Unit (RU) = a superblock of `blocks_per_ru` blocks, reclaimed whole
    (FEMU: an RU spans lines across channels/planes).
  * Each write carries a placement handle (RUH). Policy here: overwrite -> "hot",
    first write -> "cold" (needs no trace metadata).
  * Device-managed GC. Victim = full, non-active RU with fewest valid pages
    (greedy). Lazy GC defers a victim while invalid < ru_pages/8 (FEMU rule),
    unless GC is forced by near-exhaustion.
  * Isolation of GC copies (WARP Obs #8):
      - PI (Persistently Isolated): copies stay in the victim's own RUH, keeping
        each RUH pure -> lowest WAF, BUT PI reserves a per-RUH GC headroom, so it
        fragments the OP slack and is starved at low OP.
      - II (Initially Isolated): copies go to one shared "GC-RUH", pooling the GC
        slack -> more robust when OP is scarce.
    The per-RUH reservation is what produces WARP's OP-dependent II/PI crossover;
    the exact crossover point is a calibration target for FEMU validation.
  * WAF = (host_writes + gc_writes) / host_writes.

Per-block valid/invalid/erase/handle arrays are exported for the live grid.
"""
from __future__ import annotations
from collections import deque

import numpy as np

from ..config import SSDConfig

FREE = -1
ST_FREE, ST_OPEN, ST_FULL = 0, 1, 2


class FDPEngine:
    def __init__(self, cfg: SSDConfig, hot_cold: bool = True, isolation: str = "pi",
                 blocks_per_ru: int = None, lazy_gc: bool = True):
        cfg.validate()
        self.cfg = cfg
        self.ppb = cfg.pages_per_block
        self.nblocks = cfg.total_blocks
        self.lp = cfg.logical_pages
        self.hot_cold = hot_cold
        self.isolation = isolation           # "pi" | "ii"
        self.lazy_gc = lazy_gc

        # --- reclaim-unit geometry (RU = superblock) ---
        bpr = blocks_per_ru or cfg.planes
        if bpr < 1 or self.nblocks % bpr != 0:
            bpr = cfg.planes
        self.bpr = bpr
        self.n_ru = self.nblocks // bpr
        self.ru_pages = bpr * self.ppb
        self.lazy_min_invalid = self.ru_pages // 8   # FEMU: defer if ipc < npages/8

        # --- placement handles (RUHs): 0=hot, 1=cold, [last]=GC-RUH for II ---
        self.n_data_handles = 2 if hot_cold else 1
        self.n_handles = self.n_data_handles + (1 if isolation == "ii" else 0)
        self.gc_ruh = (self.n_handles - 1) if isolation == "ii" else None

        # --- per-block arrays (viz + wear) ---
        self.valid_count = np.zeros(self.nblocks, dtype=np.int32)
        self.invalid_count = np.zeros(self.nblocks, dtype=np.int32)
        self.erase_count = np.zeros(self.nblocks, dtype=np.int64)
        self.block_handle = np.full(self.nblocks, -1, dtype=np.int8)

        # --- per-RU state ---
        self.ru_valid = np.zeros(self.n_ru, dtype=np.int32)
        self.ru_written = np.zeros(self.n_ru, dtype=np.int32)
        self.ru_state = np.zeros(self.n_ru, dtype=np.int8)
        self.ru_handle = np.full(self.n_ru, -1, dtype=np.int8)

        # --- FTL maps ---
        self.forward = np.full(self.lp, FREE, dtype=np.int64)
        self.reverse = np.full(self.nblocks * self.ppb, FREE, dtype=np.int64)

        self.active_ru = [None] * self.n_handles
        self.free_rus = deque(range(self.n_ru))          # one shared OP pool

        self.host_writes = 0
        self.gc_writes = 0
        self.erases = 0

        # GC watermark (free RUs). PI reserves an extra per-RUH GC RU, fragmenting
        # the OP slack -> starves at low OP; negligible when OP is abundant.
        base = int((1.0 - cfg.gc_high_watermark) * self.n_ru)
        reserve = self.n_data_handles if isolation == "pi" else 0
        self.gc_free_thres = max(self.n_handles + 1, base + reserve)
        if self.n_ru <= self.gc_free_thres + 1:
            raise ValueError("too few reclaim units; reduce blocks_per_ru or grow device")

    # ---------------- write path ----------------
    def write(self, lpn: int):
        lpn = int(lpn) % self.lp
        handle = 0 if not self.hot_cold else (0 if self.forward[lpn] != FREE else 1)
        old = self.forward[lpn]
        if old != FREE:
            ob = old // self.ppb
            self.valid_count[ob] -= 1
            self.invalid_count[ob] += 1
            self.ru_valid[old // self.ru_pages] -= 1
            self.reverse[old] = FREE
        self.forward[lpn] = self._append(lpn, handle, is_gc=False)
        self._maybe_gc()

    # ---------------- internals ----------------
    def _append(self, lpn: int, handle: int, is_gc: bool) -> int:
        ru = self.active_ru[handle]
        if ru is None or self.ru_written[ru] >= self.ru_pages:
            ru = self._open_ru(handle)
        k = int(self.ru_written[ru])
        ppn = ru * self.ru_pages + k
        self.reverse[ppn] = lpn
        self.valid_count[ppn // self.ppb] += 1
        self.ru_valid[ru] += 1
        self.ru_written[ru] += 1
        if self.ru_written[ru] >= self.ru_pages:
            self.ru_state[ru] = ST_FULL
        if is_gc:
            self.gc_writes += 1
        else:
            self.host_writes += 1
        return ppn

    def _open_ru(self, handle: int) -> int:
        if not self.free_rus:
            if not self._gc_once(force=True):
                raise RuntimeError("no free reclaim unit; device over-utilised (raise op)")
        ru = self.free_rus.popleft()
        self.ru_state[ru] = ST_OPEN
        self.ru_handle[ru] = handle
        self.ru_written[ru] = 0
        self.ru_valid[ru] = 0
        b0 = ru * self.bpr
        self.block_handle[b0:b0 + self.bpr] = handle
        self.active_ru[handle] = ru
        return ru

    def _maybe_gc(self):
        guard = 0
        limit = 2 * self.n_ru
        while len(self.free_rus) < self.gc_free_thres:
            force = len(self.free_rus) < 2
            if not self._gc_once(force=force):
                break
            guard += 1
            if guard > limit:
                break

    def _select_victim(self, force: bool):
        active = {a for a in self.active_ru if a is not None}
        best, best_valid = -1, None
        for r in range(self.n_ru):
            if self.ru_state[r] != ST_FULL or r in active:
                continue
            v = self.ru_valid[r]
            if best_valid is None or v < best_valid:
                best_valid, best = v, r
        if best < 0:
            return -1
        if self.lazy_gc and not force:
            invalid = int(self.ru_written[best]) - int(self.ru_valid[best])
            if invalid < self.lazy_min_invalid:
                return -1
        return best

    def _gc_once(self, force: bool = False) -> bool:
        victim = self._select_victim(force)
        if victim < 0:
            return False
        handle = int(self.ru_handle[victim])
        dest = handle if self.isolation == "pi" else self.gc_ruh   # PI vs II
        base = victim * self.ru_pages
        n = int(self.ru_written[victim])
        for k in range(n):
            ppn = base + k
            lpn = int(self.reverse[ppn])
            if lpn != FREE and self.forward[lpn] == ppn:
                self.forward[lpn] = self._append(lpn, dest, is_gc=True)
        b0 = victim * self.bpr
        for b in range(b0, b0 + self.bpr):
            self.erase_count[b] += 1
            self.valid_count[b] = 0
            self.invalid_count[b] = 0
        self.erases += self.bpr
        self.reverse[base:base + self.ru_pages] = FREE
        self.ru_valid[victim] = 0
        self.ru_written[victim] = 0
        self.ru_state[victim] = ST_FREE
        self.ru_handle[victim] = -1
        self.block_handle[b0:b0 + self.bpr] = -1
        self.free_rus.append(victim)
        return True

    # ---------------- metrics ----------------
    @property
    def waf(self) -> float:
        return (self.host_writes + self.gc_writes) / self.host_writes if self.host_writes else 1.0

    def gc_stats(self):
        return {"host_writes": int(self.host_writes), "gc_writes": int(self.gc_writes),
                "waf": round(self.waf, 4), "erases": int(self.erases),
                "n_ru": int(self.n_ru), "ru_pages": int(self.ru_pages),
                "isolation": self.isolation}

    def reset_counters(self):
        self.host_writes = 0
        self.gc_writes = 0
        self.erases = 0
