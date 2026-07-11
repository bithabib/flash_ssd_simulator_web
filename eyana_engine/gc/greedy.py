"""Greedy GC: reclaim the block with the most invalid pages.

Minimises valid-page migration per erase.  This is the classic baseline and
what the paper intends (the old JS engine's greedy path was correct, but its
fallback could pick an all-valid victim -- audit A8; here victims are chosen
only among blocks with invalid pages).
"""
from __future__ import annotations
from .base import GCPolicy


class GreedyGC(GCPolicy):
    name = "greedy"

    def select_victim(self, candidate_blocks, dev) -> int:
        best, best_inv = -1, -1
        inv = dev.invalid_count
        for b in candidate_blocks:
            if inv[b] > best_inv:
                best_inv, best = inv[b], b
        return best
