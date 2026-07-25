"""Definitive test: which single statistic predicts WAF? Tests spatial vs temporal,
per-block vs global, layout vs mechanistic. Reports |Pearson r| ranking. No spin.
Run: python -m eyana_engine.predictor_shootout
"""
from __future__ import annotations
import numpy as np
from scipy import stats
from .config import SSDConfig
from .simulator import Simulator
from .device import FREE
from . import workloads

GEO = dict(channel=2, chip=2, die=2, plane=4, blocks_per_plane=32, pages_per_block=64)
REL = 3.0


def Hbin(v):
    v = np.clip(v, 1e-12, 1 - 1e-12)
    return -v * np.log2(v) - (1 - v) * np.log2(1 - v)


def gini(x):
    x = np.sort(np.asarray(x, float))
    n = x.size
    if n == 0 or x.sum() == 0:
        return 0.0
    return float((2 * np.arange(1, n + 1) - n - 1).dot(x) / (n * x.sum()))


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
    last = np.full(lp, -1, dtype=np.int64)
    ttis = []
    vrecl = []
    orig = sim._reclaim_block
    sim._reclaim_block = lambda v, p: (vrecl.append(dev.valid_count[v] / ppb), orig(v, p))[1]
    now = 0
    for x in wl(name, int(REL * lp), lp):
        lpn = int(x) % lp; now += 1
        if dev.forward_map[lpn] != FREE and last[lpn] >= 0:
            ttis.append(now - int(last[lpn]))
        sim.write(lpn); last[lpn] = now
    alloc = ~dev.is_free
    inv = dev.invalid_count[alloc].astype(float)
    v = dev.valid_count[alloc].astype(float) / ppb
    ttis = np.array(ttis, float)
    vr = np.array(vrecl)
    return {
        "WAF": sim.waf,
        # --- spatial, steady-state layout ---
        "H_sys (entropy)":        float(Hbin(v).mean()),
        "polarization":           float(((v < 0.1) | (v > 0.9)).mean()),
        "DoIPD (std invalid)":    float(inv.std()),
        "DoIPD_cv":               float(inv.std() / inv.mean()) if inv.mean() else 0.0,
        "Gini(invalid/block)":    gini(inv),
        # --- temporal, global lifetime ---
        "global TTI-CV":          float(ttis.std() / ttis.mean()) if ttis.size and ttis.mean() else 0.0,
        "global TTI-Gini":        gini(ttis),
        # --- mechanistic (GC cost) ---
        "valid@reclaim":          float(vr.mean()) if vr.size else float("nan"),
        "free-reclaim %":         float((vr < 0.1).mean() * 100) if vr.size else float("nan"),
    }


def main():
    wls = ["sequential", "uniform", "zipf1.2", "80/20"]
    ops = [0.10, 0.15, 0.25]
    recs = [run(w, op) for w in wls for op in ops]
    waf = np.array([r["WAF"] for r in recs])
    metrics = [k for k in recs[0] if k != "WAF"]

    print(f"WAF range over {len(recs)} (workload x OP) points: {waf.min():.2f}–{waf.max():.2f}\n")
    print(f"{'predictor':22} {'Pearson r':>10} {'|r|':>6} {'Spearman':>9}   category")
    print("-" * 72)
    cat = {"H_sys (entropy)": "spatial", "polarization": "spatial",
           "DoIPD (std invalid)": "spatial", "DoIPD_cv": "spatial",
           "Gini(invalid/block)": "spatial", "global TTI-CV": "temporal",
           "global TTI-Gini": "temporal", "valid@reclaim": "MECHANISTIC",
           "free-reclaim %": "MECHANISTIC"}
    ranking = []
    for m in metrics:
        x = np.array([r[m] for r in recs], float)
        ok = ~np.isnan(x)
        pr = stats.pearsonr(x[ok], waf[ok])[0] if ok.sum() > 2 else float("nan")
        sr = stats.spearmanr(x[ok], waf[ok]).correlation if ok.sum() > 2 else float("nan")
        ranking.append((abs(pr), pr, sr, m))
    for ar, pr, sr, m in sorted(ranking, reverse=True):
        flag = "  <== strong" if ar > 0.7 else ("  (weak)" if ar < 0.5 else "")
        print(f"{m:22} {pr:>+10.3f} {ar:>6.2f} {sr:>+9.3f}   {cat[m]:11}{flag}")

    print("\nVerdict:")
    strong = [m for ar, pr, sr, m in ranking if ar > 0.7]
    print(f"  from-workload predictors with |r|>0.7: "
          f"{[m for m in strong if cat[m]!='MECHANISTIC'] or 'NONE'}")
    print(f"  mechanistic measurements with |r|>0.7:  {[m for m in strong if cat[m]=='MECHANISTIC']}")


if __name__ == "__main__":
    main()
