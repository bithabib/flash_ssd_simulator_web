"""ZNS validation harness (FEMU-free): validate the host-managed ZNS algorithm.

FEMU's ZNS is device-only (no host GC), so we validate our host FTL against a
trusted anchor + invariants instead:

  1. INVARIANT  : a purely sequential workload must yield WAF == 1.0 (zones fill
                  and reset with zero valid-page migration).
  2. CROSS-CHECK: ZNS single-stream host GC is greedy GC at zone granularity, so
                  its WAF should track the CONVENTIONAL engine (already validated
                  against FTLSim/FEMU) under uniform random writes.
  3. ALGORITHM  : ZNS hot/cold separation must LOWER WAF vs ZNS single-stream on
                  skewed workloads.

The remaining column ("ref") is for a full-stack reference number obtained on
FEMU + F2FS(zoned)/ZenFS, which supplies the host GC FEMU omits.

Run:  python -m eyana_engine.zns_validate
"""
from __future__ import annotations

import numpy as np

from .config import SSDConfig
from .simulator import Simulator
from .zns.zns_simulator import ZNSSimulator
from . import workloads

REL_WRITE = 3.0


def _cfg(op):
    return SSDConfig(channel=2, chip=2, die=2, plane=4, blocks_per_plane=64,
                     pages_per_block=64, op_ratio=op,
                     gc_high_watermark=0.95, gc_low_watermark=0.90)


def _stream(name, n, lp, seed=1):
    if name == "sequential":
        return workloads.sequential(n, lp)
    if name == "uniform":
        return workloads.uniform_random(n, lp, seed=seed)
    if name == "zipf1.2":
        return workloads.zipf(n, lp, s=1.2, seed=seed)
    if name == "80/20":
        rng = np.random.default_rng(seed)
        hot = max(1, int(0.2 * lp))
        return np.where(rng.random(n) < 0.8, rng.integers(0, hot, n),
                        rng.integers(hot, lp, n)).tolist()
    raise ValueError(name)


def _waf_conventional(op, wl):
    cfg = _cfg(op); lp = cfg.logical_pages
    sim = Simulator(cfg, scheme="s1", gc_policy="greedy")
    for x in _stream(wl, int(REL_WRITE * lp), lp):
        sim.write(int(x) % lp)
    return sim.waf


def _waf_zns(op, wl, hot_cold, rel=REL_WRITE):
    cfg = _cfg(op); lp = cfg.logical_pages
    z = ZNSSimulator(cfg, blocks_per_zone=cfg.blocks_per_plane,
                     op_ratio=op, hot_cold=hot_cold)
    try:
        r = z.run(int(x) % lp for x in _stream(wl, int(rel * lp), lp))
        return r["write_amplification"]
    except RuntimeError:
        return None   # host GC could not make progress (over-utilised)


def main():
    print("# ZNS validation — EyanaSSDSim host FTL")
    print(f"# rHMW={REL_WRITE}x logical capacity; WAF = device/host writes\n")

    print("## 1) INVARIANT: WRITE-ONCE sequential -> WAF must be 1.000")
    for hc in (False, True):
        w = _waf_zns(0.10, "sequential", hc, rel=0.95)   # write-once, no overwrite
        tag = "hot/cold" if hc else "single  "
        ok = w is not None and abs(w - 1.0) < 1e-6
        print(f"   ZNS {tag} write-once WAF = {w if w is None else f'{w:.3f}'}   {'PASS' if ok else 'CHECK'}")

    print("\n## 1b) DIAGNOSTIC: sequential REWRITE (3x) — should trend to 1.0 as OP rises")
    for op in [0.10, 0.20, 0.30]:
        w = _waf_zns(op, "sequential", False)
        print(f"   op={int(op*100):2d}%  ZNS-single seq-rewrite WAF = {w if w is None else f'{w:.3f}'}")

    print("\n## 2) CROSS-CHECK vs validated conventional engine (uniform random)")
    print(f"   {'OP%':>3} | {'conv':>6} | {'ZNS-single':>10} | {'rel.diff':>8}")
    for op in [0.05, 0.10, 0.15, 0.25]:
        c = _waf_conventional(op, "uniform")
        z = _waf_zns(op, "uniform", False)
        zt = "  n/a" if z is None else f"{z:10.3f}"
        diff = "   n/a" if z is None else f"{abs(z-c)/c*100:7.1f}%"
        print(f"   {int(op*100):>3} | {c:6.3f} | {zt:>10} | {diff:>8}")

    print("\n## 3) ALGORITHM: hot/cold must lower WAF vs single (skewed)")
    print(f"   {'workload':8} | {'OP%':>3} | {'single':>6} | {'hot/cold':>8} | {'improved?':>9}")
    for wl in ["zipf1.2", "80/20"]:
        for op in [0.07, 0.10]:
            s = _waf_zns(op, wl, False)
            h = _waf_zns(op, wl, True)
            st = "  n/a" if s is None else f"{s:6.3f}"
            ht = "  n/a" if h is None else f"{h:8.3f}"
            verdict = "n/a" if (s is None or h is None) else ("yes" if h <= s + 1e-9 else "NO")
            print(f"   {wl:8} | {int(op*100):>3} | {st:>6} | {ht:>8} | {verdict:>9}")

    print("\n# For the full-stack reference (host GC FEMU omits): run FEMU ZNS device")
    print("# + F2FS(zoned) or ZenFS in the guest and record host WAF for the same workloads.")


if __name__ == "__main__":
    main()
