"""Cost-benefit GC (Kawaguchi et al., FAST-style).

Scores each candidate block by  (age * (1 - u)) / (2u)  where u is the fraction
of valid pages and `age` is time since the block's last modification.  This
balances migration cost against the benefit of reclaiming space and biases
against repeatedly cleaning hot blocks -- a policy the reviewers asked the
simulator to support beyond plain greedy (R1-2, R2-W1, R3-2).
"""
from __future__ import annotations
from .base import GCPolicy


class CostBenefitGC(GCPolicy):
    name = "cost_benefit"

    def select_victim(self, candidate_blocks, dev) -> int:
        best, best_score = -1, float("-inf")
        ppb = dev.cfg.pages_per_block
        now = dev.now_seq
        for b in candidate_blocks:
            valid = dev.valid_count[b]
            u = valid / ppb
            if u >= 1.0:
                continue  # no benefit: nothing to reclaim
            age = max(1, now - dev.last_modified[b])
            # benefit/cost; higher is better. u==0 -> effectively infinite.
            score = float("inf") if u == 0 else (age * (1.0 - u)) / (2.0 * u)
            if score > best_score:
                best_score, best = score, b
        # fall back to any block with invalid pages if all were fully valid
        if best == -1:
            for b in candidate_blocks:
                if dev.invalid_count[b] > 0:
                    return b
        return best
