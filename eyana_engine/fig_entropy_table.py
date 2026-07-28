"""Render the entropy-model test verdict as a clean table image for the professor.
Output: figures/entropy_test_table.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

cols = ["Claim (entropy model)", "Prediction", "Measured result", "Verdict"]
rows = [
    ["A. Per-block entropy = useful GC signal", "picks victims",
     "H(0.1)=H(0.9)=0.469 — can't tell 10% from 90% valid", "REFUTED"],
    ["B. Uniform pins blocks at p≈0.5 ('trap')", "high trap%",
     "only 1–5% of blocks near 0.5 (spread 0.5–0.75)", "MISLOCATED"],
    ["C. System entropy H_sys predicts WAF", "positive corr.",
     "corr(H_sys, WAF) = -0.35  (wrong sign)", "REFUTED"],
    ["D. Polarization -> low WAF", "negative corr.",
     "corr(polarization, WAF) = +0.43  (wrong sign)", "REFUTED"],
    ["E. Separation lowers entropy -> lowers WAF", "both down",
     "WAF down (1.21->1.14) but H_sys UP (0.73->0.78)", "REFUTED"],
    ["F. Cost-benefit fails the entropy trap", "CB worse",
     "greedy 2.172  ≈  cost-benefit 2.178", "NOT SHOWN"],
    ["G. Entropy-targeting GC (distillation) helps", "WAF down",
     "WAF UP on every workload (+42% to +124%)", "REFUTED"],
    ["Baseline: valid-frac-at-reclaim -> WAF", "(our result)",
     "corr = +0.94  — the real predictor (temporal)", "CONFIRMED"],
]

def vcolor(v):
    return {"REFUTED": "#fbe0dd", "MISLOCATED": "#fdf1d6", "NOT SHOWN": "#fdf1d6",
            "CONFIRMED": "#dff2e2"}.get(v, "#ffffff")
def vtext(v):
    return {"REFUTED": "#a5281b", "CONFIRMED": "#1e6b34"}.get(v, "#7a5a12")

HEAD = "#34495e"
fig, ax = plt.subplots(figsize=(13.8, 4.4))
ax.axis("off")
tbl = ax.table(cellText=rows, colLabels=cols, cellLoc="left", loc="center")
tbl.auto_set_font_size(False); tbl.set_fontsize(10.0); tbl.scale(1, 2.05)

widths = [0.335, 0.10, 0.43, 0.135]
for j, wj in enumerate(widths):
    for i in range(len(rows) + 1):
        tbl[i, j].set_width(wj)
for j in range(len(cols)):
    c = tbl[0, j]; c.set_facecolor(HEAD); c.set_text_props(color="white", fontweight="bold")
    c.set_height(0.13)
for i, row in enumerate(rows, start=1):
    zebra = "#f4f6f8" if i % 2 == 0 else "#ffffff"
    for j in range(len(cols)):
        cell = tbl[i, j]; cell.set_facecolor(zebra); cell.set_edgecolor("#d0d5da")
        if j == 3:
            cell.set_facecolor(vcolor(row[3]))
            cell.set_text_props(ha="center", fontweight="bold", color=vtext(row[3]))

ax.set_title("Does an entropy model govern SSD write amplification? — Test in EyanaSSDSim",
             fontsize=13.5, fontweight="bold", pad=16)
fig.text(0.5, 0.015,
         "Decisive test: the entropy-OPTIMAL GC policy (most polarized 88%, lowest entropy 0.27) "
         "gave the WORST WAF (3.53 vs 2.17).  WAF is governed by WHEN pages die "
         "(valid-frac-at-reclaim, r=0.94), not by the spatial entropy of the layout.",
         ha="center", fontsize=8.8, color="#555", wrap=True)
out = os.path.join(ROOT, "figures", "entropy_test_table.png")
fig.savefig(out, dpi=170, bbox_inches="tight", facecolor="white")
print("wrote", out)
