# EyanaSSDSim — Engine Correctness Audit

Audit of the three simulation code paths prior to the Python rebuild. Read-only;
no code was modified. Severity: **critical** = wrong/invalid paper data, **high** =
systematic skew, **medium/low** = localized or edge-case.

---

## Engine 1 — `static/src/js/advance_flash_ssd_simulator.js` (THE PAPER'S DATA ENGINE)

Hierarchical SSD (channel→chip→die→plane→block_container→block→page) with S1–S6
allocation, greedy GC, and WAF = internal_write/host_write. This is the engine
whose output became the paper's figures, so its bugs are the most consequential.

### CRITICAL — affects published results
- **A1. Allocation schemes collapse to duplicates (chip = 1).** With `chip:1` the
  chip dimension is degenerate, so **S2 ≡ S4** and **S3 ≡ S5** — they generate
  byte-identical block-address sequences. The paper compares "S1–S5" and claims
  *S1/S4 best for sequential, S5 best for uniform random, S3 best for Zipf*
  (Fig. allocation_policy_compare_fft). But S3≡S5 means "S5 best for random" and
  "S3 best for Zipf" cannot both reflect distinct policies — only 3 of the 5 are
  actually distinct. **The allocation-policy comparison is methodologically broken.**
- **A2. S6 die coordinate uses wrong modulus (line 523):** `% plane` instead of
  `% die` → non-bijective mapping, dereferences a non-existent block, crashes on
  init. (Paper evaluated S1–S5, so likely unused, but the scheme is broken.)

### HIGH — systematic skew of WAF/capacity
- **A3. Blocks close one page early (line 666):** `offset == page - 1` marks a
  64-page block full at 63 pages. Every dynamically written block wastes 1 page →
  ~1.5% capacity loss, GC triggers earlier/more often, **WAF inflated across all
  workloads.** Inconsistent with initial fill (lines 159–161) which uses 64.
- **A4. GC bulk-erase fast path is dead code (lines 797, 666):** gated on
  `invalid_pages == 64`, unreachable because of A3, so every GC does a full
  393k-entry mapping-table scan → wrong timing/latency numbers.

### MEDIUM / LOW
- **A5.** Fully-invalid GC branch omits erase-time accounting (line 797–805) →
  undercounts cumulative time.
- **A6.** `will_run_gc` OP handling ignores over-provisioning in the trigger math
  (lines 700–704); OP applied only as logical-LBA shrinkage — verify intended.
- **A7.** `return None;` (line 554) — Python in JS, ReferenceError on bad scheme.
- **A8.** Min-valid fallback can set victim to `""` → GC crash / non-termination
  when all blocks valid (lines 765–787).
- **A9.** No intra-request LBA wraparound at address-space boundary (858–880).
- **A10.** Checkpoint filename bug `i + 1` in string context (line 905) — cosmetic.
- **A11.** `p_block` leaks global (line 585).

### Verified CORRECT
WAF definition (GC writes counted as internal only), invalidation accounting,
greedy victim = max invalid pages, valid-page migration, S1–S5 individually
bijective (except the degeneracy A1), no async race (sequential awaits).

---

## Engine 2 — `static/src/js/flash_ssd_simulation.js` (educational 32-block toy)

Animation-driven teaching demo (32 blocks × 4 pages). **Not** the paper's data
source, but user-facing and heavily broken.

### CRITICAL
- **B1.** Full blocks never removed from `block_list` (splice commented, 1010/1016)
  → full block reselected, `written_page[-1]` = undefined → TypeError crash.
- **B2.** Parallel-mode free-page search `while(true)` has no disk-full guard →
  infinite loop / tab hang once full (compounded by B1, B4).

### HIGH
- **B3.** GC never reclaims invalid pages in partially-filled blocks (only fully
  full blocks enqueued) → deleted data in non-full blocks is un-collectable.
- **B4.** Erase resets page `data` but not `state` to `"free"` → erased blocks look
  full forever in s1–s6 modes.
- **B5.** `globalFileSize` decremented on every write incl. GC, never re-credited on
  delete/erase → monotonic decrease → spurious "device full."

### MEDIUM / LOW
- **B6.** No GC trigger watermark / no over-provisioning.
- **B7.** Non-selective GC victim (erases all eligible blocks).
- **B8.** WAF /0 → Infinity/NaN edge cases; dead write-combining cache (KB/byte bug).
- **B9.** `updateCacheRegister` uses undefined index `i`.
- **B10.** No latency model (fixed 1s animation delays).
- **B11.** "Parallel" writes actually serial (`push(await ...)`).
- **B12.** Shared mutable globals mutated across interleaved async ops.
- **B13.** `getRandomBlockParallel` can return undefined → crash.
- **B14.** Over-decrement on partial final page.

---

## Engine 3 — `readme_documentation_src/.../ssd_simulator_simple.py` (OSTEP teaching sim)

Log-structured FTL teaching tool. **No S1–S6 placement, never computes WAF** →
poor seed for the rebuild (weaker than the JS engine).

### CRITICAL
- **C1.** GC erases victim without checking migration write succeeded (262–272) →
  data loss / dangling map when device full.

### HIGH
- **C2.** GC-migration writes counted as logical/host writes (268, 319–320) → WAF
  denominator polluted (`is_gc_write` param is dead code).
- **C3.** No WAF metric produced at all.
- **C4.** No watermark validation; defaults (`high=10` vs `num_blocks=7`) make GC
  dead code.

### MEDIUM / LOW
- **C5.** GC is round-robin first-fit, **not greedy** (238–259).
- **C6.** `live_count` initialized, never maintained.
- **C7.** `gc_current_block` not advanced when low-water not reached.
- **C8.** float `int(x/pages)` instead of `//`.
- **C9.** First allocation erases never-written block, inflating erase stats.
- **C10.** DIRECT mode no capacity bound check.

---

## Bottom line for the paper

Three bugs affect the **published numbers**, and must be fixed and re-run:
1. **A1** (S2≡S4, S3≡S5) — invalidates the allocation-policy comparison / Fourier
   claims. Fix: use `chip ≥ 2` so all schemes are distinct, OR drop the degenerate
   schemes and reframe.
2. **A3** (63-vs-64 page off-by-one) — inflates WAF across every workload.
3. **A4/A5** — timing/latency numbers off.

The new Python engine must: count host vs GC writes separately, implement true
greedy victim selection, use a configuration where S1–S6 are genuinely distinct,
close blocks at the correct page count, and have unit tests pinning WAF/erase math.
