"""FDP validation harness: EyanaSSDSim vs FEMU/WARP.

Runs our FDP engine (and the conventional baseline) across the same synthetic
matrix WARP uses, and prints a table with a blank FEMU column to fill in after
running FEMU on the SAME workloads. The goal is to compare *trends* and, where
geometry matches, magnitudes.

  workloads : uniform random, zipf(1.2), zipf(2.2), 80/20
  configs   : conventional | FDP-single | FDP-PI | FDP-II
  op sweep  : 3, 5, 7, 10, 15, 25 %   (WARP's crossover region is ~7-9%)

FEMU mapping (bbssd) to reproduce each row on the FEMU side:
  conventional : plain bb-ssd (fdp off)
  FDP-single   : fdp on, 1 data RUH
  FDP-PI       : fdp on, RUH type = Persistently Isolated (NVME_RUHT_PERSISTENTLY_ISOLATED)
  FDP-II       : fdp on, RUH type = Initially Isolated     (NVME_RUHT_INITIALLY_ISOLATED)
  gc strategy  : GC_GLOBAL_GREEDY (our victim policy); op_ratio via -device ...,op=..
  workload     : fio, write-only, one stream per RUH, rHMW ~= REL_WRITE x capacity

Run:  python -m eyana_engine.fdp_validate            (quick default matrix)
      python -m eyana_engine.fdp_validate --full     (larger device, slower)
"""
from __future__ import annotations
import sys

import numpy as np

from .config import SSDConfig
from .simulator import Simulator
from .fdp.fdp_engine import FDPEngine
from . import workloads

REL_WRITE = 3.0    # host-written volume as a multiple of logical capacity (rHMW)


def _geometry(full=False):
    # Kept close to FEMU's default parallelism (8 ch x 8 luns) while staying fast.
    if full:
        return dict(channel=8, chip=2, die=4, plane=1, blocks_per_plane=64, pages_per_block=64)
    return dict(channel=4, chip=2, die=2, plane=2, blocks_per_plane=48, pages_per_block=64)


def _cfg(op, full=False):
    return SSDConfig(op_ratio=op, gc_high_watermark=0.95, gc_low_watermark=0.90,
                     **_geometry(full))


def _workload(name, n, lp, seed=1):
    if name == "uniform":
        return workloads.uniform_random(n, lp, seed=seed)
    if name == "zipf1.2":
        return workloads.zipf(n, lp, s=1.2, seed=seed)
    if name == "zipf2.2":
        return workloads.zipf(n, lp, s=2.2, seed=seed)
    if name == "80/20":
        rng = np.random.default_rng(seed)
        hot = max(1, int(0.2 * lp))
        return np.where(rng.random(n) < 0.8,
                        rng.integers(0, hot, n),
                        rng.integers(hot, lp, n)).tolist()
    raise ValueError(name)


def _run(config, op, wl, full=False):
    cfg = _cfg(op, full)
    lp = cfg.logical_pages
    n = int(REL_WRITE * lp)
    stream = _workload(wl, n, lp)
    if config == "conventional":
        sim = Simulator(cfg, scheme="s1", gc_policy="greedy")
        for x in stream:
            sim.write(int(x) % lp)
        return sim.waf
    hot_cold = config != "fdp_single"
    iso = "ii" if config == "fdp_ii" else "pi"
    eng = FDPEngine(cfg, hot_cold=hot_cold, isolation=iso)
    for x in stream:
        eng.write(int(x) % lp)
    return eng.waf


def main(full=False):
    workloads_list = ["uniform", "zipf1.2", "zipf2.2", "80/20"]
    configs = [("conventional", "conventional"), ("fdp_single", "FDP-single"),
               ("fdp_pi", "FDP-PI"), ("fdp_ii", "FDP-II")]
    ops = [0.03, 0.05, 0.07, 0.10, 0.15, 0.25]

    geo = _geometry(full)
    cfg0 = _cfg(0.10, full)
    print(f"# EyanaSSDSim vs FEMU — FDP validation matrix")
    print(f"# geometry: {geo}  (planes={cfg0.planes}, "
          f"RU={cfg0.planes} blocks = {cfg0.planes*cfg0.pages_per_block} pages, "
          f"raw={cfg0.raw_capacity_bytes/1024/1024:.0f} MiB)")
    print(f"# rHMW={REL_WRITE}x logical capacity; WAF = physical/host writes\n")

    header = f"| {'workload':8} | {'config':12} | {'OP%':>3} | {'WAF_ours':>8} | {'WAF_FEMU':>8} | {'match?':>6} |"
    sep = "|" + "-" * 10 + "|" + "-" * 14 + "|" + "-" * 5 + "|" + "-" * 10 + "|" + "-" * 10 + "|" + "-" * 8 + "|"
    print(header)
    print(sep)
    rows = []
    for wl in workloads_list:
        for key, label in configs:
            for op in ops:
                waf = _run(key, op, wl, full)
                rows.append((wl, label, int(op * 100), round(waf, 3)))
                print(f"| {wl:8} | {label:12} | {int(op*100):>3} | {waf:8.3f} | {'':>8} | {'':>6} |")
        print(sep)

    # also dump CSV for easy side-by-side with FEMU
    out = "fdp_validation_results.csv"
    with open(out, "w") as f:
        f.write("workload,config,op_pct,waf_ours,waf_femu\n")
        for wl, label, op, waf in rows:
            f.write(f"{wl},{label},{op},{waf},\n")
    print(f"\n# wrote {out} ({len(rows)} rows) — paste FEMU WAF into the waf_femu column")


if __name__ == "__main__":
    main(full="--full" in sys.argv)
