"""Re-run the validation workloads on a 1 GB SSD (the size used for the
FTLSim/FEMU comparison) and print WAF at 10% and 25% OP."""
import os
import numpy as np
from .config import SSDConfig
from .simulator import Simulator
from . import workloads
from .run_experiments import _base_sequence, _replay, _precondition, PAGE, PASSES, TOTAL_WRITES

TDIR = os.path.join(os.path.dirname(__file__), "..", "real_data", "traces")


def cfg_1gb(op):
    # 2*2*2*4=32 planes; 38 blocks/plane * 256 pages * 4096 B ~= 1.27 GB
    return SSDConfig(channel=2, chip=2, die=2, plane=4, blocks_per_plane=38,
                     pages_per_block=256, page_size=PAGE, op_ratio=op,
                     gc_high_watermark=0.95, gc_low_watermark=0.90)


def trace_base(kind, path, n):
    reader = workloads.etw_trace_writes if kind == "etw" else workloads.msr_trace_writes
    base = []
    for lpn in reader(path, page_size=PAGE):
        base.append(lpn)
        if len(base) >= n:
            break
    return np.asarray(base, dtype=np.int64)


def run(workload, op, total=TOTAL_WRITES, precondition=False):
    cfg = cfg_1gb(op)
    sim = Simulator(cfg, scheme="s1", gc_policy="greedy")
    if precondition:
        _precondition(sim, cfg, 0.80)
    if workload in ("sequential", "uniform", "zipf"):
        # workload footprint = 80% of capacity (the paper's "80% valid blocks"),
        # capped to stay within the usable logical space
        footprint = min(int(0.80 * cfg.total_pages), int(0.98 * cfg.logical_pages))
        base = _base_sequence(workload, total // PASSES, footprint)
    elif workload == "TPC-C":
        base = trace_base("etw", os.path.join(TDIR, "W2K8.TPCC.trace.csv.bz2"), total // PASSES)
        base = base % cfg.logical_pages
    elif workload == "prxy":
        base = trace_base("msr", os.path.join(TDIR, "prxy_0.csv"), total // PASSES)
        base = base % cfg.logical_pages
    _replay(sim, base, PASSES)
    return sim.waf, int(len(np.unique(base)))


if __name__ == "__main__":
    print(cfg_1gb(0.10).summary())
    # reference bars read from Figure 12
    ftl = {"sequential": 1.78, "uniform": 2.55, "zipf": 1.13, "TPC-C": 6.05, "prxy": 8.50}
    femu = {"sequential": 1.05, "uniform": 1.28, "zipf": 1.00, "TPC-C": 1.50, "prxy": 1.00}
    print(f"\n{'workload':11} {'Eyana@10%':>10} {'FTLSim':>7} | {'Eyana@25%':>10} {'FEMU':>6} {'uniqLPN':>8}")
    print("-" * 62)
    for wl in ("sequential", "uniform", "zipf", "TPC-C", "prxy"):
        w10, u = run(wl, 0.10)
        w25, _ = run(wl, 0.25)
        print(f"{wl:11} {w10:10.3f} {ftl[wl]:7.2f} | {w25:10.3f} {femu[wl]:6.2f} {u:8}")
