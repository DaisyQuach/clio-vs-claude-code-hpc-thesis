#!/bin/bash
# Stage-2 delivery: copy run artifacts to locked paths, write verification records, regenerate manifest.
set -u
cd /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/clio/trial_05R || exit 2
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh >/dev/null 2>&1
S=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/.agent_runtime/E2-example16-clio-05R/session_b/clio_home/config/agent-blueprints/factorio-flat/skills/morphorm/scripts
R=work/stage2/run
JID=16243174
O=outputs/stage2
mkdir -p $O/generated_config $O/run_logs work/verify
cp -p $R/input_deck.i $O/input_deck.i
cp -p jobs/stage2_job_script.sbatch $O/job_script.sbatch
for f in interface.xml engine_operations.xml engine_input_deck.xml analyze_2_input_deck.xml analyze_2_operations.xml analyze_helmholtz_input_deck.xml analyze_helmholtz_operations.xml mpirun.source xmlgenerator_stdout.log; do cp -p $R/$f $O/generated_config/$f; done
cp -p work/verify/stage2_xml_params.txt $O/generated_config/verification_xml_params.txt
cp -p $R/restart_input.exo $O/restart_input.exo
cp -p $R/morphorm_oc_optimizer_diagnostics.txt $O/morphorm_oc_optimizer_diagnostics.txt
cp -p $R/engine_output.exo $O/engine_output.exo
cp -p $R/analyze_id_2_output_scenario_id_1/iteration40.exo $O/final_analyze_output.exo
cp -p logs/stage2_${JID}.out logs/stage2_${JID}.err $O/run_logs/
cp -p $R/morphorm_stage2.log $O/run_logs/
for f in engine_1_0 analyze_2_1 analyze_helmholtz_2 opt_criteria_history.csv; do [ -f $R/$f ] && cp -p $R/$f $O/run_logs/$f; done
sacct -j $JID --format=JobID,JobName,State,ExitCode,Submit,Start,End,Elapsed,AllocCPUS,ReqMem,MaxRSS,NodeList -P > jobs/sacct_${JID}.txt
cp -p jobs/sacct_${JID}.txt $O/run_logs/
# verification records (bundled checks)
python3 $S/diag_summary.py $O/morphorm_oc_optimizer_diagnostics.txt --compare-first-to 2.360040e+05 > work/verify/stage2_diag_summary.json 2>&1; echo diag rc=$?
python3 $S/exo_summary.py $O/engine_output.exo > work/verify/stage2_engine_output.json 2>&1; echo engine rc=$?
python3 $S/exo_summary.py $O/final_analyze_output.exo > work/verify/stage2_iteration40.json 2>&1; echo final rc=$?
python3 $S/exo_summary.py $O/restart_input.exo > work/verify/stage2_restart_input.json 2>&1; echo restart rc=$?
cp -p work/verify/stage2_diag_summary.json work/verify/stage2_engine_output.json work/verify/stage2_iteration40.json work/verify/stage2_restart_input.json work/verify/stage2_first_objective_check.json $O/run_logs/
sha256sum $O/restart_input.exo outputs/stage1/engine_output.exo
