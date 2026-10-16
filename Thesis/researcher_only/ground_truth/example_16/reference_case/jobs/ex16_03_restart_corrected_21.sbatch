#!/bin/bash
#SBATCH --job-name=ex16_03_restart_corrected_21
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/ground_truth/example_16/reference_case/logs/slurm_%x_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/ground_truth/example_16/reference_case/logs/slurm_%x_%j.err
# Frozen Slurm resource contract (ThesisExperiments/common/base_inputs/compute_resources.md).
# Researcher-only ground-truth rebuild; see ../README.md and ../../SOURCE_AUDIT.md.
export REF=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/ground_truth/example_16/reference_case
export DECK=topology_mech_ex16_restart_corrected_21.i RUN=restart_corrected_21 MESH=topology_mech_ex16.exo EXPECT_ITERS=40 PREFIX=ex16_restart_corrected_21
export CKPT="$REF/stage1/engine_output.exo" STAGE1_DIR="$REF/stage1" INTENDED_RESUME=20 EXPECT_RESUME_MATCH=true
export CHECK_ARGS="--max-iterations 40 --no-symmetry-sides --restart-file initialguess.exo --restart-field control --restart-iteration 21 --write-restart false --simp-min 1e-3"
exec bash "$REF/tools/ref_run_job.sh"
