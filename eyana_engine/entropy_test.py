"""Empirically test the entropy-model claims (A-G) in EyanaSSDSim. Reports the
truth per claim: no spin.

Definitions used:
  block valid fraction v_b (allocated blocks only)
  binary entropy H(v) = -v log2 v - (1-v) log2(1-v)   (0 log 0 = 0)
  H_sys   = mean_b H(v_b)                 (system disorder, "polarization inverse")
  polar   = fraction of blocks with v<0.1 or v>0.9     (pure states)
  trap    = fraction of blocks with 0.4<v<0.6          (max-entropy region)
"""
from __future__ import annotations
import numpy as np
from .config import SSDConfig
from .simulator import Simulator
from .fdp.fdp_engine import FDPEngine
from . import workloads
from .gc.base import GCPolicy

GEO = dict(channel=2, chip=2, die=2, plane=4, blocks_per_plane=32, pages_per_block=64)
REL = 3.0


def Hbin(v):
    v = np.clip(v, 1e-12, 1 - 1e-12)
    return -v * np.log2(v) - (1 - v) * np.log2(1 - v)


def wl(name, n, lp, seed=1):
    if name == "sequential": return workloads.sequential(n, lp)
    if name == "uniform":    return workloads.uniform_random(n, lp, seed=seed)
    if name == "zipf1.2":    return workloads.zipf(n, lp, s=1.2, seed=seed)
    if name == "80/20":
        rng = np.random.default_rng(seed); hot = max(1, int(0.2 * lp))
        return np.where(rng.random(n) < 0.8, rng.integers(0, hot, n),
                        rng.integers(hot, lp, n)).tolist()
    raise ValueError(name)


class EntropyMaxGC(GCPolicy):
    """'Distillation' victim policy: reclaim the block whose valid fraction is
    CLOSEST TO 0.5 (maximum entropy) -- the entropy model's prescription."""
    name = "entropy_max"
    def select_victim(self, candidates, dev):
        ppb = dev.cfg.pages_per_block
        best, bestd = -1, None
        for b in candidates:
            d = abs(dev.valid_count[b] / ppb - 0.5)
            if bestd is None or d < bestd:
                bestd, best = d, b
        return best


def run_conv(name, op, policy="greedy"):
    cfg = SSDConfig(op_ratio=op, gc_high_watermark=0.95, gc_low_watermark=0.90, **GEO)
    lp = cfg.logical_pages
    sim = Simulator(cfg, scheme="s1", gc_policy=policy if policy != "entropy_max" else "greedy")
    if policy == "entropy_max":
        sim.policy = EntropyMaxGC()
    ppb = cfg.pages_per_block
    recl = []
    orig = sim._reclaim_block
    sim._reclaim_block = lambda v, p: (recl.append(sim.dev.valid_count[v] / ppb), orig(v, p))[1]
    for x in wl(name, int(REL * lp), lp):
        sim.write(int(x) % lp)
    alloc = ~sim.dev.is_free
    v = sim.dev.valid_count[alloc].astype(float) / ppb
    return dict(waf=sim.waf,
                Hsys=float(Hbin(v).mean()) if v.size else 0.0,
                polar=float(((v < 0.1) | (v > 0.9)).mean()) if v.size else 0.0,
                trap=float(((v > 0.4) & (v < 0.6)).mean()) if v.size else 0.0,
                vrecl=float(np.mean(recl)) if recl else float("nan"),
                vdist=v)


def run_fdp(name, op, hot_cold):
    cfg = SSDConfig(op_ratio=op, gc_high_watermark=0.95, gc_low_watermark=0.90, **GEO)
    lp = cfg.logical_pages
    eng = FDPEngine(cfg, hot_cold=hot_cold, isolation="pi")
    ppb = cfg.pages_per_block
    for x in wl(name, int(REL * lp), lp):
        eng.write(int(x) % lp)
    alloc = eng.valid_count + eng.invalid_count > 0
    v = eng.valid_count[alloc].astype(float) / ppb
    return dict(waf=eng.waf, Hsys=float(Hbin(v).mean()) if v.size else 0.0,
                polar=float(((v < 0.1) | (v > 0.9)).mean()) if v.size else 0.0)


def main():
    from scipy import stats
    wls = ["sequential", "uniform", "zipf1.2", "80/20"]
    ops = [0.10, 0.15, 0.25]

    print("=" * 74)
    print("A) Per-block entropy vs valid-ratio (is entropy a reparametrization?)")
    v = np.linspace(0.01, 0.99, 99)
    print(f"   H(0.1)={Hbin(0.1):.3f}  H(0.9)={Hbin(0.9):.3f}  -> "
          f"{'SYMMETRIC: entropy cannot tell 10%-valid from 90%-valid' if abs(Hbin(0.1)-Hbin(0.9))<1e-6 else 'asymmetric'}")

    print("\n" + "=" * 74)
    print("B/C/D) Block-state distribution, H_sys, polarization vs WAF (greedy)")
    print(f"   {'workload':10} {'OP':>4} {'WAF':>6} {'H_sys':>6} {'polar%':>7} {'trap%':>6} {'v@reclaim':>9}")
    rows = []
    for w in wls:
        for op in ops:
            r = run_conv(w, op)
            rows.append((w, op, r))
            print(f"   {w:10} {int(op*100):>3}% {r['waf']:6.3f} {r['Hsys']:6.3f} "
                  f"{r['polar']*100:6.1f} {r['trap']*100:5.1f} {r['vrecl']:9.3f}")
    waf = np.array([r['waf'] for *_, r in rows])
    Hs = np.array([r['Hsys'] for *_, r in rows])
    pol = np.array([r['polar'] for *_, r in rows])
    vr = np.array([r['vrecl'] for *_, r in rows])
    print(f"\n   corr(H_sys, WAF)      Pearson={stats.pearsonr(Hs,waf)[0]:+.3f} "
          f"Spearman={stats.spearmanr(Hs,waf).correlation:+.3f}")
    print(f"   corr(polarization,WAF) Pearson={stats.pearsonr(pol,waf)[0]:+.3f} "
          f"Spearman={stats.spearmanr(pol,waf).correlation:+.3f}")
    print(f"   corr(v@reclaim, WAF)   Pearson={stats.pearsonr(vr,waf)[0]:+.3f}  "
          f"(the simple baseline predictor)")

    print("\n" + "=" * 74)
    print("E) Hot/cold separation lowers H_sys and WAF? (FDP single vs PI, 80/20 & zipf)")
    print(f"   {'workload':10} {'single WAF/H':>14} {'PI WAF/H':>14}")
    for w in ["80/20", "zipf1.2"]:
        s = run_fdp(w, 0.15, False); p = run_fdp(w, 0.15, True)
        print(f"   {w:10} {s['waf']:.3f}/{s['Hsys']:.3f}     {p['waf']:.3f}/{p['Hsys']:.3f}"
              f"   {'H down & WAF down' if p['Hsys']<s['Hsys'] and p['waf']<s['waf'] else 'mixed'}")

    print("\n" + "=" * 74)
    print("F) Does cost-benefit leave the entropy trap? (uniform, trap% under policies)")
    for pol_name in ["greedy", "cost_benefit", "entropy_max"]:
        r = run_conv("uniform", 0.15, pol_name)
        print(f"   {pol_name:13} WAF={r['waf']:.3f}  trap%={r['trap']*100:5.1f}  "
              f"polar%={r['polar']*100:5.1f}  H_sys={r['Hsys']:.3f}")

    print("\n" + "=" * 74)
    print("G) 'Distillation' -- does entropy-targeting GC reduce WAF? (vs greedy/CB)")
    print(f"   {'workload':10} {'greedy':>8} {'cost_ben':>9} {'entropy_max':>12}")
    for w in wls:
        g = run_conv(w, 0.15, "greedy")['waf']
        c = run_conv(w, 0.15, "cost_benefit")['waf']
        e = run_conv(w, 0.15, "entropy_max")['waf']
        verdict = "HELPS" if e < min(g, c) else ("HURTS" if e > max(g, c) else "~same")
        print(f"   {w:10} {g:8.3f} {c:9.3f} {e:12.3f}   entropy_max {verdict}")


if __name__ == "__main__":
    main()
