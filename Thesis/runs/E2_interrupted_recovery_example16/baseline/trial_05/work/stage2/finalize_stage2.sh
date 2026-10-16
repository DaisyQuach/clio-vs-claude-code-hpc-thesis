#!/bin/bash
# Post-completion steps for Stage 2 (job 16169770): sacct record, verification, deliverables, manifest.
set -u
ROOT=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/baseline/trial_05
cd "$ROOT"
JID=16169770
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh >/dev/null 2>&1
echo "FINALIZE_START_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> work/stage2/stage2_timestamps.txt
sacct -j $JID --format=JobID,JobName,State,ExitCode,Submit,Start,End,Elapsed,AllocCPUS,ReqMem,MaxRSS,NodeList -P > jobs/stage2_sacct_$JID.txt
cat jobs/stage2_sacct_$JID.txt
echo "VERIFY_STAGE2_RESULTS_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> work/stage2/stage2_timestamps.txt
python3 -I work/verification/verify_stage2_results.py work/stage2/run > work/stage2/stage2_results_verification.json; echo "verify_stage2_results rc=$?"
python3 -I work/verification/continuation_evidence.py work/stage1/run work/stage2/run work/stage2/run/input_deck.i 21 > work/stage2/continuation_evidence.json; echo "continuation_evidence rc=$?"
python3 -I - <<'PY'
import json
for f in ["work/stage2/stage2_results_verification.json", "work/stage2/continuation_evidence.json"]:
    d = json.load(open(f)); print(f)
    for k, v in d["checks"].items(): print("  ", "PASS" if v else "FAIL", k)
    print("   ALL_CHECKS_PASS", d["ALL_CHECKS_PASS"])
PY
# ---- deliverables
R=work/stage2/run; O=outputs/stage2
mkdir -p $O/generated_config $O/run_logs
cp -p $R/input_deck.i $O/input_deck.i
cp -p jobs/stage2_job.sbatch $O/job_script.sbatch
cp -p $R/interface.xml $R/engine_input_deck.xml $R/engine_operations.xml $R/analyze_2_input_deck.xml $R/analyze_2_operations.xml $R/analyze_helmholtz_input_deck.xml $R/analyze_helmholtz_operations.xml $R/mpirun.source $R/xmlgenerator.log $R/xmlgenerator_timestamps.txt $O/generated_config/
cp -p work/stage2/generated_config_verification.json $O/generated_config/generated_config_verification.json
cp -p $R/restart_input.exo $O/restart_input.exo
cp -p $R/morphorm_oc_optimizer_diagnostics.txt $O/morphorm_oc_optimizer_diagnostics.txt
cp -p $R/engine_output.exo $O/engine_output.exo
cp -p $R/analyze_id_2_output_scenario_id_1/iteration40.exo $O/final_analyze_output.exo
cp -p work/stage2/continuation_evidence.json $O/continuation_evidence.json
cp -p work/stage2/stage2_results_verification.json $O/stage2_results_verification.json
cp -p logs/stage2_$JID.out logs/stage2_$JID.err $R/morphorm_stage2.log $R/opt_criteria_history.csv jobs/stage2_sacct_$JID.txt $O/run_logs/
cp -p $R/engine_1_0 $O/run_logs/engine_1_0.log; cp -p $R/analyze_2_1 $O/run_logs/analyze_2_1.log; cp -p $R/analyze_helmholtz_2 $O/run_logs/analyze_helmholtz_2.log
cp -p $R/analyze_id_2_output_scenario_id_1/iteration40_criteria_history.csv $O/run_logs/ 2>/dev/null
cp -p work/verification/verify_generated_config_stage2.py work/verification/verify_stage2_results.py work/verification/continuation_evidence.py $O/run_logs/
# cancelled attempt 1 (restart_iteration 20) evidence, kept for provenance
mkdir -p $O/run_logs/attempt1_restart20_cancelled_job16169758
A=work/stage2/attempt1_restart20_cancelled_job16169758
cp -p logs/stage2_16169758.out logs/stage2_16169758.err jobs/stage2_attempt1_sacct_16169758.txt $A/input_deck.i $A/engine_operations.xml $A/morphorm_oc_optimizer_diagnostics.txt $A/generated_config_verification_attempt1_restart20.json $O/run_logs/attempt1_restart20_cancelled_job16169758/
cp -p $A/morphorm_stage2.log $O/run_logs/attempt1_restart20_cancelled_job16169758/morphorm_stage2_attempt1.log 2>/dev/null
# ---- integrity
sha256sum $O/restart_input.exo outputs/stage1/engine_output.exo
(cd outputs && find . -type f ! -name SHA256SUMS.txt | sort | xargs sha256sum > SHA256SUMS.txt && sha256sum -c SHA256SUMS.txt | grep -vc ': OK$' ; echo "manifest entries: $(wc -l < SHA256SUMS.txt) files: $(find . -type f ! -name SHA256SUMS.txt | wc -l)")
echo "FINALIZE_END_UTC=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> work/stage2/stage2_timestamps.txt
