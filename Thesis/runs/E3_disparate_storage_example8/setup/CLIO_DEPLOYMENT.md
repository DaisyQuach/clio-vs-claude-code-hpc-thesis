# E3 CLIO deployment — authoritative definition (researcher, 2026-10-10 UTC)

This supersedes `setup/CLIO_DEPLOYMENT_ASSUMPTION.md`. The researcher's definition is recorded in §1–§5. Mapping it onto
the actual CLIO software and the E3 automation is in `setup/CLIO_RUNBOOK.md`.

## 1. Session deployment
- **Researcher, manually:** obtains the CHPC compute allocation and deploys/starts the CLIO service/agent on that
  allocated compute node, using the established CLIO deployment procedure.
- **CLIO Desktop:** runs on the researcher's local Windows machine. It connects to the already-running CHPC CLIO service
  through the established SSH tunnel/API connection.
- **The Desktop is the conversation/control interface only.** It is not an E3 data-storage endpoint, and it must not
  directly access E3 files, GitHub, Globus or CHPC trial directories.

## 2. Storage and external-resource access
- **Only the CHPC side touches E3 resources.** The CLIO agent/tool processes on the CHPC compute node are the only trial
  components that access them.
- **GitHub:** read only by the CHPC-side process, using the same pinned private-repository commit and read-only procedure
  as the baseline.
- **Globus:** accessed only through the approved CHPC-side staging helper (`globus_stage_file.sh`) and the approved
  private source collection (`6dcea62e-130d-47a9-8b77-80fba6f58693`). It may stage approved files only into the trial's
  `staging-inbox/`, and from there into that trial's node-local `$TMPDIR` location.
- **Prohibited for the CLIO agent:** reading the Globus source path directly, using another Globus collection,
  writing or deleting through Globus, and accessing `researcher_only/` or `setup/`.
- **Persistence:** trial inputs, outputs, audit records and session exports are stored only in the designated E3 CHPC
  trial directory. Node-local copies are temporary execution/staging material.

## 3. Trial records
- **Fresh session and workspace per trial:** each CLIO trial has its own fresh CLIO session and its own CHPC trial
  workspace, `clio/trial_01` … `clio/trial_05`.
- **What is recorded for each trial:**
  - allocation/job ID and compute-node hostname;
  - CLIO service/API version and Desktop/client version;
  - model identifier and session/conversation identifier;
  - UTC start/end time;
  - exact task-prompt hash, repository commit pin and Globus collection ID;
  - all staging and audit logs.
- **Session export:** after completion, the complete CLIO conversation/session record is exported or retained in the
  trial's evidence area, together with API request/response or event logs if the deployment exposes them.
- **Tunnel log:** the Desktop connection/tunnel log may be retained as operational evidence, but it must not contain
  credentials or authorization tokens.

## 4. Automation boundary
- **Manual, before a trial:** the researcher may establish the allocation, deploy CLIO, and establish the local SSH
  tunnel.
- **Automated, once the CLIO service is reachable:** trial setup, task dispatch, artifact staging, workflow execution,
  log capture, audit and result retention follow the automated E3 procedure.
- **No permissions may be added or broadened during a counted trial.**

## 5. Experimental parity
- **Five valid CLIO trials,** matching baseline trial_01 … trial_05.
- **Same as the baseline:** approved packet content, task prompt, storage map, read-only GitHub/Globus access model,
  staging checks, timing boundaries, audit rules and scoring procedure.
- **Invalid or interrupted attempts** are retained as invalid evidence, never overwritten or silently replaced.
