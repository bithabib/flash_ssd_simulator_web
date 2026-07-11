"""Run a workload on the headless engine and yield grid snapshots on a fixed
wall-clock interval, so the browser sees almost-live changes with a time/ETA.

Used by the web backend to stream SSD state to the browser (Server-Sent
Events), moving the heavy simulation off the browser onto the corrected engine.
"""
from __future__ import annotations
import time

from .config import SSDConfig
from .simulator import Simulator
from . import workloads


def default_cfg(op=0.10, channel=2, chip=2, die=2, plane=4,
                blocks_per_plane=38, ppb=256):
    """A small, visualization-friendly device by default (1.27 GB-class).

    channel/chip/die/plane are user-selectable so the live grid can mirror the
    parallel geometry drawn by the advance simulator.
    """
    return SSDConfig(channel=channel, chip=chip, die=die, plane=plane,
                     blocks_per_plane=blocks_per_plane, pages_per_block=ppb,
                     page_size=4096, op_ratio=op, gc_policy="greedy",
                     gc_high_watermark=0.95, gc_low_watermark=0.90)


def _snapshot(sim, phase, done, total, phase_start):
    """Build a snapshot dict including progress, throughput and ETA."""
    dev = sim.dev
    elapsed = max(1e-6, time.monotonic() - phase_start)
    rate = done / elapsed  # writes per second in this phase
    remaining = max(0, total - done)
    eta = remaining / rate if rate > 0 else 0.0
    return {
        "phase": phase,                 # "preconditioning" | "running" | "done"
        "progress": round(min(100.0, 100.0 * done / total), 2) if total else 100.0,
        "host_writes": sim.host_writes,
        "gc_writes": sim.gc_writes,
        "waf": round(sim.waf, 4),
        "erases": sim.erases,
        "elapsed_sec": round(elapsed, 1),
        "eta_sec": round(eta, 1),
        "writes_per_sec": int(rate),
        "invalid": dev.invalid_count.tolist(),
        "valid": dev.valid_count.tolist(),
        "erase": dev.erase_count.tolist(),
        "total_blocks": dev.cfg.total_blocks,
        # parallel geometry so the frontend can draw the nested channel/chip/
        # die/plane grid and map each flat block index back to its unit.
        "geo": {
            "channel": dev.cfg.channel,
            "chip": dev.cfg.chip,
            "die": dev.cfg.die,
            "plane": dev.cfg.plane,
            "blocks_per_plane": dev.cfg.blocks_per_plane,
            "pages_per_block": dev.cfg.pages_per_block,
            "size_gb": round(dev.cfg.raw_capacity_bytes / (1024 ** 3), 2),
        },
    }


def _reader(kind):
    if kind == "etw":
        return workloads.etw_trace_writes
    if kind == "msr":
        return workloads.msr_trace_writes
    raise ValueError(f"unknown trace kind {kind!r}")


def simulate_stream(trace_path, kind="msr", op=0.10, interval_sec=1.0,
                    limit=2_000_000, precondition=0.80,
                    channel=2, chip=2, die=2, plane=4, blocks_per_plane=38,
                    pages_per_block=256):
    """Generator: replays `trace_path` through the engine and yields a grid
    snapshot roughly every `interval_sec` seconds of wall-clock (plus a final
    snapshot). Snapshots are emitted during BOTH preconditioning and the trace
    replay, so the user sees progress and an ETA immediately.
    """
    cfg = default_cfg(op=op, channel=channel, chip=chip, die=die, plane=plane,
                      blocks_per_plane=blocks_per_plane, ppb=pages_per_block)
    sim = Simulator(cfg, scheme="s1", gc_policy="greedy")
    lp = cfg.logical_pages

    # phase 1: precondition to ~80% valid so GC engages (stream by time)
    if precondition:
        fill = min(int(precondition * cfg.total_pages), int(0.98 * lp))
        p_start = time.monotonic()
        last = p_start
        yield _snapshot(sim, "preconditioning", 0, fill, p_start)  # immediate
        for p in range(fill):
            sim.write(p)
            now = time.monotonic()
            if now - last >= interval_sec:
                last = now
                yield _snapshot(sim, "preconditioning", p + 1, fill, p_start)
        sim.reset_counters()

    # phase 2: replay the trace lazily (no full materialization), stream by time
    reader = _reader(kind)
    r_start = time.monotonic()
    last = r_start
    n = 0
    yield _snapshot(sim, "running", 0, limit, r_start)  # immediate
    for lpn in reader(trace_path, page_size=4096, max_lpn=lp):
        sim.write(int(lpn) % lp)
        n += 1
        now = time.monotonic()
        if now - last >= interval_sec:
            last = now
            yield _snapshot(sim, "running", n, limit, r_start)
        if limit and n >= limit:
            break

    yield _snapshot(sim, "done", 1, 1, r_start)  # final state, 100%
