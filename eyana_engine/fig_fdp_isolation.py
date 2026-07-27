"""Figure version of the FDP-isolation validation table (Table 3):
single vs PI WAF, for FEMU and EyanaSSDSim, on synthetic 80/20 and real prxy_1.
Shows both systems agree that PI (hot/cold) isolation reduces WAF.
Output: figures/fdp_isolation_validation.png
"""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BG = "#f7f6f3"
C_SINGLE = "#b9b2a4"     # FDP-single (muted)
C_PI = {"FEMU": "#c0392b", "EyanaSSDSim": "#1e8449"}

# (workload -> {system: (single, pi)})
data = {
    "80/20 (synthetic, OP 10%)": {
        "FEMU":        (1.244, 1.086),
        "EyanaSSDSim": (1.237, 1.150),
    },
    "prxy_1 (real, 3M writes, OP 25%)": {
        "FEMU":        (1.561, 1.487),
        "EyanaSSDSim": (1.256, 1.059),
    },
}

fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.8), facecolor=BG)
systems = ["FEMU", "EyanaSSDSim"]
x = np.arange(len(systems))
w = 0.36

for ax, (wl, d) in zip(axes, data.items()):
    singles = [d[s][0] for s in systems]
    pis = [d[s][1] for s in systems]
    b1 = ax.bar(x - w/2, singles, w, color=C_SINGLE, label="FDP-single", edgecolor="white")
    b2 = ax.bar(x + w/2, pis, w, color=[C_PI[s] for s in systems], label="FDP-PI (hot/cold)",
                edgecolor="white")
    for i, s in enumerate(systems):
        sv, pv = d[s]
        gain = (pv / sv - 1) * 100
        ax.text(i - w/2, sv + 0.012, f"{sv:.3f}", ha="center", fontsize=8.5, color="#555")
        ax.text(i + w/2, pv + 0.012, f"{pv:.3f}", ha="center", fontsize=8.5, fontweight="bold",
                color=C_PI[s])
        # reduction arrow/label above the pair
        top = max(sv, pv)
        ax.annotate(f"{gain:+.1f}%", xy=(i, top + 0.055), ha="center", fontsize=10,
                    fontweight="bold", color=C_PI[s])
    ax.set_title(wl, fontsize=11.5, pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(systems, fontsize=10.5)
    ax.set_ylabel("Write Amplification Factor (WAF)", fontsize=10)
    lo = min(singles + pis)
    ax.set_ylim(lo - 0.12, max(singles + pis) + 0.16)
    ax.set_facecolor(BG)
    ax.grid(axis="y", alpha=0.25)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.legend(loc="upper right", fontsize=9, framealpha=0.9)

fig.suptitle("FDP isolation validation — PI (hot/cold) lowers WAF on both FEMU and EyanaSSDSim",
             fontsize=13, y=1.0)
fig.tight_layout(rect=[0, 0, 1, 0.96])
out = os.path.join(ROOT, "figures", "fdp_isolation_validation.png")
fig.savefig(out, dpi=160, facecolor=BG, bbox_inches="tight")
print("wrote", out)
