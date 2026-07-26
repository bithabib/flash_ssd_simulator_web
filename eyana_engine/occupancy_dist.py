"""Occupancy distribution figure: for each workload, the steady-state valid-fraction
of ALL blocks (the 'bulk' that bimodality/entropy measure) vs the valid-fraction of
blocks GC actually PICKS at reclaim (the low tail it exploits).

Shows why bulk shape (bimodality) misleads and DoIPD (dispersion / tail) is what
matters. Output: figures/occupancy_distribution.png
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .config import SSDConfig
from .simulator import Simulator
from . import workloads

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GEO = dict(channel=2, chip=2, die=2, plane=4, blocks_per_plane=32, pages_per_block=64)
OP, REL = 0.15, 3.0
BG = "#f7f6f3"


def wl(name, n, lp, seed=1):
    if name == "sequential": return workloads.sequential(n, lp)
    if name == "uniform random": return workloads.uniform_random(n, lp, seed=seed)
    if name == "zipf-1.2": return workloads.zipf(n, lp, s=1.2, seed=seed)
    if name == "80/20":
        rng = np.random.default_rng(seed); hot = max(1, int(0.2 * lp))
        return np.where(rng.random(n) < 0.8, rng.integers(0, hot, n),
                        rng.integers(hot, lp, n)).tolist()
    raise ValueError(name)


def run(name):
    cfg = SSDConfig(op_ratio=OP, gc_high_watermark=0.95, gc_low_watermark=0.90, **GEO)
    lp, ppb = cfg.logical_pages, cfg.pages_per_block
    sim = Simulator(cfg, scheme="s1", gc_policy="greedy")
    dev = sim.dev
    recl = []
    orig = sim._reclaim_block
    sim._reclaim_block = lambda v, p: (recl.append(dev.valid_count[v] / ppb), orig(v, p))[1]
    for x in wl(name, int(REL * lp), lp):
        sim.write(int(x) % lp)
    alloc = ~dev.is_free
    occ = dev.valid_count[alloc].astype(float) / ppb        # steady-state occupancy
    inv = dev.invalid_count[alloc].astype(float)
    return dict(name=name, waf=sim.waf, occ=occ, recl=np.array(recl),
                doipd=float(inv.std()))


def main():
    runs = [run("sequential"), run("uniform random"), run("zipf-1.2"), run("80/20")]
    fig, axes = plt.subplots(2, 2, figsize=(11.5, 7.4), facecolor=BG)
    bins = np.linspace(0, 1, 26)
    for ax, r in zip(axes.ravel(), runs):
        ax.hist(r["occ"], bins=bins, density=True, color="#b9b2a4", alpha=0.85,
                label="all blocks (steady state)")
        if r["recl"].size:
            ax.hist(r["recl"], bins=bins, density=True, histtype="step", lw=2.2,
                    color="#c0392b", label="blocks GC picks (at reclaim)")
            ax.axvline(r["recl"].mean(), color="#c0392b", ls="--", lw=1.4)
        # shade the 'cheap victim' tail
        ax.axvspan(0, 0.1, color="#1e8449", alpha=0.10)
        ax.set_title(f"{r['name']}   ·   WAF={r['waf']:.2f}   ·   DoIPD={r['doipd']:.1f}",
                     fontsize=11, loc="left")
        ax.set_xlabel("block occupancy (valid fraction)", fontsize=9.5)
        ax.set_ylabel("density", fontsize=9.5)
        ax.set_xlim(0, 1); ax.set_facecolor(BG)
        ax.tick_params(labelsize=8); ax.grid(alpha=0.25)
        for s in ax.spines.values(): s.set_visible(False)
        ax.legend(fontsize=8, loc="upper center")
    fig.suptitle("How occupancy is distributed — the bulk (grey) vs what GC actually reclaims (red)\n"
                 "green band = 'free' near-empty victims. OP=15%, greedy GC.",
                 fontsize=12.5)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    out = os.path.join(ROOT, "figures", "occupancy_distribution.png")
    fig.savefig(out, dpi=155, facecolor=BG, bbox_inches="tight")
    print("wrote", out)
    for r in runs:
        near0 = (r["occ"] < 0.1).mean() * 100
        print(f"  {r['name']:14} WAF={r['waf']:.2f}  DoIPD={r['doipd']:5.1f}  "
              f"steady-state near-empty={near0:4.1f}%  mean v@reclaim={r['recl'].mean():.3f}")


if __name__ == "__main__":
    main()
