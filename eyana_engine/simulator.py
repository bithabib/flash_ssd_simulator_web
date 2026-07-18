"""Deterministic SSD simulator: write path, garbage collection, and stats.

WAF = physical_writes / host_writes, where physical_writes = host_writes +
gc_migration_writes.  These counters are strictly separated so WAF cannot be
polluted by GC copy-forward writes (the central correctness fix from the audit).
"""
from __future__ import annotations
import numpy as np
from .config import SSDConfig
from .device import Device, FREE
from .allocation import Allocator
from . import gc as gc_mod


class Simulator:
    def __init__(self, cfg: SSDConfig, scheme: str = "s1", gc_policy: str = None):
        self.cfg = cfg
        self.dev = Device(cfg)
        self.alloc = Allocator(cfg, scheme)
        self.policy = gc_mod.make_policy(gc_policy or cfg.gc_policy)

        # counters
        self.host_writes = 0
        self.gc_writes = 0
        self.reads = 0
        self.erases = 0
        self.time_us = 0.0
        self.waf_series = []   # (host_writes, waf) samples for time plots

    # ---------- public API ----------
    def write(self, lpn: int):
        if not (0 <= lpn < self.cfg.logical_pages):
            raise IndexError(f"lpn {lpn} out of range [0,{self.cfg.logical_pages})")
        dev = self.dev
        p = self.alloc.plane_index(lpn)

        # trigger GC before allocating if the plane is above the high watermark
        if dev.plane_utilisation(p) >= self.cfg.gc_high_watermark:
            self._garbage_collect(p)

        # invalidate the previous physical location, if any
        old = dev.forward_map[lpn]
        if old != FREE:
            ob = old // self.cfg.pages_per_block
            dev.valid_count[ob] -= 1
            dev.invalid_count[ob] += 1

        ppn = dev.alloc_page(p)
        if ppn is None:                       # plane full: force GC then retry once
            self._garbage_collect(p, force=True)
            ppn = dev.alloc_page(p)
            if ppn is None:
                raise RuntimeError(f"plane {p} full even after GC (raise OP or "
                                   f"lower gc_high_watermark)")
        self._place(lpn, ppn, host=True)

    def read(self, lpn: int) -> bool:
        """Return True if the LPN is currently mapped (a real read would hit)."""
        hit = self.dev.forward_map[lpn] != FREE
        if hit:
            self.reads += 1
            self.time_us += self.cfg.t_read_page
        return bool(hit)

    # ---------- internals ----------
    def _place(self, lpn: int, ppn: int, host: bool):
        dev = self.dev
        dev.now_seq += 1
        dev.reverse_map[ppn] = lpn
        dev.forward_map[lpn] = ppn
        b = ppn // self.cfg.pages_per_block
        dev.valid_count[b] += 1
        dev.last_modified[b] = dev.now_seq
        if host:
            self.host_writes += 1
        else:
            self.gc_writes += 1
        self.time_us += self.cfg.t_write_page

    def _plane_candidates(self, p: int):
        dev = self.dev
        lo, hi = p * dev.bpp, (p + 1) * dev.bpp
        ab = dev.active_block[p]
        out = []
        for b in range(lo, hi):
            if dev.is_free[b] or b == ab:
                continue
            if dev.invalid_count[b] > 0:
                out.append(b)
        return out

    def _garbage_collect(self, p: int, force: bool = False):
        if self.cfg.gc_granularity == "superblock":
            return self._gc_superblock(p, force)
        dev, cfg = self.dev, self.cfg
        # reclaim until we drop to the low watermark (or nothing left to reclaim)
        while True:
            util = dev.plane_utilisation(p)
            if not force and util <= cfg.gc_low_watermark:
                break
            candidates = self._plane_candidates(p)
            if not candidates:
                break                          # no invalid pages to reclaim
            victim = self.policy.select_victim(candidates, dev)
            if victim < 0 or dev.invalid_count[victim] == 0:
                break
            self._reclaim_block(victim, p)
            force = False                      # only force the first pass

    # GC scratch: lines kept free per plane so a line reclaim always has room to
    # migrate into (mirrors FEMU's gc_thres reserve). 2 = 1 in-use + 1 migration.
    _SB_RESERVE = 2

    def _gc_superblock(self, p: int, force: bool = False):
        """FEMU-style GC at *line/superblock* granularity: reclaim the emptiest
        line (fewest valid pages, greedy) ONE at a time, lazily, keeping a small
        per-plane free reserve so migration never runs dry.  A line L is the set
        {plane*bpp + L}; the whole line is erased together."""
        dev = self.dev
        bpp, planes = dev.bpp, dev.planes

        def plane_free_min():
            return min(len(dev.free_list[pp]) for pp in range(planes))

        guard, limit = 0, 4 * bpp
        while force or plane_free_min() < self._SB_RESERVE:
            active_L = {int(ab) % bpp for ab in dev.active_block if ab != -1}
            # greedy: allocated line with the FEWEST valid pages. Prefer non-open
            # lines; fall back to open ones only if nothing else is reclaimable
            # (erase_block safely resets an active pointer) -- avoids both the
            # stall-crash and the thrash of always allowing open lines.
            best_L, best_valid = -1, None
            fb_L, fb_valid = -1, None
            for L in range(bpp):
                valid, alloc = 0, False
                for pp in range(planes):
                    b = pp * bpp + L
                    if not dev.is_free[b]:
                        alloc = True
                        valid += int(dev.valid_count[b])
                if not alloc:
                    continue
                if fb_valid is None or valid < fb_valid:
                    fb_valid, fb_L = valid, L        # fallback: any allocated line
                if L in active_L:
                    continue
                if best_valid is None or valid < best_valid:
                    best_valid, best_L = valid, L
            L = best_L if best_L >= 0 else fb_L      # fallback to open line if needed
            if L < 0:
                break
            self._reclaim_line(L)
            force = False
            guard += 1
            if guard > limit:
                break

    def _reclaim_line(self, L: int):
        """Reclaim line L like FEMU: collect its live pages, ERASE the whole line
        first (freeing one block per plane), THEN migrate the survivors back into
        their own planes.  Erasing before migrating guarantees free room, so
        migration can never run dry -- the crux that makes this crash-proof."""
        dev = self.dev
        ppb, bpp = self.cfg.pages_per_block, self.dev.bpp
        # 1. collect live (lpn, plane) across the whole line
        live = []
        for pp in range(dev.planes):
            b = pp * bpp + L
            if dev.is_free[b]:
                continue
            base = b * ppb
            seg = dev.reverse_map[base:base + ppb]
            for off in range(ppb):
                lpn = int(seg[off])
                if lpn != FREE and dev.forward_map[lpn] == base + off:
                    live.append((lpn, pp))
        # 2. erase the whole line first -> frees a block in every touched plane
        for pp in range(dev.planes):
            b = pp * bpp + L
            if not dev.is_free[b]:
                dev.erase_block(b)
                self.erases += 1
                self.time_us += self.cfg.t_erase_block
        # 3. migrate survivors back (each stays in its plane; room is guaranteed)
        for lpn, pp in live:
            new_ppn = dev.alloc_page(pp)
            if new_ppn is None:                     # cannot happen after erase
                raise RuntimeError("superblock GC: no room even after line erase")
            self._place(lpn, new_ppn, host=False)
            self.erases += 1
            self.time_us += self.cfg.t_erase_block

    def _reclaim_block(self, victim: int, p: int):
        """Migrate live pages of `victim` (staying in plane p), then erase it."""
        dev = self.dev
        ppb = self.cfg.pages_per_block
        base = victim * ppb
        for off in range(ppb):
            ppn = base + off
            lpn = dev.reverse_map[ppn]
            if lpn != FREE and dev.forward_map[lpn] == ppn:   # live page -> migrate
                new_ppn = dev.alloc_page(p)
                if new_ppn is None:
                    raise RuntimeError("no free page for GC migration; watermark "
                                       "leaves insufficient headroom")
                dev.valid_count[victim] -= 1
                self._place(lpn, new_ppn, host=False)
        dev.erase_block(victim)
        self.erases += 1
        self.time_us += self.cfg.t_erase_block

    def reset_counters(self):
        """Zero write/erase/time counters (used after preconditioning) so WAF
        reflects only the measured workload phase.  Device state is kept."""
        self.host_writes = 0
        self.gc_writes = 0
        self.erases = 0
        self.reads = 0
        self.time_us = 0.0
        self.waf_series = []
        self.dev.erase_count[:] = 0

    # ---------- metrics ----------
    @property
    def physical_writes(self) -> int:
        return self.host_writes + self.gc_writes

    @property
    def waf(self) -> float:
        return self.physical_writes / self.host_writes if self.host_writes else 1.0

    def sample_waf(self):
        self.waf_series.append((self.host_writes, self.waf))

    def snapshot(self) -> dict:
        dev = self.dev
        return {
            "host_writes": self.host_writes,
            "gc_writes": self.gc_writes,
            "physical_writes": self.physical_writes,
            "waf": self.waf,
            "erases": self.erases,
            "reads": self.reads,
            "time_us": self.time_us,
            "invalid_per_block": dev.invalid_count.copy(),
            "valid_per_block": dev.valid_count.copy(),
            "erase_per_block": dev.erase_count.copy(),
        }
