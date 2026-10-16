# Trial context

| Item | Value |
|---|---|
| Trial identifier | `E3-clio-trial_06` (also in $E3_TRIAL_ID) |
| Trial root (working directory) | `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/clio/trial_06` |
| Node-local staging directory | `/scratch/local/u1282901/16250333/e3/clio/E3-clio-trial_06` (also in $E3_STAGING_DIR) |
| Control repository commit | `62954055b4e848f2155258c5b8c628eab97c8586` (snapshot in `agent-inputs/control/`) |
| e3-private-source | `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/globus_source_root` — Globus collection `6dcea62e-130d-47a9-8b77-80fba6f58693` (noninteractive Globus CLI) is the only permitted access method; the path shown is the host path, for provenance only. Do not read it directly. |
| e3-chpc-candidate-archive | `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/chpc_candidate_archive` (read-only POSIX) |
| Approved software interface | `source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/automation/environment/load_morphorm_e3.sh` |
| Globus | pinned CLI `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/automation/environment/tools/globus-cli-3.43.0/bin/globus`; stage private-source files only with `globus_stage_file.sh` (destination: `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/clio/trial_06/staging-inbox/` via collection `7cf0baa1-8bd0-4e91-a1e6-c19042952a7c`; details in `agent-inputs/globus_access.txt`) |
| Record-keeping helpers | `agent-inputs/control/scripts/non_destructive_preflight_helpers/` (they read `agent-inputs/permitted_roots.txt`) |

`agent-inputs/` is read-only. Write only in `work/ jobs/ logs/ outputs/ provenance/ staging-manifest/` and the staging directory;
`staging-inbox/` receives Globus transfers only (do not edit it).

Access: read only this trial root, the two collections above, the control snapshot and the approved software interface.
Researcher-only records, other trials and experiments, original software/source trees, completed reference material, and
scoring or validation records are prohibited for the session and for every Slurm job it submits. Trials run under the
researcher's account, so this is a procedural rule rather than a filesystem restriction; every path used is audited
(`agent-inputs/control/protocol/access_rules.md`).
