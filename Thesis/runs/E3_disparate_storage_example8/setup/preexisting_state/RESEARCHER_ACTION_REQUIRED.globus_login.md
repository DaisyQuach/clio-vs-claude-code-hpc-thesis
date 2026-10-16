# RESEARCHER ACTION REQUIRED — Globus authentication (E3 readiness stopped at Phase 2.2)

Date: 2026-10-10 UTC. Status in `setup/E3_BLOCKER_STATUS.yaml`. E3 is **NO-GO**.

No Globus session exists for this account, so readiness stopped before any login, collection or transfer step. No
credentials, tokens or authorization codes were requested, printed or stored.

## What was prepared
The Globus CLI was not installed anywhere, so a pinned copy was installed without authentication:
- **Location:** `automation/environment/tools/globus-cli-3.43.0/`, a virtualenv on CHPC module `python/3.12.4`.
- **Lock file:** `automation/environment/tools/globus-cli-3.43.0.requirements.lock.txt`.
- **Check:** `globus version` reports 3.43.0, and `globus whoami` reports `MissingLoginError`.

## Your action (on a CHPC login node, in your own terminal)
```bash
module load python/3.12.4
G=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/automation/environment/tools/globus-cli-3.43.0/bin/globus
$G login --no-local-server
```
Open the URL it prints in your own browser. Complete the University of Utah login, MFA and consent. Paste the one-time
authorization code only into your own terminal when the CLI asks for it. Do not paste it into this conversation.

## Verify afterwards (safe, read-only)
```bash
$G whoami
```
Expected: your Globus identity (for example `<uNID>@utah.edu`), exit 0.

## Then send
> Globus authentication is complete. Resume E3 readiness.

## What happens next (for planning only; nothing done yet)
- **Phase 2:** list only the collections available to you. Then create a private guest collection, read-only for E3 and
  shared with no one else, rooted at `globus_source_root/` only.
  - CHPC may require approval for a guest collection on its home-directory endpoint. If so, I will stop again and give you
    the exact helpdesk request.
  - Creating the guest collection may also ask for a one-time data-access consent. That is your action again.
- **Phase 5 will need your decision on how CLIO is deployed.** The current E3 documents don't define it. Do you want local
  CLIO Desktop connected to CHPC, or a documented remote/headless CLIO runner? You can decide this now in parallel. No
  CLIO trial directories (`clio/trial_02..05`) or runner will be created until you decide.
