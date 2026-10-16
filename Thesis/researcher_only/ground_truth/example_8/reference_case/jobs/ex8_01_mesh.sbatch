#!/bin/bash
#SBATCH --job-name=ex8_01_mesh
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
export JOU=topology_mech_ex8.jou NX=48 NY=24 NZ=12 LX=2.0 LY=1.0 LZ=0.5 SIDESETS=ss_sym
exec bash "$REF/tools/ref_mesh_job.sh"
