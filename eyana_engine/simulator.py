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

    def _gc_superblock(self, p: int, force: bool = False):
        """FEMU-style GC at *line/superblock* granularity.

        A line L is the set of blocks {plane*bpp + L for every plane}; FEMU
        erases a whole line at once, so the victim is chosen by aggregate invalid
        pages across the line and ALL its blocks' live pages are migrated. Trigger
        is device-global utilisation with the same high/low watermarks.
        """
        dev, cfg = self.dev, self.cfg
        nblocks = cfg.total_blocks
        bpp, planes = dev.bpp, dev.planes
        while True:
            used = nblocks - int(dev.is_free.sum())
            if not force and used / nblocks <= cfg.gc_low_watermark:
                break
            # within-plane indices currently used as an active (open) block
            active_L = {int(ab) % bpp for ab in dev.active_block if ab != -1}
            best_L, best_inv = -1, 0
            for L in range(bpp):
                if L in active_L:
                    continue                       # never GC the open line
                inv, allfree = 0, True
                for pp in range(planes):
                    b = pp * bpp + L
                    if not dev.is_free[b]:
                        allfree = False
                        inv += int(dev.invalid_count[b])
                if allfree:
                    continue
                if inv > best_inv:
                    best_inv, best_L = inv, L
            if best_L < 0 or best_inv == 0:
                break                              # nothing worth reclaiming
            self._reclaim_line(best_L)
            force = False

    def _reclaim_line(self, L: int):
        """Migrate live pages of every block in line L (each staying in its own
        plane), then erase the whole line."""
        dev = self.dev
        ppb, bpp = self.cfg.pages_per_block, self.dev.bpp
        for pp in range(dev.planes):
            b = pp * bpp + L
            if dev.is_free[b]:
                continue
            base = b * ppb
            for off in range(ppb):
                ppn = base + off
                lpn = dev.reverse_map[ppn]
                if lpn != FREE and dev.forward_map[lpn] == ppn:
                    new_ppn = dev.alloc_page(pp)
                    if new_ppn is None:
                        raise RuntimeError("no free page for superblock GC "
                                           "migration; raise OP or watermark")
                    dev.valid_count[b] -= 1
                    self._place(lpn, new_ppn, host=False)
            dev.erase_block(b)
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
