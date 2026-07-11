"""Conventional SSD vs ZNS write-amplification & wear comparison.

Runs identical workloads on:
  1. conventional device-managed SSD (greedy GC)            -> device WAF
  2. ZNS + host GC, single stream                           -> host WA
  3. ZNS + host GC, hot/cold zone separation                -> host WA

The hot/cold ZNS variant is expected to win on skewed (Zipf) workloads, because
the host can physically separate frequently-updated data from write-once data --
something a conventional device cannot do without host hints.
"""
from __future__ import annotations
from ..config import SSDConfig
from ..simulator import Simulator
from .. import workloads, metrics
from .zns_simulator import ZNSSimulator


def _cfg(op, small=False):
    if small:   # fast smoke: ~0.06 GiB, small zones
        return SSDConfig(channel=2, chip=2, die=2, plane=2, blocks_per_plane=32,
                         pages_per_block=32, op_ratio=op,
                         gc_high_watermark=0.95, gc_low_watermark=0.90)
    return SSDConfig(channel=2, chip=2, die=2, plane=4, blocks_per_plane=64,
                     pages_per_block=64, op_ratio=op,
                     gc_high_watermark=0.95, gc_low_watermark=0.90)


def _gen(pattern, n, lp, seed=0):
    return {
        "sequential": workloads.sequential(n, lp),
        "uniform":    workloads.uniform_random(n, lp, seed=seed),
        "zipf":       workloads.zipf(n, lp, s=1.2, seed=seed),
    }[pattern]


def run(op=0.10, small=False, fill=2, bpz=None):
    cfg = _cfg(op, small=small)
    lp = cfg.logical_pages
    n = int(lp * fill)
    rows = []
    for pat in ("sequential", "uniform", "zipf"):
        # 1. conventional
        conv = Simulator(cfg, scheme="s1", gc_policy="greedy")
        for lpn in _gen(pat, n, lp):
            conv.write(lpn)
        # 2. ZNS single-stream
        z1 = ZNSSimulator(cfg, blocks_per_zone=bpz, op_ratio=op, hot_cold=False)
        r1 = z1.run(_gen(pat, n, lp))
        # 3. ZNS hot/cold
        z2 = ZNSSimulator(cfg, blocks_per_zone=bpz, op_ratio=op, hot_cold=True)
        r2 = z2.run(_gen(pat, n, lp))
        rows.append((pat, conv.waf, r1["write_amplification"],
                     r2["write_amplification"],
                     metrics.gini(conv.snapshot()["erase_per_block"]),
                     r2["gini"]))
    return cfg, rows


if __name__ == "__main__":
    import sys, time
    small = "--small" in sys.argv
    t0 = time.time()
    cfg, rows = run(op=0.10, small=small, fill=2, bpz=4 if small else None)
    print(cfg.summary())
    print(f"(ran in {time.time()-t0:.1f}s)")
    print(f"\nWrite amplification (lower is better), OP=10%\n")
    hdr = f"{'workload':11} {'Conv WAF':>9} {'ZNS-1':>7} {'ZNS-HC':>7}   {'Conv Gini':>9} {'ZNS-HC Gini':>11}"
    print(hdr); print("-" * len(hdr))
    for pat, cw, z1, z2, cg, zg in rows:
        print(f"{pat:11} {cw:9.3f} {z1:7.3f} {z2:7.3f}   {cg:9.3f} {zg:11.3f}")
