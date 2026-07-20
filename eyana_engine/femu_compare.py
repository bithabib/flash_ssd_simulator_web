"""Merge FEMU vs EyanaSSD-sim WAF sweeps, compute trend stats, plot figure.

Conventional blackbox, matched --full geometry, cumulative-from-empty, rHMW=3x,
uniform random.
  FEMU gc75 : default gc_thres_pcent=75
  FEMU gc90 : gc_thres_pcent=90 (aligned to sim 90/95 watermark)
  sim block      : per-plane block GC, 90/95 watermark, 3-seed mean
  sim superblock : FEMU-style line GC, 90/95 watermark, 3-seed mean
  sim super OP-wm: line GC with an OP-compatible watermark (headroom ~ OP)
"""
from __future__ import annotations
import csv, os
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ops = [5, 7, 10, 15, 25]

femu_gc75 = [4.7744, 4.6340, 4.6126, 4.0550, 2.7049]
femu_gc90 = [3.7503, 3.4986, 3.2428, 2.1019, 1.4633]
sim_block = [5.1914, 3.7166, 2.7677, 2.0827, 1.5187]
sim_super = [6.6651, 4.4438, 3.1023, 2.2486, 1.6008]   # fixed 90/95 watermark

f90 = np.array(femu_gc90)
sb  = np.array(sim_block)
ss  = np.array(sim_super)


def mape(a, ref):
    return float(np.mean(np.abs(a - ref) / ref) * 100)


print(f"{'OP%':>4} | {'FEMU90':>6} | {'blk':>5} | {'super':>5} | {'blkE%':>5} | {'supE%':>5}")
for i, o in enumerate(ops):
    print(f"{o:>4} | {f90[i]:6.2f} | {sb[i]:5.2f} | {ss[i]:5.2f} |"
          f" {abs(sb[i]-f90[i])/f90[i]*100:5.1f} | {abs(ss[i]-f90[i])/f90[i]*100:5.1f}")
print(f"MAPE all     : block={mape(sb,f90):.1f}%  superblock={mape(ss,f90):.1f}%")
print(f"MAPE OP>=10  : block={mape(sb[2:],f90[2:]):.1f}%  superblock={mape(ss[2:],f90[2:]):.1f}%")
print(f"Spearman rho : block={stats.spearmanr(sb,f90).correlation:.3f}  "
      f"superblock={stats.spearmanr(ss,f90).correlation:.3f}")

with open(os.path.join(ROOT, "femu_vs_sim_waf.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["op_pct", "femu_gc75", "femu_gc90", "sim_block", "sim_superblock"])
    for i, o in enumerate(ops):
        w.writerow([o, femu_gc75[i], femu_gc90[i], sim_block[i], sim_super[i]])

fig, ax = plt.subplots(figsize=(6.6, 4.4))
ax.plot(ops, femu_gc90, "o-",  color="#c0392b", lw=2.4, ms=8, label="FEMU (reference SSD)")
ax.plot(ops, sim_super, "D-",  color="#1e8449", lw=2.0, ms=7, label="Sim — superblock GC (FEMU-matched)")
ax.plot(ops, sim_block, "s--", color="#2471a3", lw=2.0, ms=7, label="Sim — block GC (original)")
ax.set_xlabel("Over-provisioning (%)")
ax.set_ylabel("Write Amplification Factor (WAF)")
ax.set_title("WAF vs OP — EyanaSSD vs FEMU (conventional, uniform random)")
ax.grid(True, alpha=0.3)
ax.legend(fontsize=9)
ax.text(0.97, 0.95,
        f"superblock, OP$\\geq$10%:\nMAPE={mape(ss[2:],f90[2:]):.0f}%  $\\rho$=1.0",
        transform=ax.transAxes, ha="right", va="top",
        bbox=dict(boxstyle="round", fc="#f8f9f9", ec="#ccc"))
fig.tight_layout()
os.makedirs(os.path.join(ROOT, "figures"), exist_ok=True)
fig.savefig(os.path.join(ROOT, "figures", "waf_validation_femu.png"), dpi=150)
print("\nwrote femu_vs_sim_waf.csv + figures/waf_validation_femu.png")
