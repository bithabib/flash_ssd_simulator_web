"""EyanaSSDSim headless simulation engine (rebuilt).

A deterministic, testable, headless SSD FTL simulator with pluggable garbage
collection, physically-distinct S1-S6 allocation, and reproducible metrics
(WAF, DoIPD, DoEC, CV, Gini, Fourier).  Replaces the ad-hoc browser-JS engine
whose correctness bugs are documented in AUDIT_FINDINGS.md.
"""
from .config import SSDConfig
from .simulator import Simulator
from .allocation import Allocator, SCHEME_ORDERS, distinct_scheme_check
from . import metrics, workloads

__all__ = ["SSDConfig", "Simulator", "Allocator", "SCHEME_ORDERS",
           "distinct_scheme_check", "metrics", "workloads"]
