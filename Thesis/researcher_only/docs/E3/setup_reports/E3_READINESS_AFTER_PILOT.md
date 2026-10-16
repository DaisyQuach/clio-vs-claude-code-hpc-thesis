# E3 readiness after the access pilot

Window: 2026-10-10T02:30Z → 04:09Z (UTC). Researcher decisions, the full blocker record and earlier versions:
`setup/E3_BLOCKER_STATUS.yaml`. Phase 3 detail: `setup/E3_PILOT_PHASE3_REPORT.md`. Pilot evidence:
`Daisy/E3_access_pilot/` (job scripts, stdout/stderr, sacct records, SHA256SUMS; all redacted).

## Verdict: **NO-GO**
Globus, GitHub at the pin, compute-node qualification, Claude 2.1.295, ordinary Morphorm/Cubit licensing, the
baseline runner and the account-name question are resolved or decided. **CLIO deployment and its runner are not.** As a
result, the final packet freeze, the five-versus-five parity and Phase 7 could not be done. No agent-input packet was
created or frozen.

## Blocker table
| Blocker | Status | Evidence / remaining action |
|---|---|---|
| Globus configuration | **Resolved** | Guest collection `daisy-e3-private-source` `6dcea62e-130d-47a9-8b77-80fba6f58693` (GCSv5 guest, on CHPC DMZ mapped collection `7cf0baa1…`), root = `globus_source_root/`; `/../` stays at root. Only the implicit owner and endpoint rules; filesystem read-only (0 write bits; Globus `mkdir` → 403). Visibility: discoverable-only, accepted by the researcher. Mandatory: the runner refuses `posix_readonly_fallback`. Pinned CLI 3.43.0 (`automation/environment/tools/`). |
| GitHub access at pinned commit | **Resolved** | Pin `62954055b4e848f2155258c5b8c628eab97c8586` (catalog v5), repository private. Readable noninteractively from the login node and from compute node notch204 (`ls-remote`, blobless clone, pin object; the runner's prepare dry run). |
| Compute-node qualification | **Resolved** | Jobs 16172196, 16172237 and 16172265 (all exit 0, notch204). `$SLURM_TMPDIR` is unset on CHPC; the fixed node-local root is the Slurm per-job `$TMPDIR` = `/scratch/local/<account>/<jobid>`. It is fresh, writable, owned by the account, 1.8 TB XFS, not readable by others, and not removed at job end (a new job ID guarantees freshness). `/tmp` is a RAM tmpfs and is not used. The automation now uses `$TMPDIR` (`e3_node_local_root`). |
| Claude 2.1.295 readiness | **Resolved (version/flags); launch auth checked by runner** | `2.1.295 (Claude Code)`, SHA-256 `4503bfe1…f358`, all headless flags present, on the login node and the compute node. No model call. Headless `auth status` is checked automatically at launch inside the isolated config; the runner stops with `ACTION_REQUIRED_claude_auth` before any session if it fails. Not exercised here, because it requires handling the credential file. |
| Ordinary Morphorm/Cubit/licence readiness | **Resolved** | E3 loader on the compute node: rc 0, 0 `ThesisExperiments` entries, executables resolve to the E3 runtime copies. Cubit licence: per-user `$HOME/.config/Coreform/`, visible to jobs. A trivial approved `cubit -batch` (`brick x 1`, no export) in job 16172237 exited 0, logged in with the licence and left no files. Morphorm was not run. |
| Baseline runner readiness | **Resolved, pending the final freeze** | Job 16172456: real runner `--dry-run` inside an allocation passes every check (allocation/`$TMPDIR`, Claude pin, flags, GitHub, Globus, sources, workspace) and wrote nothing. Test-mode plumbing on a scratch tree with a test double ran end to end: prepare at the pin, `$TMPDIR` staging, records, audit PASS, sources unchanged. Writes stayed in the trial plus the isolated runtime config. Globus staging helper unit-tested with pilot files: transfer into `staging-inbox/`, manifest hash check, node-local copy, and refusals. |
| CLIO deployment and runner readiness | **OPEN** | Researcher decision: assume local CLIO Desktop connected to CHPC; details to be clarified with E1/E2; not required now (`setup/CLIO_DEPLOYMENT_ASSUMPTION.md`). No runner, no runbook, no CLIO access-path test, and `clio/trial_02..05` not created. |
| Final packet freeze | **OPEN (not attempted)** | Blocked by CLIO. The pin, prompt hash (`63f84f79…1c20`), Globus IDs and environment pins are current but **not frozen**. No packets were created. |
| Account-name / provenance decision | **Resolved** | The runtime `PROVENANCE.md` files (Morphorm, Cubit) name the account and are reachable by agents through the permitted runtime root; browsing them is prohibited, and they are not in any packet. Kept byte-identical; no redaction proposed. The researcher accepted the account name in staging paths (`E3_ALLOW_ACCOUNT_NAME_IN_TMPDIR=1`). |
| Baseline/CLIO trial-count parity | **OPEN** | Baseline: 5/5 workspaces (trial_01..05), clean, `verify --planned` PASS. CLIO: 1/5 (trial_01 only). |

## Fixed staging procedure (identical for all ten trials; compute nodes have GitHub and Globus access)
1. Prepare: the runner clones the control repository at the pin into `$TMPDIR/e3/_control` and copies the frozen packet
   into `agent-inputs/`. That includes `globus_access.txt` and `permitted_roots.txt`, which no longer lists the private
   source.
2. Node-local staging dir: `$TMPDIR/e3/<system>/<trial_id>`, created fresh. Reuse is refused.
3. Private source: `globus_stage_file.sh` only. It runs a Globus transfer from `6dcea62e…:/<path>` to
   `7cf0baa1…:<trial>/staging-inbox/<path>`, checks the file against the collection's `MANIFEST.sha256`, then does
   `cp -p` into staging. Records go to `staging-manifest/globus_transfers.tsv` and `staged_files.tsv`.
4. Candidate archive and control snapshot: POSIX `stage_file.sh`.
5. Audit: tool-call paths, with direct POSIX reads of the private source FORBIDDEN; job scripts and job logs; and Globus
   use. The Globus check covers tool calls, the transfer log, and the account's Globus task list for the trial window,
   so any other collection, any mutation, or any destination outside `staging-inbox/` is FORBIDDEN.
6. Authentication: the runner checks `globus whoami`, `globus ls`, `git ls-remote` and `claude auth status` before
   launch and stops with ACTION_REQUIRED if any fails. Nothing is interactive mid-trial. Globus uses stored refresh
   tokens with a one-year high-assurance timeout.

## Changes made in this work
- **Control repository** (private; pushed):
  - `ab341a1c…` (catalog v4: Globus collection);
  - `62954055…` (catalog v5: Globus-only staging, `staging-inbox/` destination, `$TMPDIR`, `globus_stage_file.sh`).
- **E3 automation:**
  - pinned Globus CLI;
  - Globus mandatory (fallback refused);
  - `E3_GLOBUS_COLLECTION_ID`, `E3_GLOBUS_CLI_REL`, `E3_ALLOW_ACCOUNT_NAME_IN_TMPDIR=1`;
  - per-job `$TMPDIR` root;
  - `staging-inbox/` in `TRIAL_DIRS`;
  - Globus IDs and the CLI as a software root;
  - prepare writes `globus_access.txt`;
  - audit §7 Globus (`lib/classify_globus.py`), with direct POSIX reads of the private source forbidden;
  - verification requires private-source rows to be staged by Globus.
  Pre-change copies are in `setup/preexisting_state/{globus_readiness_pre,globus_config_pre,node_local_pre,globus_staging_pre}/`,
  each with a `.sha256` list.
- **`globus_source_root/`:** `chmod -R a-w`. Previous modes: `setup/preexisting_state/globus_source_root_modes.pre_readonly.txt`.
- **Trials:**
  - empty `staging-inbox/` added to baseline trial_01..05 and clio trial_01;
  - `e3ready_*` fields appended to the six manifests (earlier lines verified byte-identical; pre-append copies in
    `setup/preexisting_state/readiness_pilot_manifests_pre/`).
  No trial evidence was altered.
- **Status notes and records:**
  - added to `GLOBUS_ACTION_REQUIRED.md` and `COMPUTE_NODE_QUALIFICATION_ACTION_REQUIRED.md` (originals in
    `setup/preexisting_state/*.pre_pilot.md`) and to `permissions_audit_remediation.md`;
  - new `setup/integrity/` snapshot.

## Confirmations
- **Nothing scientific was run:** no counted trial, no model call, no CLIO session, no Morphorm execution, and no
  scientific Slurm job.
- **Slurm jobs submitted (all harmless, non-scored, exit 0, node notch204):**
  - 16172196: qualification;
  - 16172237: `/scratch/local` probe plus the approved trivial Cubit batch;
  - 16172265: `$TMPDIR` probe;
  - 16172456: Claude version/help, runner dry run, test-double plumbing.
- **Globus transfers:** only pilot files (tasks `6397c2c9…`, `d13f6b70…`, `58edbcfa…`, `69bfb2d3…`, `7024aae1…`), all
  mapped collection to mapped collection inside `E3_access_pilot/`. No E3 research file was transferred. The approved
  collection was only listed.
- **Integrity (2026-10-10T04:08Z):**
  - E1, E2, ThesisExperiments, `Morphorm_Full_Examples_Tests`, `Morphorm_ground_truth`, `Morphorm` and
    `morphorm_manuals` show 0 differences against the `setup/integrity/` snapshot, and 0 entries modified since 02:18Z;
  - originals: content hashes 30/30 and 5/5 PASS;
  - E3 private source manifest PASS; candidate archive has 0 write bits.
- **Disclosures:**
  - The session-scratchpad snapshots from the previous task were lost, so integrity now uses the snapshot in
    `setup/integrity/` plus mtime/ctime and content checks.
  - I ran `rm -rf automation/lib/__pycache__` once to remove a byte-code cache that my own `py_compile` had just
    created; no record shows that directory existing before.
  - I stopped two of my own hung test processes. A helper bug (exit inside command substitution, plus an NFS visibility
    delay) caused the hang; it was fixed and retested.
  - Pilot SSH probes to other login nodes were refused. No host key was added and no login was attempted.

## To reach GO
1. Define and document the CLIO deployment, which you'll clarify with E1/E2. Then ask for the CLIO runbook and runner,
   five CLIO workspaces, and a harmless access-path test.
2. Then run Phase 7:
   - create fresh packets for baseline trial_01..05 and clio trial_01..05;
   - freeze the pin, prompt hash, storage map, Globus IDs, environment pins, the five-versus-five design and the scoring
     protocol;
   - repeat the integrity checks.
