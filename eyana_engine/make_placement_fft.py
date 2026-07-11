"""Regenerate the 6 data-placement subfloat figures and the FFT spectrum at the
1.27 GB configuration (608 blocks per channel), so they match the updated text.

Placement figures: fig/layout/placement_comparison/{seq,random,zipf}_{initial,final}.png
FFT spectrum:      fig/fft_plot.png
"""
from __future__ import annotations
import json, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(__file__)
RES = os.path.join(HERE, "..", "results")
PAPER = os.path.join(HERE, "..", "..", "EyanaSSDSim-Paper")
PLACE_DIR = os.path.join(PAPER, "fig", "layout", "placement_comparison")
FIG_DIR = os.path.join(PAPER, "fig")
os.makedirs(PLACE_DIR, exist_ok=True)

# workload -> (paper file stem)
WL_FILE = {"sequential": "seq", "uniform": "random", "zipf": "zipf"}
PAGES_PER_BLOCK = 256


def _grid(invalid, valid, per_channel):
    """Render one channel (first `per_channel` blocks) as a green grid.
    Matches the paper legend: dark green = mostly valid, bright/light green =
    mostly invalid, white = free block."""
    inv = np.asarray(invalid, float)[:per_channel]
    val = np.asarray(valid, float)[:per_channel]
    n = len(inv)
    w = int(np.ceil(np.sqrt(n)))
    h = int(np.ceil(n / w))
    # colour value = VALID ratio: 1 -> dark green, 0 (all invalid) -> light green
    tot = inv + val
    ratio = np.where(tot > 0, val / np.maximum(tot, 1), np.nan)
    grid = np.full(w * h, np.nan)
    grid[:n] = ratio
    return grid.reshape(h, w)


def placement_figures(per_channel):
    from matplotlib.colors import LinearSegmentedColormap
    syn = json.load(open(os.path.join(RES, "synthetic.json")))
    place = syn["placement"]
    # light green (invalid) -> dark green (valid); matches paper legend
    cmap = LinearSegmentedColormap.from_list("valid_green", ["#c8f0c8", "#0b3d0b"])
    cmap.set_bad("white")
    for wl, stem in WL_FILE.items():
        for stage, suffix in (("stage1", "initial"), ("stage2", "final")):
            d = place[wl][stage]
            g = _grid(d["invalid"], d["valid"], per_channel)
            fig, ax = plt.subplots(figsize=(3.0, 3.0))
            ax.imshow(g, cmap=cmap, vmin=0, vmax=1, interpolation="nearest")
            ax.set_xticks([]); ax.set_yticks([])
            for s in ax.spines.values():
                s.set_visible(True)
            fig.tight_layout(pad=0.2)
            out = os.path.join(PLACE_DIR, f"{stem}_{suffix}.png")
            fig.savefig(out, dpi=150, bbox_inches="tight"); plt.close()
            print("wrote", out)


def fft_figure():
    syn = json.load(open(os.path.join(RES, "synthetic.json")))
    dist = syn["distributions"]
    colors = {"sequential": "#1f77b4", "uniform": "#ff7f0e", "zipf": "#2ca02c"}
    labels = {"sequential": "Sequential", "uniform": "Uniform rand.", "zipf": "Zipf"}
    fig, ax = plt.subplots(figsize=(6, 3.6))
    for wl in ("sequential", "uniform", "zipf"):
        x = np.asarray(dist[wl]["erase_per_block"], float)
        N = x.size
        amp = np.abs(np.fft.rfft(x)) * 2.0 / N
        amp = amp[1:N // 2]                       # drop DC, one-sided
        freq = np.arange(1, amp.size + 1)
        ax.plot(freq, amp, label=labels[wl], color=colors[wl], lw=0.8)
    ax.set_xlabel("Frequency (block variation rate)")
    ax.set_ylabel("Amplitude")
    ax.legend()
    fig.tight_layout()
    out = os.path.join(FIG_DIR, "fft_plot.png")
    fig.savefig(out, dpi=150); plt.close()
    print("wrote", out)


if __name__ == "__main__":
    # 1.27 GB device: 1216 blocks / 2 channels = 608 blocks per channel
    placement_figures(per_channel=608)
    fft_figure()
