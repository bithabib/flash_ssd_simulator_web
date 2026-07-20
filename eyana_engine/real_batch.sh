#!/bin/bash
# Phase 1: run every real trace through all sim engines (real_eval.py).
cd /home/habib/Desktop/flash_ssd_simulator_web
B=real_data/uploaded_traces
run(){ echo "===== $1 (cap $3) ====="; python3 -u -m eyana_engine.real_eval "$B/$1" "$2" "$3" 2>&1 | grep -vE "UserWarning|warnings.warn|done in"; echo; }
run prxy_sample.csv          msr  23000
run prxy_0.csv.gz            msr  200000
run prxy_1.csv.gz            msr  300000
run W2K8.TPCC.trace.csv.bz2  etw  300000
echo "PHASE1_DONE"
