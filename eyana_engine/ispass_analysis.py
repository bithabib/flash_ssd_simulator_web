"""ISPASS analysis suite for EyanaSSD — visualization & metrics for ZNS and FDP.

Produces the figures/metrics for a tool-paper submission:

  F1  Space-time occupancy map     -- zone/RU lifecycle over time (hot/cold banding)
  F2  Valid-fraction-at-reclaim    -- WHY separation lowers WAF (migration cost)
  F3  Wear distribution + DEC      -- wear hotspots / bottleneck identification
  F4  WAF evolution                -- transient -> GC-onset knee -> steady state

Metrics reported per configuration:
  WAF, mean valid-fraction at reclaim, reclaim efficiency (pages freed per page
  migrated), reclaim count, Degree of Erase Count (population std of erase counts).

Engines are instrumented by *wrapping* their GC entry points, so engine sources
are untouched.  Run:  python -m eyana_engine.ispass_analysis
"""
from __future__ import annotations
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .config import SSDConfig
from .simulator import Simulator
from .fdp.fdp_engine import FDPEngine
from .zns.zns_device import ZNSDevice
from .zns.host_ftl import HostFTL

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIG = os.path.join(ROOT, "figures")
GEO = dict(channel=2, chip=2, die=2, plane=4, blocks_per_plane=32, pages_per_block=32)
OP = 0.15
REL = 3.0
NFRAMES = 160


def wl_8020(n, lp, seed=1):
    rng = np.random.default_rng(seed)
    hot = max(1, int(0.2 * lp))
    return np.where(rng.random(n) < 0.8, rng.integers(0, hot, n),
                    rng.integers(hot, lp, n)).tolist()


def _cfg():
    return SSDConfig(op_ratio=OP, gc_high_watermark=0.95, gc_low_watermark=0.90, **GEO)


# ---------------------------------------------------------------- FDP
def run_fdp(hot_cold, isolation="pi", label=""):
    cfg = _cfg(); lp = cfg.logical_pages
    stream = wl_8020(int(REL * lp), lp)
    eng = FDPEngine(cfg, hot_cold=hot_cold, isolation=isolation)
    events, waf_ts, frames = [], [], []
    orig_gc = eng._gc_once

    def hooked(force=False):
        v = eng._select_victim(force)
        if v >= 0:
            events.append((int(eng.host_writes), int(v), int(eng.ru_valid[v]),
                           int(eng.ru_pages), int(eng.ru_handle[v])))
        return orig_gc(force)
    eng._gc_once = hooked

    step = max(1, len(stream) // NFRAMES)
    for i, x in enumerate(stream):
        eng.write(int(x) % lp)
        if i % step == 0:
            waf_ts.append((eng.host_writes, eng.waf))
            frames.append(eng.ru_valid.astype(float) / eng.ru_pages)
    return dict(label=label, kind="fdp", waf=eng.waf, events=events, waf_ts=waf_ts,
                frames=np.array(frames), wear=eng.erase_count.copy(),
                unit_pages=eng.ru_pages, n_units=eng.n_ru)


# ---------------------------------------------------------------- ZNS
def run_zns(hot_cold, label=""):
    cfg = _cfg(); lp = cfg.logical_pages
    stream = wl_8020(int(REL * lp), lp)
    dev = ZNSDevice(cfg, blocks_per_zone=cfg.blocks_per_plane)
    host = HostFTL(dev, op_ratio=OP, hot_cold=hot_cold)
    events, waf_ts, frames = [], [], []
    zone_stream = {}
    orig_gc, orig_open = host._gc_once, host._open_zone_for

    def hooked_open(s):
        z = orig_open(s)
        zone_stream[z] = s
        return z

    def hooked_gc(force=False):
        z = host._victim(force)
        if z >= 0:
            events.append((int(host.host_writes), int(z), int(host.valid_in_zone[z]),
                           int(dev.zone_pages), zone_stream.get(z, "cold")))
        return orig_gc(force)
    host._open_zone_for, host._gc_once = hooked_open, hooked_gc

    step = max(1, len(stream) // NFRAMES)
    for i, x in enumerate(stream):
        host.write(int(x) % lp)
        if i % step == 0:
            waf_ts.append((host.host_writes, host.write_amplification))
            frames.append(host.valid_in_zone.astype(float) / dev.zone_pages)
    return dict(label=label, kind="zns", waf=host.write_amplification, events=events,
                waf_ts=waf_ts, frames=np.array(frames),
                wear=dev.zone_reset_count.copy(), unit_pages=dev.zone_pages,
                n_units=dev.n_zones)


# ---------------------------------------------------------------- conventional
def run_conv(label="Conventional"):
    cfg = _cfg(); lp = cfg.logical_pages
    stream = wl_8020(int(REL * lp), lp)
    sim = Simulator(cfg, scheme="s1", gc_policy="greedy")
    events, waf_ts = [], []
    ppb = cfg.pages_per_block
    orig_reclaim = sim._reclaim_block

    def hooked(victim, p):
        # capture victim occupancy BEFORE migration/erase
        events.append((int(sim.host_writes), int(victim),
                       int(sim.dev.valid_count[victim]), ppb, -1))
        return orig_reclaim(victim, p)
    sim._reclaim_block = hooked

    step = max(1, len(stream) // NFRAMES)
    for i, x in enumerate(stream):
        sim.write(int(x) % lp)
        if i % step == 0:
            waf_ts.append((sim.host_writes, sim.waf))
    return dict(label=label, kind="conv", waf=sim.waf, events=events, waf_ts=waf_ts,
                frames=np.zeros((0, 0)), wear=sim.dev.erase_count.copy(),
                unit_pages=ppb, n_units=cfg.total_blocks)


# ---------------------------------------------------------------- metrics
def metrics(r):
    ev = r["events"]
    if ev:
        vf = np.array([e[2] / e[3] for e in ev])          # valid fraction at reclaim
        eff = float(np.mean([(e[3] - e[2]) / max(e[2], 1) for e in ev]))
    else:
        vf, eff = np.array([]), float("nan")
    w = r["wear"].astype(float)
    return {
        "config": r["label"],
        "WAF": round(r["waf"], 4),
        "reclaims": len(ev),
        "mean_valid_frac_at_reclaim": round(float(vf.mean()), 4) if vf.size else None,
        "reclaim_efficiency": round(eff, 3) if eff == eff else None,
        "DEC_erase_std": round(float(w.std()), 3),
        "wear_max": int(w.max()) if w.size else 0,
    }


def main():
    os.makedirs(FIG, exist_ok=True)
    runs = [
        run_conv("Conventional"),
        run_fdp(False, "pi", "FDP-single"),
        run_fdp(True, "pi", "FDP-PI (hot/cold)"),
        run_zns(False, "ZNS-single"),
        run_zns(True, "ZNS hot/cold"),
    ]

    # ---- metrics table
    rows = [metrics(r) for r in runs]
    hdr = ["config", "WAF", "reclaims", "mean_valid_frac_at_reclaim",
           "reclaim_efficiency", "DEC_erase_std", "wear_max"]
    print(f"\n{'config':20} {'WAF':>7} {'reclaims':>9} {'validFrac':>10} "
          f"{'reclEff':>8} {'DEC':>7} {'wearMax':>8}")
    for m in rows:
        print(f"{m['config']:20} {m['WAF']:7.3f} {m['reclaims']:9d} "
              f"{str(m['mean_valid_frac_at_reclaim']):>10} "
              f"{str(m['reclaim_efficiency']):>8} {m['DEC_erase_std']:7.2f} "
              f"{m['wear_max']:8d}")
    import csv
    with open(os.path.join(ROOT, "ispass_metrics.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=hdr); w.writeheader(); w.writerows(rows)

    # ---- F1 space-time occupancy (ZNS + FDP, single vs hot/cold)
    show = [r for r in runs if r["kind"] in ("zns", "fdp") and r["frames"].size]
    fig, axes = plt.subplots(2, 2, figsize=(11, 6.4))
    for ax, r in zip(axes.ravel(), show):
        im = ax.imshow(r["frames"].T, aspect="auto", origin="lower",
                       cmap="viridis", vmin=0, vmax=1,
                       extent=[0, r["waf_ts"][-1][0], 0, r["n_units"]])
        ax.set_title(f"{r['label']}  (WAF={r['waf']:.2f})", fontsize=10)
        ax.set_xlabel("host writes"); ax.set_ylabel("zone / reclaim-unit id")
        fig.colorbar(im, ax=ax, label="valid fraction")
    fig.suptitle("F1 — Space-time occupancy: unit lifecycle (hot/cold banding)", fontsize=12)
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "ispass_f1_spacetime.png"), dpi=140)

    # ---- F2 valid-fraction-at-reclaim distribution
    fig, ax = plt.subplots(figsize=(6.8, 4.3))
    for r in runs:
        if not r["events"]:
            continue
        vf = np.array([e[2] / e[3] for e in r["events"]])
        ax.hist(vf, bins=30, range=(0, 1), histtype="step", lw=2, density=True,
                label=f"{r['label']} (μ={vf.mean():.2f})")
    ax.set_xlabel("valid fraction of victim unit at reclaim")
    ax.set_ylabel("density"); ax.grid(alpha=.3); ax.legend(fontsize=8)
    ax.set_title("F2 — Migration cost: valid pages present when a unit is reclaimed")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "ispass_f2_valid_at_reclaim.png"), dpi=140)

    # ---- F3 wear distribution
    fig, ax = plt.subplots(figsize=(6.8, 4.3))
    for r in runs:
        w = np.sort(r["wear"].astype(float))[::-1]
        if w.max() == 0:
            continue
        ax.plot(np.linspace(0, 100, w.size), w, lw=2,
                label=f"{r['label']} (DEC={w.std():.2f})")
    ax.set_xlabel("units sorted by wear (%)"); ax.set_ylabel("erase / reset count")
    ax.grid(alpha=.3); ax.legend(fontsize=8)
    ax.set_title("F3 — Wear distribution & hotspots (Degree of Erase Count)")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "ispass_f3_wear.png"), dpi=140)

    # ---- F4 WAF evolution
    fig, ax = plt.subplots(figsize=(6.8, 4.3))
    for r in runs:
        ts = np.array(r["waf_ts"])
        ax.plot(ts[:, 0], ts[:, 1], lw=2, label=f"{r['label']} (final {r['waf']:.2f})")
    ax.set_xlabel("host writes"); ax.set_ylabel("cumulative WAF")
    ax.grid(alpha=.3); ax.legend(fontsize=8)
    ax.set_title("F4 — WAF evolution: fill transient → GC onset → steady state")
    fig.tight_layout(); fig.savefig(os.path.join(FIG, "ispass_f4_waf_evolution.png"), dpi=140)

    print("\nwrote figures/ispass_f1_spacetime.png, f2_valid_at_reclaim.png, "
          "f3_wear.png, f4_waf_evolution.png  + ispass_metrics.csv")


if __name__ == "__main__":
    main()
