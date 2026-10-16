#!/bin/bash
# Assemble the locked deliverables for FROZEN-EX8-v1 from the accepted run directory (work/run2) into outputs/.
set -euo pipefail
TRIAL="$1"; RUN="$TRIAL/work/run2"; OUT="$TRIAL/outputs"; JID="$2"
mkdir -p "$OUT/generated_config" "$OUT/run_logs"
cp -p "$TRIAL/work/mesh/mesh.jou"                       "$OUT/mesh.jou"
cp -p "$RUN/mesh.exo"                                   "$OUT/mesh.exo"
cp -p "$TRIAL/work/mesh/mesh_verification.json"         "$OUT/mesh_verification.json"
cp -p "$RUN/input_deck.i"                               "$OUT/input_deck.i"
cp -p "$RUN/job_script.sbatch"                          "$OUT/job_script.sbatch"
for f in interface.xml analyze_2_input_deck.xml analyze_helmholtz_input_deck.xml engine_input_deck.xml \
         analyze_2_operations.xml analyze_helmholtz_operations.xml engine_operations.xml mpirun.source; do
  cp -p "$RUN/$f" "$OUT/generated_config/$f"
done
cp -p "$RUN/morphorm_oc_optimizer_diagnostics.txt"      "$OUT/morphorm_oc_optimizer_diagnostics.txt"
cp -p "$RUN/engine_output.exo"                          "$OUT/engine_output.exo"
cp -p "$RUN/analyze_id_2_output_scenario_id_1/iteration50.exo" "$OUT/final_analyze_output.exo"
cp -p "$TRIAL/logs/slurm-$JID.out"                      "$OUT/run_logs/slurm-$JID.out"
cp -p "$TRIAL/logs/slurm-$JID.err"                      "$OUT/run_logs/slurm-$JID.err"
cp -p "$RUN/morphorm_run.log"                           "$OUT/run_logs/morphorm_run.log"
cp -p "$RUN/engine_1_0"                                 "$OUT/run_logs/engine_1_0.log"
cp -p "$RUN/analyze_2_1"                                "$OUT/run_logs/analyze_2_1.log"
cp -p "$RUN/analyze_helmholtz_2"                        "$OUT/run_logs/analyze_helmholtz_2.log"
cp -p "$RUN/opt_criteria_history.csv"                   "$OUT/run_logs/opt_criteria_history.csv"
cp -p "$RUN/xmlgen_stdout.log"                          "$OUT/run_logs/xmlgen_stdout.log"
cp -p "$TRIAL/work/mesh/cubit_stdout.log"               "$OUT/run_logs/cubit_stdout.log"
cp -p "$RUN/generated_config_verification.json"         "$OUT/generated_config_verification.json"
cp -p "$RUN/results_verification.json"                  "$OUT/results_verification.json"
cp -p "$RUN/runtime_bc_check_iteration50.json"          "$OUT/runtime_bc_check_iteration50.json"
cp -p "$RUN/runtime_filter_symmetry_check.json"         "$OUT/runtime_filter_symmetry_check.json"
rm -f "$OUT/.gitkeep"
cd "$OUT" && rm -f SHA256SUMS.txt && find . -type f ! -name SHA256SUMS.txt | sed 's|^\./||' | LC_ALL=C sort | xargs sha256sum > SHA256SUMS.txt
echo "assembled $(wc -l < SHA256SUMS.txt) files; sha256sum -c:"; sha256sum -c SHA256SUMS.txt --quiet && echo OK
