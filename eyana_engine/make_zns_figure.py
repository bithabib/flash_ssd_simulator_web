"""Run the conventional-SSD vs ZNS comparison and produce a figure for the paper.

Compares, under identical workloads:
  1. Conventional device-managed SSD (greedy GC)
  2. ZNS with host-managed GC, single write stream
  3. ZNS with host-managed GC + hot/cold zone separation
"""
import os, json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .config import SSDConfig
from .simulator import Simulator
from . import workloads, metrics
from .zns.zns_simulator import ZNSSimulator

FIG = os.path.join(os.path.dirname(__file__), "..", "..", "EyanaSSDSim-Paper", "fig")
RES = os.path.join(os.path.dirname(__file__), "..", "results")


def _cfg(op=0.10):
    # modest device so the host-managed ZNS GC runs quickly; results are qualitative
    return SSDConfig(channel=2, chip=2, die=2, plane=2, blocks_per_plane=32,
                     pages_per_block=32, op_ratio=op,
                     gc_high_watermark=0.95, gc_low_watermark=0.90)


def _gen(pat, n, lp, seed=0):
    return {"sequential": workloads.sequential(n, lp),
            "uniform": workloads.uniform_random(n, lp, seed=seed),
            "zipf": workloads.zipf(n, lp, s=1.2, seed=seed)}[pat]


def run(op=0.10, fill=2, bpz=4):
    cfg = _cfg(op)
    lp = cfg.logical_pages
    n = int(lp * fill)
    rows = {}
    for pat in ("sequential", "uniform", "zipf"):
        conv = Simulator(cfg, scheme="s1", gc_policy="greedy")
        for lpn in _gen(pat, n, lp):
            conv.write(lpn)
        z1 = ZNSSimulator(cfg, blocks_per_zone=bpz, op_ratio=op, hot_cold=False)
        r1 = z1.run(_gen(pat, n, lp))
        z2 = ZNSSimulator(cfg, blocks_per_zone=bpz, op_ratio=op, hot_cold=True)
        r2 = z2.run(_gen(pat, n, lp))
        rows[pat] = {
            "conv_waf": round(conv.waf, 3),
            "zns_waf": round(r1["write_amplification"], 3),
            "znshc_waf": round(r2["write_amplification"], 3),
            "conv_gini": round(metrics.gini(conv.snapshot()["erase_per_block"]), 3),
            "zns_gini": round(r1["gini"], 3),
            "znshc_gini": round(r2["gini"], 3),
        }
    return rows


def main():
    rows = run()
    json.dump(rows, open(os.path.join(RES, "zns_comparison.json"), "w"), indent=2)
    print(json.dumps(rows, indent=2))
    wls = ["sequential", "uniform", "zipf"]
    labels = ["Sequential", "Uniform random", "Zipf"]
    x = np.arange(len(wls)); w = 0.25
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.6))
    # WAF
    ax1.bar(x - w, [rows[p]["conv_waf"] for p in wls], w, label="Conventional (greedy GC)", color="#1f77b4")
    ax1.bar(x, [rows[p]["zns_waf"] for p in wls], w, label="ZNS (host GC)", color="#ff7f0e")
    ax1.bar(x + w, [rows[p]["znshc_waf"] for p in wls], w, label="ZNS + hot/cold", color="#2ca02c")
    ax1.set_xticks(x); ax1.set_xticklabels(labels); ax1.set_ylabel("WAF"); ax1.set_title("Write amplification")
    ax1.legend(fontsize=8); ax1.grid(axis="y", ls="--", alpha=0.4)
    # Gini
    ax2.bar(x - w, [rows[p]["conv_gini"] for p in wls], w, label="Conventional (greedy GC)", color="#1f77b4")
    ax2.bar(x, [rows[p]["zns_gini"] for p in wls], w, label="ZNS (host GC)", color="#ff7f0e")
    ax2.bar(x + w, [rows[p]["znshc_gini"] for p in wls], w, label="ZNS + hot/cold", color="#2ca02c")
    ax2.set_xticks(x); ax2.set_xticklabels(labels); ax2.set_ylabel("Gini (wear inequality)"); ax2.set_title("Wear-leveling")
    ax2.grid(axis="y", ls="--", alpha=0.4)
    fig.suptitle("Conventional SSD vs ZNS (host-managed GC) under identical workloads")
    fig.tight_layout()
    out = os.path.join(FIG, "zns_comparison.png")
    fig.savefig(out, dpi=150); plt.close()
    print("wrote", out)


if __name__ == "__main__":
    main()
