# RESEARCHER ACTION REQUIRED — make the E3 guest collection non-discoverable (Phase 2 completion)

Date: 2026-10-10 UTC. Status in `setup/E3_BLOCKER_STATUS.yaml`. E3 is **NO-GO**. Earlier instructions are kept in
`setup/preexisting_state/RESEARCHER_ACTION_REQUIRED.{globus_login,gcs_consent,guest_collection}.md`.

## Done
- **Verified:** `daisy-e3-private-source` (`6dcea62e-130d-47a9-8b77-80fba6f58693`) is a GCSv5 guest collection rooted at
  `globus_source_root/`. A `/../` probe stays at that root.
- **Access rules:** only the implicit owner and endpoint-service rules exist. No other identity, group or all-users rule.
- **Read-only:** `globus_source_root/` is read-only on disk (0 write bits), and a Globus `mkdir` probe was refused (403).
- **Configured:** the E3 config uses the collection ID and the pinned Globus CLI.
- **Control repo:** catalog v4 is pushed (`ab341a1c66093f32c897b5c3390ac45bead4d135`, repository private), and the pin is updated.
- **Dry run:** a login-node dry run passes every check that can run there, including Globus.

## Remaining issue
The collection record shows `public: true`, meaning it is listed in Globus search. That grants no data access, but it
conflicts with "never public". The CLI cannot change it from CHPC, because the endpoint's management server is unreachable
from the login node.

## Your action (Globus web app)
1. Open https://app.globus.org, go to **Collections**, and open **daisy-e3-private-source**.
2. Click **Edit Attributes**. Find the visibility setting (labelled "Public" or "Visibility"), set it to not public /
   private, and save.
3. While there, confirm the **Permissions** tab lists no rule for anyone but you.

## Verify afterwards (safe, read-only)
```bash
module load python/3.12.4
G=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/automation/environment/tools/globus-cli-3.43.0/bin/globus
$G api transfer GET /endpoint/6dcea62e-130d-47a9-8b77-80fba6f58693 | grep '"public"'
```
Expected: `"public": false`.

## Then send
> Guest collection visibility set to private. Resume E3 readiness.

## Next (not started)
**Phase 3:** a harmless compute-node pilot in `Daisy/E3_access_pilot/`, with one minimal Slurm job and no Claude, Morphorm,
Cubit or E3 packet. It will also settle how Globus files reach `$SLURM_TMPDIR`, using one fixed method for all ten trials.

## Still pending from you
The CLIO deployment choice for Phase 5: local CLIO Desktop connected to CHPC, or a documented remote/headless runner.
