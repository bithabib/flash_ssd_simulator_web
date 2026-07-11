"""One combined WAF + wear figure comparing all reclaim strategies on a common
device: conventional device-managed GC (greedy, cost-benefit, FIFO) and
host-managed ZNS (single stream and with hot/cold zone separation).

Replaces the separate GC-policy and ZNS figures with a single comparison.
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

STRATS = ["greedy", "cost_benefit", "fifo", "ZNS", "ZNS+hot/cold"]
COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]


def _cfg(op=0.10):
    return SSDConfig(channel=2, chip=2, die=2, plane=2, blocks_per_plane=32,
                     pages_per_block=32, op_ratio=op,
                     gc_high_watermark=0.95, gc_low_watermark=0.90)


def _gen(pat, n, lp, seed=0):
    return {"sequential": workloads.sequential(n, lp),
            "uniform": workloads.uniform_random(n, lp, seed=seed),
            "zipf": workloads.zipf(n, lp, s=1.2, seed=seed)}[pat]


def run(op=0.10, fill=2, bpz=4):
    cfg = _cfg(op); lp = cfg.logical_pages; n = int(lp * fill)
    out = {}
    for pat in ("sequential", "uniform", "zipf"):
        row = {}
        for pol in ("greedy", "cost_benefit", "fifo"):
            sim = Simulator(cfg, scheme="s1", gc_policy=pol)
            for lpn in _gen(pat, n, lp):
                sim.write(lpn)
            row[pol] = {"waf": round(sim.waf, 3),
                        "gini": round(metrics.gini(sim.snapshot()["erase_per_block"]), 3)}
        z1 = ZNSSimulator(cfg, blocks_per_zone=bpz, op_ratio=op, hot_cold=False).run(_gen(pat, n, lp))
        z2 = ZNSSimulator(cfg, blocks_per_zone=bpz, op_ratio=op, hot_cold=True).run(_gen(pat, n, lp))
        row["ZNS"] = {"waf": round(z1["write_amplification"], 3), "gini": round(z1["gini"], 3)}
        row["ZNS+hot/cold"] = {"waf": round(z2["write_amplification"], 3), "gini": round(z2["gini"], 3)}
        out[pat] = row
    return out


def main():
    data = run()
    json.dump(data, open(os.path.join(RES, "reclaim_comparison.json"), "w"), indent=2)
    print(json.dumps(data, indent=2))
    wls = ["sequential", "uniform", "zipf"]; labels = ["Sequential", "Uniform random", "Zipf"]
    x = np.arange(len(wls)); w = 0.15
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.8))
    for k, s in enumerate(STRATS):
        off = (k - 2) * w
        ax1.bar(x + off, [data[p][s]["waf"] for p in wls], w, label=s, color=COLORS[k])
        ax2.bar(x + off, [data[p][s]["gini"] for p in wls], w, label=s, color=COLORS[k])
    ax1.set_xticks(x); ax1.set_xticklabels(labels); ax1.set_ylabel("WAF"); ax1.set_title("Write amplification")
    ax1.legend(fontsize=7, ncol=2); ax1.grid(axis="y", ls="--", alpha=0.4)
    ax2.set_xticks(x); ax2.set_xticklabels(labels); ax2.set_ylabel("Gini (wear inequality)"); ax2.set_title("Wear-leveling")
    ax2.grid(axis="y", ls="--", alpha=0.4)
    fig.suptitle("Reclaim-strategy comparison: conventional GC (greedy, cost-benefit, FIFO) and host-managed ZNS")
    fig.tight_layout()
    out = os.path.join(FIG, "gc_policy_comparison.png")
    fig.savefig(out, dpi=150); plt.close()
    print("wrote", out)


if __name__ == "__main__":
    main()
