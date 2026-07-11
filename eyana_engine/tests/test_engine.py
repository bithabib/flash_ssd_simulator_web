"""Correctness tests pinning the math that the old engine got wrong.

Run:  python -m pytest eyana_engine/tests -q
"""
import numpy as np
import pytest

from eyana_engine import SSDConfig, Simulator, distinct_scheme_check
from eyana_engine.allocation import Allocator, SCHEME_ORDERS
from eyana_engine import metrics


def small_cfg(**kw):
    base = dict(channel=2, chip=2, die=2, plane=2, blocks_per_plane=8,
                pages_per_block=8, op_ratio=0.1,
                gc_high_watermark=0.75, gc_low_watermark=0.5)
    base.update(kw)
    return SSDConfig(**base)


# ---- config validation (audit A1) ----
def test_chip_one_rejected():
    with pytest.raises(ValueError):
        small_cfg(chip=1).validate()


def test_all_six_schemes_distinct_when_chip_ge_2():
    cfg = small_cfg()
    res = distinct_scheme_check(cfg)
    assert res["distinct"] == 6, res
    assert res["collisions"] == []


def test_schemes_collapse_documented_at_chip1():
    # bypass validation to demonstrate WHY chip>=2 is required
    cfg = SSDConfig(channel=2, chip=1, die=2, plane=2, blocks_per_plane=8,
                    pages_per_block=8)
    res = distinct_scheme_check(cfg)
    # find which collision group each scheme lands in
    def group_of(s):
        for g in res["collisions"]:
            if s in g:
                return set(g)
        return {s}
    # with a single chip, S2/S4 (and S6) collapse together, as do S3/S5
    assert {"s2", "s4"}.issubset(group_of("s2"))
    assert {"s3", "s5"}.issubset(group_of("s3"))
    assert res["distinct"] < 6


# ---- allocation formula ----
def test_allocation_is_bijective_over_planes():
    cfg = small_cfg()
    for s in SCHEME_ORDERS:
        a = Allocator(cfg, s)
        seen = [a.plane_index(l) for l in range(cfg.planes)]
        assert sorted(seen) == list(range(cfg.planes)), f"{s} not bijective"


# ---- WAF definition (audit C2/A-WAF) ----
def test_waf_one_when_no_gc():
    cfg = small_cfg()
    sim = Simulator(cfg, scheme="s1", gc_policy="greedy")
    # write far fewer unique pages than capacity -> no GC, no rewrites
    for lpn in range(50):
        sim.write(lpn)
    assert sim.gc_writes == 0
    assert sim.waf == 1.0
    assert sim.physical_writes == sim.host_writes == 50


def test_waf_counts_only_host_in_denominator():
    cfg = small_cfg()
    sim = Simulator(cfg, scheme="s1", gc_policy="greedy")
    # Scattered writes across most of the address space force GC victims to
    # still hold valid pages -> real migration writes (unlike a tiny hot set,
    # where greedy reclaims fully-invalid blocks with zero migration).
    rng = np.random.default_rng(7)
    span = int(cfg.logical_pages * 0.9)
    for _ in range(60000):
        sim.write(int(rng.integers(0, span)))
    assert sim.erases > 0, "expected GC to fire"
    assert sim.gc_writes > 0, "scattered workload should force valid-page migration"
    # denominator is host writes only; WAF = (host+gc)/host > 1
    assert sim.host_writes == 60000
    assert abs(sim.waf - (sim.host_writes + sim.gc_writes) / sim.host_writes) < 1e-9
    assert sim.waf > 1.0


# ---- no data loss across heavy GC (audit C1) ----
def test_no_data_loss_after_gc():
    cfg = small_cfg()
    sim = Simulator(cfg, scheme="s2", gc_policy="greedy")
    truth = {}
    rng = np.random.default_rng(0)
    span = 200
    for step in range(6000):
        lpn = int(rng.integers(0, span))
        sim.write(lpn)
        truth[lpn] = True
    # every LPN ever written must still be mapped to a live physical page
    for lpn in truth:
        ppn = sim.dev.forward_map[lpn]
        assert ppn != -1, f"lpn {lpn} lost its mapping"
        assert sim.dev.is_page_valid(ppn), f"lpn {lpn} points at a dead page"


# ---- per-block accounting stays consistent (valid/invalid vs maps) ----
def test_block_counters_match_maps():
    cfg = small_cfg()
    sim = Simulator(cfg, scheme="s3", gc_policy="cost_benefit")
    rng = np.random.default_rng(1)
    for _ in range(5000):
        sim.write(int(rng.integers(0, 300)))
    dev = sim.dev
    ppb = cfg.pages_per_block
    for b in range(cfg.total_blocks):
        if dev.is_free[b]:
            assert dev.valid_count[b] == 0 and dev.invalid_count[b] == 0
            continue
        live = 0
        for off in range(ppb):
            ppn = b * ppb + off
            if dev.is_page_valid(ppn):
                live += 1
        assert dev.valid_count[b] == live, f"block {b} valid mismatch"


# ---- block closes at exactly pages_per_block (audit A3 off-by-one) ----
def test_block_fills_all_pages():
    cfg = small_cfg(gc_high_watermark=0.99, gc_low_watermark=0.9)
    sim = Simulator(cfg, scheme="s1", gc_policy="greedy")
    # write unique pages to fill one plane's first block completely
    ppb = cfg.pages_per_block
    written = 0
    lpn = 0
    while written < ppb and lpn < cfg.logical_pages:
        p = sim.alloc.plane_index(lpn)
        if p == 0:
            sim.write(lpn)
            written += 1
        lpn += 1
    # the first fully-written block in plane 0 must hold ppb valid pages, not ppb-1
    dev = sim.dev
    plane0_blocks = [b for b in range(cfg.blocks_per_plane)]
    assert max(int(dev.valid_count[b]) for b in plane0_blocks) == ppb


# ---- metrics sanity ----
def test_metrics_uniform_vs_skewed():
    uniform = np.array([5, 5, 5, 5, 5])
    skewed = np.array([0, 0, 0, 0, 25])
    assert metrics.gini(uniform) == pytest.approx(0.0, abs=1e-9)
    assert metrics.gini(skewed) > 0.5
    assert metrics.coefficient_of_variation(uniform) == pytest.approx(0.0, abs=1e-9)
    assert metrics.coefficient_of_variation(skewed) > metrics.coefficient_of_variation(uniform)


def test_fourier_flat_signal_zero_spread():
    flat = np.ones(64)
    _, _, sigma = metrics.fourier_amplitude_spread(flat)
    assert sigma == pytest.approx(0.0, abs=1e-9)
