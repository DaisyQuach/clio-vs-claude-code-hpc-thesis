# Headless Claude baseline automation

All scripts live here and share `lib/common.sh` (frozen constants: pinned Claude Code `2.1.292`, model `claude-fable-5-1`,
Slurm contract, experiment table). Exit codes: `0` ok, `1` failure, `2` usage, `3` blocked by preflight, `4` refused (would overwrite /
ambiguous state), `5` ambiguous verification. Every script fails closed.

| Script | Purpose |
|---|---|
| `preflight.sh [--experiment SEL] [--dry-run] [--json OUT]` | pinned executable exists and `--version` is exactly 2.1.292; headless flags verified from `--help`; `auth status --json` (no model call); scheduler commands and partition; approved software and runtime hash; frozen-configuration hashes; no `CLAUDE.md` in ancestors; no researcher-only references in agent-visible text |
| `prepare_trial.sh --experiment SEL (--trial N [--suffix R] \| --all-planned)` | creates a planned, empty packet (manifest, `agent_inputs/` from the frozen configuration, `.gitkeep` dirs); refuses existing content. `--suffix R` creates a replacement packet `trial_NNR` (run id `…-NNR`, same paired block) for a trial aborted by a non-agent cause (e.g. provider session limit); the aborted packet is kept and excluded via its curation fields |
| `launch_headless_claude.sh …` | one new headless Claude Code process per call: new UUID, isolated `CLAUDE_CONFIG_DIR`, prompt file, exact argv recorded; `--dry-run` writes the plan only; `--execute-counted` runs (default inside an agent-host `sbatch --wait` job with the frozen contract; `--local` for an existing allocation) |
| `run_e1_baseline.sh --trial N [--suffix R] (--dry-run \| --execute-counted) [--local]` | one E1 trial: preflight → planned-packet verification → launch → collect evidence → completed-packet verification → manifest status |
| `run_e2_baseline.sh --trial N [--suffix R] (--dry-run \| --execute-counted) [--local] [--pause-after-session-a \| --session-b-only]` | one E2 trial: Session A → Stage-1 interlock → fresh Session B → collect → verify |
| `monitor_jobs.sh (--trial-dir D \| --job-ids …) [--watch S]` | squeue/sacct view of a trial's agent-host and workflow jobs |
| `collect_baseline_evidence.sh --trial-dir D [--dry-run]` | copies session evidence into `<trial>/logs/agent_sessions/`, gathers sacct for all job ids, hashes evidence, fills manifest ids/timestamps; never overwrites |
| `verify_trial_packet.sh --trial-dir D (--planned \| --completed) [--json OUT]` | structural verification; completed mode checks locked deliverables, `SHA256SUMS`, job ids, sacct, session records (distinct ids, no resume, isolated config, pinned version), researcher-only boundary audit of transcripts, E2 session order |
| `score_researcher_only.sh --trial-dir D [--dry-run] [--figures]` | researcher-only scientific scoring against the reference (`acceptance_spec.json`); writes `researcher_only/scores/<run_id>/`; figures only under `researcher_only/evaluation_figures/`; writes only the decision word into the manifest |
| `run_all_planned_baselines.sh --experiment SEL (--dry-run \| --execute-counted)` | five-trial batch for ONE experiment; stops at the first failed/ambiguous trial; refuses without an explicit selector and `--execute-counted` |

## Modes and guards
- `--dry-run`: no model call, no Slurm submission, no manifest-status change. The launch plan and command are written under
  `researcher_only/session_evidence/<run_id>/dryrun_<timestamp>/`. If the pinned executable is absent, dry runs may set
  `THESIS_CLAUDE_BIN_OVERRIDE=<other claude binary>` to render the plan; counted runs ignore the override and are refused.
- `--execute-counted`: required for any counted run. Refused unless `preflight.sh` passes (including the pinned 2.1.292 executable),
  the packet is a clean planned packet, and no evidence exists for the run id.
- Trial status lifecycle: `planned` → `running` (E2: `running_session_a` → `paused_after_session_a` → `running_session_b`) →
  `completed_unscored` | `ambiguous` | `failed` | `failed_stage1_boundary`; then `scoring_decision` ∈ {accepted, rejected, needs_review}.
  A trial is never marked successful because the process exited.

## Counted-run commands (after researcher approval; see `../BUILD_REPORT.md` checklist)
```bash
cd /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/automation
./preflight.sh --experiment e1-example8
./run_e1_baseline.sh --trial 1 --execute-counted
./score_researcher_only.sh --trial-dir ../runs/E1_uninterrupted_example8/baseline/trial_01 --figures
./run_e2_baseline.sh --trial 1 --execute-counted
./score_researcher_only.sh --trial-dir ../runs/E2_interrupted_recovery_example16/baseline/trial_01 --figures
```
Run from a login node or any shell with `sbatch` (each session becomes its own agent-host job), or inside an interactive
allocation with `--local`. CLIO and E3 automation are intentionally absent from this build.
