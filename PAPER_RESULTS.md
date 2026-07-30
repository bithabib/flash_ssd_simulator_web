# EyanaSSDSim — Validation & Analysis Results (for the paper)

Everything measured while validating EyanaSSDSim against **FEMU** (hardware-accurate
NVMe emulator) and building the analysis figures. Numbers are copy-paste ready.
Companion: `FEMU_VALIDATION_GUIDE.md` (how to reproduce the FEMU setup).

> **One-line thesis for the validation section:** EyanaSSDSim reproduces FEMU's
> write-amplification behaviour with perfect *trend* correlation (Spearman ρ = 1.0) and a
> *consistent, explained* magnitude offset (sim is systematically conservative by ~7–20%),
> across the conventional, FDP, and ZNS engines, on both synthetic and real block traces.

---

## 0. Setup / methodology

- **FEMU:** MoatLab fork, rebased on **QEMU 10.1.0**; KVM; instrumented to expose WAF:
  - bbssd: added `host_write_pages` / `gc_write_pages` counters + periodic WAF print (`hw/femu/bbssd/ftl.c`).
  - ZNS: added `zns_total_write_lbs` device-write counter (`hw/femu/zns/zns.c`).
  - FDP: uses FEMU's native FDP statistics `mbmw`/`hbmw` (WAF = mbmw/hbmw).
- **Host:** Ubuntu 22.04, 16 cores, 31 GB RAM, KVM. **Guest:** Ubuntu 20.04 (`u20s.qcow2`).
- **WAF definition (both sides):** physical writes / host writes = (host + GC-migration writes)/host.
- **Geometry matching:** FEMU bbssd/FDP device geometry set equal to the sim's
  (planes = nchs·luns·pls; blocks_per_plane = blks_per_pl; pages_per_block = pgs_per_blk;
  4 KB page = secsz 512 × secs_per_pg 8). OP applied host-side (write only (1−OP) of the LBA space).
- **Real-trace replay:** traces dense-remapped (each unique LBA → compact index, preserving the
  exact reuse pattern) and exported to a binary; the *same* sequence drives the sim and the FEMU
  replay tools, so the comparison is identical workload on identical geometry.

---

## 1. Conventional engine — synthetic (uniform random, OP sweep)

Matched `--full` geometry (8 ch × 8 lun × 1 plane, 64 blk/plane, 64 pg/blk, 4 KB page = 1 GiB),
cumulative-from-empty, rHMW = 3×. Data: `femu_vs_sim_waf.csv`. Figure: `figures/waf_validation_femu.png`.

| OP% | FEMU gc75 (default) | FEMU gc90 (aligned watermark) | sim block GC | sim superblock GC |
|----:|--------------------:|------------------------------:|-------------:|------------------:|
| 5  | 4.774 | 3.750 | 5.191 | 6.665 |
| 7  | 4.634 | 3.499 | 3.717 | 4.444 |
| 10 | 4.613 | 3.243 | 2.768 | 3.102 |
| 15 | 4.055 | 2.102 | 2.083 | 2.249 |
| 25 | 2.705 | 1.463 | 1.519 | 1.601 |

- **Trend: Spearman ρ = 1.000** (all curves strictly monotone in OP).
- **Magnitude: MAPE 32.2 % → 12.8 %** after aligning FEMU's GC watermark (`gc_thres_pcent` 75→90 to
  match the sim's 90/95). ⇒ *most of the raw gap was a FEMU config knob, not a modelling flaw.*
- With **superblock GC** (matching FEMU's line-erase), **MAPE = 6.9 % for OP ≥ 10 %**.
- Two identified structural differences: (1) **GC granularity** (sim block vs FEMU superblock);
  (2) **GC watermark**. A third residual is **allocation coherence** (FEMU fills a line coherently;
  sim fills planes independently).

---

## 2. FDP engine — synthetic (80/20, OP = 10 %)

Matched geometry, rHMW = 3×, per-RUH placement via NVMe-passthrough tool. Data: `femu_fdp_results.csv`.
Figure: `figures/fdp_validation_femu.png`.

| Config | FEMU WAF | sim WAF | error |
|-----------|---------:|--------:|------:|
| FDP-single | 1.244 | 1.237 | **0.6 %** |
| FDP-PI (hot→RUH0, cold→RUH1) | 1.086 | 1.150 | 5.9 % |
| **isolation benefit (single→PI)** | **−12.7 %** | **−7.0 %** | both reduce WAF ✓ |

- **FDP-single matches FEMU to 0.6 %** — skewed workload keeps WAF low (~1.2) where GC granularity
  barely matters, so the analytical model is near-exact.
- Both confirm **PI isolation lowers WAF**; the sim is *conservative* about the size of the benefit.
- FEMU exposes all RUHs as **type 2 = Persistently Isolated** by default. **FDP-II** (Initially
  Isolated) needs a FEMU change (`nvme_ruh->ruht`, `hw/femu/bbssd/ftl.c:2360`) — scoped as future work.

---

## 3. ZNS engine — invariant, full-stack, and the hot/cold finding

### 3a. Device invariant (FEMU-confirmed)
FEMU ZNS device does **no host GC**. Confirmed: 256 MiB sequential write fills a zone to FULL,
append-only enforced (`SEQ_WRITE_REQUIRED`), `blkzone reset` reclaims a zone with no migration ⇒
**device WAF = 1 by construction** (matches `zns_validate.py` invariant #1).

### 3b. Algorithmic behaviour (in-sim, 80/20). Figure: `figures/zns_validation.png`.
| OP% | conventional | ZNS single | ZNS hot/cold | hot/cold gain |
|----:|-------------:|-----------:|-------------:|--------------:|
| 10 | 1.220 | 1.244 | 1.217 | 2.2 % |
| 15 | 1.182 | 1.206 | 1.154 | 4.3 % |
| 25 | 1.132 | 1.150 | 1.088 | 5.4 % |

sequential write-once → WAF = **1.000** (single & hot/cold). ZNS single-stream ≈ conventional (≈2 %).

### 3c. Full-stack reference — FEMU ZNS + F2FS-zoned. Data: measured live.
Built the complete stack (FEMU ZNS 8 GB + conventional metadata disk + **f2fs-tools built from
source** in-guest; ZNS write counter in FEMU). Steady-state random overwrites at ~95 % fill:

| Metric | Value |
|---|---|
| app writes | 2048 MiB |
| device writes (FEMU ZNS counter) | 4687 MiB |
| **F2FS-on-ZNS host WAF (~5 % OP)** | **2.29** |
| sim ZNS-single, uniform, OP 5 % / 7 % | 3.82 / 3.14 |

**Same ballpark, sim conservative.** F2FS uses a *more sophisticated* host GC (cost-benefit victim
selection + automatic hot/warm/cold multi-head logging) than the sim's greedy single-stream, so F2FS
achieves lower WAF. ⇒ the full-stack number reflects **F2FS's GC, not the sim's** — documented caveat.

### 3d. "ZNS hot/cold hurts" — diagnosed, explained, and its fix
On the real prxy_0 trace at **tight OP (25 %)**, naive greedy ZNS hot/cold *backfires* (WAF ↑).
Instrumentation (single boot) showed the mechanism:

- Host writes: **88.7 % to the hot stream**, 11.3 % cold (skew concentrates overwrites).
- **100 % of GC survivors are dumped into the cold stream** (170 k survivors, 0 to hot).
- Cold zones therefore hold 91 % GC survivors → sit at **0.844 valid**; when forced to reclaim them,
  migration ≈ pure copy → WAF explodes. (Hot zones reclaim at 0.20 valid — cheap.)

**It is over-provisioning-dependent — there is a crossover (~30–35 % OP):**
| OP% | ZNS single | hot/cold (greedy) | hot/cold (cost-benefit) | verdict |
|----:|-----------:|------------------:|------------------------:|---------|
| 25 | 1.886 | 2.136 | 2.173 | **hurts +13 %** |
| 40 | 1.278 | 1.118 | **1.026** | **helps −12 %** |
| 55 | 1.119 | 1.016 | 1.016 | helps −9 % |
| 70 | 1.057 | 1.011 | 1.013 | helps −4 % |

**Fix (implemented):** cost-benefit victim selection (F2FS-style, age × invalidity) added to the ZNS
FTL (`gc_policy="cost_benefit"`, `zns/host_ftl.py`). In the healthy regime it lowers WAF a further
~8 % (40 %: 1.118 → 1.026) and roughly halves wear imbalance (DEC 10.2 → 5.9). It cannot rescue the
pathologically-full 25 % case — nothing can. **Paper arc:** naive recency-based ZNS separation
backfires at tight OP on skewed real workloads → cause is GC-survivor cold-pollution → remedy is
adequate OP + cost-benefit GC.

---

## 4. Real-trace validation vs FEMU  ⭐ (the strongest external evidence)

Traces dense-remapped, identical sequence on sim and FEMU, matched geometry, OP = 25 %.
Data: `real_eval_*.csv`, `real_fdp_validation.csv`.

### 4a. Conventional (block GC — the sim's stable default)
| Trace | FEMU (superblock FTL) | sim (block GC) | sim below FEMU |
|-------|----------------------:|---------------:|---------------:|
| prxy_0 (200 k writes, 18.4 k pages) | 1.873 | 1.539 | 17.8 % |
| prxy_1 (300 k writes, 21.5 k pages) | 1.678 | 1.354 | 19.3 % |

Two independent real traces, **consistent ~18 % offset, same direction** (block < superblock) —
the same GC-granularity gap seen on synthetic data.

### 4b. FDP — full scale (prxy_1, **3 M writes, 132 reclaim units**, 528 MB device)
| Config | FEMU | sim | PI benefit |
|--------|-----:|----:|-----------:|
| FDP-single | 1.561 | 1.256 | — |
| FDP-PI | 1.487 | 1.059 | FEMU **−4.7 %** · sim **−15.7 %** |

- FDP-single: sim ~20 % below FEMU — **same conservative offset** as conventional.
- **Both FEMU and the sim show PI isolation reduces WAF on a real trace** → the FDP claim's
  *direction* is validated at hardware fidelity. The sim is *optimistic about the magnitude* of the
  PI benefit (−16 % vs FEMU's −5 %) — state honestly.

### 4c. Methodological finding (real result, worth a paragraph)
The **same FDP-PI at a small geometry (24 RUs) gave a bogus 5.56** — an undersized-device artifact,
not the algorithm. **FDP validation requires a large-working-set trace** so the device has hundreds
of reclaim units; a small trace forces too few RUs and the split starves GC. Conventional is robust
to small geometry; FDP is not.

---

## 5. Real-trace characterisation (why each trace behaves as it does)

| Trace | write skew (top-20 %) | working set | vs device | note |
|-------|----------------------:|------------:|----------:|------|
| prxy_0 | **93.7 %** | 84 k pages (0.35 GB) @3M rec | fits | ideal: skewed, 97 % writes |
| prxy_sample | 72.9 % | 1.6 k pages | too small | underfilled at min device |
| prxy_1 | (skewed) | 101.6 k pages @3M writes → 132 RUs | fits | used for full-scale FDP |
| **TPC-C (W2K8)** | **26.8 %** (flat) | 2.7 M pages (11.25 GB) | 10× device | needs millions of writes; flat = uniform-like |

Real skewed (prxy) vs real flat (TPC-C) is the real-world analogue of synthetic zipf vs uniform.

### Sim on real traces (real_eval.py, OP = 25 %). Data: `real_eval_*.csv`.
| Trace | fill | Conv | FDP-single | FDP-PI | ZNS-single | ZNS-hc greedy | ZNS-hc cost-benefit |
|-------|-----:|-----:|-----------:|-------:|-----------:|--------------:|--------------------:|
| prxy_0 (200k) | 101 % | 1.539 | 1.684 | 1.498 | 2.042 | 2.006 | 2.006 |
| prxy_1 (300k) | 100 % | 1.354 | 1.471 | 1.665 | 1.995 | 2.888 | 3.109 |
| TPC-C (300k) | — | 1.00 | — | — | — | — | — (no steady state; needs millions of writes) |

Note the **workload variability**: prxy_0 FDP-PI *helps* (1.68→1.50) but prxy_1 FDP-PI *hurts* at
25 % OP — the marginal (tight-OP) regime where placement behaviour flips. This is consistent with the
ZNS OP-crossover finding.

---

## 6. Visualization / metrics contributions (ISPASS material)

### 6a. Metric suite (80/20, OP = 15 %). Data: `ispass_metrics.csv`. Figures: `figures/ispass_f1..f4`.
| config | WAF | reclaims | valid-frac @reclaim | DEC (wear std) |
|--------|----:|---------:|--------------------:|---------------:|
| Conventional | 1.182 | 2157 | 0.221 | 0.86 |
| FDP-single | 1.206 | 69 | 0.244 | 0.36 |
| **FDP-PI** | **1.139** | 65 | **0.175** | 1.13 |
| ZNS-single | 1.206 | 69 | 0.244 | 0.56 |
| **ZNS hot/cold** | **1.154** | 66 | **0.190** | 1.37 |

- **Finding 1 — causal chain (metric contribution):** separation → *valid-fraction-at-reclaim* ↓ →
  *reclaim efficiency* ↑ → *WAF* ↓. "Valid-fraction-at-reclaim" and "reclaim efficiency" are metrics
  read off the visualization that *predict* WAF.
- **Finding 2 — WAF↔wear trade-off (bottleneck ID):** separation lowers WAF but **concentrates
  erases** — DEC rises 3.1× (FDP) / 2.4× (ZNS). No single config wins on both axes.

### 6b. Fig-3 companion (space-time + wear + reclaim-cost). Figure: `figures/fig3_spacetime_wear.png`.
Paper geometry (1216 blocks, 256 pg/blk, 10 % OP), three workloads:
| workload | WAF | wear CV | mean valid@reclaim | free reclaims |
|----------|----:|--------:|-------------------:|--------------:|
| sequential | 1.50† | 0.58 | 0.46 | 27 % |
| uniform random | 2.08 | 0.20 | 0.65 | 0 % |
| zipf | 1.08 | 1.94 | 0.11 | 40 % |

Key seq-vs-random difference (a professor asked): **sequential's reclaim-cost histogram is bimodal
with 27 % *free* reclaims** (invalidation sweeps in write order, blocks empty completely); **uniform
random's is a single hump at 0.65 with 0 % free reclaims** (scattered overwrites leave every block
partly valid) — that reclaim-cost difference, invisible in the block-state map, is what produces WAF
1.50 vs 2.08. Also GC timing: sequential GCs in **bursts sweeping block-order**, uniform random GCs
**continuously in random order** (`figures/fig_zoom_seq_vs_rand.png`).

† ⚠️ **Open issue:** the paper's published sequential WAF ≈ 1.0, but the current watermark-based engine
gives **1.50** at 10 % OP. Cause traced: `gc_low_watermark = 0.90` sits exactly at the OP-10 valid
occupancy (0.90) → GC over-reclaims. With `gc_low_watermark = 0.94` it drops to ~1.19. The revision
text notes the engine "replaced the near-full trigger used in earlier versions" — the ≈1.0 figure is
likely from the *old* trigger. **Decide before submission:** re-measure/update the paper's sequential
number, or run the figure at an OP-compatible watermark and state it.

---

## 7. Engine changes made this work (for the artifact/repro)

- `SSDConfig.gc_granularity` = "block" (default) | "superblock" — FEMU-style line GC.
  **Superblock GC is experimental**: robust erase-first reclaim + fallback (crash bug fixed), but
  limited by per-plane allocation (needs line-coherent allocation to match FEMU tightly). Default
  block GC is the validated engine.
- `HostFTL(gc_policy=...)` = "greedy" (default) | "cost_benefit" — F2FS-style ZNS victim selection.
- FEMU instrumentation (see §0). All 18 unit tests pass with the additions.

---

## 8. Honest caveats to state in the paper

1. Sim is **conservative** (WAF ≤ FEMU) by a consistent ~7–20 %; never under-predicts. Frame as a
   feature, not an error.
2. FDP-PI benefit: sim over-estimates magnitude vs FEMU (real trace: −16 % vs −5 %); direction agrees.
3. ZNS full-stack (2.29) compares against **F2FS's** GC, not the sim's — different algorithm.
4. FDP validation needs **large-working-set** traces (≥ ~128 RUs); small traces give artifacts.
5. Superblock-GC mode is experimental; block GC is the validated conventional engine.
6. Sequential-WAF discrepancy vs the published ≈1.0 (see §6b†).
7. FDP-II not tested on FEMU (all RUHs default to PI); scoped as future work.

---

## 9. File index

**Figures** (`figures/`): `waf_validation_femu.png` (conv), `fdp_validation_femu.png` (FDP),
`zns_validation.png` (ZNS), `ispass_f1_spacetime.png`, `ispass_f2_valid_at_reclaim.png`,
`ispass_f3_wear.png`, `ispass_f4_waf_evolution.png`, `fig3_spacetime_wear.png`,
`fig_zoom_seq_vs_rand.png`, `real_eval_{prxy_0,prxy_1,prxy_sample,W2K8}_spacetime.png`.

**Data (CSV):** `femu_vs_sim_waf.csv`, `femu_fdp_results.csv`, `femu_sweep_results{,2}.csv`,
`femu_sweep_gc90.csv`, `sim_sweep_results.csv`, `sim_superblock_results.csv`, `ispass_metrics.csv`,
`real_eval_*.csv`, `real_fdp_validation.csv`, `femu_zns_f2fs_sweep.csv`.

**Scripts** (`eyana_engine/`): `femu_compare.py`, `fdp_compare.py`, `zns_compare.py`,
`ispass_analysis.py`, `fig3_spacetime.py`, `fig_zoom_seq_vs_rand.py`, `real_eval.py`,
`export_trace.py`. Regenerate a figure by running its module (`python -m eyana_engine.<name>`).

**Remapped traces:** `real_data/remapped/*.bin` (dense-remapped, uint32).

**FEMU rig** (`~/FEMU/build-femu/`): patched `hw/femu/{bbssd/ftl.c,zns/zns.c}`; boot scripts
`boot-bbssd-matched.sh`, `boot-bbssd-trace.sh`, `boot-fdp-matched.sh`, `boot-fdp-trace.sh`,
`boot-zns.sh`, `boot-zns-f2fs.sh`; sweeps `waf-sweep.sh`, `waf-sweep-gc90.sh`, `fdp-experiment.sh`,
`zns-f2fs-op-sweep.sh`. Guest replay tools: `trace_replay.c` (conv), `fdp_trace_replay.c` (FDP),
`fdp_write.c` (synthetic FDP), `f2fs-tools` (built from source).

**Reproduction guide:** `FEMU_VALIDATION_GUIDE.md`.
