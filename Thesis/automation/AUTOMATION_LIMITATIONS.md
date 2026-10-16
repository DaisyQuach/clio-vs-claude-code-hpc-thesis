# Automation limitations and uncertainties (read before the first counted run)

1. **RESOLVED 2026-10-09 (repinned to 2.1.295 by researcher decision; preflight PASSES).** Original note: **Pinned executable missing.** `$HOME/.local/share/claude/versions/2.1.292` does not exist (2.1.293, 2.1.294, 2.1.295 do). Preflight
   is BLOCKED and every counted entry point refuses to run. Installing it is a researcher action outside this tree (for example
   `claude install 2.1.292`, then re-run `preflight.sh`). The headless syntax was verified against 2.1.295's `--help`; preflight re-verifies
   it against whatever 2.1.292 reports.
2. **Config-dir isolation is untested against a live login.** Each session gets its own `CLAUDE_CONFIG_DIR` holding a copy of
   `~/.claude/.credentials.json` and a minimal `.claude.json`. `claude auth status --json` passes in the shared config; it is re-run
   inside the isolated directory and recorded (`auth_status_isolated_config.json`) at launch, but a real model call was never made during
   this build, so the first counted session is the first end-to-end test. If it fails to authenticate, the fallback is to launch with the
   shared `~/.claude` (set `CLAUDE_CONFIG_DIR` unset in `launch_headless_claude.sh`) and rely on `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`;
   transcripts then live under `~/.claude/projects/<slug>/`.
3. **Same Unix user.** The agent runs as the researcher. Researcher-only material is protected procedurally (never referenced in
   agent-visible text; `--dangerously-skip-permissions` is required for headless operation) and audited post hoc (transcript grep). It is not
   enforced by file permissions.
4. **Agent-host job vs. agent's own jobs.** The agent session runs inside an `sbatch --wait` job (2 h). The agent waits for its Morphorm job(s)
   inside the session; if the agent-host job hits its limit, the session is killed (`timeout_hit`) and the trial becomes `ambiguous`/`failed`.
   The 1 h 50 min internal timeout leaves time for evidence capture.
5. **Transcript location.** Expected at `$CLAUDE_CONFIG_DIR/projects/<cwd-slug>/<session-id>.jsonl`; if the layout differs in 2.1.292 the
   launcher warns ("no transcript found") and the stream JSONL remains the primary evidence.
6. **Token/cost telemetry** is taken from the `result` event of the stream (`result.json`) and is descriptive only; the subscription route
   reports no cost.
7. **Network from compute nodes.** The pilot ran Claude Code on hochhalter-np compute nodes interactively; batch jobs are assumed to have the
   same egress. If not, use `--local` inside an interactive allocation on a node with egress.
8. **E2 interlock is structural, not scientific.** It checks that Stage-1 deliverables exist and no trial jobs are active; it does not judge
   their correctness (that is the scorer's job after Session B).
9. **Cubit license.** `cubit-edu/2026.8` relies on the researcher's Coreform login in their own user configuration; batch meshing worked in the
   reference builds (jobs 16154328, 16154331). A license outage would surface as a failed mesh step inside the trial.
10. **Not implemented by design:** CLIO automation, E3 execution, automatic installation of Claude Code, any change outside `Thesis/`.

## Fixes applied during the first counted runs (2026-10-09)
11. `launch_headless_claude.sh` wrote an empty `session_record.json` because its jq program used `$end`, a jq reserved word (trial E1-01). Fixed
    (`--arg endt`); the E1-01 record was reconstructed from the raw per-session files and the repair is documented in the packet.
12. The per-session `CLAUDE_CONFIG_DIR` now lives at `Thesis/.agent_runtime/<run_id>/<label>/claude_config` instead of under
    `researcher_only/session_evidence`: Claude Code persists large tool outputs under its config dir and prints that path into the transcript, which
    produced a boundary-audit false positive (trial E1-02). The audit now blanks the session's own config-dir path before matching and also flags
    `.agent_runtime` mentions other than the session's own directory. Transcripts are still copied into the evidence directory at session end.
13. **Never edit an automation script while a batch is running.** Bash reads scripts incrementally; editing `run_e2_baseline.sh` (adding `--suffix`)
    while the E2 batch was executing shifted the file offsets and the running process misread its next line (`ompt-file: command not found`, rc 127)
    right after Session B had already completed normally (E2-01: both sessions exit 0, packet verified; status corrected by the researcher). Rule for
    the rest of the study: make automation edits only between batches, then re-run a dry run before the next counted batch.
