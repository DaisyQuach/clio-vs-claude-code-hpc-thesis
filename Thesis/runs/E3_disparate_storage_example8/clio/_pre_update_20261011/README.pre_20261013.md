# E3 CLIO trials

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
