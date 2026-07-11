"""Base class for garbage-collection victim-selection policies.

A policy only decides *which* block to reclaim among the candidate blocks of a
plane.  The FTL performs the actual valid-page migration and erase, so every
policy shares identical, verified migration accounting (fixes audit A8/B7/C5
where victim selection and migration were tangled together).
"""
from __future__ import annotations
from abc import ABC, abstractmethod


class GCPolicy(ABC):
    name = "base"

    @abstractmethod
    def select_victim(self, candidate_blocks, dev) -> int:
        """Return the block id to reclaim from `candidate_blocks`.

        `dev` is the Device, exposing per-block invalid_count / valid_count /
        erase_count arrays.  Must return a block with at least one invalid page
        (the FTL guarantees the candidate set is non-empty and contains such a
        block); returning an all-valid block is a policy error.
        """
        raise NotImplementedError
