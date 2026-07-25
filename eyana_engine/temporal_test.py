"""Temporal-locality-of-death metric for FTL, and empirical test that it predicts
WAF (the replacement for the failed spatial entropy model).

Time-To-Invalidate (TTI) of a data item = # host writes between writing an LPN and
overwriting it (its lifetime). A block is cheap to GC when the items it holds have
SIMILAR TTI -- they die together. We measure, per reclaimed block instance, the
coefficient of variation of the TTIs of the items that were invalidated in it:

    within-block TTI-CV  = std(TTI in block) / mean(TTI in block)   (lower = better)
    temporal-locality metric = mean over reclaims of within-block TTI-CV

Prediction: TTI-CV correlates POSITIVELY and strongly with WAF (mixed lifetimes ->
high WAF), unlike entropy (r = -0.35). Run: python -m eyana_engine.temporal_test
"""
from __future__ import annotations
import numpy as np
from collections import defaultdict
from scipy import stats
from .config import SSDConfig
from .simulator import Simulator
from .fdp.fdp_engine import FDPEngine
from .device import FREE
from . import workloads

GEO = dict(channel=2, chip=2, die=2, plane=4, blocks_per_plane=32, pages_per_block=64)
REL = 3.0


def wl(name, n, lp, seed=1):
    if name == "sequential": return workloads.sequential(n, lp)
    if name == "uniform":    return workloads.uniform_random(n, lp, seed=seed)
    if name == "zipf1.2":    return workloads.zipf(n, lp, s=1.2, seed=seed)
    if name == "80/20":
        rng = np.random.default_rng(seed); hot = max(1, int(0.2 * lp))
        return np.where(rng.random(n) < 0.8, rng.integers(0, hot, n),
                        rng.integers(hot, lp, n)).tolist()
    raise ValueError(name)


def run(name, op):
    cfg = SSDConfig(op_ratio=op, gc_high_watermark=0.95, gc_low_watermark=0.90, **GEO)
    lp, ppb = cfg.logical_pages, cfg.pages_per_block
    sim = Simulator(cfg, scheme="s1", gc_policy="greedy")
    dev = sim.dev
    last_write = np.full(lp, -1, dtype=np.int64)     # host-write time per LPN
    block_ttis = defaultdict(list)                   # block-instance -> TTIs of dead items
    recl_cv, vrecl = [], []

    orig = sim._reclaim_block
    def hook(v, p):
        vrecl.append(dev.valid_count[v] / ppb)
        t = block_ttis.get(v)
        if t and len(t) >= 2:
            m = float(np.mean(t))
            if m > 0:
                recl_cv.append(float(np.std(t) / m))
        block_ttis[v] = []                           # reset this block instance
        return orig(v, p)
    sim._reclaim_block = hook

    now = 0
    for x in wl(name, int(REL * lp), lp):
        lpn = int(x) % lp
        now += 1
        old = dev.forward_map[lpn]
        if old != FREE and last_write[lpn] >= 0:     # this item dies now
            block_ttis[int(old) // ppb].append(now - int(last_write[lpn]))
        sim.write(lpn)
        last_write[lpn] = now
    return dict(waf=sim.waf,
                tti_cv=float(np.mean(recl_cv)) if recl_cv else float("nan"),
                vrecl=float(np.mean(vrecl)) if vrecl else float("nan"))


def run_fdp(name, op, hot_cold):
    """within-block TTI-CV for FDP single vs PI (does separation lower it?)."""
    cfg = SSDConfig(op_ratio=op, gc_high_watermark=0.95, gc_low_watermark=0.90, **GEO)
    lp, ppb = cfg.logical_pages, cfg.pages_per_block
    eng = FDPEngine(cfg, hot_cold=hot_cold, isolation="pi")
    last_write = np.full(lp, -1, dtype=np.int64)
    ru_ttis = defaultdict(list)
    cvs = []
    orig = eng._gc_once
    def hook(force=False):
        v = eng._select_victim(force)
        if v >= 0:
            t = ru_ttis.get(v)
            if t and len(t) >= 2:
                m = float(np.mean(t))
                if m > 0: cvs.append(float(np.std(t) / m))
            ru_ttis[v] = []
        return orig(force)
    eng._gc_once = hook
    now = 0
    for x in wl(name, int(REL * lp), lp):
        lpn = int(x) % lp
        now += 1
        old = eng.forward[lpn]
        if old != FREE and last_write[lpn] >= 0:
            ru_ttis[int(old) // eng.ru_pages].append(now - int(last_write[lpn]))
        eng.write(lpn)
        last_write[lpn] = now
    return dict(waf=eng.waf, tti_cv=float(np.mean(cvs)) if cvs else float("nan"))


def main():
    wls = ["sequential", "uniform", "zipf1.2", "80/20"]
    ops = [0.10, 0.15, 0.25]
    print("Temporal locality of death (within-block TTI-CV) vs WAF")
    print(f"   {'workload':10} {'OP':>4} {'WAF':>6} {'TTI-CV':>7} {'v@reclaim':>9}")
    waf, cv, vr = [], [], []
    for w in wls:
        for op in ops:
            r = run(w, op)
            waf.append(r["waf"]); cv.append(r["tti_cv"]); vr.append(r["vrecl"])
            print(f"   {w:10} {int(op*100):>3}% {r['waf']:6.3f} {r['tti_cv']:7.3f} {r['vrecl']:9.3f}")
    waf, cv, vr = np.array(waf), np.array(cv), np.array(vr)
    m = ~np.isnan(cv)
    print(f"\n   corr(within-block TTI-CV, WAF)  Pearson={stats.pearsonr(cv[m],waf[m])[0]:+.3f} "
          f"Spearman={stats.spearmanr(cv[m],waf[m]).correlation:+.3f}")
    print(f"   corr(TTI-CV, v@reclaim)         Pearson={stats.pearsonr(cv[m],vr[m])[0]:+.3f}"
          f"   (the temporal cause of the GC-cost predictor)")
    print(f"\n   [reference]  entropy H_sys vs WAF = -0.35 (failed);  v@reclaim vs WAF = +0.94")

    print("\n   Does hot/cold separation lower within-block TTI-CV? (FDP, OP 15%)")
    print(f"   {'workload':10} {'single WAF/CV':>16} {'PI WAF/CV':>16}")
    for w in ["80/20", "zipf1.2"]:
        s = run_fdp(w, 0.15, False); p = run_fdp(w, 0.15, True)
        ok = "CV down & WAF down" if (p['tti_cv'] < s['tti_cv'] and p['waf'] < s['waf']) else "mixed"
        print(f"   {w:10} {s['waf']:.3f}/{s['tti_cv']:.3f}      {p['waf']:.3f}/{p['tti_cv']:.3f}   {ok}")


if __name__ == "__main__":
    main()
