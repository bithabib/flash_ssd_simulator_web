"""Space-time companion figure for Fig. 3 — valid fraction AND cumulative wear.

Renders, for each of the paper's three workloads (sequential, uniform random,
Zipf), two heatmaps sharing a block/time layout:

  left  : valid fraction per block over time  (dark = valid, pale = invalid,
          cream = free)   -> underpins DoIPD
  right : cumulative erase count per block    (cream = few, dark red = many)
          -> underpins DoEC / wear-levelling

Unlike Fig. 3 (two frozen stages) this shows the *continuous* evolution and adds
the wear axis, visualising the paper's stated WAF-vs-wear trade-off.

Device config matches Table 2: 2 ch x 2 chip x 2 die x 4 plane, 38 blocks/plane,
256 pages/block  => 1,216 blocks.  Output: figures/fig3_spacetime_wear.png
Run:  python -m eyana_engine.fig3_spacetime
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

# ---- paper Table 2 geometry (1,216 blocks, 256 pages/block) ----
GEO = dict(channel=2, chip=2, die=2, plane=4, blocks_per_plane=38, pages_per_block=256)
OP = 0.10          # paper's 10% OPS
REL = 2.5          # host writes as multiple of logical capacity (fill + overwrite)
NFRAMES = 220

BG = "#f7f6f3"
# valid -> invalid (dark green -> pale), free rendered as cream via 'bad'
CMAP_VALID = LinearSegmentedColormap.from_list(
    "valid", ["#cfdac8", "#8aa38b", "#4d6b57", "#2f4536"])
CMAP_VALID.set_bad("#efece4")
CMAP_WEAR = LinearSegmentedColormap.from_list(
    "wear", ["#f6ece1", "#e3b79a", "#c07c5c", "#8d4530", "#5e2418"])


def make_stream(name, n, lp, seed=1):
    if name == "sequential":
        return workloads.sequential(n, lp)
    if name == "uniform random":
        return workloads.uniform_random(n, lp, seed=seed)
    if name == "zipf":
        return workloads.zipf(n, lp, s=1.2, seed=seed)
    raise ValueError(name)


def run(name):
    cfg = SSDConfig(op_ratio=OP, gc_high_watermark=0.95, gc_low_watermark=0.90, **GEO)
    lp = cfg.logical_pages
    n = int(REL * lp)
    sim = Simulator(cfg, scheme="s1", gc_policy="greedy")
    ppb = cfg.pages_per_block
    valid_frames, wear_frames, xs, reclaim = [], [], [], []

    # record how full each victim block was when GC reclaimed it -> migration cost
    orig_reclaim = sim._reclaim_block

    def hooked(victim, p):
        reclaim.append(sim.dev.valid_count[victim] / ppb)
        return orig_reclaim(victim, p)
    sim._reclaim_block = hooked

    step = max(1, n // NFRAMES)
    for i, x in enumerate(make_stream(name, n, lp)):
        sim.write(int(x) % lp)
        if i % step == 0:
            vf = sim.dev.valid_count.astype(float) / ppb
            vf[sim.dev.is_free] = np.nan          # free blocks -> cream
            valid_frames.append(vf)
            wear_frames.append(sim.dev.erase_count.astype(float).copy())
            xs.append(sim.host_writes)
    e = sim.dev.erase_count.astype(float)
    cv = float(e.std() / e.mean()) if e.mean() > 0 else 0.0
    rc = np.array(reclaim)
    return dict(name=name, waf=sim.waf, cv=cv,
                valid=np.array(valid_frames), wear=np.array(wear_frames),
                xs=np.array(xs), nblocks=cfg.total_blocks, reclaim=rc,
                rc_mean=float(rc.mean()) if rc.size else 0.0,
                rc_free=float((rc < 0.1).mean()) if rc.size else 0.0)


def _verdict_waf(w):
    return "near-ideal" if w < 1.15 else ("efficient" if w < 1.6 else
                                          ("costly" if w < 2.5 else "very costly"))


def _verdict_cv(c):
    return "wear is even" if c < 0.30 else ("wear is moderately uneven" if c < 0.80
                                            else "wear is concentrated")


def main():
    os.makedirs(FIG, exist_ok=True)
    runs = [run("sequential"), run("uniform random"), run("zipf")]

    fig, axes = plt.subplots(3, 3, figsize=(17.0, 11.4), facecolor=BG,
                             gridspec_kw={"width_ratios": [1, 1, 0.72]})
    fig.subplots_adjust(hspace=0.46, wspace=0.42)

    for r, res in zip(axes, runs):
        axL, axR, axH = r
        ext = [0, res["xs"][-1], 0, res["nblocks"]]

        imL = axL.imshow(res["valid"].T, aspect="auto", origin="lower",
                         cmap=CMAP_VALID, vmin=0, vmax=1, extent=ext,
                         interpolation="nearest")
        axL.set_title(f"Valid fraction — {res['name']}\n"
                      f"WAF = {res['waf']:.2f} · {_verdict_waf(res['waf'])}",
                      fontsize=11.5, loc="left", pad=9)
        cb = fig.colorbar(imL, ax=axL, fraction=.045, pad=.03)
        cb.set_label("invalid → valid", fontsize=8, labelpad=2)
        cb.ax.tick_params(labelsize=7)

        imR = axR.imshow(res["wear"].T, aspect="auto", origin="lower",
                         cmap=CMAP_WEAR, extent=ext, interpolation="nearest")
        axR.set_title(f"Cumulative erase count — {res['name']}\n"
                      f"CV = {res['cv']:.2f} · {_verdict_cv(res['cv'])}",
                      fontsize=11.5, loc="left", pad=9)
        cb = fig.colorbar(imR, ax=axR, fraction=.045, pad=.03)
        cb.set_label("erases: few → many", fontsize=8, labelpad=2)
        cb.ax.tick_params(labelsize=7)

        for ax in (axL, axR):
            ax.set_facecolor(BG)
            ax.set_xlabel("host writes →", fontsize=9.5)
            ax.set_ylabel("block id", fontsize=9.5)
            ax.tick_params(labelsize=8)
            for s in ax.spines.values():
                s.set_visible(False)

        # ---- column 3: what GC actually finds at reclaim time (the discriminator)
        rc = res["reclaim"]
        bins = np.linspace(0, 1, 26)
        cnts, edges = np.histogram(rc, bins=bins)
        cnts = cnts / max(1, cnts.sum()) * 100
        centres = (edges[:-1] + edges[1:]) / 2
        cols = ["#3f7d52" if c < 0.1 else "#b9b2a4" for c in centres]
        axH.bar(centres, cnts, width=(edges[1] - edges[0]) * 0.92, color=cols)
        axH.axvline(res["rc_mean"], color="#8d4530", lw=1.8, ls="--")
        axH.text(res["rc_mean"], axH.get_ylim()[1] * 0.94, f" mean {res['rc_mean']:.2f}",
                 color="#8d4530", fontsize=8.5, va="top")
        axH.set_title(f"Reclaim cost — {res['name']}\n"
                      f"{res['rc_free']*100:.0f}% free reclaims "
                      f"({len(rc)} collections)", fontsize=11.5, loc="left", pad=9)
        axH.set_xlabel("valid fraction of victim at reclaim →", fontsize=9.5)
        axH.set_ylabel("% of collections", fontsize=9.5)
        axH.set_xlim(0, 1)
        axH.set_facecolor(BG)
        axH.tick_params(labelsize=8)
        axH.grid(axis="y", alpha=.25)
        for s in axH.spines.values():
            s.set_visible(False)

    fig.suptitle("Block state, wear, and reclaim cost "
                 "(1,216 blocks · 256 pages/block · 10% OPS)",
                 fontsize=13.5, y=0.985)
    out = os.path.join(FIG, "fig3_spacetime_wear.png")
    fig.savefig(out, dpi=160, facecolor=BG, bbox_inches="tight")

    print(f"{'workload':16} {'WAF':>7} {'CV(DoEC/mean)':>14}")
    for res in runs:
        print(f"{res['name']:16} {res['waf']:7.3f} {res['cv']:14.3f}")
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
