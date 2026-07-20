"""FDP validation: FEMU vs EyanaSSD-sim, single vs PI isolation (80/20, OP=10%)."""
from __future__ import annotations
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# OP=10%, 80/20 workload, rHMW=3x, matched --full geometry
femu = {"FDP-single": 1.2437, "FDP-PI": 1.0855}
sim  = {"FDP-single": 1.2367, "FDP-PI": 1.1498}

labels = ["FDP-single", "FDP-PI"]
fe = [femu[k] for k in labels]
si = [sim[k]  for k in labels]

print("FDP validation (OP=10%, 80/20):")
for k in labels:
    err = abs(sim[k] - femu[k]) / femu[k] * 100
    print(f"  {k:11s}: FEMU={femu[k]:.4f}  sim={sim[k]:.4f}  err={err:.1f}%")
print(f"  isolation benefit  FEMU={(1-femu['FDP-PI']/femu['FDP-single'])*100:.1f}%  "
      f"sim={(1-sim['FDP-PI']/sim['FDP-single'])*100:.1f}%")

import numpy as np
x = np.arange(len(labels)); w = 0.36
fig, ax = plt.subplots(figsize=(5.6, 4.2))
ax.bar(x - w/2, fe, w, color="#c0392b", label="FEMU")
ax.bar(x + w/2, si, w, color="#2471a3", label="EyanaSSD sim")
for i, (a, b) in enumerate(zip(fe, si)):
    ax.text(i - w/2, a + 0.01, f"{a:.3f}", ha="center", fontsize=8)
    ax.text(i + w/2, b + 0.01, f"{b:.3f}", ha="center", fontsize=8)
ax.set_xticks(x); ax.set_xticklabels(labels)
ax.set_ylabel("Write Amplification Factor (WAF)")
ax.set_title("FDP isolation — EyanaSSD vs FEMU (OP=10%, 80/20)")
ax.set_ylim(1.0, 1.32)
ax.legend()
ax.grid(True, axis="y", alpha=0.3)
fig.tight_layout()
os.makedirs(os.path.join(ROOT, "figures"), exist_ok=True)
fig.savefig(os.path.join(ROOT, "figures", "fdp_validation_femu.png"), dpi=150)
print("wrote figures/fdp_validation_femu.png")
