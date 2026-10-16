# RESEARCHER ACTION REQUIRED — guest collection visibility (Phase 2 completion)

Date: 2026-10-10 UTC. Status in `setup/E3_BLOCKER_STATUS.yaml`. E3 is **NO-GO**. Earlier instructions are kept in
`setup/preexisting_state/RESEARCHER_ACTION_REQUIRED.*.md`.

`daisy-e3-private-source` (`6dcea62e-130d-47a9-8b77-80fba6f58693`) has `public: true`, meaning it is listed in Globus search.
It grants no data access: the only access rules are your owner rule and the endpoint's service rule. The web app's Edit
Attributes page shows no visibility option.

The Globus CLI can change it with `globus gcs collection update <uuid> --private`, but that command must reach the endpoint's
management server. CHPC login node notchpeak1 cannot reach it, and other login nodes are not reachable without an
interactive login.

## Option A (recommended): run the update from your own computer
Your browser reached the management server when you created the collection, so your own computer should be able to.
```bash
python3 -m pip install --user globus-cli==3.43.0        # or: pipx install globus-cli==3.43.0
globus login                                            # browser login, MFA, consent (your own terminal)
globus login --gcs 70ea92f5-e653-42f3-bbe0-decb336c32cc # collection-management consent for the CHPC DMZ endpoint
globus gcs collection update 6dcea62e-130d-47a9-8b77-80fba6f58693 --private
```
Never paste codes or tokens into this conversation.

**Verify** (on a CHPC login node, safe and read-only):
```bash
module load python/3.12.4
G=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/automation/environment/tools/globus-cli-3.43.0/bin/globus
$G api transfer GET /endpoint/6dcea62e-130d-47a9-8b77-80fba6f58693 | grep '"public"'
```
Expected: `"public": false`. **Then send:**
> Guest collection visibility set to private. Resume E3 readiness.

## Option B: accept discoverability as a recorded decision
Choose this only if you judge that being listed in search, with no access rule for anyone else, satisfies "never public"
for E3. It would be recorded as a researcher decision in the blocker file and the final readiness report. **Send:**
> Accept discoverable-only Globus visibility. Resume E3 readiness.

## Still pending from you
The CLIO deployment choice for Phase 5: local CLIO Desktop connected to CHPC, or a documented remote/headless runner.
