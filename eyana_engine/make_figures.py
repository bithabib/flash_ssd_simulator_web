"""Generate all current-paper figures from results/*.json.

Outputs PNGs into figures/ (then copy the ones you want into the paper's fig/).
Run after run_experiments.py completes:  python -m eyana_engine.make_figures
"""
from __future__ import annotations
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(__file__)
RES = os.path.join(HERE, "..", "results")
FIG = os.path.join(HERE, "..", "figures")
os.makedirs(FIG, exist_ok=True)

WL_COLORS = {"sequential": "#1f77b4", "uniform": "#2ca02c", "zipf": "#d62728"}
plt.rcParams.update({"font.size": 10, "figure.dpi": 130})


def _load(name):
    p = os.path.join(RES, f"{name}.json")
    return json.load(open(p)) if os.path.exists(p) else None


def fig_waf_vs_time(syn):
    series = syn.get("waf_series", {})
    if not series:
        return
    plt.figure(figsize=(6, 3.6))
    for wl, s in series.items():
        if not s:
            continue
        a = np.array(s)
        plt.plot(a[:, 0], a[:, 1], label=wl, color=WL_COLORS.get(wl))
        gi = int(a[:, 1].argmax())
        plt.scatter([a[gi, 0]], [a[gi, 1]], color="gray", zorder=5, s=20)
        plt.scatter([a[-1, 0]], [a[-1, 1]], color="black", zorder=5, s=20)
    plt.xlabel("Host writes"); plt.ylabel("WAF")
    plt.title("WAF progression (OP=10%)"); plt.legend(); plt.tight_layout()
    plt.savefig(os.path.join(FIG, "waf_vs_time.png")); plt.close()


def _dist_fig(syn, key, fname, xlabel, title):
    dists = syn.get("distributions", {})
    if not dists:
        return
    plt.figure(figsize=(6, 3.4))
    for wl, d in dists.items():
        x = np.array(d[key], dtype=float)
        mu, sd = x.mean(), x.std()
        plt.hist(x, bins=40, alpha=0.45, color=WL_COLORS.get(wl),
                 label=f"{wl} (μ={mu:.1f}, σ={sd:.2f})", density=True)
    plt.xlabel(xlabel); plt.ylabel("density")
    plt.title(title); plt.legend(fontsize=8); plt.tight_layout()
    plt.savefig(os.path.join(FIG, fname)); plt.close()


def fig_distributions(syn):
    _dist_fig(syn, "invalid_per_block", "invalid_page_distribution.png",
              "invalid pages per block", "Invalid-page distribution (DoIPD)")
    _dist_fig(syn, "erase_per_block", "erase_count_distribution.png",
              "erase count per block", "Erase-count distribution (DoEC)")


def fig_placement(syn):
    place = syn.get("placement", {})
    if not place:
        return
    wls = list(place.keys())
    fig, axes = plt.subplots(2, len(wls), figsize=(3.2 * len(wls), 6))
    for j, wl in enumerate(wls):
        for i, stage in enumerate(("stage1", "stage2")):
            arr = place[wl].get(stage)
            ax = axes[i][j]
            if arr is None:
                ax.axis("off"); continue
            inv = np.array(arr["invalid"], dtype=float)
            n = len(inv)
            w = int(np.ceil(np.sqrt(n)))
            grid = np.full(w * w, np.nan)
            grid[:n] = inv
            ax.imshow(grid.reshape(w, w), cmap="Greens", vmin=0,
                      vmax=max(1, inv.max()))
            ax.set_xticks([]); ax.set_yticks([])
            if i == 0:
                ax.set_title(wl)
            if j == 0:
                ax.set_ylabel("before GC" if i == 0 else "after workload")
    fig.suptitle("Block invalid-page layout (brighter = more invalid)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "placement_layouts.png")); plt.close()


def fig_allocation(alloc):
    if not alloc:
        return
    rows = alloc["rows"]
    wls = ["sequential", "uniform", "zipf"]
    schemes = ["S1", "S2", "S3", "S4", "S5", "S6"]
    fig, axes = plt.subplots(1, 3, figsize=(11, 3.4))
    for ax, metric, title in zip(
            axes, ["fourier_sigma", "gini", "cv"],
            ["Fourier σ_A", "Gini", "Coeff. of variation"]):
        x = np.arange(len(schemes)); width = 0.25
        for k, wl in enumerate(wls):
            vals = [next(r[metric] for r in rows
                         if r["workload"] == wl and r["scheme"] == s)
                    for s in schemes]
            ax.bar(x + (k - 1) * width, vals, width, label=wl,
                   color=WL_COLORS[wl])
        ax.set_xticks(x); ax.set_xticklabels(schemes)
        ax.set_title(title)
        if metric == "fourier_sigma":
            ax.legend(fontsize=8)
    fig.suptitle("Allocation-scheme wear comparison (lower = better wear-leveling)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "allocation_policy_comparison.png")); plt.close()


def fig_gcpolicy(gc):
    if not gc:
        return
    rows = gc["rows"]
    wls = ["sequential", "uniform", "zipf"]
    pols = ["greedy", "cost_benefit", "fifo"]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4))
    for ax, metric, title in zip(axes, ["waf", "gini"], ["WAF", "Gini (wear)"]):
        x = np.arange(len(wls)); width = 0.25
        for k, pol in enumerate(pols):
            vals = [next(r[metric] for r in rows
                         if r["policy"] == pol and r["workload"] == wl)
                    for wl in wls]
            ax.bar(x + (k - 1) * width, vals, width, label=pol)
        ax.set_xticks(x); ax.set_xticklabels(wls); ax.set_title(title)
        if metric == "waf":
            ax.legend(fontsize=8)
    fig.suptitle("GC policy comparison")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "gc_policy_comparison.png")); plt.close()


def fig_realtrace(rt):
    if not rt or not rt.get("rows"):
        return
    traces = rt["available"]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.4))
    for name in traces:
        rows = sorted([r for r in rt["rows"] if r["trace"] == name],
                      key=lambda r: r["op"])
        ops = [r["op"] * 100 for r in rows]
        axes[0].plot(ops, [r["waf"] for r in rows], "o-", label=name)
        axes[1].plot(ops, [r["doipd"] for r in rows], "o-", label=name)
    axes[0].set_xlabel("OP (%)"); axes[0].set_ylabel("WAF"); axes[0].set_title("WAF vs OP")
    axes[1].set_xlabel("OP (%)"); axes[1].set_ylabel("DoIPD"); axes[1].set_title("DoIPD vs OP")
    axes[0].legend(); axes[1].legend()
    fig.suptitle("Real-workload WAF and invalid-page distribution vs over-provisioning")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, "real_workload_analysis.png")); plt.close()


def main():
    syn = _load("synthetic")
    if syn:
        fig_waf_vs_time(syn); fig_distributions(syn); fig_placement(syn)
    fig_allocation(_load("allocation"))
    fig_gcpolicy(_load("gcpolicy"))
    fig_realtrace(_load("realtrace"))
    print("figures written to", FIG)
    for f in sorted(os.listdir(FIG)):
        print("  ", f)


if __name__ == "__main__":
    main()
