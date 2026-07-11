"""Drive a workload through the host FTL onto a ZNS device and collect metrics."""
from __future__ import annotations
import numpy as np
from ..config import SSDConfig
from .. import metrics
from .zns_device import ZNSDevice
from .host_ftl import HostFTL


class ZNSSimulator:
    def __init__(self, cfg: SSDConfig, blocks_per_zone: int = None,
                 op_ratio: float = None, hot_cold: bool = False):
        self.cfg = cfg
        bpz = blocks_per_zone or cfg.blocks_per_plane   # default: one plane per zone
        self.dev = ZNSDevice(cfg, bpz)
        self.host = HostFTL(self.dev, op_ratio if op_ratio is not None
                            else cfg.op_ratio, hot_cold=hot_cold)

    def run(self, lpn_iter):
        for lpn in lpn_iter:
            self.host.write(int(lpn))
        return self.report()

    def report(self) -> dict:
        dev, host = self.dev, self.host
        wr = metrics.wear_report(dev.erase_count)
        return {
            "write_amplification": host.write_amplification,
            "host_writes": host.host_writes,
            "gc_writes": host.gc_writes,
            "device_writes": dev.device_writes,
            "zone_resets": dev.total_resets,
            "n_zones": dev.n_zones,
            "mean_erase": wr["mean_erase"],
            "doec_std": wr["doec_std"],
            "cv": wr["cv"],
            "gini": wr["gini"],
            "fourier_sigma": wr["fourier_sigma"],
            "erase_per_block": dev.erase_count.copy(),
            "zone_reset_count": dev.zone_reset_count.copy(),
        }
