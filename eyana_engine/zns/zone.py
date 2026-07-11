"""Zone state model for a Zoned Namespace (ZNS) device."""
from __future__ import annotations
from enum import IntEnum


class ZoneState(IntEnum):
    EMPTY = 0   # erased, write pointer at 0, ready to open
    OPEN = 1    # currently accepting sequential appends
    FULL = 2    # write pointer reached zone capacity
    CLOSED = 3  # explicitly closed (resources released); not modelled deeply here
