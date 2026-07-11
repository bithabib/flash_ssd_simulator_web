"""Generate a synthetic ZNS-showcase trace (MSR Cambridge CSV format).

There is no public ZNS block trace, so this builds a workload that *exercises*
the ZNS contract: a small, heavily-overwritten HOT set (which invalidates pages
and forces host garbage collection + whole-zone resets) interleaved with
write-once COLD sequential data (which lands in stable zones and is rarely
reset). This hot/cold skew is precisely where host-managed ZNS with hot/cold
zone separation reduces write amplification versus a conventional device.

Output format (parsed by workloads.msr_trace_writes):
    Timestamp, Workload, DiskNum, OpType, Offset(bytes), Size(bytes), ResponseTime

The file is written to real_data/uploaded_traces/ so it appears in the web
tool's trace list immediately. Run:  python -m eyana_engine.make_zns_example_trace
"""
from __future__ import annotations
import os
import random

PAGE = 4096


def generate(path, n_records=400_000, span_pages=200_000, hot_pages=8_000,
             p_hot=0.70, skew=1.3, seed=42):
    """Write an MSR-format ZNS-showcase trace.

    span_pages : size of the logical footprint (hot region + cold region)
    hot_pages  : size of the frequently-overwritten hot set (LPN [0, hot_pages))
    p_hot      : fraction of writes that target the hot set
    skew       : >1 biases hot writes toward the hottest LPNs (Zipf-like)
    """
    rng = random.Random(seed)
    cold_cursor = hot_pages          # cold LPNs start just above the hot region
    ts = 10 ** 17
    n_hot = n_cold = 0
    with open(path, "w") as f:
        for _ in range(n_records):
            ts += rng.randint(50, 5000)
            if rng.random() < p_hot:
                # hot overwrite: single page, skewed toward the hottest LPNs
                lpn = int(hot_pages * (rng.random() ** skew))
                if lpn >= hot_pages:
                    lpn = hot_pages - 1
                size = PAGE
                n_hot += 1
            else:
                # cold write-once: a short sequential run of pages
                run = rng.choice([1, 2, 4, 8])
                lpn = cold_cursor
                cold_cursor += run
                if cold_cursor >= span_pages:   # wrap once cold region is full
                    cold_cursor = hot_pages
                size = run * PAGE
                n_cold += 1
            f.write(f"{ts},zns_demo,0,Write,{lpn * PAGE},{size},0\n")
    return {"records": n_records, "hot_writes": n_hot, "cold_writes": n_cold,
            "span_pages": span_pages, "hot_pages": hot_pages, "path": path}


if __name__ == "__main__":
    here = os.path.dirname(__file__)
    out_dir = os.path.join(here, "..", "real_data", "uploaded_traces")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "zns_hotcold_demo.csv")
    info = generate(out)
    sz = os.path.getsize(out)
    print(f"wrote {info['records']:,} records "
          f"({info['hot_writes']:,} hot / {info['cold_writes']:,} cold) "
          f"-> {out}  ({sz/1e6:.1f} MB)")
