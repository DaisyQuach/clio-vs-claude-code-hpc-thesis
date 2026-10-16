#!/bin/bash
# Copy the accepted Stage-2 artifacts from the run directory to their locked deliverable paths under outputs/stage2/.
# usage: bash collect_stage2_deliverables.sh <trial_root> <jobid>
set -u
ROOT="$1"; JID="$2"; S2="$ROOT/work/stage2"; O2="$ROOT/outputs/stage2"
mkdir -p "$O2/generated_config" "$O2/run_logs"
cp -p "$S2/input_deck.i" "$O2/input_deck.i"
cp -p "$ROOT/jobs/stage2_job.sbatch" "$O2/job_script.sbatch"
for f in interface.xml engine_input_deck.xml engine_operations.xml analyze_2_input_deck.xml analyze_2_operations.xml analyze_helmholtz_input_deck.xml analyze_helmholtz_operations.xml mpirun.source xmlgenerator.log generated_config_verification.json; do cp -p "$S2/$f" "$O2/generated_config/$f"; done
cp -p "$S2/restart_input.exo" "$O2/restart_input.exo"
cp -p "$S2/morphorm_oc_optimizer_diagnostics.txt" "$O2/morphorm_oc_optimizer_diagnostics.txt"
cp -p "$S2/engine_output.exo" "$O2/engine_output.exo"
cp -p "$S2/analyze_id_2_output_scenario_id_1/iteration40.exo" "$O2/final_analyze_output.exo"
cp -p "$S2/stage2_results_verification.json" "$O2/stage2_results_verification.json"
cp -p "$S2/continuation_evidence.json" "$O2/continuation_evidence.json"
cp -p "$ROOT/logs/stage2_${JID}.out" "$O2/run_logs/slurm_${JID}.out"
cp -p "$ROOT/logs/stage2_${JID}.err" "$O2/run_logs/slurm_${JID}.err"
cp -p "$S2/morphorm_stage2.log" "$O2/run_logs/morphorm_stage2.log"
cp -p "$S2/engine_1_0" "$O2/run_logs/engine_1_0.log"
cp -p "$S2/analyze_2_1" "$O2/run_logs/analyze_2_1.log"
cp -p "$S2/analyze_helmholtz_2" "$O2/run_logs/analyze_helmholtz_2.log"
cp -p "$S2/opt_criteria_history.csv" "$O2/run_logs/opt_criteria_history.csv"
[ -f "$S2/analyze_id_2_output_scenario_id_1/iteration40_criteria_history.csv" ] && cp -p "$S2/analyze_id_2_output_scenario_id_1/iteration40_criteria_history.csv" "$O2/run_logs/iteration40_criteria_history.csv"
cp -p "$ROOT/jobs/sacct_${JID}.txt" "$O2/run_logs/sacct_${JID}.txt"
# also keep the cancelled attempt's scheduler evidence with the Stage-2 run logs
cp -p "$ROOT/logs/stage2_16166532.out" "$O2/run_logs/slurm_16166532_cancelled_attempt1.out"
cp -p "$ROOT/logs/stage2_16166532.err" "$O2/run_logs/slurm_16166532_cancelled_attempt1.err"
cp -p "$ROOT/jobs/sacct_16166532.txt" "$O2/run_logs/sacct_16166532_cancelled_attempt1.txt"
echo "copied; verifying copies against originals"
ok=1
for pair in "$S2/input_deck.i:$O2/input_deck.i" "$S2/restart_input.exo:$O2/restart_input.exo" "$S2/engine_output.exo:$O2/engine_output.exo" "$S2/analyze_id_2_output_scenario_id_1/iteration40.exo:$O2/final_analyze_output.exo" "$S2/morphorm_oc_optimizer_diagnostics.txt:$O2/morphorm_oc_optimizer_diagnostics.txt" "$ROOT/outputs/stage1/engine_output.exo:$O2/restart_input.exo"; do a="${pair%%:*}"; b="${pair##*:}"; if cmp -s "$a" "$b"; then echo "MATCH $b"; else echo "MISMATCH $a vs $b"; ok=0; fi; done
[ $ok = 1 ] && echo "ALL COPIES MATCH" || echo "COPY MISMATCH"
