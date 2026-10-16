# E3 CLIO runbook (one counted trial = one fresh allocation + one fresh dedicated CLIO server + one session)

Definition: `setup/CLIO_DEPLOYMENT.md`. Researcher decisions (2026-10-10): dedicated E3 CLIO instance per trial; approval
mode `bypass` fixed at session creation; fresh 8-CPU/32-GB allocation per trial; one harmless pilot session approved.

E3=/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8 · NN = 01 … 05 · P = a free port
(for example 1785N). Pins and paths come from `automation/baseline/baseline_e3_config.env`, the same file the baseline
uses, so both systems share one source of truth.

## 1. Allocation (researcher, manual)
```bash
salloc --account=hochhalter-np --partition=hochhalter-np --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=32G \
       --time=02:00:00 --job-name=e3-clio-trial_NN
hostname; echo "$SLURM_JOB_ID $TMPDIR"     # must be a compute node; TMPDIR=/scratch/local/<account>/<jobid>
```
This is the same 8 CPU / 32 GB / 2 h contract as the baseline agent host. Use one new allocation per trial; never reuse one.

## 2. Dedicated E3 CLIO server (researcher, manual, in that allocation's shell)
```bash
$E3/automation/clio/start_e3_clio_server.sh --trial-dir $E3/clio/trial_NN --port P --dry-run   # check
$E3/automation/clio/start_e3_clio_server.sh --trial-dir $E3/clio/trial_NN --port P
```
The script creates a fresh `$E3/.agent_runtime/clio/E3-clio-trial_NN/` (it refuses an existing one) containing:
- the same installed CLIO (`Daisy/clioSessions/CLIOruntime`, clio-agent 0.9.5b5.post2), on its own port, bound to
  127.0.0.1;
- `config.yaml` with provider `claude_code` and model `claude-fable-5-1`;
- `mcp.yaml` with **no servers**, so no web search;
- no prior workspaces, sessions, memory or traces; the core-daemon state is isolated too.

It exports `E3_TRIAL_ID`, `E3_TRIAL_ROOT`, `E3_STAGING_DIR` and `E3_SYSTEM=clio`, which CLIO's shell tool inherits as
the baseline prompt states. It also sets `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1`, runs `clio start`, and writes
`instance.json`.

## 3. Desktop (optional; control/observation only)
```bash
ssh -L P:127.0.0.1:P -J <you>@notchpeak1.chpc.utah.edu <you>@<allocated node>     # on the Windows machine
```
The Desktop must **not**:
- send messages, answer questions or grant permissions during a counted trial (any of these invalidates it, and
  verification checks there is exactly one user message);
- open or upload files;
- connect to GitHub or Globus.

You may keep the tunnel log as operational evidence if it contains no credentials.

## 4. Automated trial (after the server answers; no manual steps)
From a login node:
```bash
srun --jobid=<alloc job id> --overlap --ntasks=1 $E3/automation/clio/run_clio_e3_trial.sh --trial-dir $E3/clio/trial_NN --dry-run
srun --jobid=<alloc job id> --overlap --ntasks=1 $E3/automation/clio/run_clio_e3_trial.sh --trial-dir $E3/clio/trial_NN --execute-counted
```
The runner first checks:
- allocation and `$TMPDIR`;
- that the instance belongs to this trial, host and job;
- `/v1/health`;
- no MCP servers;
- the model;
- 0 sessions on the instance;
- GitHub at the pin, Globus, the sources and workspace freshness.

It then:
1. Prepares the **same packet as the baseline** (`prepare_baseline_trial.sh --system clio`: clone at the pin into
   `$TMPDIR/e3/_control`, `agent-inputs/` read-only, `globus_access.txt`, `trial_context.md`).
2. Creates the node-local staging dir.
3. Creates a CLIO workspace with `root_path` = the trial dir.
4. Creates a session (`mode=edit`, `approval_mode=bypass`, the pinned model).
5. Starts SSE capture (`logs/session/events.sse`) and dispatches the **byte-identical frozen prompt**
   (`baseline_e3_prompt.md`).
6. Polls every 15 s. It stops on `idle`, `error`, `cancelled` or `waiting_*`; a waiting state is cancelled, never
   answered. At 6600 s it cancels, the same limit as the baseline.
7. Retains in `logs/session/`:
   - the session JSON, the full `/export`, `/messages`, `/trace` and `/interactions`;
   - the permissions at the end;
   - the server-side transcript and semantic-trace files for the session;
   - the server log;
   - `capabilities.json` (service/API version), `clio_instance.json`, the config snapshot and `session_record.json`.
8. Runs the shared staging snapshot, output provenance, source re-verification, boundary audit and verification, plus
   `collect_clio_metrics.sh`. The audit covers paths, job scripts and logs, Globus, and memory/recall calls.

**Record manually** in `logs/session/manual_record.md`:
- CLIO Desktop version (from the Desktop's About/Versions panel), or "Desktop not connected";
- the tunnel command used, if any.

## 5. After the trial
- Stop the server: `CLIO_AGENT_HOME=$E3/.agent_runtime/clio/E3-clio-trial_NN CLIO_PORT=P <prefix>/bin/clio stop`.
  Then `exit` the allocation.
- Do not delete `.agent_runtime/clio/E3-clio-trial_NN/`. It is the instance record.
- Invalid or interrupted attempt: leave the trial directory as is, record `invalid` and the reason in the manifest
  (appended fields), and use a new numbered attempt only as decided by the researcher. Never overwrite or rerun a used
  trial directory; the runner refuses.

## Parity with the baseline (what is identical / what differs)
| Aspect | Baseline | CLIO |
|---|---|---|
| Packet, prompt, catalog, pin | prepared by `prepare_baseline_trial.sh` | same script, `--system clio`; prompt byte-identical |
| Storage access | Globus-only private source via `staging-inbox/`; archive by POSIX; `$TMPDIR` staging | same helpers, same rules |
| Agent host | 8 CPU / 32 GB / 2 h job | same contract (manual `salloc`) |
| Session limit | 6600 s | 6600 s (runner cancels) |
| Permissions | `--dangerously-skip-permissions` | `approval_mode=bypass` set at creation; the runner never answers |
| Web | none | no MCP servers (no web search) |
| Model | `claude-fable-5-1` via Claude Code 2.1.295 | `claude-fable-5-1` via CLIO's Claude Agent SDK transport (`claude-agent-sdk` 0.2.164); harness differs by design |
| Session record | stream-json, transcript | `/export`, `/messages`, `/trace`, SSE events, server transcript/trace files |
| Audit / verification / scoring | shared scripts | shared scripts (`--system clio`) plus the single-user-message check |

Which machine does what:
- **CHPC compute node (allocated):** runs the CLIO server and every tool process. It is the only component that reads
  GitHub and Globus, and the only one that writes E3 trial files.
- **E3 trial directory:** holds all persistent records.
- **Windows Desktop:** control/observation interface only. It reaches the same loopback API through the tunnel, and it
  has no E3 storage, GitHub or Globus role.
