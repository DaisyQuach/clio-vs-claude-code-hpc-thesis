#!/bin/bash
# Copy accepted Stage-1 artifacts to locked paths under outputs/ and build SHA256SUMS.txt
set -eu
TR=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/clio/trial_05
RUN=$TR/work/stage1/run
JID=$1
mkdir -p $TR/outputs/stage1/generated_config $TR/outputs/stage1/run_logs
cp $TR/work/mesh/mesh.jou $TR/outputs/mesh.jou
cp $TR/work/mesh/mesh.exo $TR/outputs/mesh.exo
cp $TR/work/verify/mesh.json $TR/outputs/mesh_verification.json
cp $RUN/input_deck.i $TR/outputs/stage1/input_deck.i
cp $TR/jobs/stage1_job.sbatch $TR/outputs/stage1/job_script.sbatch
cp $RUN/interface.xml $RUN/engine_input_deck.xml $RUN/engine_operations.xml $RUN/analyze_2_input_deck.xml $RUN/analyze_2_operations.xml $RUN/analyze_helmholtz_input_deck.xml $RUN/analyze_helmholtz_operations.xml $RUN/mpirun.source $RUN/xmlgenerator.log $TR/outputs/stage1/generated_config/
cp $TR/work/verify/stage1_generated_config.tsv $TR/outputs/stage1/generated_config/verification_xml_params.tsv
cp $RUN/morphorm_oc_optimizer_diagnostics.txt $TR/outputs/stage1/morphorm_oc_optimizer_diagnostics.txt
cp $RUN/engine_output.exo $TR/outputs/stage1/engine_output.exo
cp $RUN/analyze_id_2_output_scenario_id_1/iteration20.exo $TR/outputs/stage1/final_analyze_output.exo
cp $TR/logs/stage1_$JID.out $TR/logs/stage1_$JID.err $RUN/morphorm_stage1.log $TR/outputs/stage1/run_logs/
cp $RUN/engine_1_0 $RUN/analyze_2_1 $RUN/analyze_helmholtz_2 $TR/outputs/stage1/run_logs/
[ -f $RUN/opt_criteria_history.csv ] && cp $RUN/opt_criteria_history.csv $TR/outputs/stage1/run_logs/
[ -f $RUN/engine_restart.exo ] && cp $RUN/engine_restart.exo $TR/outputs/stage1/run_logs/engine_restart.exo
cd $TR/outputs && rm -f SHA256SUMS.txt && find . -type f ! -name SHA256SUMS.txt | sort | sed 's|^\./||' | xargs sha256sum > SHA256SUMS.txt && sha256sum -c SHA256SUMS.txt --quiet && echo MANIFEST_OK
