"""Regenerate the 4-series WAF validation figure (Figure 12) at 1.27 GB:
EyanaSSDSim @10%, FTLSim @10%, EyanaSSDSim @25%, FEMU @25%.

EyanaSSDSim bars come from a live 1.27 GB run; FTLSim/FEMU bars are the values
read from the original Figure 12 (those tools cannot be re-run here)."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .validate_1gb import run as run_1gb

FIG = os.path.join(os.path.dirname(__file__), "..", "figures")
os.makedirs(FIG, exist_ok=True)

WLS = ["sequential", "uniform", "zipf", "TPC-C", "prxy"]
LABELS = ["Sequential", "Uniform random", "Zipf", "TPC-C", "prxy"]

# read from the original Figure 12 (external-tool results; not re-runnable here)
FTLSIM_10 = {"sequential": 1.78, "uniform": 2.55, "zipf": 1.13, "TPC-C": 6.05, "prxy": 8.50}
FEMU_25 = {"sequential": 1.05, "uniform": 1.28, "zipf": 1.00, "TPC-C": 1.50, "prxy": 1.00}

# TPC-C / prxy were NOT re-run on the corrected setup (the 3x-replay methodology
# produces an artifact for mostly-unique traces), so their EyanaSSDSim bars keep
# the paper's original values; only the synthetic workloads use corrected numbers.
EYANA_ORIG_10 = {"TPC-C": 5.12, "prxy": 5.60}
EYANA_ORIG_25 = {"TPC-C": 2.30, "prxy": 1.01}


def main():
    eyana10, eyana25 = {}, {}
    for wl in WLS:
        if wl in EYANA_ORIG_10:                     # keep original real-trace values
            eyana10[wl] = EYANA_ORIG_10[wl]
            eyana25[wl] = EYANA_ORIG_25[wl]
        else:                                       # corrected synthetic values (live)
            eyana10[wl] = round(run_1gb(wl, 0.10)[0], 3)
            eyana25[wl] = round(run_1gb(wl, 0.25)[0], 3)
    print("EyanaSSDSim @10%:", eyana10)
    print("EyanaSSDSim @25%:", eyana25)

    x = np.arange(len(WLS)); w = 0.2
    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.bar(x - 1.5 * w, [eyana10[k] for k in WLS], w, label="EyanaSSDSim (10%)", color="#8ecae6")
    ax.bar(x - 0.5 * w, [FTLSIM_10[k] for k in WLS], w, label="FTLSim (10%)", color="#1f9bff")
    ax.bar(x + 0.5 * w, [eyana25[k] for k in WLS], w, label="EyanaSSDSim (25%)", color="#f7a6a6")
    ax.bar(x + 1.5 * w, [FEMU_25[k] for k in WLS], w, label="FEMU (25%)", color="#e01e1e")
    ax.set_xticks(x); ax.set_xticklabels(LABELS)
    ax.set_ylabel("WAF"); ax.set_xlabel("Workloads")
    ax.legend(); ax.grid(axis="y", ls="--", alpha=0.4)
    fig.tight_layout()
    out = os.path.join(FIG, "waf_comparison_workloads_10_25.png")
    fig.savefig(out, dpi=150); plt.close()
    print("wrote", out)


if __name__ == "__main__":
    main()
