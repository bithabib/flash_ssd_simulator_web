"""Wear-leveling and distribution metrics.

Includes the paper's DoIPD / DoEC (standard deviations) plus two robust
dispersion metrics -- Coefficient of Variation and the Gini coefficient --
and the Fourier amplitude spread.  Providing CV and Gini alongside the Fourier
analysis directly answers the reviewers who asked why a frequency-domain method
is used instead of, or in addition to, standard statistical dispersion measures
(R1-6, R1-a5, R2-S3, R3-3).
"""
from __future__ import annotations
import numpy as np


def doipd(invalid_per_block) -> float:
    """Degree of Invalid Page Distribution = population std of invalid pages."""
    x = np.asarray(invalid_per_block, dtype=float)
    return float(x.std())  # population std (ddof=0), matches the paper's formula


def doec(erase_per_block) -> float:
    """Degree of Erase Count = population std of erase counts (wear_degree)."""
    x = np.asarray(erase_per_block, dtype=float)
    return float(x.std())


def coefficient_of_variation(x) -> float:
    """CV = std / mean.  Scale-free dispersion; 0 == perfectly uniform wear."""
    x = np.asarray(x, dtype=float)
    m = x.mean()
    return float(x.std() / m) if m > 0 else 0.0


def gini(x) -> float:
    """Gini coefficient in [0,1]; 0 == perfectly even wear, 1 == maximally skewed.

    A widely-accepted inequality measure -- included as the intuitive,
    domain-standard counterpart to the Fourier amplitude spread.
    """
    x = np.asarray(x, dtype=float)
    if x.size == 0 or np.all(x == 0):
        return 0.0
    if np.any(x < 0):
        x = x - x.min()
    xs = np.sort(x)
    n = xs.size
    cum = np.cumsum(xs)
    # relative mean absolute difference formulation
    return float((2.0 * np.sum((np.arange(1, n + 1)) * xs) / (n * cum[-1])) - (n + 1.0) / n)


def fourier_amplitude_spread(x):
    """Return (amplitudes, mean_amplitude, std_amplitude) of the one-sided DFT.

    Matches the paper's sigma_A: std of |X[k]| over k in [0, N/2).
    """
    x = np.asarray(x, dtype=float)
    N = x.size
    X = np.fft.rfft(x)
    amp = np.abs(X)
    # Exclude the DC term (k=0): it encodes the mean erase level, not the
    # block-to-block *variation* that wear-leveling is about.  With DC removed,
    # a perfectly uniform erase distribution correctly yields zero spread.
    amp = amp[1: N // 2] if N > 2 else amp[1:]
    mu = float(amp.mean()) if amp.size else 0.0
    sigma = float(amp.std()) if amp.size else 0.0
    return amp, mu, sigma


def wear_report(erase_per_block) -> dict:
    """All wear-uniformity metrics in one place for a fair side-by-side."""
    e = np.asarray(erase_per_block, dtype=float)
    _, mu_a, sigma_a = fourier_amplitude_spread(e)
    return {
        "mean_erase": float(e.mean()),
        "doec_std": doec(e),
        "cv": coefficient_of_variation(e),
        "gini": gini(e),
        "fourier_sigma": sigma_a,
        "fourier_mean_amp": mu_a,
    }
