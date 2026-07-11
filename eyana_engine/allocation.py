"""Static page-allocation schemes S1-S6.

Every scheme is expressed through ONE general priority-order formula (the law
stated in the paper), so the six schemes can never drift apart through
copy-paste errors (audit findings A1/A2 in the old JS engine).

A scheme maps an LPN to a *parallel unit* = (channel, chip, die, plane).
The block and page within that plane are chosen dynamically by the FTL
(log-structured within the plane), which is what actually spreads wear.
"""
from __future__ import annotations
from .config import SSDConfig

# Priority order of the four parallel dimensions for each scheme, matching the
# paper's definitions.  Left = highest priority (varies fastest with LPN).
SCHEME_ORDERS = {
    "s1": ("chip", "die", "plane", "channel"),
    "s2": ("channel", "chip", "die", "plane"),
    "s3": ("channel", "plane", "chip", "die"),
    "s4": ("channel", "die", "chip", "plane"),
    "s5": ("channel", "plane", "die", "chip"),
    "s6": ("channel", "die", "plane", "chip"),
}

_DIMS = ("channel", "chip", "die", "plane")


class Allocator:
    """Maps LPN -> flat plane index in [0, planes)."""

    def __init__(self, cfg: SSDConfig, scheme: str):
        scheme = scheme.lower()
        if scheme not in SCHEME_ORDERS:
            raise ValueError(f"unknown allocation scheme {scheme!r}; "
                             f"valid: {sorted(SCHEME_ORDERS)}")
        self.cfg = cfg
        self.scheme = scheme
        self.order = SCHEME_ORDERS[scheme]
        self._counts = {"channel": cfg.channel, "chip": cfg.chip,
                        "die": cfg.die, "plane": cfg.plane}

    def unit(self, lpn: int) -> dict:
        """Return the (channel, chip, die, plane) coordinate for an LPN.

        General law: for priority order A,B,C,D with radices n_A..n_D
            A = lpn % n_A
            B = (lpn // n_A) % n_B
            C = (lpn // (n_A*n_B)) % n_C
            D = (lpn // (n_A*n_B*n_C)) % n_D
        """
        coord = {}
        divisor = 1
        for dim in self.order:
            n = self._counts[dim]
            coord[dim] = (lpn // divisor) % n
            divisor *= n
        return coord

    def plane_index(self, lpn: int) -> int:
        """Flatten the coordinate to a plane id in [0, planes).

        Uses a fixed physical ordering (channel outermost) independent of the
        allocation scheme, so the scheme only changes *which* LPNs share a
        plane, not the plane numbering.
        """
        c = self.unit(lpn)
        cfg = self.cfg
        return (((c["channel"] * cfg.chip + c["chip"]) * cfg.die
                 + c["die"]) * cfg.plane + c["plane"])

    def channel_of_plane(self, plane_index: int) -> int:
        return plane_index // (self.cfg.chip * self.cfg.die * self.cfg.plane)


def distinct_scheme_check(cfg: SSDConfig, n_probe: int = 4096) -> dict:
    """Diagnostic: return which schemes produce identical LPN->plane maps.

    Guards against the audit-A1 regression: with a valid config (chip>=2) all
    six schemes must be pairwise distinct.
    """
    sigs = {}
    for s in SCHEME_ORDERS:
        a = Allocator(cfg, s)
        sigs[s] = tuple(a.plane_index(l) for l in range(min(n_probe, cfg.logical_pages)))
    groups: dict = {}
    for s, sig in sigs.items():
        groups.setdefault(sig, []).append(s)
    return {"distinct": len(set(sigs.values())), "collisions":
            [g for g in groups.values() if len(g) > 1]}
