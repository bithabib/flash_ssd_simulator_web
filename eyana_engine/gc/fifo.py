"""FIFO GC: reclaim the oldest-written block that has invalid pages.

Included so EyanaSSDSim can reproduce FEMU's queueing/FIFO-style reclaim for
apples-to-apples WAF validation (the paper attributes some EyanaSSDSim-vs-FEMU
WAF differences to FEMU's FIFO reclaim vs. greedy).
"""
from __future__ import annotations
from .base import GCPolicy


class FifoGC(GCPolicy):
    name = "fifo"

    def select_victim(self, candidate_blocks, dev) -> int:
        best, best_age = -1, float("inf")
        for b in candidate_blocks:
            if dev.invalid_count[b] == 0:
                continue
            if dev.created_seq[b] < best_age:
                best_age, best = dev.created_seq[b], b
        return best if best != -1 else candidate_blocks[0]
