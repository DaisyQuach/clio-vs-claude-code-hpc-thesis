#!/bin/bash
#SBATCH --job-name=ex16_02_stage1
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
export DECK=topology_mech_ex16.i RUN=stage1 MESH=topology_mech_ex16.exo EXPECT_ITERS=20 PREFIX=ex16_stage1
export CHECK_ARGS="--max-iterations 20 --no-symmetry-sides --initial-density 0.15 --write-restart true --simp-min 1e-3"
exec bash "$REF/tools/ref_run_job.sh"
