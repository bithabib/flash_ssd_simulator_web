"""ZNS correctness tests: sequential write, whole-zone reset, no data loss, WA."""
import numpy as np
import pytest

from eyana_engine import SSDConfig
from eyana_engine.zns import ZNSDevice, HostFTL, ZNSSimulator, ZoneState


def cfg():
    return SSDConfig(channel=2, chip=2, die=2, plane=2, blocks_per_plane=8,
                     pages_per_block=8, op_ratio=0.2)


def test_zone_geometry_divides():
    c = cfg()
    dev = ZNSDevice(c, blocks_per_zone=8)
    assert dev.n_zones * dev.bpz == c.total_blocks
    assert dev.zone_pages == 8 * c.pages_per_block


def test_bad_zone_size_rejected():
    with pytest.raises(ValueError):
        ZNSDevice(cfg(), blocks_per_zone=7)   # 128 % 7 != 0


def test_sequential_append_and_full_then_reset():
    dev = ZNSDevice(cfg(), blocks_per_zone=2)  # small zones
    z = 0
    for i in range(dev.zone_pages):
        dev.append(z, lpn=i)
    assert dev.state[z] == ZoneState.FULL
    with pytest.raises(RuntimeError):
        dev.append(z, lpn=999)                 # cannot append past full
    dev.reset(z)
    assert dev.state[z] == ZoneState.EMPTY
    assert dev.wp[z] == 0
    # every block in the zone was erased exactly once
    assert dev.erase_count[0:dev.bpz].tolist() == [1, 1]


def test_wa_is_one_without_gc():
    c = cfg()
    sim = ZNSSimulator(c, blocks_per_zone=8, op_ratio=0.2, hot_cold=False)
    # write few unique pages: no zone ever fills enough to require GC
    rep = sim.run(range(20))
    assert rep["gc_writes"] == 0
    assert rep["write_amplification"] == 1.0
    assert rep["device_writes"] == rep["host_writes"] == 20


def test_no_data_loss_through_host_gc():
    c = cfg()
    sim = ZNSSimulator(c, blocks_per_zone=4, op_ratio=0.25, hot_cold=True)
    rng = np.random.default_rng(0)
    span = int(c.logical_pages * 0.6)
    latest = {}
    for _ in range(8000):
        lpn = int(rng.integers(0, span))
        sim.host.write(lpn)
        latest[lpn] = True
    assert sim.dev.total_resets > 0, "expected host GC to reset zones"
    for lpn in latest:
        ppn = sim.host.forward[lpn]
        assert ppn != -1
        assert sim.dev.reverse[ppn] == lpn, f"lpn {lpn} not recoverable after GC"


def test_wa_identity():
    c = cfg()
    sim = ZNSSimulator(c, blocks_per_zone=4, op_ratio=0.25, hot_cold=False)
    rng = np.random.default_rng(1)
    span = int(c.logical_pages * 0.6)
    for _ in range(8000):
        sim.host.write(int(rng.integers(0, span)))
    h, g = sim.host.host_writes, sim.host.gc_writes
    assert sim.dev.device_writes == h + g
    assert abs(sim.host.write_amplification - (h + g) / h) < 1e-9


def test_valid_in_zone_matches_maps():
    c = cfg()
    sim = ZNSSimulator(c, blocks_per_zone=4, op_ratio=0.25, hot_cold=True)
    rng = np.random.default_rng(2)
    for _ in range(6000):
        sim.host.write(int(rng.integers(0, int(c.logical_pages * 0.5))))
    dev, host = sim.dev, sim.host
    for z in range(dev.n_zones):
        base = dev.zone_base_ppn(z)
        live = 0
        for off in range(dev.zone_pages):
            ppn = base + off
            lpn = dev.reverse[ppn]
            if lpn != -1 and host.forward[lpn] == ppn:
                live += 1
        assert host.valid_in_zone[z] == live, f"zone {z} valid mismatch"
