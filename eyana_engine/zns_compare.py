"""ZNS validation figure: host-managed ZNS FTL — single-stream vs hot/cold zone
separation across OP (80/20 workload), plus the sequential->WAF=1 invariant
(corroborated on FEMU's ZNS device: append-only zones, reset, no device GC).

Smaller-but-representative geometry so the (slow) host-GC sim is tractable; this
figure shows the *algorithmic trend*, not FEMU magnitude matching (FEMU ZNS has
no host GC, so magnitude must come from the analytical host FTL).
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .config import SSDConfig
from .zns.zns_simulator import ZNSSimulator
from .simulator import Simulator
from . import workloads

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REL = 3.0
GEO = dict(channel=2, chip=2, die=2, plane=4, blocks_per_plane=32, pages_per_block=32)


def wl_8020(n, lp, seed=1):
    rng = np.random.default_rng(seed)
    hot = max(1, int(0.2 * lp))
    return np.where(rng.random(n) < 0.8, rng.integers(0, hot, n),
                    rng.integers(hot, lp, n)).tolist()


def zns_waf(op, hot_cold, seq=False):
    cfg = SSDConfig(op_ratio=op, gc_high_watermark=0.95, gc_low_watermark=0.90, **GEO)
    lp = cfg.logical_pages
    z = ZNSSimulator(cfg, blocks_per_zone=cfg.blocks_per_plane, op_ratio=op, hot_cold=hot_cold)
    if seq:
        stream = workloads.sequential(int(0.95 * lp), lp)   # write-once
    else:
        stream = (int(x) % lp for x in wl_8020(int(REL * lp), lp))
    try:
        return z.run(stream)["write_amplification"]
    except RuntimeError:
        return None


def conv_waf(op):
    cfg = SSDConfig(op_ratio=op, gc_high_watermark=0.95, gc_low_watermark=0.90, **GEO)
    lp = cfg.logical_pages
    sim = Simulator(cfg, scheme="s1", gc_policy="greedy")
    for x in wl_8020(int(REL * lp), lp):
        sim.write(int(x) % lp)
    return sim.waf


ops = [0.10, 0.15, 0.25]
single = [zns_waf(o, False) for o in ops]
hotcold = [zns_waf(o, True) for o in ops]
conv = [conv_waf(o) for o in ops]
seq_single = zns_waf(0.10, False, seq=True)
seq_hc = zns_waf(0.10, True, seq=True)

print("ZNS validation (80/20 workload):")
print(f"  sequential write-once -> WAF: single={seq_single:.3f}  hot/cold={seq_hc:.3f}  "
      f"(invariant = 1.0; FEMU device confirms)")
print(f"{'OP%':>4} | {'conv':>6} | {'ZNS-1':>6} | {'ZNS-hc':>6} | {'hc gain':>7}")
for i, o in enumerate(ops):
    g = "n/a" if (single[i] is None or hotcold[i] is None) else f"{(1-hotcold[i]/single[i])*100:.1f}%"
    print(f"{int(o*100):>4} | {conv[i]:6.3f} | {single[i]:6.3f} | {hotcold[i]:6.3f} | {g:>7}")

opx = [int(o * 100) for o in ops]
fig, ax = plt.subplots(figsize=(6.4, 4.3))
ax.plot(opx, conv,    "^:",  color="#7f8c8d", lw=1.8, ms=7, label="Conventional (reference)")
ax.plot(opx, single,  "s--", color="#2471a3", lw=2.0, ms=7, label="ZNS single-stream")
ax.plot(opx, hotcold, "o-",  color="#1e8449", lw=2.2, ms=8, label="ZNS hot/cold separation")
ax.axhline(1.0, color="#c0392b", lw=1.5, ls="-.", label="Sequential invariant (WAF=1, FEMU-confirmed)")
ax.set_xlabel("Over-provisioning (%)")
ax.set_ylabel("Write Amplification Factor (WAF)")
ax.set_title("ZNS host-managed GC — EyanaSSD (80/20 workload)")
ax.grid(True, alpha=0.3)
ax.legend(fontsize=8.5)
fig.tight_layout()
os.makedirs(os.path.join(ROOT, "figures"), exist_ok=True)
fig.savefig(os.path.join(ROOT, "figures", "zns_validation.png"), dpi=150)
print("wrote figures/zns_validation.png")
