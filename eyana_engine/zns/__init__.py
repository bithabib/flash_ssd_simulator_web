"""Zoned Namespace (ZNS) subsystem for EyanaSSDSim (follow-up-paper track).

Models a ZNS device (sequential-write zones, whole-zone reset, no device GC) with
a host-side FTL that performs log-structured mapping and garbage collection, with
optional hot/cold data separation across zones.
"""
from .zone import ZoneState
from .zns_device import ZNSDevice
from .host_ftl import HostFTL
from .zns_simulator import ZNSSimulator

__all__ = ["ZoneState", "ZNSDevice", "HostFTL", "ZNSSimulator"]
