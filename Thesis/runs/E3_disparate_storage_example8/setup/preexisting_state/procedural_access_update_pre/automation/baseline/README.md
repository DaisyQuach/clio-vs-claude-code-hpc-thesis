# E3 baseline automation (headless Claude Code)

Pinned system (same as the active thesis baseline protocol, read from `Thesis/automation/lib/common.sh` and
`Thesis/researcher_only/RESEARCHER_DECISIONS.md` without modifying them): Claude Code **2.1.295** at
`$HOME/.local/share/claude/versions/2.1.295`, model **`claude-fable-5-1`**, harness defaults, autoupdater disabled, one new
process per trial, isolated `CLAUDE_CONFIG_DIR`, never `--resume/--continue/--fork-session`.

| File | Purpose |
|---|---|
| `run_baseline_e3_trial.sh --trial-dir D (--dry-run \| --execute-counted)` | all checks → prepare → node-local staging → headless launch → records → audit → metrics → verification |
| `prepare_baseline_trial.sh` | fresh-workspace check; noninteractive clone at the pinned commit; copies only `README.md task/ catalog/ protocol/ scripts/` into `agent-inputs/control/`; writes `trial_context.md`, `permitted_roots.txt`, `CONTROL_COMMIT.txt`; makes `agent-inputs/` read-only |
| `verify_baseline_trial.sh --trial-dir D (--planned \| --completed)` | structure/freshness, or deliverables + distributed-context records + hashes + audit |
| `collect_baseline_metrics.sh --trial-dir D` | `provenance/commands.tsv`, `tool_calls.tsv`, `metrics.json` (descriptive only) |
| `baseline_e3_prompt.md` | the prompt; must be byte-identical to `task/task_prompt.md` at the pinned commit (checked) |
| `baseline_e3_config.env.example` / `baseline_e3_config.env` | pinned version, model, repo URL + commit, Globus mode, timeout (no secrets) |

## Running a counted trial (researcher action; not done at setup)
`--execute-counted` must run **inside** a Slurm allocation with the frozen agent-host contract (this script never calls `sbatch`):
```bash
#!/bin/bash -l
#SBATCH --account=hochhalter-np --partition=hochhalter-np --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=32G --time=02:00:00
/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/automation/baseline/run_baseline_e3_trial.sh \
  --trial-dir /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/baseline/trial_01 --execute-counted
```
It stops with exit 3 and `logs/ACTION_REQUIRED_<code>.md` (nothing launched) if: no allocation / no `$SLURM_TMPDIR`; `$SLURM_TMPDIR`
contains the account name (unless accepted); pinned Claude Code missing, flags missing or not authenticated headlessly; control
repository unreadable noninteractively or pin missing; Globus not configured or interactive (unless `E3_GLOBUS_MODE=posix_readonly_fallback`
is set as a researcher decision); collections fail verification; legacy `agent_inputs/` present without `--accept-legacy-agent-inputs`.

Current blockers for `baseline/trial_01` (after remediation, 2026-10-10): ground truth not technically isolated
(`setup/GROUND_TRUTH_ISOLATION_ACTION_REQUIRED.md`; the sandbox prototype in `automation/sandbox/` is not yet integrated here),
compute-node qualification (`setup/COMPUTE_NODE_QUALIFICATION_ACTION_REQUIRED.md`) and Globus not configured
(`setup/GLOBUS_ACTION_REQUIRED.md`). The legacy `agent_inputs/` was archived out of the trial; `--accept-legacy-agent-inputs` must
not be used. The approved software interface written into `agent-inputs/` is now `automation/environment/load_morphorm_e3.sh`,
and the pinned control commit is `c3b87369b51ee9e33f66c55f9608a16e447ab3e7`. A dry run (`--dry-run`) is read-only and can be run anywhere.

## What a trial records (all inside the trial directory except the isolated Claude config)
`logs/session/` (launch plan and argv, prompt + SHA-256, stream, transcript, tool inputs, result, session record, auth status),
`provenance/` (preparation, control/source versions, agent-inputs hashes, automation commands with exit status, node-local placement,
boundary audit, sources after trial, output hashes, metrics, commands, verification), `staging-manifest/` (agent staged/returned files,
final node-local listing and totals), `manifest.yaml` `e3dc_*` fields. Paths under `$HOME` are written as the literal `$HOME`.
The isolated Claude configuration is `E3/.agent_runtime/baseline/<trial_id>/claude_config` (mode 700; credential copy removed after the session).
