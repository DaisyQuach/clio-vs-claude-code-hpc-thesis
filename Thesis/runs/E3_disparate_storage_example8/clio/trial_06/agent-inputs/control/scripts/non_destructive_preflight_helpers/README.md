# Non-destructive preflight and record-keeping helpers

All helpers only read source collections and append records inside the trial root. None deletes, moves or edits a source.
They use `$E3_TRIAL_ROOT` (default: current directory), `$E3_STAGING_DIR`, and `agent-inputs/permitted_roots.txt`.

| Script | Writes |
|---|---|
| `record_search.sh <alias> <path> <method> <purpose>` | `provenance/sources_searched.tsv` |
| `globus_stage_file.sh <path_in_collection> [staged_rel_path]` | private source collection only: Globus transfer into `staging-inbox/`, manifest-checked copy in `$E3_STAGING_DIR`; `staging-manifest/globus_transfers.tsv`, `staged_files.tsv` |
| `stage_file.sh <source_file> [staged_rel_path]` | POSIX collections only (candidate archive, control snapshot): copy in `$E3_STAGING_DIR`, `staging-manifest/staged_files.tsv` |
| `return_file.sh <staged_file> <dest_rel_to_trial_root>` | copy in the trial root, `staging-manifest/returned_files.tsv` |
| `record_node_placement.sh` | `provenance/node_local_placement.txt` |
| `verify_collection.sh <collection_root>` | `provenance/control_and_source_versions.txt` |
| `hash_outputs.sh` | `outputs/SHA256SUMS.txt` |
