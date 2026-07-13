"""Flexible Data Placement (FDP) engine: device-managed GC + host placement hints.

Contrast with the other two engines EyanaSSDSim provides:
  * conventional : device GC, no hints  -> hot & cold data mix in every block.
  * ZNS          : host GC, sequential zones, whole-zone reset.
  * FDP (here)   : device GC, but the host tags each write with a placement
                   handle (RUH) and the device keeps same-handle data in the
                   same reclaim unit (RU). GC still runs on the device, yet each
                   victim block holds data of a single lifetime class, so it is
                   mostly-invalid together and little valid data is migrated.

Placement policy (best for analysing arbitrary trace files, needs no extra
metadata): overwrite -> "hot" handle, first-write -> "cold" handle. GC migrates
a victim's survivors back into the SAME handle's stream so separation is kept.
"""
from __future__ import annotations
from collections import deque

import numpy as np

from ..config import SSDConfig

FREE = -1


class FDPEngine:
    def __init__(self, cfg: SSDConfig, hot_cold: bool = True):
        cfg.validate()
        self.cfg = cfg
        self.ppb = cfg.pages_per_block
        self.nblocks = cfg.total_blocks
        self.lp = cfg.logical_pages
        self.hot_cold = hot_cold
        self.n_handles = 2 if hot_cold else 1   # 0 = hot (overwrites), 1 = cold

        self.forward = np.full(self.lp, FREE, dtype=np.int64)          # lpn -> ppn
        self.reverse = np.full(self.nblocks * self.ppb, FREE, dtype=np.int64)  # ppn -> lpn
        self.valid_count = np.zeros(self.nblocks, dtype=np.int32)
        self.invalid_count = np.zeros(self.nblocks, dtype=np.int32)
        self.erase_count = np.zeros(self.nblocks, dtype=np.int64)
        self.block_handle = np.full(self.nblocks, -1, dtype=np.int8)   # RUH owning a block (-1 free)
        self.is_free = np.ones(self.nblocks, dtype=bool)

        # Free-block pool interleaved across planes so writes spread out (real
        # parallelism) instead of filling one plane at a time.
        planes, bpp = cfg.planes, cfg.blocks_per_plane
        self.free_blocks = deque(p * bpp + off
                                 for off in range(bpp) for p in range(planes))

        self.active = [None] * self.n_handles      # active (open) block per handle
        self.active_off = [0] * self.n_handles     # next free page in the active block

        self.host_writes = 0
        self.gc_writes = 0
        self.erases = 0
        # Trigger GC at the same fill level as the conventional engine's high
        # watermark, so comparisons isolate the placement-hint benefit rather
        # than a difference in GC aggressiveness. Always keep at least one active
        # block per handle plus a migration spare.
        self.min_free = max(self.n_handles + 2,
                            int((1.0 - cfg.gc_high_watermark) * self.nblocks))
        if self.nblocks <= self.min_free:
            raise ValueError("too few blocks for FDP headroom; use a larger device")

    # ---------------- write path ----------------
    def write(self, lpn: int):
        lpn = int(lpn) % self.lp
        # placement hint: overwrite -> hot handle (0), first write -> cold (1)
        if not self.hot_cold:
            handle = 0
        else:
            handle = 0 if self.forward[lpn] != FREE else 1
        # invalidate the previous physical location, if any
        old = self.forward[lpn]
        if old != FREE:
            ob = old // self.ppb
            self.valid_count[ob] -= 1
            self.invalid_count[ob] += 1
            self.reverse[old] = FREE
        ppn = self._append(lpn, handle, is_gc=False)
        self.forward[lpn] = ppn
        self._maybe_gc()

    # ---------------- internals ----------------
    def _append(self, lpn: int, handle: int, is_gc: bool) -> int:
        z = self.active[handle]
        if z is None or self.active_off[handle] >= self.ppb:
            z = self._alloc_block(handle)
        off = self.active_off[handle]
        ppn = z * self.ppb + off
        self.reverse[ppn] = lpn
        self.valid_count[z] += 1
        self.active_off[handle] += 1
        if is_gc:
            self.gc_writes += 1
        else:
            self.host_writes += 1
        return ppn

    def _alloc_block(self, handle: int) -> int:
        if not self.free_blocks:
            if not self._gc_once():
                raise RuntimeError("no free block; device over-utilised (raise op_ratio)")
        z = self.free_blocks.popleft()
        self.is_free[z] = False
        self.block_handle[z] = handle
        self.active[handle] = z
        self.active_off[handle] = 0
        return z

    def _maybe_gc(self):
        guard = 0
        limit = 2 * self.nblocks
        while len(self.free_blocks) < self.min_free:
            if not self._gc_once():
                break
            guard += 1
            if guard > limit:
                break

    def _gc_once(self) -> bool:
        """Greedy device GC: reclaim the full block with the fewest valid pages,
        migrating survivors back into their own handle's stream."""
        active = {a for a in self.active if a is not None}
        victim, best_valid = -1, None
        for b in range(self.nblocks):
            if self.is_free[b] or b in active:
                continue
            v = self.valid_count[b]
            if best_valid is None or v < best_valid:
                best_valid, victim = v, b
        if victim < 0:
            return False
        handle = int(self.block_handle[victim])
        if handle < 0:
            handle = 0
        base = victim * self.ppb
        seg = self.reverse[base:base + self.ppb]
        occ = np.nonzero(seg != FREE)[0]
        for off in occ:
            lpn = int(seg[off])
            if self.forward[lpn] == base + int(off):     # still the current copy
                self.forward[lpn] = self._append(lpn, handle, is_gc=True)
        # erase the whole victim block
        self.reverse[base:base + self.ppb] = FREE
        self.valid_count[victim] = 0
        self.invalid_count[victim] = 0
        self.erase_count[victim] += 1
        self.erases += 1
        self.is_free[victim] = True
        self.block_handle[victim] = -1
        self.free_blocks.append(victim)
        return True

    # ---------------- metrics ----------------
    @property
    def waf(self) -> float:
        return (self.host_writes + self.gc_writes) / self.host_writes if self.host_writes else 1.0

    def reset_counters(self):
        self.host_writes = 0
        self.gc_writes = 0
        self.erases = 0
