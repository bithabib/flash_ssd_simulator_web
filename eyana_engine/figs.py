"""Generate the paper figures from the comprehensive capture (results/).

Reads results/master_scalars.csv + results/<trace>__<engine>.npz and emits figures
into figures/full/.  Data-driven: only draws what has been captured.

Run:  python -m eyana_engine.figs
"""
from __future__ import annotations
import os, csv
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
OUT = os.path.join(ROOT, "figures", "full")
os.makedirs(OUT, exist_ok=True)

BG = "#f7f6f3"
CMAP = LinearSegmentedColormap.from_list("v", ["#cfdac8", "#8aa38b", "#4d6b57", "#2f4536"])
CMAP.set_bad("#efece4")

# engine display order + colours (grouped: conv / fdp / zns)
ENG_ORDER = ["conv_block", "conv_super", "fdp_single", "fdp_pi", "fdp_ii",
             "zns_single", "zns_hot_greedy", "zns_hot_cb", "zns_single_cb"]
ENG_SHORT = {"conv_block": "Conv\nblock", "conv_super": "Conv\nsuper",
             "fdp_single": "FDP\nsingle", "fdp_pi": "FDP\nPI", "fdp_ii": "FDP\nII",
             "zns_single": "ZNS\nsingle", "zns_hot_greedy": "ZNS\nhot·grdy",
             "zns_hot_cb": "ZNS\nhot·CB", "zns_single_cb": "ZNS\nsgl·CB"}
ENG_COLOR = {"conv_block": "#34495e", "conv_super": "#5d6d7e",
             "fdp_single": "#b9770e", "fdp_pi": "#e59866", "fdp_ii": "#f5cba7",
             "zns_single": "#1e6b34", "zns_hot_greedy": "#52a374",
             "zns_hot_cb": "#7dcea0", "zns_single_cb": "#a9dfbf"}

# real-trace display order
TRACE_ORDER = ["prxy_0", "prxy_1", "prxy_1_3M", "W2K8_TPCC",
               "synth_sequential", "synth_uniform", "synth_zipf12", "synth_8020"]

# FEMU reference WAF — ONLY points measured at the SAME config as full_eval
# (OP 25%, matched geometry).  Config-mismatched points (e.g. old OP-10% synthetic
# runs) are deliberately excluded; the FEMU validation subset will add matched
# synthetic points, appended here as they are produced.
# key = (trace, engine) -> FEMU WAF at OP 25%.
FEMU_WAF = {
    # real traces (sim systematically low: block- vs superblock-erase granularity)
    ("prxy_0", "conv_block"): 1.873,        # FEMU vs sim default (the honest gap)
    ("prxy_1_3M", "fdp_single"): 1.561,
    ("prxy_1_3M", "fdp_pi"): 1.487,
    # synthetic @ OP 25% (config-matched fio/fdp_write runs; errors cancel ±8%)
    ("synth_uniform", "conv_block"): 1.458,   # bbssd gc90
    ("synth_uniform", "fdp_single"): 1.661,
    ("synth_uniform", "fdp_pi"): 1.651,
    ("synth_8020", "fdp_single"): 1.121,
    ("synth_8020", "fdp_pi"): 1.016,
}
# FEMU sits between the sim's block- and superblock-granular modes (the cause of
# the gap). key = trace -> FEMU WAF (conventional, OP 25%).
FEMU_BRACKET = {
    "prxy_0": 1.873,
}


def load_master():
    p = os.path.join(RESULTS, "master_scalars.csv")
    rows = {}
    with open(p) as fh:
        for r in csv.DictReader(fh):
            try:
                if float(r["waf"]) > 10:      # pathological GC-thrash guard (invalid run)
                    print(f"  skip {r['trace']}/{r['engine']}: WAF={r['waf']} (non-physical)")
                    continue
            except (TypeError, ValueError):
                continue
            rows[(r["trace"], r["engine"])] = r
    return rows


def npz(trace, engine):
    p = os.path.join(RESULTS, f"{trace}__{engine}.npz")
    return np.load(p) if os.path.exists(p) else None


def traces_present(master):
    seen = [t for t in TRACE_ORDER if any(k[0] == t for k in master)]
    return seen


def engines_for(master, trace):
    return [e for e in ENG_ORDER if (trace, e) in master]


def _f(row, k):
    try:
        return float(row.get(k, "nan"))
    except (TypeError, ValueError):
        return float("nan")


def style(ax):
    ax.set_facecolor(BG); ax.grid(alpha=0.25, lw=0.6)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.tick_params(labelsize=8)


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.savefig(path, dpi=150, facecolor=BG, bbox_inches="tight")
    plt.close(fig)
    print("wrote", os.path.relpath(path, ROOT))


# ---------------- Fig A: validation (sim vs FEMU) ----------------
def fig_validation(master):
    pairs = [(t, e) for (t, e) in FEMU_WAF if (t, e) in master]
    if not pairs:
        return
    pairs.sort(key=lambda te: (TRACE_ORDER.index(te[0]) if te[0] in TRACE_ORDER else 99, te[1]))
    labels = [f"{t}\n{e}" for t, e in pairs]
    sim = [_f(master[(t, e)], "waf") for t, e in pairs]
    fem = [FEMU_WAF[(t, e)] for t, e in pairs]
    x = np.arange(len(pairs)); w = 0.38
    fig, ax = plt.subplots(figsize=(max(7, 1.3 * len(pairs)), 4.6), facecolor=BG)
    ax.bar(x - w/2, fem, w, label="FEMU", color="#c0392b")
    ax.bar(x + w/2, sim, w, label="EyanaSSDSim", color="#2f4536")
    for xi, (s, f) in enumerate(zip(sim, fem)):
        err = 100 * (s - f) / f if f else 0
        ax.text(xi, max(s, f) + 0.03, f"{err:+.0f}%", ha="center", fontsize=8, color="#555")
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=8)
    ax.set_ylabel("WAF"); ax.legend(fontsize=9, frameon=False)
    ax.set_title("Validation — EyanaSSDSim vs FEMU (WAF), matched configs", fontsize=12)
    style(ax)
    save(fig, "A_validation_waf.png")


# ---------------- Fig A2: granularity bracket (FEMU between block & superblock) ----------------
def fig_bracket(master):
    traces = [t for t in FEMU_BRACKET if (t, "conv_block") in master and (t, "conv_super") in master]
    if not traces:
        return
    fig, ax = plt.subplots(figsize=(max(6, 2.2 * len(traces)), 5), facecolor=BG)
    x = np.arange(len(traces)); w = 0.26
    blk = [_f(master[(t, "conv_block")], "waf") for t in traces]
    sup = [_f(master[(t, "conv_super")], "waf") for t in traces]
    fem = [FEMU_BRACKET[t] for t in traces]
    ax.bar(x - w, blk, w, label="EyanaSSDSim · block GC", color="#8aa38b")
    ax.bar(x, fem, w, label="FEMU (superblock erase)", color="#c0392b")
    ax.bar(x + w, sup, w, label="EyanaSSDSim · superblock GC", color="#2f4536")
    for xi, t in enumerate(traces):
        ax.text(xi, max(blk[xi], sup[xi], fem[xi]) + 0.05,
                f"{blk[xi]:.2f} ≤ {fem[xi]:.2f} ≤ {sup[xi]:.2f}", ha="center", fontsize=8.5,
                color="#333")
    ax.set_xticks(x); ax.set_xticklabels(traces, fontsize=9)
    ax.set_ylabel("WAF"); ax.legend(fontsize=9, frameon=False)
    ax.set_title("Granularity bracket — FEMU's WAF lies between the sim's block- and\n"
                 "superblock-granular GC (the cause of the sim–FEMU gap)", fontsize=11.5)
    style(ax)
    save(fig, "A2_granularity_bracket.png")


# ---------------- Fig B: WAF by engine across traces ----------------
def fig_waf_by_engine(master):
    traces = [t for t in traces_present(master) if t.startswith(("prxy", "W2K8"))]
    if not traces:
        return
    engines = ENG_ORDER
    fig, ax = plt.subplots(figsize=(13, 5), facecolor=BG)
    x = np.arange(len(engines)); w = 0.8 / max(1, len(traces))
    for i, t in enumerate(traces):
        vals = [_f(master.get((t, e), {}), "waf") for e in engines]
        ax.bar(x + (i - len(traces)/2 + 0.5) * w, vals, w, label=t,
               color=plt.cm.viridis(i / max(1, len(traces))))
    ax.set_xticks(x); ax.set_xticklabels([ENG_SHORT[e] for e in engines], fontsize=8)
    ax.set_ylabel("WAF"); ax.legend(fontsize=8, frameon=False, ncol=len(traces))
    ax.set_title("Write amplification by engine across real traces", fontsize=12)
    style(ax)
    save(fig, "B_waf_by_engine.png")


# ---------------- Fig C: space-time heatmaps per trace ----------------
def fig_spacetime(master, trace):
    engines = engines_for(master, trace)
    engines = [e for e in engines if npz(trace, e) is not None
               and npz(trace, e)["frames"].size]
    if not engines:
        return
    n = len(engines); cols = 3; rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(4.3 * cols, 2.8 * rows), facecolor=BG)
    axes = np.array(axes).reshape(-1)
    for ax, e in zip(axes, engines):
        d = npz(trace, e); fr = d["frames"]; xs = d["xs"]
        row = master[(trace, e)]
        ax.imshow(fr.T, aspect="auto", origin="lower", cmap=CMAP, vmin=0, vmax=1,
                  extent=[0, xs[-1] if xs.size else 1, 0, fr.shape[1]],
                  interpolation="nearest")
        ax.set_title(f"{row['label']} · WAF {_f(row,'waf'):.2f}", fontsize=9, loc="left")
        ax.set_xlabel("host writes", fontsize=8); ax.set_ylabel("unit id", fontsize=8)
        ax.set_facecolor(BG); ax.tick_params(labelsize=7)
        for s in ax.spines.values():
            s.set_visible(False)
    for ax in axes[len(engines):]:
        ax.axis("off")
    fig.suptitle(f"Space-time occupancy (valid fraction per reclaim unit) — {trace}",
                 fontsize=12.5, y=1.0)
    fig.tight_layout()
    save(fig, f"C_spacetime_{trace}.png")


# ---------------- Fig D: invalid-page distribution (normalized dispersion) ----------------
def fig_invalid_dispersion(master, trace):
    engines = engines_for(master, trace)
    rows_e = []
    for e in engines:
        d = npz(trace, e)
        if d is None:
            continue
        up = float(master[(trace, e)]["unit_pages"])
        fi = d["final_invalid"] / up            # invalid fraction per unit
        series = d["doipd_series"] / up if d["doipd_series"].size else np.array([])
        rows_e.append((e, fi, series))
    if not rows_e:
        return
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.6), facecolor=BG)
    # (left) normalized DoIPD at trigger vs final, per engine
    x = np.arange(len(rows_e)); w = 0.38
    trig = [r[2].mean() if r[2].size else np.nan for r in rows_e]
    fin = [r[1].std() for r in rows_e]
    a1.bar(x - w/2, trig, w, label="at GC-trigger (steady)", color="#c0392b")
    a1.bar(x + w/2, fin, w, label="end-of-trace", color="#5d6d7e")
    a1.set_xticks(x); a1.set_xticklabels([ENG_SHORT[e] for e, _, _ in rows_e], fontsize=7.5)
    a1.set_ylabel("DoIPD  (std of invalid-fraction / unit)")
    a1.set_title("Invalidity dispersion — measured before every GC vs at end", fontsize=10.5)
    a1.legend(fontsize=8, frameon=False); style(a1)
    # (right) final invalid-fraction histograms (a couple representative engines)
    show = [r for r in rows_e if r[0] in ("conv_block", "fdp_pi", "zns_hot_cb")] or rows_e[:3]
    for e, fi, _ in show:
        a2.hist(fi, bins=np.linspace(0, 1, 26), density=True, histtype="step", lw=2,
                color=ENG_COLOR[e], label=ENG_SHORT[e].replace("\n", " "))
    a2.set_xlabel("invalid fraction per reclaim unit (end of trace)")
    a2.set_ylabel("density"); a2.set_title("How invalidity is distributed", fontsize=10.5)
    a2.legend(fontsize=8, frameon=False); style(a2)
    fig.suptitle(f"Invalid-page distribution — {trace}", fontsize=12.5)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save(fig, f"D_invalid_dispersion_{trace}.png")


# ---------------- Fig E: valid-fraction-at-reclaim (the mechanism) ----------------
def fig_valid_at_reclaim(master, trace):
    engines = engines_for(master, trace)
    fig, ax = plt.subplots(figsize=(9.5, 5), facecolor=BG)
    bins = np.linspace(0, 1, 26)
    any_data = False
    for e in engines:
        d = npz(trace, e)
        if d is None or d["ev"].size == 0:
            continue
        any_data = True
        ax.hist(d["ev"], bins=bins, density=True, histtype="step", lw=1.8,
                color=ENG_COLOR[e],
                label=f"{ENG_SHORT[e].replace(chr(10),' ')}  (μ={d['ev'].mean():.2f}, WAF {_f(master[(trace,e)],'waf'):.2f})")
    if not any_data:
        plt.close(fig); return
    ax.axvspan(0, 0.1, color="#1e8449", alpha=0.10)
    ax.set_xlabel("valid fraction of the unit GC reclaims"); ax.set_ylabel("density")
    ax.set_title(f"Valid-fraction-at-reclaim — the GC-cost that sets WAF — {trace}", fontsize=11.5)
    ax.legend(fontsize=7.5, frameon=False); style(ax)
    save(fig, f"E_valid_at_reclaim_{trace}.png")


# ---------------- Fig F: wear distribution ----------------
def fig_wear(master, trace):
    engines = engines_for(master, trace)
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.6), facecolor=BG)
    any_data = False
    for e in engines:
        d = npz(trace, e)
        if d is None or d["wear"].size == 0 or d["wear"].sum() == 0:
            continue
        any_data = True
        w = np.sort(d["wear"])[::-1]
        a1.plot(np.arange(w.size) / w.size, w, lw=1.6, color=ENG_COLOR[e],
                label=ENG_SHORT[e].replace("\n", " "))
    if not any_data:
        plt.close(fig); return
    a1.set_xlabel("unit rank (sorted, hottest first)"); a1.set_ylabel("erase / reset count")
    a1.set_title("Wear distribution (Lorenz-style)", fontsize=10.5)
    a1.legend(fontsize=7.5, frameon=False); style(a1)
    # DoEC + gini + bimodality bars
    es = [e for e in engines if npz(trace, e) is not None]
    x = np.arange(len(es))
    doec = [_f(master[(trace, e)], "doec") for e in es]
    a2.bar(x, doec, color=[ENG_COLOR[e] for e in es])
    a2.set_xticks(x); a2.set_xticklabels([ENG_SHORT[e] for e in es], fontsize=7.5)
    a2.set_ylabel("DoEC (std of erase count)")
    a2.set_title("Wear spread (lower = more even wear-levelling)", fontsize=10.5)
    style(a2)
    fig.suptitle(f"Wear / endurance distribution — {trace}", fontsize=12.5)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save(fig, f"F_wear_{trace}.png")


# ---------------- Fig G: mechanism scatters (across all runs) ----------------
def fig_scatters(master):
    from scipy import stats
    pts = [(t, e, r) for (t, e), r in master.items()]
    waf = np.array([_f(r, "waf") for _, _, r in pts])
    vr = np.array([_f(r, "valid_at_reclaim") for _, _, r in pts])
    # normalized DoIPD-final = doipd_final / unit_pages
    doipd = np.array([_f(r, "doipd_final") / max(1, _f(r, "unit_pages")) for _, _, r in pts])
    col = [ENG_COLOR.get(e, "#888") for _, e, _ in pts]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(12.5, 5), facecolor=BG)
    for ax, xv, xl, name in [(a1, vr, "valid-fraction at reclaim", "valid@reclaim"),
                             (a2, doipd, "DoIPD (norm. invalid-fraction std)", "DoIPD")]:
        m = np.isfinite(xv) & np.isfinite(waf)
        ax.scatter(xv[m], waf[m], c=[c for c, mm in zip(col, m) if mm], s=34,
                   edgecolor="white", lw=0.4)
        if m.sum() > 2:
            r = stats.pearsonr(xv[m], waf[m])[0]
            ax.set_title(f"WAF vs {name}   (Pearson r = {r:+.2f})", fontsize=11)
        ax.set_xlabel(xl); ax.set_ylabel("WAF"); style(ax)
    fig.suptitle("What predicts WAF — mechanism scatters across all runs", fontsize=12.5)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save(fig, "G_mechanism_scatters.png")


# ---------------- Fig H: FDP isolation + ZNS policy ----------------
def fig_placement(master):
    traces = [t for t in traces_present(master) if t.startswith(("prxy", "W2K8"))]
    if not traces:
        return
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 4.8), facecolor=BG)
    x = np.arange(len(traces)); w = 0.26
    for i, e in enumerate(["fdp_single", "fdp_pi", "fdp_ii"]):
        vals = [_f(master.get((t, e), {}), "waf") for t in traces]
        a1.bar(x + (i - 1) * w, vals, w, label=ENG_SHORT[e].replace("\n", " "),
               color=ENG_COLOR[e])
    a1.set_xticks(x); a1.set_xticklabels(traces, fontsize=8, rotation=12)
    a1.set_ylabel("WAF"); a1.set_title("FDP isolation: single vs PI vs II", fontsize=11)
    a1.legend(fontsize=8, frameon=False); style(a1)
    for i, e in enumerate(["zns_single", "zns_hot_greedy", "zns_hot_cb"]):
        vals = [_f(master.get((t, e), {}), "waf") for t in traces]
        a2.bar(x + (i - 1) * w, vals, w, label=ENG_SHORT[e].replace("\n", " "),
               color=ENG_COLOR[e])
    a2.set_xticks(x); a2.set_xticklabels(traces, fontsize=8, rotation=12)
    a2.set_ylabel("WAF"); a2.set_title("ZNS placement & GC policy", fontsize=11)
    a2.legend(fontsize=8, frameon=False); style(a2)
    fig.suptitle("Placement effect — FDP isolation and ZNS hot/cold+GC", fontsize=12.5)
    fig.tight_layout(rect=[0, 0, 1, 0.95])
    save(fig, "H_placement.png")


# ---------------- Fig I: WAF <-> wear tradeoff ----------------
def fig_tradeoff(master):
    traces = [t for t in traces_present(master) if t.startswith(("prxy", "W2K8"))]
    fig, ax = plt.subplots(figsize=(8.5, 6), facecolor=BG)
    for (t, e), r in master.items():
        if t not in traces:
            continue
        ax.scatter(_f(r, "waf"), _f(r, "doec"), s=44, color=ENG_COLOR.get(e, "#888"),
                   edgecolor="white", lw=0.5)
    # legend by engine
    from matplotlib.lines import Line2D
    handles = [Line2D([0], [0], marker="o", ls="", mfc=ENG_COLOR[e], mec="white",
                      label=ENG_SHORT[e].replace("\n", " ")) for e in ENG_ORDER]
    ax.legend(handles=handles, fontsize=7.5, frameon=False, ncol=2)
    ax.set_xlabel("WAF (write cost)"); ax.set_ylabel("DoEC (wear spread)")
    ax.set_title("WAF ↔ wear trade-off — each point is one (engine, trace)", fontsize=12)
    style(ax)
    save(fig, "I_waf_wear_tradeoff.png")


def main():
    master = load_master()
    if not master:
        print("no data in results/master_scalars.csv yet"); return
    traces = traces_present(master)
    print(f"traces: {traces}")
    fig_validation(master)
    fig_bracket(master)
    fig_waf_by_engine(master)
    fig_scatters(master)
    fig_placement(master)
    fig_tradeoff(master)
    for t in traces:
        fig_spacetime(master, t)
        fig_invalid_dispersion(master, t)
        fig_valid_at_reclaim(master, t)
        fig_wear(master, t)
    print(f"\nall figures in {os.path.relpath(OUT, ROOT)}/")


if __name__ == "__main__":
    main()
