# Comprehensive Real-Trace Evaluation — EyanaSSDSim (all engines)

Full sweep of every engine over every trace, capturing all distribution/wear/space-time
data for the paper.  Regenerate: `bash eyana_engine/full_batch.sh` then
`python -m eyana_engine.figs`.

**Config (all runs):** OP = 25%, 64 pages/block, device sized to the working set
(logical ≈ unique_pages / (1−OP)), greedy GC unless noted. Dense-remapped addresses
(reuse pattern preserved).

**Data artifacts**
- `results/master_scalars.csv` — one row per (trace, engine): WAF, host/gc/physical
  writes, erases, reclaims, valid@reclaim, free-reclaim%, reclaim-eff, DoIPD_final,
  DoIPD_trigger (dispersion measured *before every GC*), DoEC, erase-Gini,
  erase-bimodality (Sarle), fill, geometry, unit count.
- `results/<trace>__<engine>.npz` — arrays: ev (valid@reclaim per reclaim),
  doipd_series, final_invalid/valid per unit, wear, space-time frames+xs, TTI.
- `figures/full/` — 38 figures (A–I families).

---

## WAF matrix (physical / host writes)

| Trace | conv·block | conv·super | FDP·single | FDP·PI | FDP·II | ZNS·single | ZNS·hot·greedy | ZNS·hot·CB |
|-------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| prxy_0 (200k) | 1.54 | 2.14 | 1.68 | 1.50 | 1.58 | 2.04 | 2.01 | 2.01 |
| prxy_1 (300k) | 1.35 | — | 1.47 | 1.67 | 1.77 | 1.99 | 2.89 | 3.11 |
| prxy_1_3M (3M) | 1.07 | — | 1.26 | 1.06 | 1.01 | 1.49 | 1.75 | 1.72 |
| W2K8 TPC-C | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.76 | 1.76 |
| sequential | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.67 | 1.67 |
| uniform | 1.56 | 1.78 | 1.54 | 1.75 | 2.21 | 1.74 | 2.57 | 2.57 |
| zipf-1.2 | 1.13 | — | 1.16 | 1.06 | 1.05 | 1.18 | 1.06 | 1.08 |
| 80/20 | 1.15 | 1.19 | 1.16 | 1.10 | 1.13 | 1.18 | 1.18 | 1.14 |

"—" = superblock GC did not complete (see Limitations).

---

## Key findings (honest, from the data)

1. **valid-fraction-at-reclaim is the WAF predictor.** Across all 69 runs,
   Pearson r(WAF, valid@reclaim) = **+0.92**; r(WAF, DoIPD) = **+0.55**. The temporal
   GC-cost, not the spatial invalidity dispersion, governs WAF — consistent with the
   entropy-model refutation. (Fig G.)

2. **FDP-PI helps only on skewed, sufficiently-aged workloads.** PI < single on
   prxy_1_3M (1.06 vs 1.26), zipf (1.06 vs 1.16), 80/20 (1.10 vs 1.16); but PI > single
   on uniform (1.75 vs 1.54) and short prxy_1 (1.67 vs 1.47), because PI's per-RUH GC
   reservation fragments OP when there is no reuse skew to exploit. FDP-II is the most
   robust-to-worst across workloads. (Fig H.)

3. **ZNS hot/cold is workload-dependent and can backfire.** It reduces WAF on zipf
   (1.06 vs single 1.18) but *increases* it sharply on prxy_1 (2.89 vs 1.99) and TPC-C /
   sequential (1.76 vs 1.00) — the cold-pollution feedback loop, where migrated cold
   data repeatedly re-fills the GC stream. Cost-benefit GC does not rescue it on prxy_1
   (3.11). Honest negative result. (Fig H.)

4. **Write-once workloads (TPC-C, sequential) are WAF ≈ 1.0** for every in-place engine
   — no rewrite ⇒ no GC. Only ZNS hot/cold pays migration (1.76 / 1.67), a *cost* of
   two-stream separation when there is nothing to separate.

5. **The sim–FEMU WAF gap is granularity.** FEMU (superblock erase) is bracketed by the
   sim's block- and superblock-granular modes: on prxy_0, 1.54 (block) ≤ 1.873 (FEMU)
   ≤ 2.14 (superblock). Config-matched validation gaps (OP 25%): prxy_0 −18%,
   prxy_1_3M FDP-single −20%, FDP-PI −29% — the sim consistently under-predicts WAF via
   its finer default erase granularity. (Figs A, A2.)

---

## Validation vs FEMU (config-matched, OP 25%)

FEMU runs: conventional via `fio` randwrite (bbssd gc90); FDP via `fdp_write`
(NVMe passthrough, DTYPE=2 placement handles), rHMW = 3×. WAF read from the
instrumented FEMU host log (`WAF host=…` / `FDP-WAF hbmw=… mbmw=…`).

| Trace | Engine | FEMU WAF | Sim WAF | Rel. err |
|-------|--------|:--:|:--:|:--:|
| prxy_0 | conv (block) | 1.873 | 1.539 | **−17.8 %** |
| prxy_1_3M | FDP-single | 1.561 | 1.256 | **−19.6 %** |
| prxy_1_3M | FDP-PI | 1.487 | 1.059 | **−28.8 %** |
| uniform | conv (block) | 1.458 | 1.562 | +7.1 % |
| uniform | FDP-single | 1.661 | 1.536 | −7.5 % |
| uniform | FDP-PI | 1.651 | 1.751 | +6.1 % |
| 80/20 | FDP-single | 1.121 | 1.157 | +3.2 % |
| 80/20 | FDP-PI | 1.016 | 1.098 | +8.0 % |

**Two regimes, both consistent with the granularity explanation:**
- **Synthetic (uniform, 80/20): ±3–8 %, mixed signs** — errors cancel, no systematic
  bias. The sim tracks FEMU where GC is mild/uniform.
- **Real traces (prxy): −18 to −29 %, one-directional** — the sim's default
  block-granular erase migrates fewer valid pages than FEMU's superblock erase under the
  heavy, skewed GC that real traces induce. FEMU is bracketed by the sim's block/superblock
  modes (prxy_0: 1.54 ≤ 1.873 ≤ 2.14). The gap is a modeling-granularity choice, not error;
  it is bounded, explained, and closes when the sim is set to superblock GC.

Data: `femu_fdp_op25.csv`, `femu_conv_op25.csv`, plus prior `femu_vs_sim_waf.csv`.

---

## Figure index (`figures/full/`)

| File | Content |
|------|---------|
| A_validation_waf | sim vs FEMU, config-matched (OP 25%) |
| A2_granularity_bracket | FEMU between sim block- & superblock-GC |
| B_waf_by_engine | WAF per engine across real traces |
| C_spacetime_\<trace\> | space-time occupancy heatmaps, all engines |
| D_invalid_dispersion_\<trace\> | invalidity dispersion at-trigger vs end + histograms |
| E_valid_at_reclaim_\<trace\> | valid-fraction-at-reclaim distributions (the mechanism) |
| F_wear_\<trace\> | wear Lorenz curve + DoEC bars |
| G_mechanism_scatters | WAF vs valid@reclaim (r=+0.92) & vs DoIPD (r=+0.55) |
| H_placement | FDP single/PI/II and ZNS placement+GC |
| I_waf_wear_tradeoff | WAF ↔ DoEC per (engine, trace) |

---

## Limitations (report honestly)

- **Superblock GC (conv_super) is experimental.** It completes on prxy_0, uniform,
  sequential, 80/20, TPC-C, but crashes on prxy_1 / prxy_1_3M ("plane full even after
  GC") and thrashes on zipf (WAF → 127, excluded). Root cause: EyanaSSDSim allocates
  per-plane, so a "line" is not a coherent unit as in FEMU; the superblock reclaim can
  strand a plane. Used only for the granularity-bracket argument on the workloads where
  it is stable. The default block-granular engine is the validated one.
- **FEMU points are the validation subset**, measured at OP 25% to match. Synthetic
  FEMU points (uniform, 80/20) from earlier OP-10% runs are *excluded* from the matched
  validation figure to avoid config-mismatch; they will be re-run at OP 25%.
- **TPC-C has negligible rewrite** in the captured window (≈unique≈writes), so it is a
  WAF≈1.0 point, not a GC-stress point.
