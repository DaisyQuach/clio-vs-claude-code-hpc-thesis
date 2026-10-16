# E3 CLIO trials

> **Update 2026-10-13 (counted run).** `trial_01` stopped in preflight before anything was launched (no CLIO deployment, no
> model call): the v2 runner sourced the baseline config but did not export `E3_ALLOW_ACCOUNT_NAME_IN_TMPDIR=1` (the baseline
> runner does), so `init_node_local_staging.sh` raised ACTION_REQUIRED `tmpdir_contains_account_name`. The runner now exports
> it exactly as `run_baseline_e3_trial.sh` line 32 (pre-fix copy: `automation/clio/.run_clio_e3_trial_v2.sh.pre_export_fix_20261013`).
> `trial_01` is kept as a record (`e3dc_status: aborted_before_launch`, excluded); its replacement is the new directory
> `trial_06` (the runner accepts only `trial_NN`; same convention as baseline 02R = `baseline/trial_06`).
>
> **Own-runtime audit rule (researcher decision 2026-10-13).** The shared `audit_boundary.sh` (unchanged) flags every path
> under `.agent_runtime/`, including the CLIO agent's own runtime, which it reaches by design (blueprint skills such as
> `skills/hpc-batch-jobs/scripts/wait_job.sh`, and CLIO's saved long tool outputs). The runner now applies
> `Thesis/automation/clio/lib/e3_own_runtime_audit.py` after the shared audit: only this trial's own blueprint directory and
> this session's own `tool-output/<session id>/` are re-labelled OWN_RUNTIME; every other finding stays and the verdict is
> recomputed with the shared rules. The shared output is kept unchanged as `provenance/boundary_audit.shared.txt`
> (pre-change runner: `automation/clio/.run_clio_e3_trial_v2.sh.pre_own_runtime_20261013`). `trial_02` (science 34/34 in a
> test scoring) also FAILed on a researcher edit of this README during its run; it is excluded, not scored, and replaced
> by `trial_07`. Counted CLIO E3 trials: 03, 04, 05, 06, 07.

> **Update 2026-10-11 (CLIO v2 runner).** Runner: `automation/clio/run_clio_e3_trial_v2.sh`. It runs inside each trial's own
> allocation (baseline agent-host contract) and builds a fresh CLIO deployment there with the shared launcher
> `Thesis/automation/clio/launch_clio_session.sh` (the same one used for E1/E2). This replaces the manual
> `start_e3_clio_server.sh` step. CLIO pins and decisions live in `Thesis/automation/clio/clio_trial_config.env`; they are
> placeholders until the researcher fills them in, and counted runs are refused until then. Each manifest gained `e3clio2_*` fields.
> Pre-update copies of the manifests and READMEs are in `_pre_update_20261011/`. The text below is unchanged.

Planned workspaces: `trial_01` … `trial_05`, matching baseline trial_01 … trial_05. The deployment definition is in
`setup/CLIO_DEPLOYMENT.md`, and the procedure in `setup/CLIO_RUNBOOK.md`.

Each trial uses:
- its own fresh CLIO session;
- the same frozen control packet as the baseline;
- the same permitted collections: the private source by Globus only, through `staging-inbox/`;
- the node-local `$TMPDIR` staging;
- the same procedural researcher-only access policy and audit.

Invalid or interrupted attempts are retained and marked invalid; they are never overwritten. Previous versions of this
file are in `setup/preexisting_state/`.
