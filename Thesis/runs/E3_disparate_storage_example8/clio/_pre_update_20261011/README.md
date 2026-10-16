# E3 CLIO trials

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
