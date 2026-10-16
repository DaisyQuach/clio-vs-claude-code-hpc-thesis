#!/usr/bin/env bash
# Copies the accepted run's deliverables into outputs/ at their locked paths and writes the SHA-256 manifest.
set -euo pipefail
TR=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/baseline/trial_06
JID=$1; FINAL_EXO=$2   # FINAL_EXO: path of the final analyze output file (iteration 50)
cd "$TR"
mkdir -p outputs/generated_config outputs/run_logs
cp -p work/mesh/mesh.jou outputs/mesh.jou
cp -p work/run/mesh.exo outputs/mesh.exo
cp -p work/mesh/mesh_verification.json outputs/mesh_verification.json
cp -p work/run/input_deck.i outputs/input_deck.i
cp -p jobs/morphorm_oc50_symplane.sbatch outputs/job_script.sbatch
for f in interface.xml engine_input_deck.xml engine_operations.xml analyze_2_input_deck.xml analyze_2_operations.xml analyze_helmholtz_input_deck.xml analyze_helmholtz_operations.xml mpirun.source; do cp -p work/run/$f outputs/generated_config/$f; done
cp -p work/run/generated_config_verification.txt outputs/generated_config/generated_config_verification.txt
cp -p work/run/xmlgenerator.log outputs/generated_config/xmlgenerator.log
cp -p work/run/morphorm_oc_optimizer_diagnostics.txt outputs/morphorm_oc_optimizer_diagnostics.txt
cp -p work/run/engine_output.exo outputs/engine_output.exo
cp -p "$FINAL_EXO" outputs/final_analyze_output.exo
cp -p logs/slurm-$JID.out outputs/run_logs/slurm-$JID.out
cp -p logs/slurm-$JID.err outputs/run_logs/slurm-$JID.err
cp -p work/run/morphorm_run.log outputs/run_logs/morphorm_run.log
cp -p work/mesh/cubit_run.log outputs/run_logs/cubit_run.log
cp -p work/run/opt_criteria_history.csv outputs/run_logs/opt_criteria_history.csv 2>/dev/null || true
for d in engine_1_0 analyze_2_1 analyze_helmholtz_2; do [[ -f work/run/$d ]] && cp -p work/run/$d outputs/run_logs/performer_log_$d.txt; done
E3_TRIAL_ROOT=$TR bash agent-inputs/control/scripts/non_destructive_preflight_helpers/hash_outputs.sh
echo "finalized_utc $(date -u +%FT%TZ)"
