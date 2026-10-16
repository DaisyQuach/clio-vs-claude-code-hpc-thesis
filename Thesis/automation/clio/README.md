# CLIO arm automation (planned counted trials; set up 2026-10-11)

This folder holds the CLIO counterpart of the headless Claude Code baseline automation in `../`. **Nothing here has run a
counted trial.**

- **Baseline files are reused, read-only.** Every baseline file is used as is: `../lib/common.sh` (model, Slurm contract,
  session limit, experiment table, manifest helpers), `../preflight.sh`, `../verify_trial_packet.sh`,
  `../collect_baseline_evidence.sh` and `../score_researcher_only.sh`. The baseline packets, scores and evidence are not
  touched.
- **Design and parity decisions:** `clioSessions/CLIO_E1_API_pilots/THESIS_NOTES_methods_and_evaluation.md`.
- **Pilot evidence behind the defaults:** `clioSessions/CLIO_E1_API_pilots/pilot_program_20261011*/STUDY.md`.

| File | Purpose |
|---|---|
| `clio_trial_config.env` | CLIO pins and parity decisions. Values starting with `TBD` are placeholders: dry runs render them, counted runs refuse |
| `prepare_clio_trial.sh --experiment e1-example8\|e2-example16 (--trial N [--suffix R] \| --all-planned)` | Planned packet `runs/<exp>/clio/trial_NN`, built with the same copy commands, frozen hash and manifest keys as the baseline packet (`system: clio`), plus `clio_*` keys |
| `preflight_clio.sh --experiment SEL [--dry-run]` | Runs the baseline preflight, then checks the CLIO install and pin, the pinned Claude Code CLI, credentials, placeholders, blueprint and tuning values. No model call |
| `launch_clio_session.sh …` | One fresh CLIO deployment plus one CLIO session. Modes: `--dry-run`, `--execute-counted`, `--validate-deployment` (no model call). Default `--via-slurm` (an `sbatch --wait` agent-host job with the baseline contract); `--local` inside an allocation |
| `run_e1_clio.sh --trial N (--dry-run \| --execute-counted)` | One E1 trial, run in the baseline's order |
| `run_e2_clio.sh --trial N (--dry-run \| --execute-counted) [--pause-after-session-a \| --session-b-only]` | One E2 trial: Session A, the baseline's interlock, then Session B on a new deployment in a new agent-host job |
| `run_all_planned_clio.sh --experiment SEL (--dry-run \| --execute-counted)` | Five-trial batch for one experiment; stops at the first failed or ambiguous trial |
| `collect_clio_evidence.sh --trial-dir D` | Runs the baseline collector, then adds `logs/agent_sessions/<label>/clio/`, `logs/clio_evidence_SHA256SUMS.txt` and the `clio_*` manifest fields |
| `verify_clio_supplement.sh --trial-dir D` | CLIO checks run after the baseline verifier: settings read back, CLI/CLIO pins, one user message, fresh deployment, audit of the CLIO exports, usage present |
| `lib/clio_session_runner.py` | API runner: preflight read-back, configuration freeze, one verbatim prompt, poll, SSE capture (`stream.jsonl`), exports |
| `lib/clio_usage.py` | Usage from the session's own Claude Code transcripts, including cache writes, plus stream-audit reset reasons. Writes `result.json` (baseline-shaped) and `clio/usage_*` |

E3 uses the same launcher and runner through `runs/E3_disparate_storage_example8/automation/clio/run_clio_e3_trial_v2.sh`.

## One CLIO session = one fresh deployment
`$THESIS_ROOT/.agent_runtime/<run_id>/<label>/` holds:
- `clio_home/`: `CLIO_AGENT_HOME`. Contains the installed user config minus `workspaces.json`, with no MCP servers by default.
- `claude_config/`: an isolated `CLAUDE_CONFIG_DIR`. The credential copy is removed at session end.
- `core_state/`: a private clio-core daemon on its own port. Without it, the daemon is node-global and shared with any other CLIO deployment on that node.
- `bin/claude`: points to the baseline's Claude Code `2.1.295`. Otherwise CLIO drives the newest installed CLI; the pilots used 2.1.296.

The environment also sets:
- `CLIO_BIN_DIR`, `CLIO_NO_UPDATE_CHECK=1` and `CLIO_STREAM_AUDIT_LOG`;
- the runtime tuning values from the config;
- `DISABLE_AUTOUPDATER=1`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` and `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1`;
- `THESIS_TRIAL_ID`.

Session settings are read back from the API and must match before the prompt is sent:
- model `claude_code`/`claude-fable-5-1`;
- approval `bypass`;
- effort: by default none is sent, so the CLI default applies, as in the baseline;
- blueprint and version.

## Records: the same places and names as the baseline
- **Staging:** `researcher_only/session_evidence/<run_id>/<label>/` during the run, so Session B cannot see Session A's records.
- **Copy in the packet:** `logs/agent_sessions/<label>/`, containing:
  - `session_record.json`: baseline keys plus CLIO keys;
  - `launch_plan.json`, `launch_command.txt`, `launch_env.txt`, `prompt.md` and `prompt.sha256`;
  - `stream.jsonl`: CLIO's SSE events;
  - `transcript_<id>.jsonl`: the Claude Code transcripts CLIO's provider wrote;
  - `result.json`: tokens, cache reads/writes, cost and API calls;
  - agent-host sbatch, sacct and stdout/stderr;
  - `clio/`: configuration freeze, health, runtime settings, blueprint, the full API exports (messages, transcript, trace, interactions, attempts, provenance), usage per call, stream-audit rows and runner logs.
- **Trial level:** `logs/slurm_sacct.psv`, `logs/evidence_SHA256SUMS.txt`, `logs/packet_verification.json` and `logs/clio_supplement_verification.json`.
- **Scoring:** `../score_researcher_only.sh --trial-dir runs/<exp>/clio/trial_NN [--figures]`. Unchanged, so the same scorer, acceptance spec and tolerances apply. It writes `researcher_only/scores/<run_id>/`.

## Validation done at setup (2026-10-11, all outside the trial records)
All validation output is in `clioSessions/CLIO_E1_API_pilots/thesis_clio_deploy_validation_20261011T234016Z/`.

1. Dry runs of `run_e1_clio.sh` and `run_e2_clio.sh`. A counted preflight is refused while placeholders remain (exit 3).
2. `--validate-deployment` on a compute node: the deployment came up healthy; only `sandbox` was degraded, the same as in the pilots. Settings read back correctly, factorio-flat 0.4.0 was attached, and CLIO selected CLI 2.1.295.
3. One end-to-end smoke session on a scratch copy of a planned packet, with a tiny prompt and no workflow:
   - collector, baseline verifier and CLIO supplement ran;
   - the baseline verifier failed only on the missing scientific deliverables, as expected;
   - the CLIO supplement passed, including CLI 2.1.295 seen in the transcripts.

   The smoke test found and fixed one runner bug. Cost: $0.47.

## Counted-run commands (after the researcher fills `clio_trial_config.env`)
```bash
cd /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/automation/clio
./preflight_clio.sh --experiment e1-example8
./run_e1_clio.sh --trial 1 --execute-counted
../score_researcher_only.sh --trial-dir ../../runs/E1_uninterrupted_example8/clio/trial_01 --figures
./run_e2_clio.sh --trial 1 --execute-counted
../score_researcher_only.sh --trial-dir ../../runs/E2_interrupted_recovery_example16/clio/trial_01 --figures
```
The rules from `../AUTOMATION_LIMITATIONS.md` still apply:
- never edit these scripts while a batch is running;
- check subscription headroom before a batch (provider limits aborted baseline E1-04/04R and E2-02/04);
- replacement packets use `--suffix R`.
