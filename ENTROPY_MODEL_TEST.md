# Empirical Test of the Entropy Model for SSD FTL — Honest Results

**Question.** Does an information-theoretic *entropy* model govern SSD write amplification
(WAF)? The model claims: (i) system disorder (Shannon entropy of block valid/invalid
mixture) drives WAF; (ii) "bimodal polarization" of blocks toward pure (0 % / 100 % valid)
states minimizes WAF; (iii) garbage-collecting high-entropy (≈50 %-valid) blocks
("distillation") reduces WAF.

**Method.** Implemented the entropy metrics and an entropy-targeting GC policy in
EyanaSSDSim; measured WAF, system entropy `H_sys` (mean per-block binary entropy),
block-state polarization, and valid-fraction-at-reclaim across four workloads
(sequential, uniform random, Zipf-1.2, 80/20) and three over-provisioning levels
(10/15/25 %). Device: 1024 blocks × 64 pages, greedy GC unless noted. Regenerate:
`python -m eyana_engine.entropy_test`.

**Bottom line: the entropy model's quantitative claims are refuted by the data.**
WAF is governed by a *temporal* property (do a block's pages die together?), measured by
valid-fraction-at-reclaim (r = 0.94), **not** by the *spatial* entropy or polarization of
the block layout (r = −0.35 / +0.43, both wrong-signed).

---

## Table 1 — Claim-by-claim verdict

| Claim | Prediction | Measured | Verdict |
|-------|-----------|----------|---------|
| **A.** Per-block entropy is a useful signal | distinguishes GC victims | H(0.1)=H(0.9)=0.469 → **cannot tell 10 %-valid from 90 %-valid** | ✗ symmetric; worse than valid-count |
| **B.** Uniform pins blocks at p≈0.5 (entropy trap) | trap% high for uniform | only **1–5 %** of uniform blocks near 0.5; they spread 0.5–0.75 | ⚠ mislocated |
| **C.** System entropy `H_sys` predicts WAF | positive correlation | corr(H_sys, WAF) = **−0.35** | ✗ **refuted** (wrong sign) |
| **D.** Polarization → low WAF | negative correlation | corr(polarization, WAF) = **+0.43** | ✗ **refuted** (wrong sign) |
| **E.** Hot/cold separation lowers entropy → lowers WAF | H↓ and WAF↓ together | WAF ↓ (1.21→1.14) but H_sys **↑** (0.73→0.78) | ✗ **refuted** |
| **F.** Cost-benefit fails the entropy trap | CB ≫ greedy WAF | greedy 2.172 ≈ CB 2.178 | ⚠ no distinct failure |
| **G.** Entropy-targeting GC ("distillation") reduces WAF | WAF↓ | **WAF ↑ on every workload** (see Table 3) | ✗ **refuted** |
| Baseline: valid-fraction-at-reclaim predicts WAF | — | corr = **+0.94** | ✓ the real predictor |

## Table 2 — What actually predicts WAF (correlation across all workloads × OP)

| Predictor | Pearson r with WAF | Interpretation |
|-----------|:------------------:|----------------|
| valid-fraction at reclaim (temporal) | **+0.94** | strong — pages dying together is what matters |
| system entropy `H_sys` (spatial) | −0.35 | none / wrong sign |
| block polarization (spatial) | +0.43 | none / wrong sign |

## Table 3 — The decisive test: the entropy-optimal GC policy gives the WORST WAF

Entropy-max GC = reclaim the block closest to 50 % valid (maximum entropy), i.e. the
model's own prescription. Controlled comparison (same workload, same OP = 15 %):

| Workload | greedy | cost-benefit | **entropy-max** | entropy-max vs best |
|----------|:------:|:------------:|:---------------:|:-------------------:|
| sequential | 1.119 | 1.212 | **1.594** | +42 % WORSE |
| uniform    | 2.172 | 2.178 | **3.529** | +62 % WORSE |
| Zipf-1.2   | 1.115 | 1.112 | **1.687** | +52 % WORSE |
| 80/20      | 1.191 | 1.186 | **2.664** | +124 % WORSE |

On the uniform workload the entropy-max policy achieved the model's stated goal —
**highest polarization (88 % vs 48 %), lowest entropy (0.27 vs 0.46)** — yet produced the
**worst WAF (3.53 vs 2.17)**. Optimizing the entropy objective directly makes WAF worse.

## Table 4 — Full measured matrix (greedy GC)

| Workload | OP | WAF | H_sys | polar % | trap % | v@reclaim |
|----------|:--:|:---:|:-----:|:-------:|:------:|:---------:|
| sequential | 10 | 1.994 | 0.046 | 93.3 | 0.0 | 0.601 |
| sequential | 15 | 1.119 | 0.064 | 92.3 | 0.0 | 0.155 |
| sequential | 25 | 1.000 | 0.000 | 100.0 | 0.0 | 0.000 |
| uniform | 10 | 2.951 | 0.332 | 80.7 | 0.7 | 0.746 |
| uniform | 15 | 2.172 | 0.464 | 48.4 | 1.1 | 0.645 |
| uniform | 25 | 1.555 | 0.685 | 21.6 | 5.3 | 0.481 |
| Zipf-1.2 | 10 | 1.125 | 0.895 | 1.4 | 29.9 | 0.158 |
| Zipf-1.2 | 15 | 1.115 | 0.890 | 0.6 | 24.0 | 0.152 |
| Zipf-1.2 | 25 | 1.094 | 0.871 | 0.8 | 20.1 | 0.136 |
| 80/20 | 10 | 1.225 | 0.868 | 7.1 | 49.9 | 0.252 |
| 80/20 | 15 | 1.191 | 0.879 | 7.1 | 48.5 | 0.229 |
| 80/20 | 25 | 1.135 | 0.890 | 4.0 | 38.4 | 0.184 |

Notice rows for Zipf/80-20: **high entropy (0.87–0.90) yet low WAF (1.1–1.2)** — the direct
contradiction of the model. Their blocks are "disordered" (many warm blocks) but their hot
pages die together, so GC is cheap.

---

## Why the entropy model fails (the physics)

Entropy is a **static, spatial** measure — it counts how mixed a block's valid/invalid pages
are *right now*. But WAF is set by a **temporal** property: **do a block's pages become
invalid at the same time?** A block can look "disordered" (partly valid) yet be cheap to GC
if its valid pages are cold (skipped) and its hot pages die together. Zipf/80-20 workloads
have exactly this structure — high entropy, low WAF. The entropy model measures the wrong
axis (space, not time), which is why (a) its metric anti-correlates with WAF and (b) a policy
that optimizes it makes WAF worse.

## Recommendation for the paper

1. **Report this as a rigorous negative result** — it is publishable and it *protects* the
   paper: *"We formalized and tested an entropy model of FTL behaviour; system entropy and
   polarization do not predict WAF (r = −0.35 / +0.43), and an entropy-optimal GC policy is
   the worst (+42–124 % WAF). WAF is governed instead by valid-fraction-at-reclaim
   (r = 0.94) — a temporal, not spatial, property."*
2. EyanaSSDSim's visualization strengthens the message: **the maximally-polarized picture is
   not the low-WAF picture.**
3. If a positive contribution is wanted, pivot to the *temporal* framing (which is what
   SepBit/DOGI/FDP-TTI actually exploit); cite entropy only as the tested-and-rejected
   alternative.
