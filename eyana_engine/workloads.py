"""Workload generators and real-trace reader.

Synthetic: sequential, uniform-random, Zipf.  Deterministic via an explicit
seed (no global RNG state) so runs are reproducible -- the determinism the
paper claims and the reviewers questioned is made explicit and controllable
here, while a `jitter` hook allows optional stochastic variation for studies.

Real: MSR Cambridge / blktrace CSV format
  DevMajor,DevMinor,CPU,RecordID,Timestamp(ns),PID,Action,OpType,Sector+Size,Proc
Only write requests are emitted as LPNs (page-granular).
"""
from __future__ import annotations
import numpy as np


def sequential(n, logical_pages, start=0):
    for i in range(n):
        yield (start + i) % logical_pages


def uniform_random(n, logical_pages, seed=0):
    rng = np.random.default_rng(seed)
    for lpn in rng.integers(0, logical_pages, size=n):
        yield int(lpn)


def zipf(n, logical_pages, s=1.1, seed=0, hot_space=None):
    """Zipf-distributed LPNs. `s` is the skew; larger => more locality."""
    rng = np.random.default_rng(seed)
    span = hot_space or logical_pages
    # sample ranks via zipf then map into [0, span)
    ranks = rng.zipf(s, size=n)
    for r in ranks:
        yield int((r - 1) % span)


def irregular_random(n, logical_pages, seed=0, n_clusters=8, spread=0.05):
    """Dispersed stochastic accesses with weak, shifting locality (the paper's
    'irregular random' pattern)."""
    rng = np.random.default_rng(seed)
    centers = rng.integers(0, logical_pages, size=n_clusters)
    width = max(1, int(logical_pages * spread))
    for _ in range(n):
        c = centers[rng.integers(0, n_clusters)]
        yield int((c + rng.integers(-width, width + 1)) % logical_pages)


# ---- real trace reader (MSR / blktrace) ----
def msr_trace_writes(path, page_size=4096, writes_only=True, max_lpn=None):
    """Yield page-granular LPNs for write requests in an MSR Cambridge CSV trace.

    Format: Timestamp, Workload, DiskNum, OpType, Offset(bytes), Size(bytes),
            ResponseTime
      128166391024154329,prxy,0,Write,1105182720,1024,1514
    """
    import gzip
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt", errors="ignore") as fh:
        for line in fh:
            parts = line.strip().split(",")
            if len(parts) < 6:
                continue
            op = parts[3].strip()
            if writes_only and op not in ("Write", "W"):
                continue
            try:
                offset = int(parts[4])   # already in bytes
                size = int(parts[5])
            except ValueError:
                continue
            start_page = offset // page_size
            npages = max(1, size // page_size)
            for k in range(npages):
                lpn = start_page + k
                if max_lpn:
                    lpn %= max_lpn
                yield lpn


def _int_auto(tok):
    """Parse an int that may be hex (0x-prefixed) or decimal."""
    tok = tok.strip()
    return int(tok, 16) if tok[:2].lower() == "0x" else int(tok)


def etw_trace_writes(path, page_size=4096, writes_only=True, max_lpn=None):
    """Yield page-granular LPNs from a Windows ETW DiskIO trace (SNIA TPC-C set).

    Event rows look like:
      DiskWrite, TimeStamp, Process ( PID), ThreadID, IrpPtr, ByteOffset,
                 IOSize, ElapsedTime, DiskNum, IrpFlags, ...
    Byte offsets/sizes are absolute bytes.  Read the file already decompressed,
    or pass a path to the .bz2 and it will be streamed via bz2.
    """
    import bz2
    opener = bz2.open if str(path).endswith(".bz2") else open
    with opener(path, "rt", errors="ignore") as fh:
        for line in fh:
            s = line.lstrip()
            if not (s.startswith("DiskWrite") or
                    (not writes_only and s.startswith("DiskRead"))):
                continue
            if s.startswith("DiskWriteInit") or s.startswith("DiskReadInit"):
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 7:
                continue
            try:
                # ByteOffset and IOSize are hex (0x...) in the ETW DiskIO trace
                byte_off = _int_auto(parts[5])
                io_size = _int_auto(parts[6])
            except (ValueError, IndexError):
                continue
            if io_size <= 0:
                continue
            start_page = byte_off // page_size
            npages = max(1, io_size // page_size)
            for k in range(npages):
                lpn = start_page + k
                if max_lpn:
                    lpn %= max_lpn
                yield lpn


GENERATORS = {
    "sequential": sequential,
    "uniform": uniform_random,
    "zipf": zipf,
    "irregular": irregular_random,
}
