# Staging rules

1. Staging target: the node-local directory in `$E3_STAGING_DIR` (under the Slurm per-job node-local `$TMPDIR`, as
   `$TMPDIR/e3/<system>/<trial_id>`), created fresh and empty for this trial. Record its host and free space in
   `provenance/node_local_placement.txt`.
2. Stage only from the collections listed in `catalog/permitted_storage_catalog.yaml`, and only what you need.
   The private source collection (`e3-private-source`) is reached **only by Globus**, with
   `scripts/non_destructive_preflight_helpers/globus_stage_file.sh`. It transfers the file into this trial's
   `staging-inbox/` (the only permitted Globus destination), checks it against the collection's `MANIFEST.sha256`, and copies
   it into `$E3_STAGING_DIR`. Do not read the collection's host path directly, and do not use any other Globus collection
   or destination. The candidate archive and the control snapshot are read by POSIX path with `stage_file.sh`. Copy with a byte-preserving copy (`cp -p`, `rsync -a` without `--delete`/`--remove-source-files`,
   or a Globus transfer if the catalog provides one). Never move, link-and-edit, or modify a source file.
3. After each copy, compute the SHA-256 of the source and of the staged copy; they must match. Append one line per file to
   `staging-manifest/staged_files.tsv`.
4. Node-local storage is visible only on the agent-host node. Anything a Slurm job on another node needs must be copied from
   staging into the trial workspace (for example `work/`); record each such copy in `staging-manifest/returned_files.tsv`.
5. Edit only copies. If you adapt a staged file, keep the staged original unchanged and write the adapted file under `work/`.
6. Do not delete the staging directory; it is released with the allocation.
7. `globus_stage_file.sh`, `stage_file.sh` and `return_file.sh` in `scripts/non_destructive_preflight_helpers/` implement rules 2–5.
   Do not edit or delete anything in `staging-inbox/`; it is a transfer record.
8. A Slurm job may read only the trial workspace, the staging directory, the permitted collections and the approved
   software interface (`protocol/access_rules.md`). Job scripts are kept under `jobs/` and audited like the session.
