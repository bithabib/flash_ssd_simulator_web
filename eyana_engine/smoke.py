"""Quick end-to-end sanity run: WAF + wear metrics per workload and policy."""
from eyana_engine import SSDConfig, Simulator, metrics, workloads


def run(pattern, scheme="s1", policy="greedy", op=0.10, n=None, seed=0):
    cfg = SSDConfig(channel=2, chip=2, die=2, plane=4, blocks_per_plane=64,
                    pages_per_block=64, op_ratio=op, gc_policy=policy,
                    gc_high_watermark=0.95, gc_low_watermark=0.90)
    sim = Simulator(cfg, scheme=scheme, gc_policy=policy)
    n = n or int(cfg.logical_pages * 3)          # ~3x fill -> steady-state GC
    gen = {
        "sequential": workloads.sequential(n, cfg.logical_pages),
        "uniform":    workloads.uniform_random(n, cfg.logical_pages, seed=seed),
        "zipf":       workloads.zipf(n, cfg.logical_pages, s=1.2, seed=seed),
    }[pattern]
    for lpn in gen:
        sim.write(lpn)
    snap = sim.snapshot()
    wr = metrics.wear_report(snap["erase_per_block"])
    dp = metrics.doipd(snap["invalid_per_block"])
    return cfg, snap, wr, dp


if __name__ == "__main__":
    cfg0 = SSDConfig(channel=2, chip=2, die=2, plane=4, blocks_per_plane=64,
                     pages_per_block=64)
    print(cfg0.summary())
    print(f"logical pages={cfg0.logical_pages}  planes={cfg0.planes}\n")
    hdr = f"{'pattern':10} {'pol':12} {'WAF':>6} {'DoIPD':>7} {'DoEC':>7} {'CV':>6} {'Gini':>6} {'FFTσ':>9}"
    print(hdr); print("-" * len(hdr))
    for policy in ("greedy", "cost_benefit"):
        for pat in ("sequential", "uniform", "zipf"):
            cfg, snap, wr, dp = run(pat, policy=policy)
            print(f"{pat:10} {policy:12} {snap['waf']:6.3f} {dp:7.2f} "
                  f"{wr['doec_std']:7.3f} {wr['cv']:6.3f} {wr['gini']:6.3f} "
                  f"{wr['fourier_sigma']:9.2f}")
