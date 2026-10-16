# GLOBUS ACTION REQUIRED — private source collection is NOT configured

**Status update 2026-10-10 UTC (readiness pilot): RESOLVED.** Private guest collection `daisy-e3-private-source`
(`6dcea62e-130d-47a9-8b77-80fba6f58693`) is rooted at `globus_source_root/`. It is read-only on disk, its only access
rules are the implicit owner and endpoint ones, and discoverable-only visibility was accepted by the researcher. It is
configured in the baseline config and in catalog v5 (pin `62954055…`). The `posix_readonly_fallback` is withdrawn
(Globus is mandatory). Details: `setup/E3_BLOCKER_STATUS.yaml`, `setup/E3_READINESS_AFTER_PILOT.md`. The text below is
the original record.

Status: **not configured.** No Globus CLI (`globus`), Globus SDK, Globus Connect Personal or Globus credentials exist in this
environment (checked: `which globus`, `python3 -c "import globus_sdk"`, `module avail` shows no Globus module, no `~/.globus*`).
Creating a collection requires an authenticated Globus identity (interactive login/consent, possibly MFA) and a CHPC endpoint
owner/administrator action, which were not attempted or bypassed.

## Directory to register (and nothing above it)
```
/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/globus_source_root
```
It is complete and verified: 13 files, `MANIFEST.sha256` (SHA-256 `44735ea762399004a7975a895c25ac28bc7dada8cd7e92d6d96f6aaa293a465c`)
and `MANIFEST.tsv`. Do **not** share the E3 root: it also contains `researcher_only/`.

## Exact remaining manual actions
1. In the Globus web app (app.globus.org), log in with the University of Utah identity.
2. On the CHPC managed endpoint that serves `/uufs/chpc.utah.edu/common/home/...` (CHPC's DTN collection), create a **guest collection**
   rooted at the directory above; set it **read-only**; share with no one except the researcher identity (private).
   If guest collections are not permitted on that endpoint, ask CHPC support (helpdesk@chpc.utah.edu) to enable it.
3. Record the collection UUID in `automation/baseline/baseline_e3_config.env` (`E3_GLOBUS_COLLECTION_ID=`) and in
   `catalog/permitted_storage_catalog.yaml` (`globus_collection_id`) of the control repository (new commit, then update
   `E3_CONTROL_COMMIT`).
4. For noninteractive use on compute nodes: install the Globus CLI (`pip install --user globus-cli`), run `globus login` once
   interactively, and verify `globus whoami` and `globus ls <UUID>:/` work in a batch job (access qualification step 2).
5. Optional hardening before registration: `chmod -R o-rwx globus_source_root` (see `permissions_audit.md`).

Until then every counted trial stops with `logs/ACTION_REQUIRED_globus_not_configured.md` unless a researcher deliberately sets
`E3_GLOBUS_MODE=posix_readonly_fallback` (recorded as a deviation in each trial's launch plan and manifest).
