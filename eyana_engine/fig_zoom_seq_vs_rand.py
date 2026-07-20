"""Zoomed comparison: sequential vs uniform random.

At full scale the valid-fraction maps look alike. This zooms into a densely
sampled steady-state window and adds the GC victim-order view, which separates
the two workloads unambiguously:

  col 1  valid fraction, zoom in TIME  (all blocks)
  col 2  valid fraction, zoom in TIME + BLOCK (small block range)
  col 3  GC victim block id vs time -> ordered sweep (seq) vs scatter (random)

Run:  python -m eyana_engine.fig_zoom_seq_vs_rand
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from .config import SSDConfig
from .simulator import Simulator
from . import workloads

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "figures")
GEO = dict(channel=2, chip=2, die=2, plane=4, blocks_per_plane=38, pages_per_block=256)
OP, REL = 0.10, 2.5
W0, W1 = 500_000, 540_000        # steady-state zoom window (host writes)
DENSE = 200                      # sample every N writes inside the window
BLK_LO, BLK_HI = 0, 120          # block range for the tighter zoom

BG = "#f7f6f3"
CMAP = LinearSegmentedColormap.from_list(
    "valid", ["#cfdac8", "#8aa38b", "#4d6b57", "#2f4536"])
CMAP.set_bad("#efece4")


def run(name):
    cfg = SSDConfig(op_ratio=OP, gc_high_watermark=0.95, gc_low_watermark=0.90, **GEO)
    lp, ppb = cfg.logical_pages, cfg.pages_per_block
    n = int(REL * lp)
    sim = Simulator(cfg, scheme="s1", gc_policy="greedy")
    frames, xs, victims = [], [], []

    orig = sim._reclaim_block

    def hooked(victim, p):
        if W0 <= sim.host_writes <= W1:
            victims.append((sim.host_writes, int(victim)))
        return orig(victim, p)
    sim._reclaim_block = hooked

    stream = (workloads.sequential(n, lp) if name == "sequential"
              else workloads.uniform_random(n, lp, seed=1))
    nxt = W0
    for x in stream:
        sim.write(int(x) % lp)
        hw = sim.host_writes
        if W0 <= hw <= W1 and hw >= nxt:
            vf = sim.dev.valid_count.astype(float) / ppb
            vf[sim.dev.is_free] = np.nan
            frames.append(vf)
            xs.append(hw)
            nxt = hw + DENSE
        if hw > W1 and len(frames):
            break
    return dict(name=name, frames=np.array(frames), xs=np.array(xs),
                victims=np.array(victims), nblocks=cfg.total_blocks)


def main():
    os.makedirs(FIG, exist_ok=True)
    runs = [run("sequential"), run("uniform random")]

    fig, axes = plt.subplots(2, 3, figsize=(16.5, 8.2), facecolor=BG,
                             gridspec_kw={"width_ratios": [1, 1, 1]})
    fig.subplots_adjust(hspace=0.42, wspace=0.30)

    for row, res in zip(axes, runs):
        a1, a2, a3 = row
        x0, x1 = res["xs"][0], res["xs"][-1]

        # --- col 1: time zoom, all blocks
        a1.imshow(res["frames"].T, aspect="auto", origin="lower", cmap=CMAP,
                  vmin=0, vmax=1, extent=[x0, x1, 0, res["nblocks"]],
                  interpolation="nearest")
        a1.set_title(f"{res['name']} — time zoom (all {res['nblocks']} blocks)",
                     fontsize=11, loc="left", pad=8)
        a1.set_ylabel("block id", fontsize=9.5)

        # --- col 2: time + block zoom
        sub = res["frames"][:, BLK_LO:BLK_HI]
        a2.imshow(sub.T, aspect="auto", origin="lower", cmap=CMAP, vmin=0, vmax=1,
                  extent=[x0, x1, BLK_LO, BLK_HI], interpolation="nearest")
        a2.set_title(f"{res['name']} — blocks {BLK_LO}–{BLK_HI}",
                     fontsize=11, loc="left", pad=8)
        a2.set_ylabel("block id", fontsize=9.5)

        # --- col 3: which block GC chose, over time
        v = res["victims"]
        if v.size:
            a3.scatter(v[:, 0], v[:, 1], s=4, c="#8d4530", alpha=.55, linewidths=0)
        a3.set_ylim(0, res["nblocks"])
        a3.set_xlim(x0, x1)
        a3.set_title(f"{res['name']} — GC victim order ({len(v)} collections)",
                     fontsize=11, loc="left", pad=8)
        a3.set_ylabel("victim block id", fontsize=9.5)
        a3.grid(alpha=.22)

        for ax in row:
            ax.set_facecolor(BG)
            ax.set_xlabel("host writes →", fontsize=9.5)
            ax.tick_params(labelsize=8)
            for s in ax.spines.values():
                s.set_visible(False)

    fig.suptitle(f"Zoomed comparison: sequential vs uniform random "
                 f"(steady state, host writes {W0:,}–{W1:,})", fontsize=13, y=0.98)
    out = os.path.join(FIG, "fig_zoom_seq_vs_rand.png")
    fig.savefig(out, dpi=165, facecolor=BG, bbox_inches="tight")

    # quantitative: how ordered is the victim sequence?
    print(f"{'workload':16} {'collections':>12} {'|Δvictim| median':>17} {'monotone runs':>14}")
    for res in runs:
        v = res["victims"]
        if v.size < 2:
            continue
        d = np.abs(np.diff(v[:, 1]))
        mono = np.mean(np.diff(v[:, 1]) > 0)
        print(f"{res['name']:16} {len(v):12d} {np.median(d):17.1f} {mono*100:13.1f}%")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
