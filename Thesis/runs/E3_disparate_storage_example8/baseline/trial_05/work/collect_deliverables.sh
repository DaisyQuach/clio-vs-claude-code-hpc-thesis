#!/usr/bin/env bash
# Copies the accepted run's files to the locked deliverable paths (cp -p), then hashes outputs/.
set -euo pipefail
T=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/baseline/trial_05
R=$T/work/run; J=$1
mkdir -p $T/outputs/generated_config $T/outputs/run_logs
cp -p $T/work/mesh/mesh.jou                  $T/outputs/mesh.jou
cp -p $R/mesh.exo                            $T/outputs/mesh.exo
cp -p $T/work/mesh/mesh_verification.json    $T/outputs/mesh_verification.json
cp -p $R/input_deck.i                        $T/outputs/input_deck.i
cp -p $T/jobs/morphorm_spc_v1.sbatch         $T/outputs/job_script.sbatch
cp -p $R/interface.xml $R/analyze_2_input_deck.xml $R/analyze_2_operations.xml $R/analyze_helmholtz_input_deck.xml \
      $R/analyze_helmholtz_operations.xml $R/engine_input_deck.xml $R/engine_operations.xml $R/mpirun.source $T/outputs/generated_config/
cp -p $R/generated_config_verification.txt   $T/outputs/generated_config/generated_config_verification.txt
cp -p $R/xmlgenerator.log                    $T/outputs/generated_config/xmlgenerator.log
cp -p $R/morphorm_oc_optimizer_diagnostics.txt $T/outputs/morphorm_oc_optimizer_diagnostics.txt
cp -p $R/engine_output.exo                   $T/outputs/engine_output.exo
cp -p $R/analyze_id_2_output_scenario_id_1/iteration50.exo $T/outputs/final_analyze_output.exo
cp -p $R/opt_criteria_history.csv            $T/outputs/opt_criteria_history.csv
cp -p $R/analyze_id_2_output_scenario_id_1/iteration50_criteria_history.csv $T/outputs/iteration50_criteria_history.csv
cp -p $T/logs/slurm-$J.out                   $T/outputs/run_logs/slurm-$J.out
cp -p $T/logs/slurm-$J.err                   $T/outputs/run_logs/slurm-$J.err
cp -p $R/morphorm_run.log                    $T/outputs/run_logs/morphorm_run.log
cp -p $T/work/mesh/cubit_run.log             $T/outputs/run_logs/cubit_run.log
E3_TRIAL_ROOT=$T $T/agent-inputs/control/scripts/non_destructive_preflight_helpers/hash_outputs.sh
