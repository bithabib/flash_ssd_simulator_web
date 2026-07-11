"""ZNS device: physical zones over the standard geometry.

A zone spans `blocks_per_zone` physical blocks and must be written strictly
sequentially (enforced here). The device performs NO garbage collection --
space is reclaimed only by an explicit whole-zone reset, which erases every
block in the zone. This is the defining ZNS contract; the host (HostFTL) is
responsible for valid-page migration and reclaim.
"""
from __future__ import annotations
import numpy as np
from ..config import SSDConfig
from .zone import ZoneState

FREE = -1


class ZNSDevice:
    def __init__(self, cfg: SSDConfig, blocks_per_zone: int):
        cfg.validate()
        if cfg.total_blocks % blocks_per_zone != 0:
            raise ValueError(
                f"total_blocks ({cfg.total_blocks}) must be divisible by "
                f"blocks_per_zone ({blocks_per_zone})")
        self.cfg = cfg
        self.bpz = blocks_per_zone
        self.n_zones = cfg.total_blocks // blocks_per_zone
        self.zone_pages = blocks_per_zone * cfg.pages_per_block

        self.wp = np.zeros(self.n_zones, dtype=np.int64)        # write ptr (page offset)
        self.state = np.full(self.n_zones, ZoneState.EMPTY, dtype=np.int8)
        self.reverse = np.full(cfg.total_pages, FREE, dtype=np.int32)  # ppn -> lpn
        self.erase_count = np.zeros(cfg.total_blocks, dtype=np.int64)
        self.zone_reset_count = np.zeros(self.n_zones, dtype=np.int64)
        self.device_writes = 0   # total physical page programs (host appends + migrations)
        self.total_resets = 0

    def zone_base_ppn(self, z: int) -> int:
        return z * self.zone_pages

    def append(self, z: int, lpn: int) -> int:
        """Sequentially append one page for `lpn` to zone `z`; return its ppn."""
        if self.state[z] == ZoneState.EMPTY:
            self.state[z] = ZoneState.OPEN
        if self.state[z] != ZoneState.OPEN:
            raise RuntimeError(f"zone {z} not open (state={ZoneState(self.state[z]).name})")
        if self.wp[z] >= self.zone_pages:
            raise RuntimeError(f"zone {z} full")
        ppn = self.zone_base_ppn(z) + int(self.wp[z])
        self.reverse[ppn] = lpn
        self.wp[z] += 1
        self.device_writes += 1
        if self.wp[z] == self.zone_pages:
            self.state[z] = ZoneState.FULL
        return ppn

    def reset(self, z: int) -> None:
        """Erase the whole zone (every block), returning it to EMPTY."""
        base = self.zone_base_ppn(z)
        self.reverse[base:base + self.zone_pages] = FREE
        self.wp[z] = 0
        self.state[z] = ZoneState.EMPTY
        self.zone_reset_count[z] += 1
        self.total_resets += 1
        b0 = z * self.bpz
        self.erase_count[b0:b0 + self.bpz] += 1

    def summary(self) -> str:
        zmb = self.zone_pages * self.cfg.page_size / (1024 ** 2)
        return (f"ZNS: {self.n_zones} zones x {self.bpz} blocks "
                f"({zmb:.1f} MiB/zone, {self.zone_pages} pages/zone)")
