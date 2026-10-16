# E3 CLIO deployment — recorded assumption (not a runbook, not a runner)

**Superseded 2026-10-10 by the researcher's authoritative definition: `setup/CLIO_DEPLOYMENT.md`.** Kept as history.

Date: 2026-10-10 UTC. Researcher decision: **assume local CLIO Desktop connected to CHPC**. The details will be
clarified together with Experiments 1 and 2. A working CLIO path is not required at this stage.

Consequences (nothing below has been built or tested):
- No CLIO runner was created, and `clio/trial_02..05` were not created. Only `clio/trial_01/` exists (planned, clean
  `agent-inputs/` and `staging-inbox/`).
- Before any counted CLIO trial, a runbook must answer each of these:
  - **Which machine runs the agent session.** Presumably the researcher's computer running CLIO Desktop, connected to a
    CHPC allocation. The account already runs `clio-desktop-alloc`, `clio-agent-daisy` and `cws-clioruntime` jobs on
    `hochhalter-np`; E3 has not inspected or used them.
  - **Which machine reads GitHub and Globus.**
  - **Which machine writes E3 trial files, and how artifacts reach CHPC.**
  - **How the session record (tool calls, transcript) is captured** so that `automation/audit_boundary.sh` can audit it.
- **Parity with the baseline** is required for: the same frozen packet at the same pin, the Globus-only private source
  with the same `staging-inbox/` destination, the node-local `$TMPDIR`, the same timing boundaries, audit rules,
  retention, invalid-attempt handling, and scoring.
- Until then, CLIO deployment and runner readiness is **open**, and E3 is NO-GO.
