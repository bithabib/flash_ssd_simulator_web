"""Real-trace evaluation: replay a real block trace through every engine and
produce the ISPASS metrics + space-time / reclaim-cost figures.

Methodology (honest replay of a sparse-address trace on a right-sized device):
  * DENSE remap: each unique written LBA -> a compact page index, preserving the
    exact reuse pattern and skew (no modulo aliasing).
  * device sized to the working set: logical_pages ~= unique_pages / (1 - OP),
    so the trace fills the device and GC is actually exercised.

Metrics per config: WAF, mean valid-fraction at reclaim, reclaim efficiency
(pages freed per page migrated), reclaims, Degree of Erase Count (std).

Usage:  python -m eyana_engine.real_eval <trace_path> <kind msr|etw> [cap_writes]
"""
from __future__ import annotations
import os, sys, gzip, bz2
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

from .config import SSDConfig
from .simulator import Simulator
from .fdp.fdp_engine import FDPEngine
from .zns.zns_device import ZNSDevice
from .zns.host_ftl import HostFTL
from . import workloads

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "figures")
OP = 0.25          # 25% over-provisioning -> enough GC headroom for 2-stream hot/cold
PPB = 64           # smaller block -> more blocks/zones for a small working set + faster
PLANES = 16        # 2 x 2 x 2 x 2  -> ZNS zones = 16, FDP RUs = blocks_per_plane
NFRAMES = 200
BG = "#f7f6f3"
CMAP = LinearSegmentedColormap.from_list("v", ["#cfdac8", "#8aa38b", "#4d6b57", "#2f4536"])
CMAP.set_bad("#efece4")


def load_trace(path, kind, cap):
    """Return (dense_sequence, n_unique).  Dense-remaps LBAs, preserving reuse."""
    if kind == "etw":
        gen = workloads.etw_trace_writes(path)
    else:
        gen = workloads.msr_trace_writes(path)
    remap, seq = {}, []
    for lpn in gen:
        d = remap.get(lpn)
        if d is None:
            d = len(remap); remap[lpn] = d
        seq.append(d)
        if len(seq) >= cap:
            break
    return np.array(seq, dtype=np.int64), len(remap)


def make_cfg(n_unique):
    # logical ~= working set (device holds all touched pages); OP is the GC spare.
    total_pages = n_unique / (1 - OP)
    total_blocks = int(round(total_pages / PPB))
    bpp = max(8, int(round(total_blocks / PLANES)))     # >=8 blocks/plane for GC room
    cfg = SSDConfig(channel=2, chip=2, die=2, plane=2, blocks_per_plane=bpp,
                    pages_per_block=PPB, op_ratio=OP,
                    gc_high_watermark=0.95, gc_low_watermark=0.90)
    return cfg


def _frames(get_valid, nblocks, seq, stepper):
    pass  # (placeholder; per-engine capture is inline below)


def run_conv(cfg, seq):
    lp = cfg.logical_pages
    sim = Simulator(cfg, scheme="s1", gc_policy="greedy")
    ev, frames, xs = [], [], []
    orig = sim._reclaim_block
    sim._reclaim_block = lambda v, p: (ev.append(sim.dev.valid_count[v] / PPB), orig(v, p))[1]
    step = max(1, len(seq) // NFRAMES)
    for i, x in enumerate(seq):
        sim.write(int(x) % lp)
        if i % step == 0:
            vf = sim.dev.valid_count.astype(float) / PPB
            vf[sim.dev.is_free] = np.nan
            frames.append(vf); xs.append(sim.host_writes)
    return _pack("Conventional", sim.waf, ev, sim.dev.erase_count, frames, xs, cfg.total_blocks)


def run_fdp(cfg, seq, hot_cold, label):
    lp = cfg.logical_pages
    eng = FDPEngine(cfg, hot_cold=hot_cold, isolation="pi")
    ev, frames, xs = [], [], []
    orig = eng._gc_once

    def hook(force=False):
        v = eng._select_victim(force)
        if v >= 0:
            ev.append(eng.ru_valid[v] / eng.ru_pages)
        return orig(force)
    eng._gc_once = hook
    step = max(1, len(seq) // NFRAMES)
    for i, x in enumerate(seq):
        eng.write(int(x) % lp)
        if i % step == 0:
            frames.append(eng.ru_valid.astype(float) / eng.ru_pages)
            xs.append(eng.host_writes)
    return _pack(label, eng.waf, ev, eng.erase_count, frames, xs, eng.n_ru)


def run_zns(cfg, seq, hot_cold, label, gc_policy="greedy"):
    lp = cfg.logical_pages
    dev = ZNSDevice(cfg, blocks_per_zone=cfg.blocks_per_plane)
    host = HostFTL(dev, op_ratio=OP, hot_cold=hot_cold, gc_policy=gc_policy)
    ev, frames, xs = [], [], []
    orig = host._gc_once

    def hook(force=False):
        z = host._victim(force)
        if z >= 0:
            ev.append(host.valid_in_zone[z] / dev.zone_pages)
        return orig(force)
    host._gc_once = hook
    step = max(1, len(seq) // NFRAMES)
    for i, x in enumerate(seq):
        host.write(int(x) % lp)
        if i % step == 0:
            frames.append(host.valid_in_zone.astype(float) / dev.zone_pages)
            xs.append(host.host_writes)
    return _pack(label, host.write_amplification, ev, dev.zone_reset_count,
                 frames, xs, dev.n_zones)


def _pack(label, waf, ev, wear, frames, xs, nunits):
    ev = np.array(ev); w = np.asarray(wear, float)
    # robust reclaim efficiency: pages freed per page migrated, computed on totals
    freed = ev.size            # each reclaim frees one unit's worth of pages (relative)
    migrated = float(ev.sum())  # sum of valid fractions = fraction of a unit migrated
    return dict(label=label, waf=waf, reclaims=len(ev),
                vfrac=float(ev.mean()) if ev.size else float("nan"),
                free_pct=float((ev < 0.1).mean() * 100) if ev.size else float("nan"),
                reff=float((freed - migrated) / migrated) if migrated > 0 else float("nan"),
                dec=float(w.std()), frames=np.array(frames), xs=np.array(xs),
                nunits=nunits, ev=ev)


def main():
    if len(sys.argv) < 3:
        print("usage: python -m eyana_engine.real_eval <trace> <msr|etw> [cap]"); return
    path, kind = sys.argv[1], sys.argv[2]
    cap = int(sys.argv[3]) if len(sys.argv) > 3 else 2_000_000
    name = os.path.basename(path).split(".")[0]

    seq, nuniq = load_trace(path, kind, cap)
    cfg = make_cfg(nuniq)
    print(f"trace={name}  writes={len(seq):,}  unique_pages={nuniq:,}")
    print(f"device: {cfg.total_blocks} blocks x {PPB} pg = {cfg.total_pages:,} pages "
          f"(logical {cfg.logical_pages:,}, OP {OP:.0%}); fill = {nuniq/cfg.logical_pages:.0%}\n")

    import time
    jobs = [("Conventional", lambda: run_conv(cfg, seq)),
            ("FDP-single", lambda: run_fdp(cfg, seq, False, "FDP-single")),
            ("FDP-PI", lambda: run_fdp(cfg, seq, True, "FDP-PI")),
            ("ZNS-single", lambda: run_zns(cfg, seq, False, "ZNS-single")),
            ("ZNS hot/cold (greedy)", lambda: run_zns(cfg, seq, True, "ZNS hot/cold (greedy)")),
            ("ZNS hot/cold (cost-benefit)",
             lambda: run_zns(cfg, seq, True, "ZNS hot/cold (cost-benefit)", gc_policy="cost_benefit")),
            ("ZNS-single (cost-benefit)",
             lambda: run_zns(cfg, seq, False, "ZNS-single (cost-benefit)", gc_policy="cost_benefit"))]
    runs = []
    for nm, fn in jobs:
        t = time.time()
        runs.append(fn())
        print(f"  [{nm:14}] done in {time.time()-t:5.1f}s  WAF={runs[-1]['waf']:.3f}", flush=True)

    print(f"{'config':16}{'WAF':>7}{'reclaims':>10}{'valid@recl':>11}"
          f"{'free%':>7}{'reclEff':>8}{'DEC':>8}")
    import csv
    rows = []
    for r in runs:
        print(f"{r['label']:16}{r['waf']:7.3f}{r['reclaims']:10d}"
              f"{r['vfrac']:11.3f}{r['free_pct']:7.1f}{r['reff']:8.2f}{r['dec']:8.2f}")
        rows.append({k: r[k] for k in ("label", "waf", "reclaims", "vfrac",
                                       "free_pct", "reff", "dec")})
    with open(os.path.join(ROOT, f"real_eval_{name}.csv"), "w", newline="") as fh:
        wtr = csv.DictWriter(fh, fieldnames=["label", "waf", "reclaims", "vfrac",
                                             "free_pct", "reff", "dec"])
        wtr.writeheader(); wtr.writerows(rows)

    # space-time figure for the four placement engines
    show = [r for r in runs if r["label"] != "Conventional" and r["frames"].size]
    fig, axes = plt.subplots(2, 2, figsize=(12.2, 6.6), facecolor=BG)
    fig.subplots_adjust(hspace=.42, wspace=.2)
    for ax, r in zip(axes.ravel(), show):
        ax.imshow(r["frames"].T, aspect="auto", origin="lower", cmap=CMAP, vmin=0, vmax=1,
                  extent=[0, r["xs"][-1], 0, r["nunits"]], interpolation="nearest")
        ax.set_title(f"{r['label']} — WAF {r['waf']:.2f} · valid@reclaim {r['vfrac']:.2f}",
                     fontsize=10.5, loc="left", pad=7)
        ax.set_xlabel("host writes →", fontsize=9); ax.set_ylabel("zone / RU id", fontsize=9)
        ax.set_facecolor(BG); ax.tick_params(labelsize=8)
        for s in ax.spines.values():
            s.set_visible(False)
    fig.suptitle(f"Real trace: {name}  ({len(seq):,} writes · {nuniq:,} pages · "
                 f"device {cfg.total_blocks} blk · {OP:.0%} OP)", fontsize=12.5, y=0.99)
    out = os.path.join(FIG, f"real_eval_{name}_spacetime.png")
    fig.savefig(out, dpi=150, facecolor=BG, bbox_inches="tight")
    print(f"\nwrote real_eval_{name}.csv + {out}")


if __name__ == "__main__":
    main()
