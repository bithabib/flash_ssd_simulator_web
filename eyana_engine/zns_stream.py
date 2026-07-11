"""Stream a workload through the ZNS host FTL and yield per-ZONE snapshots.

Mirrors stream_sim.py but for the Zoned Namespace subsystem: the device exposes
sequential-write zones and does NO GC; the host FTL maps LPNs onto zone appends
and reclaims space by migrating valid pages and resetting whole zones, optionally
with hot/cold zone separation. Each snapshot carries per-zone state so the browser
can animate zones filling, being chosen as GC victims, and resetting.
"""
from __future__ import annotations
import time

from .config import SSDConfig
from .zns.zns_device import ZNSDevice
from .zns.host_ftl import HostFTL
from . import workloads


def _reader(kind):
    if kind == "etw":
        return workloads.etw_trace_writes
    if kind == "msr":
        return workloads.msr_trace_writes
    raise ValueError(f"unknown trace kind {kind!r}")


def _zsnapshot(host, dev, phase, done, total, phase_start):
    elapsed = max(1e-6, time.monotonic() - phase_start)
    rate = done / elapsed
    remaining = max(0, total - done)
    eta = remaining / rate if rate > 0 else 0.0
    return {
        "engine": "zns",
        "phase": phase,
        "progress": round(min(100.0, 100.0 * done / total), 2) if total else 100.0,
        "host_writes": int(host.host_writes),
        "gc_writes": int(host.gc_writes),
        "wa": round(host.write_amplification, 4),
        "zone_resets": int(dev.total_resets),
        "elapsed_sec": round(elapsed, 1),
        "eta_sec": round(eta, 1),
        "writes_per_sec": int(rate),
        "hot_cold": bool(host.hot_cold),
        "n_zones": int(dev.n_zones),
        "blocks_per_zone": int(dev.bpz),
        "zone_pages": int(dev.zone_pages),
        "open_hot": int(host.open["hot"]) if host.open["hot"] is not None else -1,
        "open_cold": int(host.open["cold"]) if host.open["cold"] is not None else -1,
        # per-zone arrays (length n_zones)
        "zone_state": dev.state.tolist(),          # 0 EMPTY 1 OPEN 2 FULL 3 CLOSED
        "zone_valid": host.valid_in_zone.tolist(),  # live pages currently in zone
        "zone_wp": dev.wp.tolist(),                # write pointer (pages written)
        "zone_reset": dev.zone_reset_count.tolist(),
    }


def simulate_zns_stream(trace_path, kind="msr", op=0.10, interval_sec=1.0,
                        limit=2_000_000, precondition=0.0,
                        channel=2, chip=2, die=2, plane=4, blocks_per_plane=38,
                        pages_per_block=256, blocks_per_zone=None, hot_cold=True):
    """Generator: replay `trace_path` through a ZNS device + host FTL, yielding a
    per-zone snapshot roughly every `interval_sec` wall-clock seconds.
    """
    cfg = SSDConfig(channel=channel, chip=chip, die=die, plane=plane,
                    blocks_per_plane=blocks_per_plane, pages_per_block=pages_per_block,
                    op_ratio=op, gc_high_watermark=0.95, gc_low_watermark=0.90)
    bpz = blocks_per_zone or cfg.blocks_per_plane   # default: one plane per zone
    dev = ZNSDevice(cfg, bpz)
    host = HostFTL(dev, op_ratio=op, hot_cold=hot_cold)
    lp = cfg.logical_pages

    # phase 1: precondition with sequential first-writes so zones fill up
    if precondition:
        fill = min(int(precondition * lp), lp - 1)
        p_start = time.monotonic()
        last = p_start
        yield _zsnapshot(host, dev, "preconditioning", 0, fill, p_start)
        for p in range(fill):
            host.write(p)
            now = time.monotonic()
            if now - last >= interval_sec:
                last = now
                yield _zsnapshot(host, dev, "preconditioning", p + 1, fill, p_start)
        # measure the trace phase in isolation
        host.host_writes = 0
        host.gc_writes = 0

    # phase 2: replay the trace (LPNs wrap into the host logical range)
    reader = _reader(kind)
    r_start = time.monotonic()
    last = r_start
    n = 0
    yield _zsnapshot(host, dev, "running", 0, limit, r_start)
    for lpn in reader(trace_path, page_size=4096, max_lpn=lp):
        host.write(int(lpn) % lp)
        n += 1
        now = time.monotonic()
        if now - last >= interval_sec:
            last = now
            yield _zsnapshot(host, dev, "running", n, limit, r_start)
        if limit and n >= limit:
            break

    yield _zsnapshot(host, dev, "done", 1, 1, r_start)
