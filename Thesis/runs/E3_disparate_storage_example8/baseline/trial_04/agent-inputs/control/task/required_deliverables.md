# Required deliverables (summary of `frozen_task_specification.md` §8)

All paths are relative to the trial root. A process that exits cleanly is not a success; missing deliverables, unverified
settings, a run that did not reach 50 iterations, or missing provenance are not successes.

## Scientific
- `outputs/mesh.jou`, `outputs/mesh.exo`, `outputs/mesh_verification.txt` (or `.json`)
- `outputs/input_deck.i`, `outputs/job_script.sbatch`, `outputs/generated_config/` (all XMLGenerator files of the accepted run)
- `outputs/morphorm_oc_optimizer_diagnostics.txt`, `outputs/engine_output.exo`, `outputs/final_analyze_output.exo`
- `outputs/run_logs/`, `outputs/SHA256SUMS.txt` (every file under `outputs/` except itself)
- `jobs/job_ids.txt` (every submitted job, including failed and cancelled ones), job scripts under `jobs/`, `sacct` records under `jobs/`

## Distributed context and provenance
- `provenance/sources_searched.tsv` — `utc  collection_alias  path  method  purpose`
- `provenance/artifact_selections.md` — each examined artifact: used / adapted / not used, and why
- `staging-manifest/staged_files.tsv` — `utc  collection_alias  source_path  staged_path  bytes  source_sha256  staged_sha256`
- `staging-manifest/returned_files.tsv` — `utc  staged_path  destination_path  bytes  sha256`
- `provenance/node_local_placement.txt` — host, staging directory, free space at creation
- `provenance/control_and_source_versions.txt` — control commit used, checksum verification of each source collection used
- `work/run_summary.md` — sections required by `protocol/provenance_requirements.md`

Helpers that write these records in the required format are in `scripts/non_destructive_preflight_helpers/`.
