"""Physical device state: blocks, pages, and the page-level FTL maps.

Design notes tied to the audit:
* host vs GC writes are counted separately (fixes A-WAF pollution / C2).
* a block is full only when offset == pages_per_block (fixes off-by-one A3).
* page liveness is derived from the maps; per-block valid/invalid counters are
  maintained incrementally and cross-checked in tests.
* GC never erases a block whose valid pages have not been migrated (fixes C1).

ppn layout is arithmetic:  ppn = block_id * pages_per_block + offset.
"""
from __future__ import annotations
import numpy as np
from .config import SSDConfig

FREE = -1  # sentinel for "no LPN occupies this physical page"


class Device:
    def __init__(self, cfg: SSDConfig):
        cfg.validate()
        self.cfg = cfg
        ppb = cfg.pages_per_block
        nblocks = cfg.total_blocks
        npages = cfg.total_pages

        # FTL maps (int32 is safe for < ~8 TB at 4 KB pages)
        self.forward_map = np.full(cfg.logical_pages, FREE, dtype=np.int32)  # lpn -> ppn
        self.reverse_map = np.full(npages, FREE, dtype=np.int32)             # ppn -> lpn

        # per-block metadata
        self.valid_count = np.zeros(nblocks, dtype=np.int32)
        self.invalid_count = np.zeros(nblocks, dtype=np.int32)
        self.erase_count = np.zeros(nblocks, dtype=np.int64)
        self.created_seq = np.zeros(nblocks, dtype=np.int64)   # FIFO age
        self.last_modified = np.zeros(nblocks, dtype=np.int64)  # cost-benefit age
        self.is_free = np.ones(nblocks, dtype=bool)             # erased & unallocated

        # per-plane allocation cursors
        self.planes = cfg.planes
        self.bpp = cfg.blocks_per_plane
        self.active_block = np.full(self.planes, -1, dtype=np.int64)
        self.active_offset = np.zeros(self.planes, dtype=np.int64)
        # free block lists, one per plane (all blocks start free)
        self.free_list = [list(range(p * self.bpp, (p + 1) * self.bpp))
                          for p in range(self.planes)]

        self.now_seq = 0  # monotonically increasing write clock

    # ---- helpers ----
    def plane_of_block(self, block: int) -> int:
        return block // self.bpp

    def plane_used_blocks(self, p: int) -> int:
        return self.bpp - len(self.free_list[p])

    def plane_utilisation(self, p: int) -> float:
        return self.plane_used_blocks(p) / self.bpp

    # ---- page allocation within a plane (log-structured) ----
    def alloc_page(self, p: int):
        """Return a fresh ppn in plane p, or None if the plane has no free page."""
        ppb = self.cfg.pages_per_block
        ab = self.active_block[p]
        if ab == -1 or self.active_offset[p] == ppb:      # need a new block
            if not self.free_list[p]:
                return None
            ab = self.free_list[p].pop()
            self.active_block[p] = ab
            self.active_offset[p] = 0
            self.is_free[ab] = False
            self.created_seq[ab] = self.now_seq
        off = self.active_offset[p]
        self.active_offset[p] += 1
        return ab * ppb + off

    def is_page_valid(self, ppn: int) -> bool:
        lpn = self.reverse_map[ppn]
        return lpn != FREE and self.forward_map[lpn] == ppn

    # ---- erase a block and return it to its plane's free pool ----
    def erase_block(self, block: int):
        ppb = self.cfg.pages_per_block
        base = block * ppb
        self.reverse_map[base:base + ppb] = FREE
        self.valid_count[block] = 0
        self.invalid_count[block] = 0
        self.erase_count[block] += 1
        self.is_free[block] = True
        p = self.plane_of_block(block)
        if self.active_block[p] == block:
            self.active_block[p] = -1
            self.active_offset[p] = 0
        self.free_list[p].append(block)
