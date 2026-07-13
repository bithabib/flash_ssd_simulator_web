"""Flexible Data Placement (FDP) subsystem for EyanaSSDSim.

Models NVMe FDP (TP 4146): the host tags each write with a placement handle
(Reclaim Unit Handle, RUH); the device places same-handle writes into the same
Reclaim Unit (RU) and performs its OWN garbage collection, but keeps the data
separated by handle so GC victims are mostly-invalid together -> lower write
amplification. This sits between a conventional SSD (no hints, mixed data) and
ZNS (host-managed sequential zones).
"""
from .fdp_engine import FDPEngine

__all__ = ["FDPEngine"]
