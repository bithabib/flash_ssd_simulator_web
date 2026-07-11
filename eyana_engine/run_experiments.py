"""Reproduce every current-paper experiment from the corrected engine.

Runs at the paper's 5.03 GB geometry but with chip=2 so the six allocation
schemes are genuinely distinct (audit fix A1).  Writes all results to
results/*.json for downstream figure generation and manuscript tables.

Usage:
    python -m eyana_engine.run_experiments [--quick] [--only NAME[,NAME...]]
Experiments: synthetic, allocation, gcpolicy, realtrace, scalability
"""
from __future__ import annotations
import json, os, sys, time
import numpy as np

from .config import SSDConfig
from .simulator import Simulator
from . import workloads, metrics

RESULTS = os.path.join(os.path.dirname(__file__), "..", "results")
os.makedirs(RESULTS, exist_ok=True)

PAGE = 4096


def paper_cfg(op=0.10, gc_policy="greedy", blocks_per_plane=38, ppb=256):
    """1.27 GB device (the size used for FTLSim/FEMU validation), chip=2 so the
    six allocation schemes are distinct.  32 planes x 38 blocks x 256 pages."""
    return SSDConfig(channel=2, chip=2, die=2, plane=4,
                     blocks_per_plane=blocks_per_plane, pages_per_block=ppb,
                     page_size=PAGE, op_ratio=op, gc_policy=gc_policy,
                     gc_high_watermark=0.95, gc_low_watermark=0.90)


# Paper methodology: a base workload is replayed PASSES times; the SSD receives
# TOTAL_WRITES requests in total (base pass = TOTAL_WRITES // PASSES).
TOTAL_WRITES = 2_000_000
PASSES = 3


def _base_sequence(pat, base_len, lp, seed=0):
    """One workload pass of `base_len` requests over the logical space [0, lp)."""
    if pat == "sequential":
        return (np.arange(base_len, dtype=np.int64) % lp)
    if pat == "uniform":
        return np.random.default_rng(seed).integers(0, lp, size=base_len)
    if pat == "zipf":
        r = np.random.default_rng(seed).zipf(1.2, size=base_len)
        return (r - 1) % lp
    raise ValueError(pat)


def _snap_layout(sim):
    snap = sim.snapshot()
    return {"invalid": snap["invalid_per_block"].tolist(),
            "valid": snap["valid_per_block"].tolist()}


def _replay(sim, base, passes, sample=False):
    """Replay `base` `passes` times through `sim`; collect an optional waf series."""
    total = passes * len(base)
    step = max(1, total // 200)
    waf_series, i = [], 0
    for _ in range(passes):
        for lpn in base:
            sim.write(int(lpn))
            if sample and (i % step == 0):
                waf_series.append([sim.host_writes, round(sim.waf, 4)])
            i += 1
    return waf_series


def _precondition(sim, cfg, frac=0.80):
    """Precondition the SSD to `frac` valid blocks (paper setup) via a sequential
    fill, then reset counters so WAF/wear reflect only the measured workload."""
    fill_pages = min(int(frac * cfg.total_pages), int(0.98 * cfg.logical_pages))
    for lpn in range(fill_pages):
        sim.write(lpn)
    sim.reset_counters()


def _run(cfg, scheme, pat, total_writes=TOTAL_WRITES, passes=PASSES,
         sample=False, capture_stages=False):
    """Validated methodology: the workload footprint is 80% of capacity (the
    paper's "80% valid blocks"); replaying it `passes` times fills the device
    and drives GC.  No separate preconditioning is used.

    stage1 layout = after the first pass (device ~80% full, before heavy GC);
    stage2 layout = after all passes complete."""
    sim = Simulator(cfg, scheme=scheme, gc_policy=cfg.gc_policy)
    footprint = min(int(0.80 * cfg.total_pages), int(0.98 * cfg.logical_pages))
    base = _base_sequence(pat, total_writes // passes, footprint)
    total = passes * len(base)
    step = max(1, total // 200)
    waf_series, stage1, i = [], None, 0
    for p in range(passes):
        for lpn in base:
            sim.write(int(lpn))
            if sample and (i % step == 0):
                waf_series.append([sim.host_writes, round(sim.waf, 4)])
            i += 1
        if capture_stages and p == 0:
            stage1 = _snap_layout(sim)
    return sim, waf_series, stage1


# ---------------- experiments ----------------
def exp_synthetic(quick):
    """WAF + all wear metrics per workload per OPS, + waf-vs-time + placement snaps."""
    ops = [0.10, 0.20] if quick else [0.10, 0.20, 0.25]
    total = 600_000 if quick else TOTAL_WRITES
    out = {"ops": ops, "total_writes": total, "passes": PASSES,
           "rows": [], "waf_series": {}, "placement": {}, "distributions": {}}
    for op in ops:
        cfg = paper_cfg(op=op)
        for pat in ("sequential", "uniform", "zipf"):
            sim, series, stage1 = _run(cfg, "s1", pat, total_writes=total,
                                       sample=(op == 0.10),
                                       capture_stages=(op == 0.10))
            snap = sim.snapshot()
            wr = metrics.wear_report(snap["erase_per_block"])
            out["rows"].append({
                "op": op, "workload": pat, "waf": round(sim.waf, 4),
                "doipd": round(metrics.doipd(snap["invalid_per_block"]), 3),
                "mean_erase": round(wr["mean_erase"], 4),
                "doec": round(wr["doec_std"], 4),
                "cv": round(wr["cv"], 4), "gini": round(wr["gini"], 4),
                "fourier_sigma": round(wr["fourier_sigma"], 3),
            })
            if op == 0.10:
                out["waf_series"][pat] = series
                out["placement"][pat] = {
                    "stage1": stage1,
                    "stage2": {"invalid": snap["invalid_per_block"].tolist(),
                               "valid": snap["valid_per_block"].tolist()},
                }
                out["distributions"][pat] = {
                    "invalid_per_block": snap["invalid_per_block"].tolist(),
                    "erase_per_block": snap["erase_per_block"].tolist(),
                }
    return out


def exp_allocation(quick):
    """S1-S6 wear comparison: FFT sigma vs Gini vs CV vs DoEC (all now distinct)."""
    schemes = ["s1", "s2", "s3", "s4", "s5", "s6"]
    cfg = paper_cfg(op=0.10)
    total = 600_000 if quick else TOTAL_WRITES
    out = {"rows": [], "total_writes": total, "passes": PASSES}
    for pat in ("sequential", "uniform", "zipf"):
        for s in schemes:
            sim, _, _ = _run(cfg, s, pat, total_writes=total)
            e = sim.snapshot()["erase_per_block"]
            wr = metrics.wear_report(e)
            out["rows"].append({
                "workload": pat, "scheme": s.upper(),
                "doec": round(wr["doec_std"], 4), "cv": round(wr["cv"], 4),
                "gini": round(wr["gini"], 4),
                "fourier_sigma": round(wr["fourier_sigma"], 3),
                "waf": round(sim.waf, 4)})
    return out


def exp_gcpolicy(quick):
    """Greedy vs cost-benefit vs FIFO (answers advanced-GC reviewer concern)."""
    total = 600_000 if quick else TOTAL_WRITES
    out = {"rows": [], "total_writes": total, "passes": PASSES}
    for policy in ("greedy", "cost_benefit", "fifo"):
        cfg = paper_cfg(op=0.10, gc_policy=policy)
        for pat in ("sequential", "uniform", "zipf"):
            sim, _, _ = _run(cfg, "s1", pat, total_writes=total)
            snap = sim.snapshot()
            wr = metrics.wear_report(snap["erase_per_block"])
            out["rows"].append({
                "policy": policy, "workload": pat, "waf": round(sim.waf, 4),
                "doec": round(wr["doec_std"], 4), "gini": round(wr["gini"], 4)})
    return out


def exp_realtrace(quick):
    """TPC-C (and prxy if present) WAF + DoIPD vs OPS from real traces.

    Same methodology as synthetics: take a base of TOTAL_WRITES//PASSES trace
    writes, replay PASSES times (total ~ TOTAL_WRITES)."""
    tdir = os.path.join(os.path.dirname(__file__), "..", "real_data", "traces")
    traces = {}
    tpcc = os.path.join(tdir, "W2K8.TPCC.trace.csv.bz2")
    if os.path.exists(tpcc):
        traces["TPC-C"] = ("etw", tpcc)
    prxy = os.path.join(tdir, "prxy_0.csv")
    if os.path.exists(prxy):
        traces["prxy"] = ("msr", prxy)
    ops = [0.25, 0.10] if quick else [0.25, 0.20, 0.15, 0.10, 0.05]
    total = 600_000 if quick else TOTAL_WRITES
    base_len = total // PASSES
    out = {"ops": ops, "rows": [], "available": list(traces),
           "total_writes": total, "passes": PASSES,
           "note": "each trace runs on a device sized to its own footprint "
                   "(~85% of usable space at each OP); raw LBAs mod logical "
                   "capacity preserve both sequentiality and locality"}
    FILL = 0.85
    PPB = 64
    planes = 2 * 2 * 2 * 4
    for name, (kind, path) in traces.items():
        reader = (workloads.etw_trace_writes if kind == "etw"
                  else workloads.msr_trace_writes)
        base = []
        for lpn in reader(path, page_size=PAGE):
            base.append(lpn)
            if len(base) >= base_len:
                break
        base = np.asarray(base, dtype=np.int64)
        footprint = int(len(np.unique(base)))
        for op in ops:
            # size the device so the trace footprint fills ~FILL of usable space
            target_logical = footprint / FILL
            total_pages = target_logical / (1.0 - op)
            bpp = max(2, round(total_pages / (planes * PPB)))
            cfg = paper_cfg(op=op, blocks_per_plane=bpp, ppb=PPB)
            sim = Simulator(cfg, scheme="s1", gc_policy="greedy")
            _replay(sim, base % cfg.logical_pages, PASSES)
            snap = sim.snapshot()
            out["rows"].append({
                "trace": name, "op": op, "waf": round(sim.waf, 4),
                "doipd": round(metrics.doipd(snap["invalid_per_block"]), 3),
                "mean_invalid": round(float(snap["invalid_per_block"].mean()), 3),
                "unique_lpns": footprint, "ssd_mb": round(cfg.raw_capacity_bytes / 1e6, 1),
                "n_writes": PASSES * len(base)})
    return out


def exp_scalability(quick):
    """Show the engine runs at large capacity; report throughput + memory shape."""
    out = {"rows": []}
    caps = [("5GB", 150), ("20GB", 600)] if quick else [
        ("5GB", 150), ("20GB", 600), ("40GB", 1200)]
    for label, bpp in caps:
        cfg = paper_cfg(op=0.10, blocks_per_plane=bpp)
        sim = Simulator(cfg, scheme="s1", gc_policy="greedy")
        lp = cfg.logical_pages
        n = int(0.6 * lp)   # partial fill is enough to show it runs at scale
        t0 = time.time()
        for lpn in workloads.uniform_random(n, lp, seed=0):
            sim.write(lpn)
        dt = time.time() - t0
        out["rows"].append({
            "label": label, "raw_gb": round(cfg.raw_capacity_bytes / 1e9, 2),
            "total_blocks": cfg.total_blocks, "writes": n,
            "seconds": round(dt, 2),
            "writes_per_sec": int(n / dt) if dt else 0,
            "waf": round(sim.waf, 4)})
    return out


EXPERIMENTS = {"synthetic": exp_synthetic, "allocation": exp_allocation,
               "gcpolicy": exp_gcpolicy, "realtrace": exp_realtrace,
               "scalability": exp_scalability}


def main():
    quick = "--quick" in sys.argv
    only = None
    for a in sys.argv:
        if a.startswith("--only"):
            only = set(sys.argv[sys.argv.index(a) + 1].split(","))
    todo = [k for k in EXPERIMENTS if (only is None or k in only)]
    print(f"running: {todo}  quick={quick} total_writes={TOTAL_WRITES} passes={PASSES}")
    for name in todo:
        t0 = time.time()
        res = EXPERIMENTS[name](quick)
        path = os.path.join(RESULTS, f"{name}.json")
        with open(path, "w") as fh:
            json.dump(res, fh, indent=2)
        print(f"[{name}] done in {time.time()-t0:.1f}s -> {path}")


if __name__ == "__main__":
    main()
