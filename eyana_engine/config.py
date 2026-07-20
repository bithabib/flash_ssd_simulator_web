"""SSD configuration with validation.

Fixes audit findings A1 (degenerate chip=1 makes S2==S4, S3==S5) and A6/C4
(no GC-headroom validation) by refusing invalid geometries up front.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class SSDConfig:
    # --- geometry (parallel units) ---
    channel: int = 2
    chip: int = 2          # per channel.  MUST be >= 2 or S2==S4 and S3==S5 (audit A1)
    die: int = 2           # per chip
    plane: int = 4         # per die
    blocks_per_plane: int = 256   # blocks in each plane
    pages_per_block: int = 64
    page_size: int = 4096  # bytes

    # --- FTL / GC ---
    op_ratio: float = 0.10        # over-provisioning fraction of raw capacity
    gc_high_watermark: float = 0.95   # start GC when plane free blocks fall below (1-this)
    gc_low_watermark: float = 0.90    # stop GC once utilisation drops to this
    gc_policy: str = "greedy"         # "greedy" | "cost_benefit" | "fifo"
    gc_granularity: str = "block"     # "block" (per-plane) | "superblock" (FEMU line-GC)

    # --- latency model (microseconds) ---
    t_read_page: float = 40.0
    t_write_page: float = 200.0
    t_erase_block: float = 2000.0

    # ---- derived ----
    @property
    def planes(self) -> int:
        return self.channel * self.chip * self.die * self.plane

    @property
    def total_blocks(self) -> int:
        return self.planes * self.blocks_per_plane

    @property
    def total_pages(self) -> int:
        return self.total_blocks * self.pages_per_block

    @property
    def raw_capacity_bytes(self) -> int:
        return self.total_pages * self.page_size

    @property
    def logical_pages(self) -> int:
        """User-visible pages after reserving OP."""
        return int(self.total_pages * (1.0 - self.op_ratio))

    def validate(self) -> None:
        g = dict(channel=self.channel, chip=self.chip, die=self.die,
                 plane=self.plane, blocks_per_plane=self.blocks_per_plane,
                 pages_per_block=self.pages_per_block)
        for k, v in g.items():
            if v < 1:
                raise ValueError(f"{k} must be >= 1 (got {v})")
        # Audit A1: with only one chip the chip dimension is degenerate and the
        # six allocation schemes collapse to three (S2==S4, S3==S5).
        if self.chip < 2:
            raise ValueError(
                "chip must be >= 2, otherwise S2==S4 and S3==S5 "
                "(allocation-scheme comparison would be invalid; audit finding A1)")
        if not (0.0 <= self.op_ratio < 1.0):
            raise ValueError("op_ratio must be in [0, 1)")
        if not (0.0 < self.gc_low_watermark < self.gc_high_watermark < 1.0):
            raise ValueError("require 0 < gc_low_watermark < gc_high_watermark < 1")
        if self.gc_granularity not in ("block", "superblock"):
            raise ValueError("gc_granularity must be 'block' or 'superblock'")
        # Need at least one spare (erased) block per plane for GC to migrate into.
        if self.blocks_per_plane < 2:
            raise ValueError("blocks_per_plane must be >= 2 to leave GC headroom")
        return None

    def summary(self) -> str:
        gb = self.raw_capacity_bytes / (1024 ** 3)
        return (f"SSD {gb:.2f} GiB raw | {self.total_blocks} blocks x "
                f"{self.pages_per_block} pages | planes={self.planes} "
                f"(ch{self.channel} cp{self.chip} di{self.die} pl{self.plane}) | "
                f"OP={self.op_ratio:.0%} | GC={self.gc_policy}")
