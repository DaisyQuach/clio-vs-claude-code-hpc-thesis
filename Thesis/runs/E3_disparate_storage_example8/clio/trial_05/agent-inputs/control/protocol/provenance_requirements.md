# Provenance requirements

Every trial must leave an auditable record.

## `work/run_summary.md` (required sections, in this order)
1. Trial identifier (`$E3_TRIAL_ID`), staging directory (`$E3_STAGING_DIR`), control commit, assigned task.
2. Discovery: collections and locations searched (summary; detail in `provenance/sources_searched.tsv`).
3. Artifact selection: candidates examined and the decision for each (summary; detail in `provenance/artifact_selections.md`).
4. Staging: files and total bytes staged and returned (summary; detail in `staging-manifest/`).
5. Mesh: how it was generated, file names, verification result (counts, bounding box, set sizes).
6. Input deck(s): file names; the exact locked settings and where each appears in the generated runtime configuration.
7. Execution: every command used; every Slurm job ID submitted (also in `jobs/job_ids.txt`), with state and exit code; the job script path.
8. Completed stages and iteration counts actually reached; the stopping message of the optimizer.
9. Key output file names (deliverables in `outputs/`), with their SHA-256 (also in `outputs/SHA256SUMS.txt`).
10. Failures, retries, cancelled jobs, unresolved issues, deviations from the specification (if none, say "none").
11. Final artifact paths.

## Scheduler evidence
- `jobs/job_ids.txt`: one job ID per line for every submission (failed, cancelled and successful).
- Keep every submitted job script under `jobs/` and the scheduler's stdout/stderr under `logs/` or `outputs/run_logs/`.
- After each job finishes, record `sacct -j <id> --format=JobID,JobName,State,ExitCode,Submit,Start,End,Elapsed,AllocCPUS,ReqMem,MaxRSS,NodeList -P` output in `jobs/`.

## Timestamps and environment
- UTC timestamps for: discovery, staging, mesh generation, deck translation, job submission, job start/end, verification.
- Record `module list` (after sourcing the approved software interface) inside each job script's stdout.

## Audit evidence
- The researcher keeps the full session record (stream, transcript, tool inputs) and audits every path used, together
  with `jobs/`, `staging-manifest/`, `provenance/` and the job logs. Do not delete, truncate or rewrite any record,
  including records of failed or abandoned steps.
- `provenance/sources_searched.tsv` must list every location you searched or listed, including ones you rejected; every
  location must be in a permitted collection (`protocol/access_rules.md`).

## Integrity
- `outputs/SHA256SUMS.txt` covers every file under `outputs/` (except itself), produced with `sha256sum`.
- Every staged and returned file has matching source/destination SHA-256 recorded.
- Do not overwrite an accepted deliverable with a later attempt without recording the replacement in the summary.
