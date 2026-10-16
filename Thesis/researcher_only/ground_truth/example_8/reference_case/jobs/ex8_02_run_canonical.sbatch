#!/bin/bash
#SBATCH --job-name=ex8_02_run_canonical
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/ground_truth/example_8/reference_case/logs/slurm_%x_%j.out
#SBATCH --error=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/ground_truth/example_8/reference_case/logs/slurm_%x_%j.err
# Frozen Slurm resource contract (ThesisExperiments/common/base_inputs/compute_resources.md).
# Researcher-only ground-truth rebuild; see ../README.md and ../../SOURCE_AUDIT.md.
export REF=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/ground_truth/example_8/reference_case
export DECK=topology_mech_ex8.i RUN=run_canonical MESH=topology_mech_ex8.exo EXPECT_ITERS=50 PREFIX=ex8_canonical
export CHECK_ARGS="--max-iterations 50 --no-symmetry-sides --sym-bc-sideset ss_sym --initial-density 0.15 --write-restart false --simp-min 1e-3"
# NOTE: --no-symmetry-sides is the documented, expected translation of the canonical deck (filter-block keyword dropped by XMLGenerator).
exec bash "$REF/tools/ref_run_job.sh"
