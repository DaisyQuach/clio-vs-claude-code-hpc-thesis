# Provenance Requirements

Every trial must leave an auditable record. Record the following.

## `work/run_summary.md` (required sections, in this order)
1. Trial identifier (from the prompt) and assigned workflow.
2. Mesh: how it was generated, file names, verification result (counts, bounding box, set sizes).
3. Input deck(s): file names; the exact locked settings and where each appears in the generated runtime configuration.
4. Execution: every command used; every Slurm job ID submitted (also in `jobs/job_ids.txt`), with state and exit code; the job script path.
5. Completed stages (Stage 1, Stage 2) and iteration counts actually reached in each; the stopping message of each optimizer run; for Stage 2, the evidence that it continued from the saved Stage-1 design (which checkpoint, which field, which saved iteration, and the first evaluated compliance compared with the last Stage-1 compliance).
6. Key output file names (deliverables in `outputs/`), with their SHA-256 (also in `outputs/SHA256SUMS.txt`).
7. Failures, retries, cancelled jobs, unresolved issues, deviations from the specification (if none, say "none").
8. Final artifact paths.

## Scheduler evidence
- `jobs/job_ids.txt`: one job ID per line for every submission (failed, cancelled and successful).
- Keep every job script you submitted under `jobs/` and the scheduler's stdout/stderr files under `logs/` or `outputs/run_logs/`.
- After each job finishes, record `sacct -j <id> --format=JobID,JobName,State,ExitCode,Submit,Start,End,Elapsed,AllocCPUS,ReqMem,MaxRSS,NodeList -P` output in `jobs/`.

## Timestamps and environment
- Record UTC timestamps for: mesh generation, deck translation, job submission, job start/end, and verification steps.
- Record the output of `module list` (after sourcing the approved software interface) inside each job script's stdout.

## Integrity
- `outputs/SHA256SUMS.txt` must cover every file under `outputs/` (except itself), produced with `sha256sum`.
- Do not overwrite an accepted deliverable with a later attempt without recording the replacement in the summary.
