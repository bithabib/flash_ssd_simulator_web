"""Stream a workload through the FDP engine and yield per-BLOCK snapshots.

Mirrors stream_sim.py / zns_stream.py but for Flexible Data Placement: the device
still does its own garbage collection, but each block belongs to one placement
handle (hot/cold), so snapshots carry a per-block `handle` array the frontend
uses to tint reclaim units by handle on top of the valid/invalid coloring.
"""
from __future__ import annotations
import time

from .config import SSDConfig
from .fdp.fdp_engine import FDPEngine
from . import workloads


def _reader(kind):
    if kind == "etw":
        return workloads.etw_trace_writes
    if kind == "msr":
        return workloads.msr_trace_writes
    raise ValueError(f"unknown trace kind {kind!r}")


def _fsnapshot(eng, cfg, phase, done, total, phase_start):
    elapsed = max(1e-6, time.monotonic() - phase_start)
    rate = done / elapsed
    remaining = max(0, total - done)
    eta = remaining / rate if rate > 0 else 0.0
    return {
        "engine": "fdp",
        "phase": phase,
        "progress": round(min(100.0, 100.0 * done / total), 2) if total else 100.0,
        "host_writes": int(eng.host_writes),
        "gc_writes": int(eng.gc_writes),
        "waf": round(eng.waf, 4),
        "erases": int(eng.erases),
        "elapsed_sec": round(elapsed, 1),
        "eta_sec": round(eta, 1),
        "writes_per_sec": int(rate),
        "hot_cold": bool(eng.hot_cold),
        "invalid": eng.invalid_count.tolist(),
        "valid": eng.valid_count.tolist(),
        "erase": eng.erase_count.tolist(),
        "handle": eng.block_handle.tolist(),   # -1 free, 0 hot, 1 cold
        "total_blocks": int(eng.nblocks),
        "geo": {
            "channel": cfg.channel, "chip": cfg.chip, "die": cfg.die,
            "plane": cfg.plane, "blocks_per_plane": cfg.blocks_per_plane,
            "pages_per_block": cfg.pages_per_block,
            "size_gb": round(cfg.raw_capacity_bytes / (1024 ** 3), 2),
        },
    }


def simulate_fdp_stream(trace_path, kind="msr", op=0.10, interval_sec=1.0,
                        limit=2_000_000, precondition=0.0,
                        channel=2, chip=2, die=2, plane=4, blocks_per_plane=38,
                        pages_per_block=256, hot_cold=True):
    """Generator: replay `trace_path` through the FDP engine, yielding a per-block
    snapshot roughly every `interval_sec` wall-clock seconds."""
    cfg = SSDConfig(channel=channel, chip=chip, die=die, plane=plane,
                    blocks_per_plane=blocks_per_plane, pages_per_block=pages_per_block,
                    op_ratio=op, gc_high_watermark=0.95, gc_low_watermark=0.90)
    eng = FDPEngine(cfg, hot_cold=hot_cold)
    lp = cfg.logical_pages

    # phase 1: precondition (sequential first-writes) so the device is full and
    # GC engages during the visible trace replay -- same as the conventional mode.
    if precondition:
        fill = min(int(precondition * lp), lp - 1)
        p_start = time.monotonic()
        last = p_start
        yield _fsnapshot(eng, cfg, "preconditioning", 0, fill, p_start)
        for p in range(fill):
            eng.write(p)
            now = time.monotonic()
            if now - last >= interval_sec:
                last = now
                yield _fsnapshot(eng, cfg, "preconditioning", p + 1, fill, p_start)
        eng.reset_counters()

    # phase 2: replay the trace lazily
    reader = _reader(kind)
    r_start = time.monotonic()
    last = r_start
    n = 0
    yield _fsnapshot(eng, cfg, "running", 0, limit, r_start)
    for lpn in reader(trace_path, page_size=4096, max_lpn=lp):
        eng.write(int(lpn) % lp)
        n += 1
        now = time.monotonic()
        if now - last >= interval_sec:
            last = now
            yield _fsnapshot(eng, cfg, "running", n, limit, r_start)
        if limit and n >= limit:
            break

    yield _fsnapshot(eng, cfg, "done", 1, 1, r_start)
