# Frozen Compute-Resource Contract

These values are frozen for every trial of this study and are identical for every system under comparison.

## Morphorm (topology-optimization) jobs — every submission

```
#SBATCH --account=hochhalter-np
#SBATCH --partition=hochhalter-np
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=02:00:00
```

- No GPU request.
- Submit every computationally intensive Morphorm run (mesh generation may be done on the agent host or in a job) through
  `sbatch` with exactly these values. Do not run the optimization on the agent-host node.
- Every job script must source the approved software interface (`software_contract.md`) before calling any Morphorm or Cubit executable.
- Record every submitted job ID in `jobs/job_ids.txt` and keep the scheduler's stdout/stderr files.

## Agent host

The agent process itself runs under a Slurm allocation with the same account/partition, 1 node, 8 CPUs, 32 GB, 02:00:00.
The whole trial, including waiting for submitted jobs, must finish inside that allocation.
