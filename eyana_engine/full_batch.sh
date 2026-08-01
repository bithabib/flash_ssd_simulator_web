#!/usr/bin/env bash
# Drive the comprehensive capture over all traces + synthetic baselines.
# Writes results/master_scalars.csv + results/<trace>__<engine>.npz for everything.
set -u
cd "$(dirname "$0")/.."
PY=python3
LOG=results/full_batch.log
: > "$LOG"

run() { echo "### $*" | tee -a "$LOG"; $PY -m eyana_engine.full_eval "$@" 2>&1 | tee -a "$LOG"; }

# --- real traces (canonical dense-remapped .bin sequences) ---
run bin real_data/remapped/prxy_0.bin     prxy_0
run bin real_data/remapped/prxy_1.bin     prxy_1
run bin real_data/remapped/prxy_1_3M.bin  prxy_1_3M

# --- real TPC-C (ETW) — included for completeness (low-rewrite; expect WAF~1) ---
run real real_data/uploaded_traces/W2K8.TPCC.trace.csv.bz2 etw 3000000 W2K8_TPCC

# --- synthetic baselines (reference distributions) ---
run synth sequential  synth_sequential
run synth uniform     synth_uniform
run synth zipf1.2     synth_zipf12
run synth 80/20       synth_8020

echo "=== ALL DONE ===" | tee -a "$LOG"
