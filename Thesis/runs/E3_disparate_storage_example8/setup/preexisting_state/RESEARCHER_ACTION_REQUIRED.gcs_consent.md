# RESEARCHER ACTION REQUIRED — Globus collection-management consent (E3 readiness stopped at Phase 2.4)

Date: 2026-10-10 UTC. Status in `setup/E3_BLOCKER_STATUS.yaml`. E3 is **NO-GO**. The previous step (Globus login) is
done; its instructions are kept in `setup/preexisting_state/RESEARCHER_ACTION_REQUIRED.globus_login.md`.

## Where things stand
- `globus whoami` returns your identity.
- You own no collections, and nothing is shared by you.
- `globus ls` of `globus_source_root/` already works through CHPC's mapped collection *University of Utah -- CHPC DMZ
  Clustered Endpoint* (`7cf0baa1-8bd0-4e91-a1e6-c19042952a7c`). A mapped collection shows your whole filesystem view,
  though, so E3 needs a private **guest collection** rooted at `globus_source_root/` only.
- Checking whether that endpoint allows guest collections, and creating one, needs the `manage_collections` consent for
  its Globus Connect Server endpoint. That consent is a browser step, so I stopped. No collection was created, nothing was
  transferred, and no token or code was handled.

## Your action (on a CHPC login node, in your own terminal)
```bash
module load python/3.12.4
G=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/automation/environment/tools/globus-cli-3.43.0/bin/globus
$G login --gcs 70ea92f5-e653-42f3-bbe0-decb336c32cc --no-local-server
```
Open the URL it prints in your own browser, complete login, MFA and consent, and paste the code only into your own
terminal.

## Verify afterwards (safe, read-only)
```bash
$G gcs collection show 7cf0baa1-8bd0-4e91-a1e6-c19042952a7c
```
Expected: the collection's details print instead of `MissingLoginError`.

## Then send
> Globus collection-management consent is complete. Resume E3 readiness.

## What I will do next (nothing done yet)
1. Check that the storage gateway allows guest collections. If it does not, I will stop and give you the exact CHPC
   helpdesk request.
2. Create a guest collection named `daisy-e3-private-source`, rooted at `globus_source_root/`. It will not be public and
   will have no access rule for any other identity.
3. Make `globus_source_root/` read-only at the filesystem level, as the candidate archive already is, so Globus cannot
   write there either.
4. Verify with a non-mutating listing and record the name, UUID, type, root and policy. Then make one control-repository
   commit and update the pin.

## Decision you can make in parallel
For Phase 5: should CLIO run as local CLIO Desktop connected to CHPC, or through a documented remote/headless runner?
