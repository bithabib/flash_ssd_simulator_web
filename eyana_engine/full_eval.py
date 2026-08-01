"""Comprehensive data-capture harness for EyanaSSDSim.

Runs every engine (conventional block + superblock, FDP single/PI/II, ZNS
single/hot-cold with greedy & cost-benefit GC) over any trace (real or synthetic)
and dumps *all* the raw material needed to draw the paper's figures:

  * results/master_scalars.csv   -- one row per (trace, engine): every scalar metric
  * results/<trace>__<engine>.npz -- the distributions / space-time / wear / TTI arrays

Metrics (scalars): WAF, host/gc/physical writes, erases, reclaims, valid@reclaim,
free-reclaim%, reclaim-efficiency, DoIPD_final (std invalid per unit at end),
DoIPD_trigger (mean std invalid per unit measured *before every GC trigger* -- the
methodologically-correct dispersion), DoEC (std erase/reset per block/zone),
erase-Gini, erase-bimodality (Sarle), fill, geometry, unit count.

Arrays (.npz): ev (valid@reclaim per reclaim), doipd_series (invalid-dispersion at
each trigger), final_invalid / final_valid (per reclaim-unit at end), wear (erase or
reset count per block/zone), frames + xs (space-time), tti (per-item lifetimes).

Usage:
  python -m eyana_engine.full_eval real  <trace_path> <msr|etw> [cap] [name]
  python -m eyana_engine.full_eval synth <sequential|uniform|zipf1.2|80/20> [name]
The master CSV is appended to (deduped on trace+engine), so drive it from a shell
loop over all traces/workloads.
"""
from __future__ import annotations
import os, sys, csv, time
import numpy as np

from .config import SSDConfig
from .simulator import Simulator
from .fdp.fdp_engine import FDPEngine
from .zns.zns_device import ZNSDevice
from .zns.host_ftl import HostFTL
from .device import FREE
from . import workloads

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "results")
os.makedirs(RESULTS, exist_ok=True)

OP = 0.25
PPB = 64
PLANES = 16
NFRAMES = 200
REL = 3.0                       # synthetic: writes = REL * logical_pages

# engine ids -> human label + kind
ENGINES = [
    ("conv_block",     "Conventional (block GC)"),
    ("conv_super",     "Conventional (superblock GC)"),
    ("fdp_single",     "FDP-single"),
    ("fdp_pi",         "FDP-PI (hot/cold)"),
    ("fdp_ii",         "FDP-II (hot/cold)"),
    ("zns_single",     "ZNS-single"),
    ("zns_hot_greedy", "ZNS hot/cold (greedy)"),
    ("zns_hot_cb",     "ZNS hot/cold (cost-benefit)"),
    ("zns_single_cb",  "ZNS-single (cost-benefit)"),
]

SCALAR_FIELDS = [
    "trace", "engine", "label", "waf", "host_writes", "gc_writes",
    "physical_writes", "erases", "reclaims", "valid_at_reclaim", "free_reclaim_pct",
    "reclaim_eff", "doipd_final", "doipd_trigger", "doec", "erase_gini",
    "erase_bimodality", "n_units", "unit_pages", "fill_pct", "n_writes",
    "n_unique", "total_blocks", "op", "runtime_s",
]


# ----------------------------- helpers -----------------------------
def gini(x):
    x = np.sort(np.asarray(x, float))
    n = x.size
    if n == 0 or x.sum() == 0:
        return 0.0
    return float((2 * np.arange(1, n + 1) - n - 1).dot(x) / (n * x.sum()))


def sarle_bimodality(x):
    """Sarle's bimodality coefficient b = (g^2 + 1) / k, where g = skew, k = kurtosis
    (with sample corrections). b > 5/9 (~0.555) suggests a bimodal / heavy-tailed
    distribution; ~0.33 for a normal.  Guarded for tiny / degenerate samples."""
    x = np.asarray(x, float)
    n = x.size
    if n < 4 or x.std() == 0:
        return float("nan")
    m = x.mean(); s = x.std()
    g = (((x - m) / s) ** 3).mean()
    k = (((x - m) / s) ** 4).mean()
    corr = ((n - 1) ** 2) / ((n - 2) * (n - 3))
    return float((g ** 2 + 1) / (k + 3 * corr))


def make_cfg(n_unique, granularity="block"):
    total_pages = n_unique / (1 - OP)
    total_blocks = int(round(total_pages / PPB))
    bpp = max(8, int(round(total_blocks / PLANES)))
    return SSDConfig(channel=2, chip=2, die=2, plane=2, blocks_per_plane=bpp,
                     pages_per_block=PPB, op_ratio=OP, gc_granularity=granularity,
                     gc_high_watermark=0.95, gc_low_watermark=0.90)


def load_trace(path, kind, cap):
    gen = workloads.etw_trace_writes(path) if kind == "etw" else workloads.msr_trace_writes(path)
    remap, seq = {}, []
    for lpn in gen:
        d = remap.get(lpn)
        if d is None:
            d = len(remap); remap[lpn] = d
        seq.append(d)
        if len(seq) >= cap:
            break
    return np.array(seq, dtype=np.int64), len(remap)


def synth_seq(name, lp):
    n = int(REL * lp)
    if name == "sequential": return np.fromiter(workloads.sequential(n, lp), np.int64, n), lp
    if name == "uniform":    return np.fromiter(workloads.uniform_random(n, lp, seed=1), np.int64, n), lp
    if name == "zipf1.2":    return np.fromiter(workloads.zipf(n, lp, s=1.2, seed=1), np.int64, n), lp
    if name == "80/20":
        rng = np.random.default_rng(1); hot = max(1, int(0.2 * lp))
        s = np.where(rng.random(n) < 0.8, rng.integers(0, hot, n), rng.integers(hot, lp, n))
        return s.astype(np.int64), lp
    raise ValueError(name)


def _tti_of(seq):
    """Per-item lifetime = #writes between successive writes of the same dense LPN."""
    last = {}
    out = []
    for i, x in enumerate(seq):
        x = int(x)
        if x in last:
            out.append(i - last[x])
        last[x] = i
    return np.asarray(out, dtype=np.int64)


def _pack(engine, label, waf, host_w, gc_w, erases, ev, wear, doipd_series,
          final_invalid, final_valid, frames, xs, n_units, unit_pages,
          fill_pct, n_writes, n_unique, total_blocks, tti, runtime_s):
    ev = np.asarray(ev, float)
    wear = np.asarray(wear, float)
    scal = {
        "engine": engine, "label": label, "waf": round(float(waf), 5),
        "host_writes": int(host_w), "gc_writes": int(gc_w),
        "physical_writes": int(host_w + gc_w), "erases": int(erases),
        "reclaims": int(ev.size),
        "valid_at_reclaim": round(float(ev.mean()), 5) if ev.size else float("nan"),
        "free_reclaim_pct": round(float((ev < 0.1).mean() * 100), 3) if ev.size else float("nan"),
        "reclaim_eff": round(float((ev.size - ev.sum()) / ev.sum()), 5) if ev.sum() > 0 else float("nan"),
        "doipd_final": round(float(np.asarray(final_invalid, float).std()), 5),
        "doipd_trigger": round(float(np.mean(doipd_series)), 5) if len(doipd_series) else float("nan"),
        "doec": round(float(wear.std()), 5),
        "erase_gini": round(gini(wear), 5),
        "erase_bimodality": round(sarle_bimodality(wear), 5),
        "n_units": int(n_units), "unit_pages": int(unit_pages),
        "fill_pct": round(float(fill_pct), 3), "n_writes": int(n_writes),
        "n_unique": int(n_unique) if n_unique is not None else 0,
        "total_blocks": int(total_blocks),
        "op": OP, "runtime_s": round(float(runtime_s), 2),
    }
    arrays = dict(
        ev=ev, doipd_series=np.asarray(doipd_series, float),
        final_invalid=np.asarray(final_invalid, float),
        final_valid=np.asarray(final_valid, float),
        wear=wear, frames=np.asarray(frames, float), xs=np.asarray(xs, float),
        tti=np.asarray(tti, float),
    )
    return scal, arrays


# ----------------------------- runners -----------------------------
def run_conv(cfg, seq, engine, label, tti):
    t0 = time.time()
    dev_planes = None
    sim = Simulator(cfg, scheme="s1", gc_policy="greedy")
    dev = sim.dev
    ppb = cfg.pages_per_block
    ev, doipd_series, frames, xs = [], [], [], []
    superb = cfg.gc_granularity == "superblock"

    def snap_trigger():
        alloc = ~dev.is_free
        if alloc.any():
            doipd_series.append(float(dev.invalid_count[alloc].astype(float).std()))

    orig_gc = sim._garbage_collect
    def gc_hook(p, force=False):
        snap_trigger()
        return orig_gc(p, force)
    sim._garbage_collect = gc_hook

    if superb:
        orig_line = sim._reclaim_line
        def line_hook(L):
            tot = 0
            for pp in range(dev.planes):
                b = pp * dev.bpp + L
                if not dev.is_free[b]:
                    tot += int(dev.valid_count[b])
            ev.append(tot / (dev.planes * ppb))
            return orig_line(L)
        sim._reclaim_line = line_hook
    else:
        orig_rb = sim._reclaim_block
        def rb_hook(v, p):
            ev.append(dev.valid_count[v] / ppb)
            return orig_rb(v, p)
        sim._reclaim_block = rb_hook

    lp = cfg.logical_pages
    step = max(1, len(seq) // NFRAMES)
    for i, x in enumerate(seq):
        sim.write(int(x) % lp)
        if i % step == 0:
            vf = dev.valid_count.astype(float) / ppb
            vf[dev.is_free] = np.nan
            frames.append(vf); xs.append(sim.host_writes)
    alloc = ~dev.is_free
    return _pack(engine, label, sim.waf, sim.host_writes, sim.gc_writes, sim.erases,
                 ev, dev.erase_count, doipd_series,
                 dev.invalid_count[alloc], dev.valid_count[alloc],
                 frames, xs, cfg.total_blocks, ppb,
                 100 * alloc.mean(), len(seq), None, cfg.total_blocks, tti,
                 time.time() - t0)


def run_fdp(cfg, seq, engine, label, hot_cold, isolation, tti):
    t0 = time.time()
    eng = FDPEngine(cfg, hot_cold=hot_cold, isolation=isolation)
    ev, doipd_series, frames, xs = [], [], [], []

    def snap_trigger():
        full = eng.ru_state == 2                       # ST_FULL
        if full.any():
            inv = (eng.ru_written[full] - eng.ru_valid[full]).astype(float)
            doipd_series.append(float(inv.std()))

    orig_gc = eng._gc_once
    def gc_hook(force=False):
        v = eng._select_victim(force)
        if v >= 0:
            ev.append(eng.ru_valid[v] / eng.ru_pages)
            snap_trigger()
        return orig_gc(force)
    eng._gc_once = gc_hook

    lp = cfg.logical_pages
    step = max(1, len(seq) // NFRAMES)
    for i, x in enumerate(seq):
        eng.write(int(x) % lp)
        if i % step == 0:
            frames.append(eng.ru_valid.astype(float) / eng.ru_pages)
            xs.append(eng.host_writes)
    ru_invalid = (eng.ru_written - eng.ru_valid).astype(float)
    return _pack(engine, label, eng.waf, eng.host_writes, eng.gc_writes, eng.erases,
                 ev, eng.erase_count, doipd_series,
                 ru_invalid, eng.ru_valid, frames, xs, eng.n_ru, eng.ru_pages,
                 100.0, len(seq), None, cfg.total_blocks, tti, time.time() - t0)


def run_zns(cfg, seq, engine, label, hot_cold, gc_policy, tti):
    t0 = time.time()
    dev = ZNSDevice(cfg, blocks_per_zone=cfg.blocks_per_plane)
    host = HostFTL(dev, op_ratio=OP, hot_cold=hot_cold, gc_policy=gc_policy)
    ev, doipd_series, frames, xs = [], [], [], []
    zp = dev.zone_pages

    def snap_trigger():
        from .zns.zone import ZoneState
        full = np.array([dev.state[z] == ZoneState.FULL for z in range(dev.n_zones)])
        if full.any():
            inv = (zp - host.valid_in_zone[full]).astype(float)
            doipd_series.append(float(inv.std()))

    orig_gc = host._gc_once
    def gc_hook(force=False):
        z = host._victim(force)
        if z >= 0:
            ev.append(host.valid_in_zone[z] / zp)
            snap_trigger()
        return orig_gc(force)
    host._gc_once = gc_hook

    lp = cfg.logical_pages
    step = max(1, len(seq) // NFRAMES)
    for i, x in enumerate(seq):
        host.write(int(x) % lp)
        if i % step == 0:
            frames.append(host.valid_in_zone.astype(float) / zp)
            xs.append(host.host_writes)
    zone_invalid = (zp - host.valid_in_zone).astype(float)
    return _pack(engine, label, host.write_amplification, host.host_writes,
                 host.gc_writes, int(dev.zone_reset_count.sum()) if hasattr(dev, "zone_reset_count") else 0,
                 ev, getattr(dev, "zone_reset_count", np.zeros(dev.n_zones)),
                 doipd_series, zone_invalid, host.valid_in_zone,
                 frames, xs, dev.n_zones, zp, 100.0, len(seq), None,
                 cfg.total_blocks, tti, time.time() - t0)


DISPATCH = {
    "conv_block":     lambda cfg, seq, e, l, tti: run_conv(cfg, seq, e, l, tti),
    "conv_super":     lambda cfg, seq, e, l, tti: run_conv(cfg, seq, e, l, tti),
    "fdp_single":     lambda cfg, seq, e, l, tti: run_fdp(cfg, seq, e, l, False, "pi", tti),
    "fdp_pi":         lambda cfg, seq, e, l, tti: run_fdp(cfg, seq, e, l, True, "pi", tti),
    "fdp_ii":         lambda cfg, seq, e, l, tti: run_fdp(cfg, seq, e, l, True, "ii", tti),
    "zns_single":     lambda cfg, seq, e, l, tti: run_zns(cfg, seq, e, l, False, "greedy", tti),
    "zns_hot_greedy": lambda cfg, seq, e, l, tti: run_zns(cfg, seq, e, l, True, "greedy", tti),
    "zns_hot_cb":     lambda cfg, seq, e, l, tti: run_zns(cfg, seq, e, l, True, "cost_benefit", tti),
    "zns_single_cb":  lambda cfg, seq, e, l, tti: run_zns(cfg, seq, e, l, False, "cost_benefit", tti),
}


def append_master(row):
    path = os.path.join(RESULTS, "master_scalars.csv")
    rows = []
    if os.path.exists(path):
        with open(path) as fh:
            rows = [r for r in csv.DictReader(fh)
                    if not (r["trace"] == row["trace"] and r["engine"] == row["engine"])]
    rows.append(row)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=SCALAR_FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in SCALAR_FIELDS})


def main():
    if len(sys.argv) < 3:
        print(__doc__); return
    mode = sys.argv[1]
    if mode == "real":
        path, kind = sys.argv[2], sys.argv[3]
        cap = int(sys.argv[4]) if len(sys.argv) > 4 else 3_000_000
        name = sys.argv[5] if len(sys.argv) > 5 else os.path.basename(path).split(".")[0]
        seq, nuniq = load_trace(path, kind, cap)
    elif mode == "bin":
        path = sys.argv[2]
        name = sys.argv[3] if len(sys.argv) > 3 else os.path.basename(path).split(".")[0]
        cap = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        seq = np.fromfile(path, dtype=np.int32).astype(np.int64)
        if cap:
            seq = seq[:cap]
        nuniq = int(seq.max()) + 1                 # dense-remapped from 0
    elif mode == "synth":
        wname = sys.argv[2]
        name = sys.argv[3] if len(sys.argv) > 3 else "synth_" + wname.replace("/", "")
        # size a device the same way as real: nominal logical pages
        probe = make_cfg(20000)
        lp = probe.logical_pages
        seq, nuniq = synth_seq(wname, lp)
    else:
        print("mode must be 'real' or 'synth'"); return

    tti = _tti_of(seq)
    cfg_block = make_cfg(nuniq, "block")
    cfg_super = make_cfg(nuniq, "superblock")
    print(f"[{name}] writes={len(seq):,} unique={nuniq:,} "
          f"device={cfg_block.total_blocks} blk x {PPB}pg "
          f"logical={cfg_block.logical_pages:,} fill={nuniq/cfg_block.logical_pages:.0%} "
          f"OP={OP:.0%}  TTI(mean={tti.mean():.0f} cv={tti.std()/tti.mean():.2f})")

    for engine, label in ENGINES:
        cfg = cfg_super if engine == "conv_super" else cfg_block
        try:
            scal, arrays = DISPATCH[engine](cfg, seq, engine, label, tti)
        except Exception as ex:
            print(f"  [{engine:16}] FAILED: {type(ex).__name__}: {ex}")
            continue
        scal["trace"] = name
        scal["n_unique"] = int(nuniq)
        np.savez_compressed(os.path.join(RESULTS, f"{name}__{engine}.npz"), **arrays)
        append_master(scal)
        print(f"  [{engine:16}] WAF={scal['waf']:.3f} reclaims={scal['reclaims']:6d} "
              f"v@rec={scal['valid_at_reclaim']:.3f} DoIPD*={scal['doipd_trigger']} "
              f"DoEC={scal['doec']:.2f} bimod={scal['erase_bimodality']} "
              f"({scal['runtime_s']:.1f}s)")


if __name__ == "__main__":
    main()
