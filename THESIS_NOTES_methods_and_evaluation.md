# Thesis notes: methods and evaluation for E1–E3, Claude Code baseline vs CLIO

*Written 2026-10-11 as source material for the thesis methods, evaluation and results chapters; **updated 2026-10-13 with the
official (counted) CLIO results**. The pre-update version is `.THESIS_NOTES_methods_and_evaluation.pre_official_20261013.md`.*

- **Baseline (Part A):** the completed Claude Code baseline as it was run. Sources are in `Thesis/`, read-only.
- **CLIO (Part B):** the CLIO arm as it was configured and run (planned 2026-10-11, run 2026-10-13).
- **Official results (Part C):** all 15 counted CLIO trials accepted; CLIO vs baseline statistics, excluded attempts, caveats.
- **Placeholders:** the `⟨…⟩` names below were the open decisions in the plan. They are now resolved (values in
  `Thesis/automation/clio/clio_trial_config.env`) and are kept in the text as names for these settings.

| Placeholder | Meaning | Official value (counted trials) | Value seen in the pilots |
|---|---|---|---|
| `⟨CLIO_DESKTOP_VERSION⟩` | CLIO Desktop version. Used for observation only; never connected during a trial | not connected during trials | — |
| `⟨CLIO_CORE_VERSION⟩` | clio-core (iowarp-core) runtime version | iowarp-core 2.2.1 (private daemon per session) | 2.2.1 (shared daemon) |
| `⟨CLIO_AGENT_VERSION⟩` | clio-agent (service/API) version | 0.9.5b5.post2 | 0.9.5b5.post2 |
| `⟨BLUEPRINT_ID⟩@⟨BLUEPRINT_VERSION⟩` | Agent blueprint | **factorio-flat@0.5.0** (frozen copy of the pilot-validated hpc.2 variant; tree checksum `6076c026…e56075`) | factorio-flat@0.4.0; factorio-flat-hpc@0.4.0-hpc.1 / hpc.2 |
| `⟨CLIO_RUNTIME_TUNING⟩` | Idle-reap TTL / tool-call timeout / turn watchdog | 3600 / 3600 / 5400 s | same (CLIO defaults 15 / 600 / 900) |

---

## Part A: Baseline methods and evaluation (completed)

### A1. Study design
**Controlled study** (`Thesis/EXPERIMENTAL_DESIGN.md`): three experiments on frozen Morphorm topology-optimization workflows. Each experiment has five counted trials per system.

| | E1 uninterrupted | E2 interrupted recovery | E3 disparate storage |
|---|---|---|---|
| Workflow | Morphorm Examples Manual §7.2.8 **Example 8**: half cantilever, Helmholtz filter with a symmetry plane, 48×24×12 HEX8, OC optimizer, 50 iterations | §7.2.16 **Example 16**: full cantilever, 48×24×24 HEX8. Stage 1 = 20 iterations with a restart file; Stage 2 = 40 more iterations from the saved `control` design | Example 8, same frozen scientific formulation as E1 |
| Question | Can an agent build and complete the frozen workflow from the specification alone, headless? | Can a completely fresh process recover the workflow state from the persistent workspace and continue correctly? | Does a distributed-context deployment change workflow construction and completion? The documentation, specification and related examples are spread over a GitHub control repository, a private Globus collection and a read-only POSIX archive, and must be staged to node-local scratch |
| Sessions per trial | 1 | 2: Session A (Stage 1 only), then a **new** Session B | 1 |
| Frozen configuration | `FROZEN-EX8-v1` (sha256 `cf15ac52…0b4d`) | `FROZEN-EX16-v1` (`a67d6cba…a86b`) | `E3-SPC-v1`; control repo `DaisyQuach/daisy-e3-distributed-context-control` @ `62954055…` (catalog v5) |
| Reference | Example 8: symmetry-honored variant, F50 = **104470.1** (job 16154330). The canonical run without the symmetry plane gives F50 = 146898.5 (16154329) | Example 16: Stage 1 F20 = 236004.0 (16154332); restart from iteration 20 gives F40 = **213558.4** (16154333). The shipped restart from iteration 19 gives 213684.3 (16154334) | Same as E1 |

**Primary outcome.** Researcher-only scientific scoring against a predeclared acceptance specification: `accepted`, `rejected` or `needs_review`. A process that exits is never counted as a success by itself.

**Descriptive only.** Tokens, cost, turns and tool calls are audit metadata, not performance measures.

**Scope of inference.** n = 5 per experiment characterizes this configuration on these workflows. It does not establish general superiority.

### A2. Frozen, agent-visible packets (`Thesis/common/frozen_example8`, `frozen_example16`)
**Files in each packet:**
- `formal_configuration.md`: ID, model, harness, runtime and Cubit hashes, resources, network policy and fresh-session policy.
- `scientific_problem_specification.md`: the locked workflow.
- `compute_resources.md`: Slurm contract for the Morphorm jobs and the agent host.
- `software_contract.md`: the approved loader `common/scripts/load_approved_software.sh` (Morphorm, plus Cubit `cubit-edu/2026.8`).
- `workspace_rules.md`: write boundary, locked deliverable paths, and network policy. Network policy allows "model-provider communication and CHPC scheduler/module access only; no web search".
- `provenance_requirements.md`: required contents of `work/run_summary.md` and the manifests.
- `acceptance_visibility_boundary.md`: no scoring criteria or reference material is visible to the agent.
- `manuals/`: User Manual and Theory Manual PDFs. The Examples Manual is never included.
- `FROZEN_CONFIG_ID.txt`, `FROZEN_CONFIG_SHA256.txt` and `FROZEN_CONFIG_FILES.sha256`.

**Prompts:**
- E1 `task_prompt.md`: read every input, build mesh/deck/translation, verify, submit 50 iterations through Slurm, wait, verify, place deliverables plus a SHA-256 manifest, record everything in `work/run_summary.md`; on a blocker, preserve state and stop.
- E2 `session_a_prompt.md`: Stage 1 only, then stop.
- E2 `recovery_prompt.md`: a fresh process with "no record of any earlier process" infers the state from the workspace and continues. It is checked to contain no stage labels, filenames or iteration hints.
- E3: the prompt is `task/task_prompt.md` at the pinned commit (`baseline_e3_prompt.md`, byte-identical).

**Controls locked in the packets:** mesh resolution, set names, symmetry treatment, load placement, SIMP floor and exponent, filter, optimizer, iteration counts, deliverable names, software interface, Slurm resources, model, harness version, prompts and network policy.

### A3. Baseline system
- **Harness:** Claude Code **2.1.295**, pinned at `$HOME/.local/share/claude/versions/2.1.295`. The researcher decided 2026-10-09 to repin because 2.1.292 was not installed.
- **Model:** `claude-fable-5-1`. Effort is the harness default; none is set.
- **Exact headless command:**
  `claude --print --verbose --output-format stream-json --model claude-fable-5-1 --dangerously-skip-permissions --session-id <uuid> --disable-slash-commands --no-chrome -- "<prompt>"`.
  `--resume`, `--continue` and `--fork-session` are forbidden and checked for.
- **Environment:**
  - inherited `CLAUDE*` variables are scrubbed;
  - `DISABLE_AUTOUPDATER=1`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`;
  - a per-session `CLAUDE_CONFIG_DIR` at `Thesis/.agent_runtime/<run_id>/<label>/claude_config`, holding a credential copy (removed at session end) and a minimal `.claude.json`;
  - `THESIS_TRIAL_ID`.
- **Agent host:** an `sbatch --wait` job per session with `--account/partition=hochhalter-np --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=32G --time=02:00:00`. Session limit is 6600 s (1 h 50 min), leaving time for evidence capture. The agent submits its own Morphorm and Cubit jobs with `sbatch`.
- **Access model:** procedural. Researcher-only material is never in agent-visible text, and every transcript is audited after the fact. It is not enforced by file permissions, because the agent runs as the same Unix user.
- **Built-in tools:** Claude Code 2.1.295 exposed its built-in tools, including WebSearch and WebFetch (seen in the stream `init` event). `mcp_servers` was empty, and the network policy forbade web use.

### A4. Trial lifecycle (automation in `Thesis/automation/`; E3 in `runs/E3_disparate_storage_example8/automation/`)
1. `prepare_trial.sh` creates a planned packet:
   - copies `agent_inputs/` from the frozen configuration and makes it read-only;
   - writes `manifest.yaml` with status `planned`, the frozen hash and null outcome fields.
2. `preflight.sh` makes no model call. It checks:
   - the pinned executable and its version, and the headless flags parsed from `--help`;
   - `auth status`, scheduler and partition;
   - the approved software and runtime hash, and the frozen-configuration hashes;
   - no `CLAUDE.md` in any ancestor directory, and no researcher-only references in agent-visible text.
3. `run_e1_baseline.sh` / `run_e2_baseline.sh`. The order is: preflight → planned-packet verification → launch → collect → completed-packet verification → manifest status. Status lifecycle:
   - `planned` → `running`. E2 instead goes `running_session_a` → `paused_after_session_a` → `running_session_b`.
   - The run then ends as `completed_unscored`, `ambiguous`, `failed` or `failed_stage1_boundary`.
4. **E2 interlock between sessions.** Session B launches only if all of these hold:
   - Session A has a session record;
   - no trial Slurm jobs are pending or running;
   - `outputs/stage1/engine_output.exo`, `outputs/stage1/morphorm_oc_optimizer_diagnostics.txt` and `work/run_summary.md` exist;
   - `outputs/stage2/` is empty.

   Session B is a new process with a new UUID and its own config directory. Session A's records sit in `researcher_only/session_evidence/` until collection, so B sees only the workspace.
5. `collect_baseline_evidence.sh` copies the session evidence into `logs/agent_sessions/<label>/`, then:
   - writes `logs/slurm_sacct.psv` for the agent-host and workflow jobs, and `logs/evidence_SHA256SUMS.txt`;
   - fills the manifest ids and timestamps;
   - never overwrites anything.
6. `verify_trial_packet.sh --completed` checks:
   - all locked deliverables (13 for E1, 19 for E2), that `outputs/SHA256SUMS.txt` verifies, job ids and sacct;
   - session-record count, distinct session ids, no resume, isolated config, executable version equal to the pin, rc 0 with no timeout;
   - a **boundary audit** that greps transcripts and streams for restricted paths, with the session's own config dir blanked out;
   - for E2, session order and that the Stage-2 deck is newer than the end of Session A.
7. `score_researcher_only.sh` does the scientific scoring; see A5.
8. **Replacement policy.** A trial aborted for a non-agent cause (provider usage limit, OAuth expiry) is kept and excluded, and replaced by `trial_NNR`. Attempts are never rerun in place.
9. **E3 additions** (`run_baseline_e3_trial.sh`, run inside the allocation):
   - noninteractive clone of the control repository at the pin into `$TMPDIR`; only `README.md task/ catalog/ protocol/ scripts/` is copied into `agent-inputs/control/`;
   - `trial_context.md`, `permitted_roots.txt` and `globus_access.txt`;
   - Globus is mandatory (the POSIX fallback is refused), with node-local staging at `$TMPDIR/e3/<system>/<trial_id>`;
   - `audit_boundary.sh` classifies every path in tool calls, job scripts and job logs (FORBIDDEN → FAIL);
   - `verify_readonly_sources.sh`, then `verify_baseline_trial.sh --completed` (36 checks).

   The agent records:
   - `provenance/sources_searched.tsv`;
   - `artifact_selections.md`;
   - `staging-manifest/staged_files.tsv` and `returned_files.tsv`;
   - `node_local_placement.txt`.

   Trials ran one at a time.

### A5. Evaluation

**Scientific scoring** (`researcher_only/ground_truth/tools/score_trial.py`; specs `ACCEPT-EX8-v1`, `ACCEPT-EX16-v1.1`). E3 used the E1 scorer and spec.

- **Inputs:** the `run_id` from the manifest; `logs/packet_verification.json` (`failed` → rejected, `ambiguous` or missing → needs_review); deliverables at the locked paths (a glob fallback gives needs_review, nothing found gives rejected).
- **Comparability checks:**
  - Mesh: element and node counts, `block_1`, HEX8, bounding box, `ns_fix`/`ns_load` sizes, sidesets (`ss_sym` for Example 8).
  - Generated configuration: `check_generated_config.py`. For Example 8, `Symmetry Plane Sides` must be present in the Helmholtz deck.
  - Iteration count: Example 8 reaches 50. Example 16: Stage 1 reaches 20, the checkpoint has 21 states with `control` and `topology`, and Stage 2 reaches local iteration 40.
- **Scientific metrics:**
  - Compliance history against the reference (`max_rel_diff_compliance`, `final_rel_diff_compliance`).
  - Final nodal `Topology` field, matched by node coordinates (`max_abs_diff`, `mean_abs_diff`).
  - Example 16 continuation: the Stage-2 initial control field must match a saved Stage-1 state to ≤1e-12. A match at iteration 20 is `manual_semantics_iteration_20`.
- **Tolerances:**

  | Quantity | Accept | Review |
  |---|---|---|
  | Final compliance (relative) | 1e-6 | 1e-2 |
  | Density (max abs) | 1e-6 | 0.05 |

  Between the accept and review limits → needs_review; above the review limit → rejected.
- **Reference policy:** Example 8 = `symmetry_honored_variant`; Example 16 = `manual_semantics_iteration_20`.
- **Decision rule:** any rejected reason gives rejected; otherwise any review reason gives needs_review; otherwise accepted.
- **Outputs:**
  - `researcher_only/scores/<run_id>/score.{json,md}`;
  - figures `researcher_only/evaluation_figures/<run_id>_final_iteration{50,60}_vs_<variant>.png`;
  - only the decision word goes into the manifest.

**Descriptive telemetry** (`researcher_only/evaluation_figures/thesis_prelim/analysis/build_dataset.py`, `combined_E1_E2_E3/`):

| Metric | Source |
|---|---|
| Wall time | `session_record.json` start/end |
| API time, turns, output tokens, cost | `stream.jsonl` `result` event: `duration_api_ms`, `num_turns`, `usage`, `total_cost_usd` |
| Tool calls and time breakdown | Transcript `tool_use`→`tool_result` timestamps, classified by regex rules. Time not covered by a tool call is "model reasoning & writing" |
| Slurm submit/wait and Morphorm run time | `logs/slurm_sacct.psv` (Denver time converted to UTC) |
| Science | `score.json` |

### A6. Baseline results (all counted trials accepted; final compliance and density differences 0.0)

| | Counted trials | Mean wall (min) | Without Slurm | Slurm submit & wait | Mean API time (s) | Turns | Output tokens | Cost (USD) |
|---|---|---|---|---|---|---|---|---|
| E1 | 01, 02, 03, 05, 04R2 | 22.0 | 12.5 | 9.5 | 717 | 53.2 | 55.7k | 7.98 |
| E2 (A+B) | 01, 02R, 03, 04R, 05 | 68.3 (A 28.7, B 39.6) | 11.6 / 9.6 | 17.1 / 30.0 | 1189 | 84.6 | 103.5k | 13.57 |
| E3 | 01, 03, 04, 05, 02R (`trial_06`) | 30.9 | 13.4 | 17.6 | 699 | 49 | 52.3k | 7.45 (report: 7.40) |

**Excluded attempts.** All are non-agent causes and are kept as evidence:
- **E1-04:** session limit.
- **E1-04R:** Fable limit.
- **E2-02:** Fable limit during Session A, so `failed_stage1_boundary`.
- **E2-04:** session limit before the Stage-1 boundary.
- **E3-02:** OAuth expiry. Its audit was also a false positive on the session's own `claude_config` tool-results path.

**Curation notes:**
- **E1-01:** the session record was rebuilt after a launcher jq bug.
- **E1-04R2:** counted by researcher override. The scorer gave needs_review because packet verification was ambiguous with exit code 1.
- **E2-01:** Session B's exit code 127 came from a wrapper defect (`AUTOMATION_LIMITATIONS.md` §13).

**E3 staging:** 14.8 files per trial on average (12.2 by Globus, 2.6 from the archive) in 13.2 Globus transfers, taking about 66 s.

**Share of wall time spent on model reasoning:** E1 52.9 %, E2-A 37.1 %, E2-B 22.7 %, E3 37.7 %.

### A7. Baseline file tree (annotated; `Thesis/`, checked against the folder on 2026-10-15)
Folders marked † are on CHPC only and are not in the GitHub copy (see `EXCLUDED_FILES.md`).
```
Thesis/
├── README.md  EXPERIMENTAL_DESIGN.md  BUILD_REPORT.md
├── docs/                       README.md, E3_PLAN.md, HEADLESS_CLAUDE_SYNTAX.md, E2_FRESH_SESSION_ENFORCEMENT.md,
│                               VISIBILITY_BOUNDARY.md, CREATED_FILES.txt
├── common/
│   ├── frozen_example8/        FROZEN-EX8-v1 (E1, E3): formal_configuration.md, scientific_problem_specification.md,
│   │                           compute_resources.md, software_contract.md, workspace_rules.md, provenance_requirements.md,
│   │                           acceptance_visibility_boundary.md, task_prompt.md, FROZEN_CONFIG_{ID.txt,SHA256.txt,FILES.sha256},
│   │                           manuals/†
│   ├── frozen_example16/       FROZEN-EX16-v1 (E2): the same packet files, with session_a_prompt.md and recovery_prompt.md
│   │                           instead of task_prompt.md; manuals/†
│   └── scripts/                load_approved_software.sh, hash_frozen_config.sh, capture_environment.sh
├── automation/                 baseline E1/E2 automation (lib/common.sh = frozen constants)
│   ├── preflight.sh  prepare_trial.sh  launch_headless_claude.sh  run_e1_baseline.sh  run_e2_baseline.sh
│   ├── collect_baseline_evidence.sh  verify_trial_packet.sh  score_researcher_only.sh  monitor_jobs.sh
│   ├── run_all_planned_baselines.sh  README.md  AUTOMATION_LIMITATIONS.md  E3_README.md  lib/common.sh
│   └── clio/                   CLIO arm automation (Part B, B7)
├── .agent_runtime/†            per-session runtime state, <run_id>/<session_main|session_a|session_b>/: claude_config/ (baseline;
│                               present for E1 baseline 03–05 incl. 04R/04R2 and all E2 baseline runs), plus clio_home/,
│                               core_state/, bin/ for every E1/E2 CLIO run
├── runs/
│   ├── E1_uninterrupted_example8/
│   │   ├── baseline/trial_01 … trial_05, trial_04R, trial_04R2   (counted: 01, 02, 03, 04R2, 05)
│   │   │   ├── manifest.yaml               run_id, status, frozen hash, ids, curation_*, scoring_*
│   │   │   ├── agent_inputs/               frozen packet (read-only)
│   │   │   ├── work/                       agent's working files; run_summary.md = agent's provenance record
│   │   │   ├── jobs/                       job_ids.txt, sacct_<job>.txt (and, where the agent put them, its sbatch scripts)
│   │   │   ├── outputs/                    locked deliverables + SHA256SUMS.txt
│   │   │   └── logs/
│   │   │       ├── agent_sessions/session_main/   session_record.json, stream.jsonl, transcript_<uuid>.jsonl, result.json,
│   │   │       │                                  launch_{plan.json,command.txt,env.txt}, prompt.md(.sha256), agent_host_*,
│   │   │       │                                  auth_status_isolated_config.json, start/end_utc.txt, exit_code.txt, stderr.log
│   │   │       └── slurm_sacct.psv  evidence_SHA256SUMS.txt  packet_verification.json  slurm-<job>.out/.err
│   │   └── clio/                   CLIO trials (B7)
│   ├── E2_interrupted_recovery_example16/
│   │   ├── baseline/trial_01 … trial_05, trial_02R, trial_04R    (counted: 01, 02R, 03, 04R, 05;
│   │   │                                                          logs/agent_sessions/session_a + session_b)
│   │   └── clio/                   CLIO trials (B7)
│   └── E3_disparate_storage_example8/
│       ├── README.md
│       ├── setup/              E3_SETUP_REPORT.md, CLIO_DEPLOYMENT.md, CLIO_RUNBOOK.md, other reports and action records,
│       │                       source inventory, baseline_execution/ (freeze/, jobs/trial_01–06.sbatch, preflight/,
│       │                       postprocess/, postprocess_r1/, submission manifests), integrity/†
│       ├── automation/         audit_boundary.sh, init_*/record_* helpers, verify_readonly_sources.sh, README.md,
│       │                       baseline/ (run_baseline_e3_trial.sh, prepare/verify/collect, baseline_e3_config.env, baseline_e3_prompt.md),
│       │                       clio/ (run_clio_e3_trial.sh and start_e3_clio_server.sh [2026-10-09, never run],
│       │                       run_clio_e3_trial_v2.sh, collect_clio_metrics.sh), lib/, templates/, sandbox/, environment/†
│       ├── github_control_repo_worktree/  globus_source_root/ (Globus-only)  chpc_candidate_archive/ (read-only)
│       ├── researcher_only/    evaluation/ (E3 scoring scope), example8_reference/, provenance/
│       ├── baseline/trial_01 … trial_06   (counted: 01, 03, 04, 05, 06 = 02R)
│       │                       README.md, manifest.yaml (e3dc_*), TRIAL_STATUS.json, agent-inputs/, work/, jobs/, outputs/,
│       │                       staging-inbox/, staging-manifest/, provenance/,
│       │                       logs/session/ (session_record.json, stream.jsonl, transcript, tool_inputs.jsonl, result.json,
│       │                       launch_*, prompt.md), logs/slurm-<job>.out/.err
│       ├── clio/               CLIO trials (B7)
│       └── .agent_runtime/†    baseline/E3-baseline-trial_01 … 06/ (claude_config/, execution/); clio/E3-clio-trial_02/ only
└── researcher_only/            never agent-visible
    ├── README.md  RESEARCHER_DECISIONS.md
    ├── docs/                   E3/, E3_PLAN.md, HEADLESS_CLAUDE_SYNTAX.md, E2_FRESH_SESSION_ENFORCEMENT.md, VISIBILITY_BOUNDARY.md
    ├── ground_truth/           README.md; example_8/ and example_16/: reference_case/ (acceptance_spec.json, ACCEPTANCE_SPEC.md,
    │                           results/, jobs/, mesh/, inputs/, figures/, reference runs, SHA256SUMS.txt), manual_reference/,
    │                           source_inputs/, SOURCE_AUDIT.md; tools/ (score_trial.py, check_generated_config.py, …)
    ├── batch_logs/             logs of every baseline and CLIO batch (e1_batch_*, e2_*, clio_counted_*, e3_clio_trial_*)
    ├── session_evidence/<run_id>/<label>/    copy of each session's evidence
    ├── scores/<run_id>/score.{json,md}       every counted trial of both arms; E3_baseline_scores_and_telemetry.csv
    └── evaluation_figures/     <run_id>_final_iteration{50,60}_vs_<reference>.png (E1 and E2 both arms, E3 baseline),
                                thesis_prelim/, combined_E1_E2_E3/, E3_baseline_prelim/
```

---

## Part B: CLIO counterparts (set up 2026-10-11, counted trials run 2026-10-13)

### B1. CLIO system under test
| Component | Version | Role in a trial |
|---|---|---|
| CLIO Desktop | `⟨CLIO_DESKTOP_VERSION⟩` = not connected | None. It is not connected to send, answer or grant anything during a counted trial; any human message invalidates the trial. It may be used read-only afterwards to view sessions |
| clio-agent service / API | `⟨CLIO_AGENT_VERSION⟩` = 0.9.5b5.post2 (`clioSessions/CLIOruntime`) | Runs the agent loop (GACT), its tools (shell, file, artifacts, etc.), sessions, traces and the HTTP API on `127.0.0.1:<port>` |
| clio-core runtime | `⟨CLIO_CORE_VERSION⟩` = iowarp-core 2.2.1 | Context/data store daemon. A **private** daemon per session (`CLIO_RUNTIME_STATE_DIR`, `CLIO_CORE_PORT`) |
| LM provider | `claude_code` via claude-agent-sdk 0.2.164 | Drives a Claude Code CLI subprocess. Pinned to **2.1.295**, the baseline harness binary, which is placed first on `PATH`. Without the pin CLIO drives the newest installed CLI (2.1.296 in the pilots); the bundled CLI is 2.1.292 |
| Model | `claude-fable-5-1` | Same as the baseline |
| Agent blueprint | `⟨BLUEPRINT_ID⟩@⟨BLUEPRINT_VERSION⟩` = factorio-flat@0.5.0 (`Thesis/automation/clio/blueprints/factorio-flat-0.5.0/`, deployed into each session's own config) | Attached to the session; id and version are read back and verified |

### B2. Deployment: one fresh CLIO deployment per session
**Where it runs.** Each session runs inside its own agent-host Slurm job, using exactly the baseline contract (sbatch, 1 node, 1 task, 8 CPU, 32G, 2 h, `hochhalter-np`). The CLIO service, the API runner and every tool process run on that compute node, never on a login node. The agent submits its own Morphorm and Cubit jobs, as in the baseline.

**State.** All state lives in `Thesis/.agent_runtime/<run_id>/<label>/`, the baseline's per-session location. For E3 it is `runs/E3…/.agent_runtime/clio/<trial_id>/session_main/`. It contains:

| Path | Contents |
|---|---|
| `clio_home/` | `CLIO_AGENT_HOME`: config copied from the installed user config minus `workspaces.json`, with no prior workspaces, sessions, memory or traces. `mcp.yaml` has no servers |
| `claude_config/` | Isolated `CLAUDE_CONFIG_DIR`, built like the baseline's: credential copy plus minimal `.claude.json`. The credential copy is removed at session end |
| `core_state/` | The private clio-core daemon |
| `bin/claude` | Points to Claude Code 2.1.295 |

**Environment** (recorded in `launch_env.txt`):
- inherited `CLAUDE*` and `CLIO*` variables are scrubbed;
- `CLIO_BIN_DIR`, `CLIO_NO_UPDATE_CHECK=1`;
- `CLIO_ALLOWED_ROOTS` = trial root : CLIO home : `$TMPDIR`;
- `CLIO_STREAM_AUDIT_LOG`;
- `⟨CLIO_RUNTIME_TUNING⟩`: `CLIO_CLAUDE_CODE_STREAM_IDLE_TTL_S`, `CLIO_MCP_CALL_TIMEOUT_S`, `CLIO_GACT_TURN_TIMEOUT_S`;
- `DISABLE_AUTOUPDATER=1`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`, `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`;
- `THESIS_TRIAL_ID`;
- for E3 only: `E3_TRIAL_ID`, `E3_TRIAL_ROOT`, `E3_STAGING_DIR` and `E3_SYSTEM=clio`.

**E2 sessions.** Session B gets a **new deployment in a new agent-host job**. Sessions A and B share only the trial workspace; in the baseline they shared only the workspace too, since each had its own process and config directory.

### B3. API procedure per session (`Thesis/automation/clio/lib/clio_session_runner.py`; stdlib HTTP against `127.0.0.1:<port>`)
1. `GET /v1/health`. It must be healthy; the only non-ready item allowed is `sandbox` (kernel too old). The runner waits up to 180 s for `lm_provider` to be ready.
   It also saves `/openapi.json`, `/v1/settings/runtime`, `/v1/capabilities` and `/v1/session-defaults`, and checks `GET /v1/sessions` is empty (a fresh deployment).
2. `POST /v1/workspaces` with `root_path` = the trial root.
3. `POST /v1/sessions` with `model={provider_id: claude_code, model_id: claude-fable-5-1}`, `mode=edit` and `approval_mode=bypass`. No effort is set by default (see B4).
4. `POST /v1/sessions/{sid}/agent-blueprint` with `⟨BLUEPRINT_ID⟩`.
5. `PATCH` the session to re-assert approval, model and metadata, then `GET` it back. Model, provider, approval, effort, blueprint id and **version** must all equal the configuration; otherwise nothing is sent.
6. Write `configuration_freeze.json`.
7. Start SSE capture of `/v1/sessions/{sid}/events` into `stream.jsonl`.
8. `POST /v1/sessions/{sid}/messages` with the **frozen prompt file verbatim** (no banner) and `behavior={execution_mode: execute, confirmation_policy: bypass}`. A message without `confirmation_policy` falls back to `ask`.
9. Poll every 15 s:
   - `idle` after running → `finished_idle`;
   - `waiting_permission` or `waiting_user` → cancel. These are never answered, because a headless baseline could not answer either;
   - `error` or `cancelled` → end;
   - 6600 s reached → cancel (`timeout`).
10. Export the session record: transcript and full export, messages, trace, interactions, questions, attempts, agent tasks, execution provenance, final blueprint and permissions.

### B4. Parity with the baseline
| Aspect | Baseline (Claude Code) | CLIO (planned) | Status |
|---|---|---|---|
| Packet / `agent_inputs` | Frozen packet, `prepare_trial.sh` | Same copy commands and frozen hash (`prepare_clio_trial.sh`); byte-identical, verified | identical |
| Prompt | Prompt file as the CLI argument | Same file as the only user message, verbatim | identical text |
| User messages | 1 per session | 1 per session (`CLIO_MAX_NUDGES=0`). The pilots allowed up to 4 nudges | identical (decision) |
| Model | claude-fable-5-1 | claude-fable-5-1 | identical |
| Claude Code CLI binary | 2.1.295 | 2.1.295 driven by CLIO's provider (PATH pin; recorded and verified per session) | identical binary; different harness around it (by design) |
| Effort | CLI default | none sent → CLI default (`CLIO_EFFORT=default`). The pilots used `high` | identical (decision) |
| Permissions | `--dangerously-skip-permissions` | `approval_mode=bypass` on the session and the message; nothing answered | equivalent |
| Agent host | sbatch 8 CPU / 32G / 2 h | Same contract (shared constants) | identical |
| Session limit | 6600 s | 6600 s (runner cancels) | identical |
| Fresh session | New process, UUID, `CLAUDE_CONFIG_DIR` | New deployment (CLIO home, Claude config, core daemon), new workspace and session | equivalent |
| Memory | Auto-memory off | Auto-memory off; CLIO memory starts empty per deployment; memory/recall calls audited (E3) | equivalent |
| Web / network | No MCP; built-in WebSearch/WebFetch present but forbidden by policy | No user-configured MCP servers (`CLIO_MCP_POLICY=none`, empty `mcp.yaml`). **Correction 2026-10-13:** the factorio-flat blueprint declares its own web MCP (`web: clio-kit mcp-server web`), so one web tool (`web_fetch`) was mounted in every counted session (45 tools offered) | equivalent: a web tool present but forbidden in both arms; neither arm ever called one (baseline transcripts show only Bash and a single Read; CLIO only `shell_bash` and `load_skill`) |
| Tools and system prompt | Claude Code built-ins | CLIO tools plus the blueprint's experts and skills | **differs by design: the independent variable** |
| Scoring / verification | `score_researcher_only.sh`, `verify_trial_packet.sh` | The same scripts, unchanged, plus a CLIO supplement | identical |
| Evidence layout | `logs/agent_sessions/<label>/…` | The same files and names plus `clio/` | identical, extended |

### B5. Telemetry collected "in the same manner"
| Baseline record | CLIO record (same path/name) | Origin |
|---|---|---|
| `session_record.json` | Same keys (`session_id`, `executable_version` = the Claude CLI version seen, `config_dir`, `exit_code`, `timeout_hit`, `resume_used`, …) plus `clio_agent_version`, `end_reason`, `effective_session_settings`, `user_messages_in_session`, `clio_core` | launcher |
| `stream.jsonl` (stream-json) | `stream.jsonl` (CLIO SSE events, one JSON per line) | runner |
| `transcript_<uuid>.jsonl` | `transcript_<sdk-session-id>.jsonl`: the Claude Code transcripts CLIO's provider wrote in the isolated config dir | usage collector |
| `result.json` (`num_turns`, `usage`, `total_cost_usd`, `duration_ms`) | `result.json`, same keys: `usage` includes cache reads and writes; `total_cost_usd` is recomputed at list price; `num_turns` = Claude API calls; `duration_api_ms` = null | usage collector |
| `launch_plan.json`, `launch_command.txt`, `launch_env.txt`, `prompt.md(.sha256)`, `agent_host.sbatch`, `agent_host_sacct.psv`, `auth_status_isolated_config.json` | Same | launcher |
| `logs/slurm_sacct.psv`, `logs/evidence_SHA256SUMS.txt`, manifest ids | Same (baseline collector, unchanged) | collector |
| — | `clio/`: configuration freeze, health, runtime settings, blueprint, API exports, `usage_per_call.csv`, `usage_summary.json` (cache writes, full re-sends, **stream-audit reset reasons**, idle reaps), runner events and poll log | CLIO-only |

The analysis builder (`build_dataset.py`) can read CLIO trials from the same files. Two fields differ in meaning and need a mapping:
- `num_turns`: API calls for CLIO, agent turns for the baseline;
- `duration_api_ms`: not available from CLIO.

### B6. Run procedure and status (as planned 2026-10-11; see the 2026-10-13 update at the end of this section)
**Packets:**
- E1 and E2: `runs/E1…/clio/trial_01–05` and `runs/E2…/clio/trial_01–05`, planned 2026-10-11. Run ids `E1-example8-clio-NN` and `E2-example16-clio-NN`; paired blocks `E1-NN` and `E2-NN`.
- E3: `runs/E3…/clio/trial_01–05` (existing, with `e3clio2_*` fields appended).

**Commands:**
- E1/E2:
  1. `preflight_clio.sh`;
  2. `run_e1_clio.sh` / `run_e2_clio.sh --trial N --execute-counted`;
  3. `../score_researcher_only.sh --trial-dir …/clio/trial_NN --figures`.
- E3: `sbatch … run_clio_e3_trial_v2.sh --trial-dir …/clio/trial_NN --execute-counted`, then the E3 scoring procedure (E1 scorer plus the verification adapter, as in `setup/baseline_execution/postprocess`).

**Blocking decisions** (counted runs refuse until they are set in `clio_trial_config.env`):
- `⟨CLIO_AGENT_VERSION⟩`, `⟨CLIO_CORE_VERSION⟩`, `⟨CLIO_DESKTOP_VERSION⟩`;
- `⟨BLUEPRINT_ID⟩@⟨BLUEPRINT_VERSION⟩`.

**Pre-filled decisions** (reconfirm before counted runs):
- runtime tuning (3600 / 3600 / 5400; set 15 / 600 / 900 to test stock CLIO);
- effort `default`, nudges 0, MCP `none`, private core daemon.

**Other researcher decisions:**
- Trial order and pairing with the baseline: sequential, like the baseline.
- How to handle a provider usage limit: the baseline replacement policy (`--suffix R`).

**Validation done (no counted trial):**
- dry runs of the E1, E2 and E3 runners;
- a compute-node deployment check without model calls;
- one $0.47 end-to-end smoke session on a scratch packet copy outside `Thesis/`.

The CLI pin, the blueprint read-back and the evidence pipeline worked, and the baseline verifier and CLIO supplement ran on the result. Records: `clioSessions/CLIO_E1_API_pilots/thesis_clio_deploy_validation_20261011T234016Z/`.

**Update 2026-10-13: how the counted trials were actually run.**
- Decisions filled in `clio_trial_config.env`: clio-agent 0.9.5b5.post2, iowarp-core 2.2.1, Desktop not connected,
  blueprint factorio-flat 0.5.0 (frozen copy, `blueprints/factorio-flat-0.5.0.PROVENANCE.md`), tuning 3600 / 3600 / 5400 s,
  effort default, 0 nudges, MCP none, private clio-core, stream audit on. A no-model deployment check on a compute node
  (`thesis_clio_deploy_validation_20261013/`) passed first.
- Driver: `Thesis/automation/clio/run_counted_thesis_clio.sh` ran E1 trials 1–5, then E2 1–5, then E3, one trial at a time,
  each scored right after it ended (E1/E2: `score_researcher_only.sh`, unchanged; E3: `score_e3_clio.sh`, the E3 baseline's
  recorded scoring procedure). Before each trial a one-line Fable call checked that the provider accepted calls.
- Replacements followed the baseline policy (`prepare_clio_trial.sh --suffix R`, or a new trial directory for E3 as the
  baseline did with 02R = `trial_06`); wrappers in `clioSessions/CLIO_E1_API_pilots/official_thesis_clio/`
  (`resume_with_replacement.sh`, `run_e3_remaining.sh`, `run_e3_remaining2.sh`), logs in `researcher_only/batch_logs/`.
- Two automation fixes made between trials (pre-change copies kept next to the scripts):
  1. `run_clio_e3_trial_v2.sh` now exports `E3_ALLOW_ACCOUNT_NAME_IN_TMPDIR` exactly as the baseline runner does (its
     absence stopped E3 trial_01 before launch).
  2. **E3 own-runtime audit rule** (researcher decision 2026-10-13): the shared E3 boundary audit (`audit_boundary.sh`,
     unchanged) flags any read outside the trial root. A CLIO agent necessarily reads its own blueprint skills
     (`<clio_home>/config/agent-blueprints/<bp>/`) and its own session's tool-output spill files
     (`<clio_home>/state/workspaces/*/tool-output/<session id>/`). `automation/clio/lib/e3_own_runtime_audit.py` re-labels
     only those lines as `OWN_RUNTIME`, keeps the shared audit's output unchanged in `provenance/boundary_audit.shared.txt`,
     and recomputes the verdict with the shared rules; every other forbidden path still fails. This is the CLIO analogue of
     the baseline E3-02 false positive on the session's own `claude_config` tool-results path. Documented in
     `runs/E3…/clio/README.md`.
- Session times (UTC, 2026-10-13, from `session_record.json`): E1 03:04–06:10 (incl. 03R); E2 06:12–10:51, then 05R
  14:35–15:49 after a re-login; E3 trial_02 15:59–16:30 (excluded), counted 03–07 17:17–19:51.

### B7. CLIO file tree (new or changed in `Thesis/`; checked against the folder on 2026-10-15)
Folders marked † are on CHPC only and are not in the GitHub copy.
```
Thesis/README.md  Thesis/automation/README.md          CLIO sections added (pre-change copies in automation/clio/_pre_update_20261011/)
Thesis/automation/clio/
├── README.md  clio_trial_config.env                   pins/decisions (filled in 2026-10-13)
├── prepare_clio_trial.sh  preflight_clio.sh  launch_clio_session.sh
├── run_e1_clio.sh  run_e2_clio.sh  run_all_planned_clio.sh
├── run_counted_thesis_clio.sh  score_e3_clio.sh       (2026-10-13: counted driver, E3 scoring)
├── collect_clio_evidence.sh  verify_clio_supplement.sh
├── blueprints/  factorio-flat-0.5.0/  factorio-flat-0.5.0.PROVENANCE.md  factorio-flat-0.5.0.SHA256SUMS.txt
├── lib/  clio_common.sh  clio_session_runner.py  clio_usage.py  e3_own_runtime_audit.py (2026-10-13)
└── _pre_update_20261011/  automation_README.md  Thesis_README.md  clio_trial_config.env.pre_counted_20261013
Thesis/runs/E1_uninterrupted_example8/clio/       README.md  README.pre_20261011.md  trial_01 … trial_05, trial_03R (03 excluded)
Thesis/runs/E2_interrupted_recovery_example16/clio/   README.md  README.pre_20261011.md  trial_01 … trial_05, trial_05R (05 excluded)
    trial_NN/  manifest.yaml (system: clio, clio_* fields)  agent_inputs/ (frozen, read-only)  work/  jobs/  outputs/
               logs/  slurm_sacct.psv  evidence_SHA256SUMS.txt  clio_evidence_SHA256SUMS.txt  packet_verification.json
                      clio_supplement_verification.json  slurm-<job>.out/.err
                      agent_sessions/<session_main | session_a + session_b>/  the baseline-named records (session_record.json,
                         stream.jsonl, transcript_<id>.jsonl, result.json, launch_*, prompt.md, agent_host_*, …) + clio/
Thesis/runs/E3_disparate_storage_example8/
├── automation/clio/  run_clio_e3_trial_v2.sh (new, used)  README.md  (v1 run_clio_e3_trial.sh, start_e3_clio_server.sh kept)
├── clio/  README.md (v2 + 2026-10-13 notes)
│          _pre_update_20261011/  README.md  README.pre_20261013.md  trial_01 … trial_05 (earlier planned packets, superseded)
│          trial_01 … trial_07  (counted: 03–07; 01 aborted before launch, 02 excluded)
│              README.md  manifest.yaml (e3dc_*, e3clio2_*)  agent-inputs/  work/  jobs/  outputs/  staging-inbox/
│              staging-manifest/  provenance/ (incl. boundary_audit.shared.txt)
│              logs/session/  session_record.json, stream.jsonl, transcript_<id>.jsonl, export.json, messages.json,
│                             tool_inputs.jsonl, result.json, launch_*, prompt.md, clio/
└── .agent_runtime/†clio/  E3-clio-trial_02/ only
Thesis/.agent_runtime/†<run_id>/<label>/{clio_home, claude_config, core_state, bin}   E1/E2 CLIO deployments
Thesis/researcher_only/session_evidence/<run_id>/<label>/                             copy of each session's evidence
Thesis/researcher_only/scores/<run_id>/                                               E1-example8-clio-*, E2-example16-clio-*, E3-clio-03 … 07
Thesis/researcher_only/batch_logs/   clio_counted_*.log, clio_replacement_*.log, clio_e3_*.log, e3_clio_trial_*.out
```
Outside `Thesis/`: the analysis (`official_aggregate.py`, `official_compare.py`, `official_observability.py`, `data/`,
`figures/` H1–H6, `observability/`, batch wrappers) is `clioSessions/CLIO_E1_API_pilots/official_thesis_clio/` on CHPC and
`analysis/official_thesis_clio/` on GitHub; the official deck is `slides/CLIO_vs_Claude_Code_official_thesis.pptx`
(`make_official_slides.py`) in both.

### B8. Why the CLIO arm is configured this way (from the non-counted pilots; see `pilot_program_*/STUDY.md`, slides)
1. **Cost.** CLIO's idle reaper (default 15 s) closed the Claude Code subprocess during every tool call longer than 15 s. The next call re-sent the whole history as one message, re-writing 140–210k tokens to cache at $20/M.
   - Program 20261011 with defaults: E1 $21.86, E2 $40.43, E3 $12.27.
   - Baseline: $7.98, $13.57, $7.45.
   - With the TTL raised (tuned program, n=1 per cell, 0 full re-sends in all six runs):
     - stock factorio-flat: E1 $9.63, E2 $17.72, E3 $9.60;
     - factorio-flat-hpc variant: E1 $7.88, E2 $17.88, E3 $7.62.
   - All six tuned runs passed or were accepted. The remaining E2 gap comes from more output and incremental cache writes, plus about 21.5k tokens written to cache on each session's first call (CLIO's system prompt and blueprint are not pre-cached; Claude Code's first call writes about 2.3k).
2. **E3 failure mode.** A blocking wait hit the 600 s tool timeout, then the 900 s turn watchdog, and the session errored with no outputs. The fix is to keep the watchdog above the tool timeout. With 3600 s / 5400 s, both tuned E3 runs were accepted.
3. **Harness version drift.** CLIO silently used Claude Code 2.1.296 (the newest installed CLI) while the baseline used 2.1.295. The arm now pins 2.1.295 and verifies it from the transcripts.
4. **Effort.** The pilots ran at `high`; the baseline used the CLI default. The counted arm sends no effort.
5. **Shared clio-core daemon.** One daemon per node is shared across CLIO deployments; the validation found one serving another deployment's config at 15.9 GiB. The counted arm uses a private daemon. Confirmed on 2026-10-12: two concurrent pilots on one node shared the daemon, and when one stopped, the other lost its store (`ClioCoreRuntimeLostError`). One E2 pilot was invalidated and rerun with a private daemon.
6. **Cache-write telemetry.** CLIO's session-level usage reports cache writes as 0 (its opt-in stream audit does record them per call). The arm reads usage from the session's own Claude Code transcripts, the same source as the baseline.
7. **Blueprint candidate.** factorio-flat-hpc 0.4.0-hpc.2 (pilot program 20261012_bpv2, n=1 per experiment, default effort) adds:
   - tool-call formatting rules;
   - reports written once;
   - bundled Morphorm/Exodus checks and a Slurm wait helper;
   - pilot-informed Morphorm guidance on the filter keyword form and restart-state counting.

   Results: E1 $5.48 (0.69× baseline), E2 $10.87 (0.80×), E3 $7.77 (1.04×), all passed or accepted, with model time at or below the baseline. It is a candidate for `⟨BLUEPRINT_ID⟩@⟨BLUEPRINT_VERSION⟩`. Report its pilot-informed content as a threat to validity (see B9).

   **Upstream (2026-10-12):** submitted as factorio-flat **0.5.0** in iowarp/clio-agent-marketplace PR #96 (commit 8e913d8). The content is hpc.2's, with small fixes: neutral wording, packet mode loads the skills for the packet's toolchain, and `wait_job.sh` finishes only on a final `sacct` state. If the counted CLIO arm pins the merged 0.5.0 rather than hpc.2, state that it is not byte-identical to the piloted variant (details in `pilot_program_20261012_bpv2/STUDY.md`).

   **Used in the counted trials (decision 2026-10-13):** the pilot-validated hpc.2 content, frozen and named factorio-flat 0.5.0
   (only the front-matter id/title/version changed). It is not byte-identical to the PR #96 version; cite the tree checksum
   in `Thesis/automation/clio/blueprints/factorio-flat-0.5.0.PROVENANCE.md`.
8. **Observability.** Measured on E1, E2 and E3 (`observability_study/OBSERVABILITY.md`): CLIO's own records answer 11.5–12 of 14 diagnostic questions vs 8.5 for Claude Code, but only with the opt-in stream audit (8.5–9 without it). The counted arm keeps `CLIO_STREAM_AUDIT_LOG` on.

### B9. Threats to validity to state in the thesis
- **Harness confound.** CLIO adds its own system prompt, tools and blueprint around the same model and CLI. That is the treatment, so the comparison is between systems, not models.
- **Pilot-informed tuning.** Runtime tuning and any blueprint variant were chosen after pilots on the same tasks; report this. The factorio-flat-hpc variant adds generic HPC and Morphorm guidance the baseline lacked.
- **Not identical conditions.**
  - Shared partition load differs between trials (Slurm wait variance).
  - **Compute-node speed.** The same E1 Morphorm job runs about 9.7 min on notch351 (all five baseline E1 jobs) and about 17 min on notch272–274. Node was not pinned in either arm. In the counted CLIO arm, 4 of 5 E1 jobs landed on notch273/274 (mean 15.7 min vs 9.8 min for the baseline), which explains E1's higher CLIO wall time; in E3, 2 of 5 CLIO jobs landed on notch351 (9.8–9.9 min) while all baseline E3 jobs ran on notch272–274 (~17 min). Compare agent speed with "time outside Slurm" (Part C).
  - **One-off 20-min tool call.** In one tuned pilot (E3 h3), CLIO's trace shows one shell call (a loop of `cat` over nine small staged files) running for 20 min while its two parallel siblings finished in seconds. The cause is not recorded (no process exit time). Watch for this in counted trials; it adds wall time but not cost.
  - The model provider and subscription limits are external.
  - The access boundary is procedural for both systems.
- **Different telemetry semantics.** `num_turns` and API time differ between the systems. Compare costs from per-call usage at the same list prices.
- **Sample size.** n = 5 per arm per experiment. Exact permutation and Mann-Whitney tests are reported, but "no detectable difference" is not evidence of equality.
- **Different days.** Baseline trials ran 2026-10-09/10, CLIO trials 2026-10-13; partition load and nodes differ.
- **E3 own-runtime audit rule.** Added for the CLIO arm only, before trials 03–07 (decision 2026-10-13); it re-labels reads of the agent's own runtime and nothing else. The shared audit's raw FAIL output is kept with each trial. State it in the methods.
- **Analysis correction (2026-10-13).** The first aggregation dropped four CLIO E3 Morphorm jobs because their agent-chosen names (e.g. `E3-clio-trial_03-spc`) matched the agent-host filter; fixed (filter now matches only the host job name `e3-clio-trial_NN`). Only the Morphorm-job metrics changed; pre-fix copies: `official_thesis_clio/.official_aggregate.py.pre_jobname_fix_20261013`, `.data_pre_jobname_fix_20261013/`.


---

## Part C: Official results (counted trials, 2026-10-13)

Sources: `clioSessions/CLIO_E1_API_pilots/official_thesis_clio/` (`official_aggregate.py` → `data/*.csv`;
`official_compare.py` → `data/stats.csv`, `figures/H1–H6`), scores in `Thesis/researcher_only/scores/<run_id>/`, deck
`slides/CLIO_vs_Claude_Code_official_thesis.pptx`. Rebuild: `python3 official_aggregate.py && python3 official_compare.py`,
then `slides/.venv/bin/python slides/make_official_slides.py`.

### C1. Outcomes (thesis scorer, same acceptance specs and tolerances as the baseline)

| | Claude Code baseline | CLIO (factorio-flat 0.5.0) |
|---|---|---|
| E1 | 5/5 accepted (01, 02, 03, 04R2, 05) | **5/5 accepted** (01, 02, 03R, 04, 05) |
| E2 | 5/5 accepted (01, 02R, 03, 04R, 05) | **5/5 accepted** (01, 02, 03, 04, 05R) |
| E3 | 5/5 accepted (01, 02R=`trial_06`, 03, 04, 05) | **5/5 accepted** (03, 04, 05, 06, 07) |

Science checks of every accepted CLIO trial are identical to the baseline's:
- E1 and E3: generated configuration 34/34 checks; final compliance relative difference 0.0 against the accepted
  reference (symmetry-honoured variant), all 51 iterations compared.
- E2: Stage 1 33/33 and Stage 2 35/35 checks; final compliance relative difference 0.0 for both stages.
- No nudges (0 extra user messages) in any counted trial of either arm; no CLIO session needed a full context re-send
  (0 full re-sends in all 15 trials).

**E3 boundary audit:** trials 03–07 PASS under the own-runtime rule (B6 update): 9, 9, 8, 9 and 10 own-runtime reads,
no other findings; the shared audit's raw output (FAIL only because of those reads) is kept in each trial's
`provenance/boundary_audit.shared.txt`. Supplementary CLIO verification PASS in all 15 trials.

### C2. Excluded CLIO attempts (all non-agent causes; kept as evidence, listed in `data/trial_attempts.csv`)
- **E1-03:** CLIO's version probe of the pinned CLI failed transiently on notch272 (`[Errno 14] Bad address`), so CLIO fell
  back to Claude Code 2.1.296 instead of the pinned 2.1.295; only the CLI-pin checks failed. Replaced by 03R.
- **E2-05:** Session B made zero API calls: the Claude Code OAuth login had expired and could not be refreshed
  (`ClaudeCodeSignedOutError`, 0 tokens). Replaced by 05R after a re-login.
- **E3-01:** aborted before launch (runner did not export `E3_ALLOW_ACCOUNT_NAME_IN_TMPDIR`; no agent, deployment or model
  call). Runner fixed; replaced by `trial_06`.
- **E3-02:** completed and passed 34/34 checks in a test scoring, but the audit failed on (a) own-runtime reads and (b) a
  researcher edit to `clio/README.md` during the trial. Researcher-caused; excluded, not scored; replaced by `trial_07`.

### C3. Mean per run (n = 5 each)

| | System | Wall (min) | Outside Slurm | Slurm submit & wait | Model reasoning & writing | API calls | Output tokens | Cost (USD) |
|---|---|---|---|---|---|---|---|---|
| E1 | Baseline | 22.0 | 12.5 | 9.5 | 11.6 | 34.2 | 55.7k | 7.98 |
| E1 | CLIO | 26.8 | 10.3 | 16.5 | 8.9 | 29.2 | 37.8k | **5.75** |
| E2 (A+B) | Baseline | 68.3 (A 28.7, B 39.6) | 21.1 (11.6 / 9.6) | 47.1 | 19.6 | 70.2 | 103.5k | 13.57 |
| E2 (A+B) | CLIO | 58.2 (A 24.1, B 34.1) | 16.2 (8.7 / 7.5) | 42.0 | 14.3 | 50.8 | 69.3k | **10.59** |
| E3 | Baseline | 30.9 | 13.4 | 17.6 | 11.7 | 49.0 | 52.3k | 7.45 |
| E3 | CLIO | 28.2 | 12.5 | 15.7 | 9.3 | 27.0 | 36.8k | **6.21** |

Share of wall time spent on model reasoning: CLIO E1 33.4 %, E2-A 31.1 %, E2-B 19.9 %, E3 33.1 %
(baseline 52.9 %, 37.1 %, 22.7 %, 37.7 %).

### C4. CLIO vs baseline (CLIO mean vs baseline mean: ratio of means [bootstrap 95 % CI], exact permutation p, 252 splits)

A difference is called only when p < 0.05 **and** the CI excludes 1 (bold). Costs are recomputed from per-call usage at
the same list prices for both arms.

| Metric | E1 | E2 | E3 |
|---|---|---|---|
| Cost per run (USD) | 5.75 vs 7.98: **0.72×** [0.64, 0.83], p=0.008 | 10.59 vs 13.57: **0.78×** [0.74, 0.83], p=0.008 | 6.21 vs 7.45: **0.83×** [0.78, 0.89], p=0.008 |
| Session wall time (min) | 26.8 vs 22.0: **1.22×** [1.12, 1.32], p=0.008 | 58.2 vs 68.3: 0.85× [0.71, 1.03], p=0.167 | 28.2 vs 30.9: 0.91× [0.77, 1.03], p=0.325 |
| Time outside Slurm (min) | 10.3 vs 12.5: 0.82× [0.63, 1.03], p=0.175 | 16.2 vs 21.1: **0.77×** [0.68, 0.89], p=0.032 | 12.5 vs 13.4: 0.94× [0.77, 1.15], p=0.548 |
| Model reasoning & writing (min) | 8.9 vs 11.6: 0.77× [0.57, 1.00], p=0.127 | 14.3 vs 19.6: **0.73×** [0.65, 0.84], p=0.016 | 9.3 vs 11.7: 0.80× [0.65, 1.00], p=0.127 |
| Tool time (min) | 1.3 vs 0.9: **1.51×** [1.21, 1.92], p=0.016 | 1.9 vs 1.5: 1.27× [1.00, 1.59], p=0.143 | 3.2 vs 1.7: 1.85× [0.97, 3.86], p=0.151 |
| Slurm submit & wait (min) | 16.5 vs 9.5: **1.74×** [1.39, 2.05], p=0.008 | 42.0 vs 47.1: 0.89× [0.68, 1.17], p=0.389 | 15.7 vs 17.6: 0.90× [0.71, 1.06], p=0.484 |
| Morphorm job run time (min) | 15.7 vs 9.8: **1.61×** [1.28, 1.82], p=0.032 | 41.2 vs 46.7: 0.88× [0.67, 1.15], p=0.365 | 14.3 vs 17.2: 0.83× [0.65, 1.01], p=0.318 |
| API calls | 29.2 vs 34.2: 0.85× [0.68, 1.06], p=0.325 | 50.8 vs 70.2: **0.72×** [0.64, 0.81], p=0.008 | 27.0 vs 49.0: **0.55×** [0.52, 0.58], p=0.008 |
| Output tokens | 37.8k vs 55.7k: **0.68×** [0.55, 0.88], p=0.032 | 69.3k vs 103.5k: **0.67×** [0.61, 0.73], p=0.008 | 36.8k vs 52.3k: **0.70×** [0.65, 0.76], p=0.008 |
| Cache-write tokens | 160.6k vs 209.1k: **0.77×** [0.71, 0.83], p=0.008 | 301.3k vs 327.9k: **0.92×** [0.88, 0.98], p=0.048 | 182.9k vs 175.5k: 1.04× [0.97, 1.12], p=0.309 |
| Cache-read tokens | 2.57M vs 4.02M: **0.64×** [0.51, 0.83], p=0.024 | 4.38M vs 7.25M: **0.60×** [0.51, 0.70], p=0.008 | 2.84M vs 5.23M: **0.54×** [0.49, 0.60], p=0.008 |
| Cancelled Morphorm jobs | 0.0 vs 0.0 | 0.0 vs 0.8 (p=0.048) | 0.0 vs 0.0 |

### C5. Interpretation for the results chapter
1. **Same science, lower cost.** CLIO with factorio-flat 0.5.0 reached the identical accepted result in all 15 trials and
   cost less in every experiment: 0.72× (E1), 0.78× (E2) and 0.83× (E3) of the baseline, each p = 0.008 (all 5 CLIO runs
   cheaper than all 5 baseline runs).
2. **Where the saving comes from.** Less output (0.67–0.70×, lower in all three; for E1 permutation p = 0.032, Mann-Whitney
   p = 0.056), fewer API calls (E2 0.72×, E3 0.55×) and therefore fewer cache reads (0.54–0.64×). Cache writes
   fall less (E1 0.77×, E2 0.92×, E3 1.04× n.s.): CLIO's larger first-call system prompt and blueprint offset part of the gain.
3. **Time.** Agent-side time (outside Slurm) was lower in E2 (0.77×) and not detectably different in E1 and E3. E1 wall
   time was higher (1.22×) only because of Slurm: 4 of 5 CLIO E1 Morphorm jobs ran on the slower notch273/274 nodes
   (15.7 vs 9.8 min). Morphorm job time is node-dependent and not an agent effect.
4. **Fewer wasted jobs in E2.** 4 of 5 baseline E2 runs cancelled and resubmitted a Stage-2 job (restart-index mistake);
   no CLIO run did (0.0 vs 0.8 cancelled jobs per run, p = 0.048). The blueprint's restart-state guidance was informed by
   the non-counted pilots (threat to validity, B9).
5. **Tool time** was higher for CLIO in E1 (1.3 vs 0.9 min, 1.51×) — CLIO's tool wrapper and the blueprint's verification
   helpers — but it is a small part of wall time.
6. **Not tested here:** CLIO's context engine (no session approached the context limit), the Desktop, and stock
   factorio-flat 0.4.0 without HPC guidance. The comparison is between systems (harness + blueprint + same model and CLI),
   not between models.

### C6. Figures (`official_thesis_clio/figures/`, PNG and PDF)
- H1 cost decomposition
- H2 per-call context and cache writes
- H3 time breakdown
- H4 work volume
- H5 per-run distributions
- H6 scorecard vs baseline

### C7. Integrity checks after the batch
- All 5,916 baseline files match the SHA-256 snapshot taken before the CLIO batch
  (`official_thesis_clio/baseline_integrity_before.sha256`, `sha256sum -c` rc = 0).
- No credential copies left under `Thesis/` or `clioSessions/`; no batch processes left running.

### C8. Observability on the counted trials (same method as `observability_study/OBSERVABILITY.md`)
Script: `official_thesis_clio/official_observability.py` (a copy of the pilot script with the counted-trial inputs) →
`official_thesis_clio/observability/{data,figures}`. Only records a system writes about itself count; runner files are
excluded. One change from the pilots: the counted runner kept CLIO's SSE event stream, which records
`tool.call.progress` while a tool runs, so Q4 (liveness of a long tool) is now "recorded" for CLIO.

| | E1 | E2 | E3 |
|---|---|---|---|
| Claude Code: points / 14 (fully recorded) | 8.5 (6) | 8.5 (6) | 8.5 (6) |
| CLIO with stream audit | **12 (11)** | **12 (11)** | **12 (11)** |
| CLIO without the opt-in audit | 9 (8) | 9 (8) | 9 (8) |
| Distinct record types per run (baseline vs CLIO) | 31 vs 103 | 31 vs 103 | 31–35 vs 103 |
| Structured records per model call | 18–29 vs 188–246 | 21–24 vs 217–230 | 15–18 vs 213–257 |
| Own-record storage per run (CLIO incl. full exports) | 2.6 vs 21 MB (323 MB) | 4.0 vs 37 MB (849 MB) | 2.5 vs 23 MB (347 MB) |

- CLIO only: typed cache-reset reasons (Q2), typed failure reasons (Q5), live configuration read-back (Q6), skills
  loaded (Q8), prompt-prefix hashes (Q12), runtime health (Q13). Baseline only: running rate-limit state (Q10).
  Neither: Slurm-job attribution (Q9), file-to-call attribution (Q14); both derivable from tool output.
- Used on the counted trials:
  - The audit typed all 535 CLIO model calls: 515 incremental, 20 full first calls (one per session), zero
    `session_evicted` re-sends. This confirms that the idle-reaper fix held.
  - E2-05's cause was recorded as a typed `ClaudeCodeSignedOutError` (0 tokens).
  - E1-03's CLI fallback was explained by the server log's failed version probe.

### C9. Which parts of CLIO E1–E3 exercised
- **Exercised:**
  - the agent loop (GACT);
  - the `claude_code` provider and the blueprint;
  - the runtime settings and the telemetry;
  - clio-core as the session store, used passively.
- **Tools actually called:** only `shell_bash` (25–55 calls per session) and `load_skill` (2), of 45 tools offered.
- **Not exercised:**
  - the context engine (no compaction: `compaction.auto_skipped`; recall and memory tools never called);
  - the assimilation (CAE), transfer (CTE) and exploration (CEE) engines. No agent tool exposes them, and the experiments
    used plain files, Slurm and Globus as in the baseline.
- **Thesis framing:** E1–E3 compare CLIO as an agent harness, not its data engines. The engines were tested separately,
  without a model, in `clioSessions/CLIO_engine_pilots/`.

### C10. Qualitative conclusions per experiment
- **All three.** Swapping the agent system around the same model and CLI did not change scientific reliability on these
  frozen workflows. Every CLIO trial reached the accepted result with no human input or nudges. What changed was the
  working style:
  - less writing;
  - fewer, larger model calls;
  - far richer records about itself (C8).
- **E1 (uninterrupted).** This is the cleanest view of the harness plus blueprint. The blueprint's Morphorm and Slurm
  guidance and bundled check scripts let the agent go straight to a correct deck and job, so it wrote less (output 0.68×).
  Agent time was not detectably different. The higher wall time comes from Slurm node assignment, not from the agent.
- **E2 (interrupted recovery): CLIO's clearest advantage.** The gain does not come from memory or session continuity:
  Session B was a new deployment, as in the baseline. It comes from encoded domain knowledge:
  - 4 of 5 baseline runs started Stage 2 from the wrong saved state, then cancelled and resubmitted; no CLIO run did;
  - model time was 0.73× and time outside Slurm 0.77×.

  Thesis point: in recovery work, explicit knowledge of restart semantics mattered more than raw model ability. That
  knowledge was informed by the pilots (B9).
- **E3 (disparate storage).** Still cheaper in every run (0.83×) and the largest cut in model calls (0.55×). Time and
  accumulated context were indistinguishable from the baseline. In the data-handling half of the task both systems
  behaved alike:
  - they read the catalog, artifact cards and protocol;
  - they staged a similar number of files: 14.4 (CLIO) vs 14.8 (baseline) per run;
  - they made a similar number of Globus transfers: 11.6 vs 13.2;
  - they recorded provenance the same way.

### C11. Why E3 improved least
The smaller E3 gain is **not** because E3 relied more on clio-core: the core was used in E3 exactly as little as in E1
(C9). The reasons, from the records:
1. **The blueprint has nothing for the data half.** Every E3 session loaded the same two skills as E1 (`morphorm`,
   `hpc-batch-jobs`). factorio-flat 0.5.0 has no skill for storage discovery, relevance judgement, Globus staging or
   provenance. CLIO helped only with E3's E1-like half.
2. **The data engines were not in play.** The agent called only `shell_bash` and `load_skill`. Staging went through
   Globus and plain files exactly as in the baseline. No agent tool exposes the transfer (CTE), assimilation (CAE) or
   exploration (CEE) engines.
3. **E3's context is dominated by reading that cannot be skipped.** Cache writes, about half the cost, track how large
   the context grows:
   - E1: CLIO's context ended smaller (161k vs 221k tokens), so cache-write cost fell (0.77×).
   - E3: it ended about the same (183k vs 187k), so cache-write cost did not fall (1.04×). Any agent must read the control
     documents, catalog, artifact cards and staging records. CLIO also starts each session with a larger fixed prompt
     (≈22k vs ≈9k tokens).
4. **Fewer calls, same work.** CLIO packed E3 into 27 calls instead of 49. Each call carried more new context (≈6.2k vs
   ≈3.5k tokens), so the saving appears in cache reads (0.54×) and cost, not in time.
5. **Tool-layer overhead** shows where tool calls are many and small: E3 tool time was 3.2 vs 1.7 min, mostly reading and
   record-keeping around staging.

**Suggested thesis wording:** CLIO's advantage here comes from its harness and the domain knowledge in its blueprint,
not from its data engines, which were not used. It is largest where that knowledge applies (E2's restart semantics, then
E1's deck and job construction) and smallest in E3. E3's extra work is finding and staging data, which CLIO targets
through engines that neither the blueprint nor the agent's tools addressed in this study. E3 therefore does not show that
CLIO is weak at data-movement workflows; it shows that this part of CLIO was not tested.

### C12. Future work: E3 with the clio-core engines (Levels 1 and 2 piloted 2026-10-13/14; Level 3 not run)
Three levels, from cheapest to most informative:
1. **Transparent transfer engine (FUSE staging).** Mount `clio_cte_fuse` over a private, disk-only `long_term` CTE tier at
   the exact path `$E3_STAGING_DIR` already uses (`$TMPDIR/e3/clio/<trial>`). The agent-visible packet, prompt and
   helpers stay byte-identical. Tests whether E3 runs unchanged on the engine. Not expected to change agent cost or
   time: about 15 small files are staged.
2. **Agent-visible engines.** A tool (MCP server over the CTE/CAE Python API) plus a blueprint skill for storage
   discovery, staging and provenance. The agent stages and looks up artifacts through the engine. This changes the
   treatment, not only the storage.
3. **Engine-dependent.** Assimilation that parses Exodus/HDF5 and semantic search (the `clio_cte_indexer` chimod) would let
   the agent query campaign data instead of reading it. Both are missing in iowarp-core 2.2.1 (engine probe), so this
   needs upstream work first.

Known constraints from the engine pilots:
- crash durability: 0/237 files survived a kill -9 even after fsync; use a clean unmount and stop;
- small files are ≈20× slower on the mount;
- the mount is node-local, as `$TMPDIR` already is, so the existing "returned files" rule still applies.

**Level 1 pilot result (2026-10-13, non-counted, `clioSessions/CLIO_engine_pilots/e3_fuse_staging_20261013/STUDY.md`).**
- **Setup:** claude-sonnet-5-5, frozen factorio-flat 0.5.0, Claude Code 2.1.295, n = 1 per arm.
  - Plain arm: node-local staging.
  - Fuse arm: `$E3_STAGING_DIR` on a FUSE mount of a private clio-core **2.3.1** transfer engine (the latest release; it
    ships the indexer and crash-consistency fixes). The agent's own session store stayed 2.2.1, which clio-agent
    0.9.5b5.post2 requires.
- **Result:**
  - Both arms were accepted by the thesis scorer, with the same session wall (28.6 vs 29.0 min) and the same Morphorm job
    time (18:09 on the same node).
  - Every staged file was correct on the mount (11/11) and identical after a clean unmount, stop and recovery.
  - The agent saw no difference.
- **Conclusion:** E3 is **compatible** with the transfer engine under its staging directory. At about 2 MB of small files
  staged by Globus there is **no measurable benefit**.
- **Side finding:** under Sonnet, CLIO sometimes ended a session silently when the model wrote its tool calls as text
  (2 of 4 starts; never under Fable in the 20 official sessions). It is recorded as a developer finding.

**Level 2 pilot result (2026-10-14, non-counted, `CLIO_engine_pilots/e3_fuse_staging_20261013/level2/LEVEL2.md`).**
- **Design:** three arms, claude-sonnet-5-5, all on frozen factorio-flat 0.5.0 plus changes:
  - A: no skill, plain storage (the Level-1 plain run);
  - B: a generic data-staging/provenance skill, plain storage;
  - C: the same skill plus four agent tools over the clio-core 2.3.1 engines (BM25 search over the staged files, which are
    indexed as they are written; ingest; read; manifest), with staging on the engine mount.
- **Result:**
  - All four runs were accepted.
  - **The agent never called an engine tool (0 calls in 2 of 2 engine runs)**, although the tools were in its toolset and
    it loaded the skill that describes them. It found values with grep/sed as before.
  - The skill alone changed staging behaviour: half the files and half the Globus transfers of arm A (8/5 vs 16/10),
    with the same cost and time.
  - One engine run's extra cost ($3.14 vs about $1.3) came from a degenerate 128k-token Sonnet reply that CLIO kept in
    context, not from the engine.
- **Thesis framing:**
  - Offering the engines is not the same as using them. In this task the agent's existing shell habits were cheaper than
    the new tools, and written knowledge (the skill) changed behaviour where tools did not, consistent with C10–C11.
  - Showing an engine benefit would need a task where reading is expensive (large or many documents, long campaigns:
    E6-like) or a protocol that requires the engine step. The latter changes the task and must be reported as such.
