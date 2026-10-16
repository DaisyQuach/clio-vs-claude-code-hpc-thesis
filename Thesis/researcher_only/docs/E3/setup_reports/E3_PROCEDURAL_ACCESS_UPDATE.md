# E3 procedural-access update

Window: 2026-10-10T02:17Z → 2026-10-10T02:30Z (UTC), login node notchpeak1, no allocation.
**No counted trial was run. Claude was not invoked for any trial or session. No Slurm job was submitted. Morphorm and
Cubit were not executed, and no result was created.** The only Claude Code executions were `--version`/`--help` of the
pinned binary, made by the read-only runner dry runs and one hash/version re-check. None of them made a model call.

**Verdict: E3 is still NOT ready for a counted trial.** Technical isolation no longer blocks it. The operational blockers
in §5 do.

## 1. Access policy adopted
E3 uses the same procedural researcher-only access model as Experiments 1 and 2:
- Completed Example 8 reference material stays researcher-only by experimental protocol.
- Baseline and CLIO agents are explicitly prohibited from accessing:
  - researcher-only paths;
  - original source roots;
  - E1/E2 directories;
  - `ThesisExperiments`;
  - completed reference packages;
  - scoring records and validation records.
- Researcher-only material is excluded from the agent-visible task packet, and agents are instructed and audited not to
  access it. Because experimental agents and Slurm jobs run under the researcher's account, this separation is
  procedural rather than a technically enforced filesystem security boundary.
- The prohibition appears in four places:
  - the task prompt;
  - `trial_context.md`, written into every `agent-inputs/`;
  - `protocol/access_rules.md`, `staging_rules.md` and `provenance_requirements.md`;
  - the catalog and every artifact card.
- After each trial it is audited by `automation/audit_boundary.sh`:
  - agent tool calls;
  - since this update, also the job scripts and job logs (§6);
  - writes outside the trial;
  - changes to collections and `researcher_only/`.
- The runner config sets `E3_ACCESS_MODEL=procedural_researcher_only`, and the runner refuses any other value. The value
  is written to `launch_plan.json`, `session_record.json` and `provenance/preparation.txt`.
- `automation/sandbox/` is kept as an optional development safeguard and login-node visibility check. It is not the E3
  runtime boundary, it is not used by the runner, and it does not technically isolate Slurm jobs submitted under the
  same account. `setup/GROUND_TRUTH_ISOLATION_ACTION_REQUIRED.md` is kept with its original text. It now has a dated
  status section: technical isolation is "not adopted for the current E3 protocol".

## 2. The exact limitation
The agent process and every Slurm job or job step it creates run as the researcher's Unix account. Same-account
processes can therefore read researcher-only paths. This includes:
- E3 `researcher_only/`;
- `Morphorm_ground_truth/`;
- `Thesis/researcher_only/`;
- the completed Example 8 runs in the example-test collection;
- the Example 8 material in the Morphorm documentation tree;
- E1/E2 and `ThesisExperiments`.

Owner-only modes (`700`/`600`) do not prevent this. The separation consists of three parts:
- **Exclusion:** none of this material is in `agent-inputs/`, the control repository, the private source collection or
  the candidate archive (§4).
- **Prohibition:** the prompt, `trial_context.md` and the protocol.
- **Audit:** reads by an agent tool call are detected from the session record. Absolute paths in job scripts or job
  logs are detected by the new audit section.

A same-account process could read a file without leaving a recognisable path in those records, for example a path
built at run time. The audit cannot prove that this did not happen. This residual limitation is the same as in E1/E2.
No E3 document claims technical inaccessibility or sandbox isolation.

## 3. Legacy packets moved from trial_02..05
All four packets were identical to each other and to the trial_01 packet archived at remediation. Each held 14 files
(3,718,426 bytes): the pre-E3 "planned only" note, the `FROZEN-EX8-v1` configuration and specification files, and two
manuals. Each was moved with `mv -n` (no deletion). For the rename only, `u+w` was set on the directory, and `555` was
restored afterwards.

Per-file SHA-256 lists were written before each move and verified after it. All 4 × 14 files are identical, and modes and
sizes are unchanged. Log: `setup/preexisting_state/legacy_baseline_trials02-05_move_log.tsv`.

| From | To (archival) | Hash list | Moved (UTC) |
|---|---|---|---|
| `baseline/trial_02/agent_inputs/` | `setup/preexisting_state/legacy_baseline_trial02_agent_inputs/` | `…/legacy_baseline_trial02_agent_inputs.sha256` | 02:18:57Z |
| `baseline/trial_03/agent_inputs/` | `setup/preexisting_state/legacy_baseline_trial03_agent_inputs/` | `…/legacy_baseline_trial03_agent_inputs.sha256` | 02:18:58Z |
| `baseline/trial_04/agent_inputs/` | `setup/preexisting_state/legacy_baseline_trial04_agent_inputs/` | `…/legacy_baseline_trial04_agent_inputs.sha256` | 02:18:58Z |
| `baseline/trial_05/agent_inputs/` | `setup/preexisting_state/legacy_baseline_trial05_agent_inputs/` | `…/legacy_baseline_trial05_agent_inputs.sha256` | 02:18:58Z |

The SHA-256 of each hash list is `4a70f780…cbb59`. It is the same for all four, and the same as the trial_01 archive.

Files in each packet: `acceptance_visibility_boundary.md`, `compute_resources.md`, `E3_PLANNED_NOT_EXECUTABLE.md`,
`formal_configuration.md`, `FROZEN_CONFIG_FILES.sha256`, `FROZEN_CONFIG_ID.txt`, `FROZEN_CONFIG_SHA256.txt`,
`manuals/Morphorm_Theory_Manual.pdf`, `manuals/Morphorm_User_Manual.pdf`, `provenance_requirements.md`,
`scientific_problem_specification.md`, `software_contract.md`, `task_prompt.md`, `workspace_rules.md`.

Each of trial_02..05 was then initialised with the existing `automation/init_trial_workspace.sh`:
- **Created:** `agent-inputs/` (empty placeholder with `.gitkeep`), `staging-manifest/` and `provenance/`.
- **Appended:** the `e3dc_*` manifest fields. The original manifest was kept as
  `setup/preexisting_state/baseline_trial_0N_manifest.pre_e3dc.yaml`.
- **Added:** a `README.md` stating that `agent-inputs/` is the only valid packet, together with the access policy.

**Manifests:** `e3proc_*` fields were appended to the six trial manifests (baseline trial_01..05, clio trial_01):
- access model and note;
- `e3proc_sandbox_required: false`;
- valid packet;
- for trial_02..05, the legacy archive path, hash list, move time, and a note that the legacy `frozen_configuration_*`
  fields do not apply;
- `e3proc_counted_trial_ready: false`.

For each manifest, the lines before the appended fields were checked byte-for-byte against its pre-update copy.
`verify_baseline_trial.sh --planned` PASSes for baseline trial_01..05.

**CLIO:** only `clio/trial_01/` exists. It never had a legacy packet, and its `agent-inputs/` is empty. A README and
`e3proc_*` fields were added. *Ambiguity, not resolved by guessing:* if five paired CLIO trials are intended,
`clio/trial_02..05` do not exist yet, and no CLIO runner or procedure exists.

## 4. No completed Example 8 solution in the agent-visible packet
The check covered 121 agent-visible files:
- the control repository at the new pin (fresh clone, `git archive`);
- `globus_source_root/`;
- `chpc_candidate_archive/`;
- baseline trial_01..05 and clio trial_01;
- the E3 loader and modulefiles.

Each file's SHA-256 was compared against every hash in the researcher-only Example 8 records (180 distinct hashes).
There were two kinds of match:
- The empty-file hash, matched by the `.gitkeep` placeholders.
- `geometry_and_loading_figure.png`, the documented problem-statement figure (half domain, mesh, fixed face, load edge,
  symmetry plane; setup report §3 note ²).

No agent-visible file has an Example 8-related name, and no file contains a deck, journal, mesh or job script. No `.i` or
`.jou` file exists outside the candidate archive's Examples 1, 7, 13 and 16. A content scan for Example 8 deck, ground-truth
and source-root names found nothing. The trial manifests and READMEs name the archive location only for trial_01..05,
following the remediation precedent for trial_01, and that location is prohibited and audited. The legacy packets hold the
E1 specification and the manuals, not a solution.

## 5. Remaining blockers before a counted E3 trial
| # | Requirement | Status (2026-10-10) |
|---|---|---|
| 1 | Private Globus source configured and verified | **Open.** No collection, CLI or credentials exist; `E3_GLOBUS_COLLECTION_ID` is empty (`GLOBUS_ACTION_REQUIRED.md`). The alternative is a recorded `posix_readonly_fallback` decision, which has not been made. |
| 2 | Non-scored compute-node qualification of the staging path and `$SLURM_TMPDIR` | **Open.** Not run (`COMPUTE_NODE_QUALIFICATION_ACTION_REQUIRED.md` §2 (a)–(f); the sandbox probe (g) is now optional). |
| 3 | Pinned Claude Code 2.1.295 available; headless baseline configuration verified | **Partly verified.** File present, `--version` = 2.1.295, SHA-256 `4503bfe1…f358` unchanged, required flags present (login node, today). Headless `auth status` in an isolated config dir on a compute node has **not** been verified. |
| 4 | Private GitHub control repository readable at the pinned commit | **Verified from the login node:** noninteractive `ls-remote`; fresh clone at `bd0b042` passes `catalog/checksums.sha256`. Compute-node confirmation (access plan item 1) is pending. |
| 5 | Final agent-visible packet and source hashes frozen | **Open.** The current pin is `bd0b042`, and the collection manifests verify. Recording a Globus collection ID will need a new catalog commit and pin. The open decision on the account name in the runtime copies' `PROVENANCE.md` (remediation §12 item 6) must also be settled. |
| 6 | Every intended counted trial has a clean, unambiguous agent-input location | **Done for the existing directories** (baseline trial_01..05, clio trial_01). **Open:** confirm the intended CLIO trial count (§3). |
| 7 | Standard Morphorm/Cubit environment and licence work in the ordinary planned job environment | **Open.** The E3 loader and runtime copies are kept and pinned. Licence and runtime must be confirmed on a compute node (`COMPUTE_NODE_QUALIFICATION_ACTION_REQUIRED.md` §2a, new). The sandbox licence gap is no longer a blocker. |
| 8 | Baseline and CLIO procedures, prompts, permissions, storage access, cache policy and evidence collection frozen and documented | **Baseline:** documented and updated (prompt `63f84f79…1c20`, pin `bd0b042`, access model); the final freeze waits on items 1, 5 and 7. **CLIO:** no runner or procedure exists, so this is open. |

Technical ground-truth isolation is **not** on this list.

## 6. Automation changes (no launch performed)
- **`run_baseline_e3_trial.sh`:**
  - requires `E3_ACCESS_MODEL=procedural_researcher_only`;
  - adds an `access_model` check line;
  - records `access_model` and `sandbox_used: false` in the launch plan and session record;
  - header states the model.
- **No sandbox requirement:** the runner never required the sandbox, so none had to be removed.
- **Unchanged behaviour:**
  - pinned binary;
  - fresh workspace;
  - frozen packet only;
  - catalog-guarded sources;
  - fresh `$SLURM_TMPDIR/e3/baseline/<trial_id>`;
  - full records;
  - nothing from Example 8 is copied.
- **`prepare_baseline_trial.sh`:** `trial_context.md` gains an "Access" paragraph, and `preparation.txt` records
  `access_model`.
- **`baseline_e3_config.env`:** `E3_CONTROL_COMMIT=bd0b042…` (earlier values kept in a comment) and `E3_ACCESS_MODEL`.
  The `.example` file gains `E3_ACCESS_MODEL`.
- **`baseline_e3_prompt.md`:** byte-identical to `task/task_prompt.md` at `bd0b042`. It adds an explicit prohibition of
  researcher-only records, other trials and experiments, original software and source trees, completed reference
  material, and scoring and validation records. It also says that every path used is audited.
- **`audit_boundary.sh`:** new §6 scans `jobs/`, `outputs/run_logs/` and job logs in `logs/` (session records excluded):
  - a forbidden absolute path → FAIL;
  - a restricted name → REVIEW.
- **Tests:**
  - scratch trees under `E3_ROOT_OVERRIDE`: clean → PASS, planted ground-truth path in a job script → FAIL, Example 8
    name in a job log → REVIEW;
  - real-tree `--dry-run` on trial_01/02: stops at `globus_not_configured` as expected and writes nothing;
  - dry run with a scratch fallback config on trial_03: all checks PASS, and the plan shows the new pin, prompt hash and
    access model;
  - `bash -n` on every script;
  - `verify_readonly_sources.sh --with-originals`: PASS (30 + 5 originals; collections PASS; archive 0 write bits).
- **Runtime:** the E3-local Morphorm/Cubit runtime copies, loader, modulefiles and pinning records are unchanged. No
  credential, token or licence content was written anywhere.

## 7. GitHub
- Repository: `DaisyQuach/daisy-e3-distributed-context-control` (SSH `git@github.com:DaisyQuach/daisy-e3-distributed-context-control.git`).
- New commit **`bd0b042de8bd38fe1149e9fc64aea832beb1bf3c`** (parent `c3b8736`), pushed. `git ls-remote` shows `main` = `bd0b042`.
- Privacy: the API reports `private: true`, `visibility: private`, and an unauthenticated API request returns HTTP 404.
- **Files changed:**
  - `README.md`;
  - `task/task_prompt.md`;
  - `protocol/access_rules.md`, `staging_rules.md`, `provenance_requirements.md`;
  - `catalog/permitted_storage_catalog.yaml` (version 3, `access_model`);
  - all five artifact cards (`access` field);
  - `catalog/checksums.sha256` (regenerated; covers every tracked file).
- **Unchanged:** the frozen specification, deliverables and packages.
- **Pre-commit scan:** no manuals or binaries; no Example 8 or ground-truth names; no researcher-only, E1/E2 or
  `ThesisExperiments` paths; no account name; no credentials or tokens; no licence or scoring material.

## 8. Protected trees unchanged; nothing executed
`find -printf '%p %y %s %m %T@ %C@'` snapshots were taken at 02:18:22Z (before any write) and 02:26:30Z, and compared
line by line:

| Tree | Entries before / after | Differences |
|---|---|---|
| `Thesis/runs/E1_uninterrupted_example8` | 1757 / 1757 | 0 |
| `Thesis/runs/E2_interrupted_recovery_example16` | 2659 / 2659 | 0 |
| `ThesisExperiments` (stat only) | 39897 / 39897 | 0 |
| `Morphorm_Full_Examples_Tests` | 1255 / 1255 | 0 |
| `Morphorm_ground_truth` (stat only; never opened) | 1073 / 1073 | 0 |
| `Morphorm` (source/docs) | 130855 / 130855 | 0 |
| `morphorm_manuals` | 4 / 4 | 0 |
| `Thesis/common` | 36 / 36 | 0 |
| `Thesis/researcher_only` | 1599 / 1599 | 0 |

**Nothing was executed:** no agent session, no Morphorm, no Cubit, no Slurm submission, and no new sandbox test. Read-only
use of other trees: `Thesis/automation/AUTOMATION_LIMITATIONS.md` was grepped for the E1/E2 wording, and nothing else
outside E3 was opened.

**Deletions:** there were none. `rm -rf`, `git reset` and `git checkout` were not used. The pin was verified by
`git archive` in a fresh scratchpad clone.

**Disclosures:**
- I edited `automation/audit_boundary.sh` before copying it. The pre-edit file was rebuilt by reversing the edit, and its
  SHA-256 equals the remediation record `0a047870…db80`. It is stored with the other backups, but its mtime is not the
  original.
- The Claude Code harness saved two oversized tool outputs to its own session store under the account home, a path that
  contains the account name. I read one of them. I created no such path myself, and no E3 record contains the account
  name.

## 9. Records of this update
- **Pre-update copies of all 29 edited files:** `setup/preexisting_state/procedural_access_update_pre/` (relative paths
  preserved), with `procedural_access_update_pre.sha256`.
- **Changed-path list and SHA-256 of every created or edited file:** `setup/procedural_access_update/`.
- **Status sections:** an update notice heads `E3_SETUP_REPORT.md` and `E3_REMEDIATION_REPORT.md`, and superseded
  statements are marked inline. Status updates were also added to:
  - `GROUND_TRUTH_ISOLATION_ACTION_REQUIRED.md`;
  - `COMPUTE_NODE_QUALIFICATION_ACTION_REQUIRED.md`;
  - `access_qualification_plan.md` (item 7 redefined; pin `bd0b042`);
  - `permissions_audit.md` and `permissions_audit_remediation.md`;
  - `researcher_only/README.md` and `researcher_only/evaluation/E3_SCORING_SCOPE.md` (§5);
  - `README.md`, `automation/README.md`, `automation/baseline/README.md`, `automation/environment/README.md`;
  - `automation/sandbox/README.md` and `sandbox_validation_plan.md`;
  - `clio/README.md`.
- **Left unchanged as evidence:** `automation/sandbox/validation_record_login_node.txt`.
