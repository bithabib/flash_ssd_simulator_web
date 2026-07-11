"""Pluggable garbage-collection policies."""
from .base import GCPolicy
from .greedy import GreedyGC
from .cost_benefit import CostBenefitGC
from .fifo import FifoGC

_REGISTRY = {"greedy": GreedyGC, "cost_benefit": CostBenefitGC, "fifo": FifoGC}


def make_policy(name: str) -> GCPolicy:
    name = name.lower()
    if name not in _REGISTRY:
        raise ValueError(f"unknown gc_policy {name!r}; valid: {sorted(_REGISTRY)}")
    return _REGISTRY[name]()
