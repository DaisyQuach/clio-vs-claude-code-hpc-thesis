# E2 fresh-session recovery: how it is enforced

| Requirement | Mechanism | Evidence |
|---|---|---|
| New process for Session B | `run_e2_baseline.sh` calls `launch_headless_claude.sh` twice; each call starts a new `claude --print` process (inside its own agent-host Slurm job) | two `session_record.json` files with different PIDs/hosts/job ids |
| No `--resume`, `--continue`, session-id reuse, branch or fork | the launcher's argv is fixed; forbidden flags are asserted absent; a fresh `uuidgen` per session | `launch_command.txt`, `verify_trial_packet.sh --completed` (`no_resume`, `distinct_session_ids`) |
| No reuse of Session A process state | Session A ends (process exit or timeout) before the interlock; each session has its **own `CLAUDE_CONFIG_DIR`** (own projects/transcripts, no auto-memory, `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`) | `launch_env.txt`, `isolated_config` check |
| Session B sees only persistent trial artifacts | Session A's launch records, stream, stderr and transcript are staged under `researcher_only/session_evidence/<run_id>/session_a/` and copied into `<trial>/logs/agent_sessions/` **only after Session B ends** (collector) | collector timestamps; `session_order` check |
| Recovery prompt is neutral | `recovery_prompt.md` names no artifact file, stage label, iteration count or summary | `recovery_prompt_neutral` check in `verify_trial_packet.sh` |
| Stage-1 boundary | interlock between sessions: Session A record exists, no trial Slurm jobs active, `outputs/stage1/{engine_output.exo,morphorm_oc_optimizer_diagnostics.txt}` and `work/run_summary.md` exist, no `outputs/stage2` content; otherwise the trial is marked `failed_stage1_boundary` and Session B is not launched | manifest status, run log |

Residual limitation: both sessions run as the same Unix user, so the boundary against researcher-only material is procedural
(never referenced in agent-visible text) plus a post-hoc transcript audit (`boundary_audit`), not a kernel-enforced isolation.
