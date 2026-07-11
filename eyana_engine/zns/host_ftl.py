"""Host-side FTL for a ZNS device: log-structured mapping + host garbage collection.

Because a ZNS device forbids in-place update and does no GC itself, the host must
(1) map LPNs onto sequential zone appends, and (2) reclaim space by migrating the
valid pages of a victim zone and then resetting it.

Two placement strategies are supported:
  * single-stream: all writes (and migrations) go to one open zone.
  * hot/cold separation: overwrites go to a "hot" zone, first-writes/migrations to
    a "cold" zone. This is the capability a conventional block device cannot offer
    without hints, and it is where ZNS reduces write amplification on skewed loads.

Total write amplification (host-visible) = device_writes / host_writes, where
device_writes = host appends + GC migration appends.
"""
from __future__ import annotations
import numpy as np
from .zns_device import ZNSDevice, FREE
from .zone import ZoneState


class HostFTL:
    def __init__(self, dev: ZNSDevice, op_ratio: float = 0.10,
                 hot_cold: bool = False):
        self.dev = dev
        cfg = dev.cfg
        self.hot_cold = hot_cold
        self.forward = np.full(cfg.logical_pages, FREE, dtype=np.int32)  # lpn -> ppn
        self.valid_in_zone = np.zeros(dev.n_zones, dtype=np.int64)
        self.free_zones = list(range(dev.n_zones))   # all EMPTY at start
        # GC headroom = open streams + a migration spare. The actual
        # over-provisioning slack that keeps GC progressing comes from logical
        # capacity being (1-op)*physical, NOT from reserving the whole OP as
        # free zones (doing so leaves GC zero working room -> infinite loop).
        n_streams = 2 if hot_cold else 1
        self.min_free = n_streams + 2
        if dev.n_zones <= self.min_free:
            raise ValueError(f"too few zones ({dev.n_zones}) for {n_streams} "
                             f"streams; use smaller blocks_per_zone")
        self.open = {"hot": None, "cold": None}       # stream -> zone id
        self.host_writes = 0
        self.gc_writes = 0

    # ---------- write path ----------
    def write(self, lpn: int):
        if not (0 <= lpn < self.dev.cfg.logical_pages):
            raise IndexError(f"lpn {lpn} out of host logical range")
        stream = "hot" if (self.hot_cold and self.forward[lpn] != FREE) else "cold"
        self._append(lpn, stream, is_gc=False)
        self._maybe_gc()

    # ---------- internals ----------
    def _open_zone_for(self, stream: str) -> int:
        z = self.open[stream]
        if z is not None and self.dev.state[z] == ZoneState.OPEN:
            return z
        # need a fresh zone
        if not self.free_zones:
            raise RuntimeError("no free zone to open (raise op_ratio)")
        z = self.free_zones.pop()
        self.open[stream] = z
        return z

    def _append(self, lpn: int, stream: str, is_gc: bool):
        dev = self.dev
        # invalidate previous location
        old = self.forward[lpn]
        if old != FREE:
            self.valid_in_zone[old // dev.zone_pages] -= 1
        z = self._open_zone_for(stream)
        ppn = dev.append(z, lpn)
        self.forward[lpn] = ppn
        self.valid_in_zone[z] += 1
        if is_gc:
            self.gc_writes += 1
        else:
            self.host_writes += 1

    def _maybe_gc(self):
        # keep at least min_free empty zones available; guard against a
        # no-progress loop when the device is genuinely over-utilised.
        guard = 0
        limit = 2 * self.dev.n_zones
        while len(self.free_zones) < self.min_free:
            before = len(self.free_zones)
            if not self._gc_once():
                break
            guard += 1
            if len(self.free_zones) <= before and guard > limit:
                raise RuntimeError(
                    "ZNS host GC made no progress; device over-utilised "
                    "(raise op_ratio or reduce workload footprint)")

    def _victim(self):
        """Greedy: FULL, non-open zone with the fewest valid pages."""
        dev = self.dev
        best, best_valid = -1, None
        open_ids = {self.open["hot"], self.open["cold"]}
        for z in range(dev.n_zones):
            if dev.state[z] != ZoneState.FULL or z in open_ids:
                continue
            v = self.valid_in_zone[z]
            if best_valid is None or v < best_valid:
                best_valid, best = v, z
        return best

    def _gc_once(self) -> bool:
        dev = self.dev
        z = self._victim()
        if z < 0:
            return False
        base = dev.zone_base_ppn(z)
        # Vectorised live-page scan: a page is live iff its LPN maps back to it.
        seg = dev.reverse[base:base + dev.zone_pages]        # lpn at each page (or FREE)
        occ = np.nonzero(seg != FREE)[0]                     # occupied offsets
        if occ.size:
            lpns = seg[occ]
            live_mask = self.forward[lpns] == (base + occ)   # still current?
            live_lpns = lpns[live_mask]
            # migrate in physical order (sequential-append safe) to the cold stream
            for lpn in live_lpns:
                self._append(int(lpn), "cold", is_gc=True)
        dev.reset(z)
        self.valid_in_zone[z] = 0
        self.free_zones.append(z)
        return True

    # ---------- metrics ----------
    @property
    def write_amplification(self) -> float:
        w = self.host_writes
        return (self.host_writes + self.gc_writes) / w if w else 1.0
