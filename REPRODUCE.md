# How to set up and run the official E1–E3 experiments

This guide covers the official (counted) thesis study only: Claude Code baseline vs CLIO with factorio-flat 0.5.0,
experiments E1–E3, five counted trials per arm. The non-counted pilots and the clio-core engine tests are not part of
it and are not in this repository.

Everything below is how the counted trials were actually run (baseline 2026-10-09/10, CLIO 2026-10-13). Each step
names the script that does it. The scripts are in `Thesis/` exactly as they were used.

---

## 1. Setup used

### Compute
| Item | Value |
|---|---|
| Cluster | CHPC notchpeak (University of Utah), Rocky Linux 8 |
| Slurm account / partition / QOS | `hochhalter-np` / `hochhalter-np` / `hochhalter-np` |
| Agent host (one Slurm job per agent session) | 1 node, 1 task, 8 CPU, 32 GB, 02:00:00 (`Thesis/automation/lib/common.sh`) |
| Session limit | 6600 s (1 h 50 min), so evidence can be collected inside the 2 h job |
| Morphorm jobs | submitted by the agent itself with `sbatch`, same account and partition, 1 node × 8 CPU, 32 GB, 02:00:00 |
| Node-local scratch (E3 staging) | `$TMPDIR/e3/<system>/<trial_id>` inside the agent-host job |

### Scientific software (the agent's only approved interface)
| Item | Value |
|---|---|
| Loader | `source Thesis/common/scripts/load_approved_software.sh` (E3: `runs/E3…/automation/environment/load_morphorm_e3.sh`). The Thesis loader delegates to `/uufs/chpc.utah.edu/common/home/chet/Daisy/ThesisExperiments/common/scripts/load_approved_software.sh` (frozen approved-runtime loader, not in this repo) |
| Morphorm | `morphorm/approved-runtime`: engine `0d767ac7`, analyze `60c5e37c`; modulefile SHA-256 `dec9d78b…3e58`, inventory SHA-256 `fa0d97b9…e4d2`; CHPC `gcc/11.2.0`, `openmpi/5.0.3` |
| Mesher | Coreform Cubit 2026.8 (`cubit-edu/2026.8`, modulefile SHA-256 `9c5bc2f9…19ad`) |
| Documentation given to the agent | Morphorm User Manual and Theory Manual PDFs only (not in this repo: `*.pdf` excluded). Never the Examples Manual |

Full hashes are in `Thesis/common/frozen_example8/formal_configuration.md` and `frozen_example16/formal_configuration.md`.

### Frozen task packets and references
| | E1 | E2 | E3 |
|---|---|---|---|
| Workflow | Morphorm Example 8 (half cantilever, Helmholtz filter with symmetry plane, 50 OC iterations) | Example 16 (full cantilever; Stage 1 = 20 iterations with restart, Stage 2 = 40 more from the saved design) | Example 8 |
| Frozen packet | `Thesis/common/frozen_example8` (`FROZEN-EX8-v1`) | `Thesis/common/frozen_example16` (`FROZEN-EX16-v1`) | `E3-SPC-v1`: control repo `DaisyQuach/daisy-e3-distributed-context-control` @ `62954055b4e848f2155258c5b8c628eab97c8586` (catalog v5) + private Globus guest collection `6dcea62e-130d-47a9-8b77-80fba6f58693` + read-only POSIX archive `runs/E3…/chpc_candidate_archive` |
| Sessions per trial | 1 | 2 (Session A, then a new Session B) | 1 |
| Acceptance spec | `ACCEPT-EX8-v1` | `ACCEPT-EX16-v1.1` | `ACCEPT-EX8-v1` |

### Agent systems
| | Claude Code baseline | CLIO |
|---|---|---|
| Harness | Claude Code **2.1.295**, headless | clio-agent **0.9.5b5.post2** (service + HTTP API), clio-core **iowarp-core 2.2.1** (private daemon per session), claude-agent-sdk 0.2.164, driving the **same Claude Code 2.1.295 binary** |
| Model | `claude-fable-5-1` | `claude-fable-5-1` |
| Effort | CLI default | none sent (CLI default) |
| Permissions | `--dangerously-skip-permissions` | `approval_mode=bypass` on the session and the message |
| User messages | the frozen prompt only | the frozen prompt only (0 nudges) |
| Blueprint | – | **factorio-flat 0.5.0**, frozen copy `Thesis/automation/clio/blueprints/factorio-flat-0.5.0/` (tree checksum `6076c026…e56075`, provenance in `factorio-flat-0.5.0.PROVENANCE.md`) |
| MCP servers | none | none configured (`mcp.yaml` empty; the blueprint's own `web` tool was mounted but never called) |
| Runtime tuning | – | stream idle TTL 3600 s, MCP call timeout 3600 s, turn watchdog 5400 s |
| Isolation | new process, new session UUID, own `CLAUDE_CONFIG_DIR` per session | new CLIO home, Claude config dir and clio-core daemon per session |

Exact headless baseline command:
```
claude --print --verbose --output-format stream-json --model claude-fable-5-1 --dangerously-skip-permissions \
  --session-id <uuid> --disable-slash-commands --no-chrome -- "<prompt>"
```
CLIO settings and every value above: `Thesis/automation/clio/clio_trial_config.env`. The CLIO deployment config used in
every counted session is in `setup/clio_deployment_config/` (`config.yaml`, `mcp.yaml`, installed blueprint list).

The full methods (parity table, telemetry, scoring rules) are in `THESIS_NOTES_methods_and_evaluation.md`, Parts A and B.

---

## 2. One-time preparation

The scripts use absolute CHPC paths. Place the tree at `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis` (the E1/E2
scripts find their root from their own location, but the E3 scripts, frozen loaders and Slurm job files name that path),
or change those paths consistently before running.

1. **Restore what is not in this repo** (`EXCLUDED_FILES.md`, `PUBLIC_EXCLUSIONS.md`; the Morphorm manuals, example
   files and `runmorphorm.py` come with a licensed Morphorm installation): the manual PDFs in the frozen packets, the E3 software
   copies in `runs/E3…/automation/environment/` (Cubit, Morphorm runtime, Globus CLI) and the frozen approved-runtime
   loader under `ThesisExperiments/`.
2. **Claude Code login**: `claude` → `/login` with the subscription account. A login lasts about 14 h
   (`claudeAiOauth.expiresAt` in `~/.claude/.credentials.json`). The runners copy it into each session's isolated config
   and delete the copy afterwards. Check that it will outlast a batch before starting one.
3. **Pinned Claude Code 2.1.295** at `~/.local/share/claude/versions/2.1.295`:
   ```bash
   curl -fL -o ~/.local/share/claude/versions/2.1.295 \
     https://downloads.claude.ai/claude-code-releases/2.1.295/linux-x64/claude
   chmod 755 ~/.local/share/claude/versions/2.1.295
   sha256sum ~/.local/share/claude/versions/2.1.295   # 4503bfe11a6c7fcc1e0b39b5e0d347c04248f750b03b0977b3ad6b531fe6f358
   ```
   Newer Claude Code versions delete old binaries from that folder automatically. Check the file (256,113,848 bytes)
   before every batch.
4. **CLIO install** (CLIO arm only) at `CLIO_PREFIX=/uufs/chpc.utah.edu/common/home/chet/Daisy/clioSessions/CLIOruntime`
   with the CLIO installer, clio-agent 0.9.5b5.post2 / iowarp-core 2.2.1 (`preflight_clio.sh` checks the versions). The
   launcher copies `$CLIO_PREFIX/user/config/` into every deployment, so it must hold:
   - `config.yaml` and `mcp.yaml` as in `setup/clio_deployment_config/` (provider `claude_code`, model `claude-fable-5-1`,
     no MCP servers);
   - the installed marketplace blueprints, including `agent-blueprints/factorio-flat/` (the stock 0.4.0 is replaced in
     each deployment by the frozen 0.5.0 copy from `CLIO_BLUEPRINT_SOURCE_DIR`).

   Note: on CHPC this `user/config` directory was emptied on 2026-10-15, after the official runs. Restore it from
   `setup/clio_deployment_config/` and a fresh install before re-running the CLIO arm.
5. **E3 sources**: SSH read access to the control repository (cloned non-interactively at the pinned commit), a logged-in
   Globus CLI with access to the guest collection, and the read-only POSIX archive. `runs/E3…/automation/verify_readonly_sources.sh`
   checks them.
6. **Fresh trial packets.** The trial folders in `Thesis/runs/` hold the finished trials, and every prepare script refuses
   to write into a folder that has content. To run again, start from a copy of the tree with the `runs/*/baseline/trial_*`
   and `runs/*/clio/trial_*` folders, `researcher_only/scores/` and `researcher_only/session_evidence/` removed (keep the
   CHPC originals untouched), then prepare new packets as below.

---

## 3. Running the Claude Code baseline

### E1 and E2 (`Thesis/automation/`, README there)
Run from a login node; each session becomes its own agent-host `sbatch --wait` job.
```bash
cd Thesis/automation
./prepare_trial.sh --experiment e1-example8 --all-planned        # planned packets trial_01..05
./prepare_trial.sh --experiment e2-example16 --all-planned
./preflight.sh --experiment e1-example8                          # no model call
./run_e1_baseline.sh --trial 1 --dry-run                         # writes the launch plan only
./run_e1_baseline.sh --trial 1 --execute-counted                 # one trial
./score_researcher_only.sh --trial-dir ../runs/E1_uninterrupted_example8/baseline/trial_01 --figures
./run_e2_baseline.sh --trial 1 --execute-counted                 # Session A -> interlock -> new Session B
./score_researcher_only.sh --trial-dir ../runs/E2_interrupted_recovery_example16/baseline/trial_01 --figures
./run_all_planned_baselines.sh --experiment e1-example8 --execute-counted   # or: five trials in a row
```
Each run does: preflight → planned-packet check → launch → evidence collection → completed-packet check → manifest
status. The official baseline batches' logs are `Thesis/researcher_only/batch_logs/e1_batch_*.log`, `e2_*.log`.

### E3 (`Thesis/runs/E3_disparate_storage_example8/`)
Each trial is one self-contained Slurm job (the runner never calls `sbatch` itself):
```bash
cd Thesis/runs/E3_disparate_storage_example8
sbatch setup/baseline_execution/jobs/trial_01.sbatch     # official jobs: trial_01..05 chained with afterany, trial_06 = 02R
```
`trial_NN.sbatch` calls `setup/baseline_execution/jobs/e3_baseline_counted_trial.sh`, which checks the freeze
(`freeze/baseline_freeze.json`) and then runs `automation/baseline/run_baseline_e3_trial.sh --execute-counted`: clone the
control repo at the pin, prepare `agent-inputs/`, create node-local staging, launch headless Claude Code with the frozen
prompt, record staging/provenance, boundary audit, metrics and `verify_baseline_trial.sh --completed`. Submission
records: `setup/baseline_execution/submission_manifest*.tsv`. Scoring and figures: `setup/baseline_execution/postprocess/`
(E1 scorer and spec, as recorded in `researcher_only/docs/E3/E3_BASELINE_EXECUTION_REPORT.md`).

---

## 4. Running the CLIO arm

All CLIO automation is in `Thesis/automation/clio/` (README there). It reuses the baseline's `lib/common.sh`,
`preflight.sh`, `verify_trial_packet.sh`, `collect_baseline_evidence.sh` and `score_researcher_only.sh` unchanged.
```bash
cd Thesis/automation/clio
./prepare_clio_trial.sh --experiment e1-example8 --all-planned
./prepare_clio_trial.sh --experiment e2-example16 --all-planned
./preflight_clio.sh --experiment e1-example8                     # install, pins, blueprint, credentials; no model call
# optional, no model call: start a deployment on a compute node, create a session, read every setting back, stop
./launch_clio_session.sh --trial-dir ../../runs/E1_uninterrupted_example8/clio/trial_01 --run-id E1-example8-clio-01 \
  --session-label session_main --prompt-file ../../runs/E1_uninterrupted_example8/clio/trial_01/agent_inputs/task_prompt.md --validate-deployment
./run_e1_clio.sh --trial 1 --dry-run
```
The official CLIO trials were run with one driver, which runs E1 trials 1–5, then E2 1–5, then E3, one at a time,
and scores each trial as soon as it ends:
```bash
nohup ./run_counted_thesis_clio.sh > /dev/null 2>&1 &          # optional: --from e2:1 to start later in the order
```
What it runs per trial:
- before each trial, a one-line `claude-fable-5-1` call in a 5-minute job to check the provider accepts calls (retries
  every 15 min for up to 6 h);
- E1/E2: `run_e1_clio.sh` / `run_e2_clio.sh --trial N --execute-counted`, then `../score_researcher_only.sh --figures`;
- E3: `sbatch --wait` (agent-host contract) of `runs/E3…/automation/clio/run_clio_e3_trial_v2.sh --trial-dir …/clio/trial_NN --execute-counted`,
  then `score_e3_clio.sh`;
- it stops at the first trial that does not end cleanly. Log: `researcher_only/batch_logs/clio_counted_*.log`.

Per session the launcher builds a fresh deployment under `.agent_runtime/<run_id>/<label>/` (CLIO home, isolated Claude
config, private clio-core, `bin/claude` → 2.1.295) inside the agent-host job. The API runner
(`lib/clio_session_runner.py`) checks health, creates the workspace and session, attaches the blueprint, reads every
setting back and refuses to continue on a mismatch, sends the frozen prompt verbatim, polls to the end, and exports the
session. `collect_clio_evidence.sh` and `verify_clio_supplement.sh` then write the baseline-shaped records plus `clio/`.

---

## 5. Replacements and exclusions

A trial stopped by a non-agent cause (provider usage limit, expired login, infrastructure) is kept, excluded, and
replaced, never rerun in place:
- E1/E2: `prepare_trial.sh` / `prepare_clio_trial.sh --trial N --suffix R`, then the run script with `--suffix R`
  (CLIO wrapper used officially: `analysis/official_thesis_clio/resume_with_replacement.sh`);
- E3: a new trial folder (`trial_06`, `trial_07`), as the baseline did (wrappers `run_e3_remaining*.sh`).

Official exclusions and their causes: `THESIS_NOTES_methods_and_evaluation.md` §C2 and
`analysis/official_thesis_clio/data/trial_attempts.csv`.

---

## 6. Scoring and analysis

- **Scientific decision** (the primary outcome): `score_researcher_only.sh` → `researcher_only/scores/<run_id>/score.{json,md}`.
  Accept: final compliance and density within 1e-6 of the reference; review up to 1e-2 / 0.05; otherwise rejected.
- **Telemetry and comparison** (descriptive):
  ```bash
  cd analysis/official_thesis_clio
  python3 official_aggregate.py        # -> data/*.csv (per run, per session, attempts)
  python3 official_compare.py          # -> data/stats.csv, figures/H1–H6 (ratio of means, bootstrap CI, exact permutation p)
  python3 official_observability.py    # -> observability/
  ```
- **Deck**: `python slides/make_official_slides.py` (needs `python-pptx`; reads `analysis/official_thesis_clio` from its CHPC location `clioSessions/CLIO_E1_API_pilots/official_thesis_clio`) → `slides/CLIO_vs_Claude_Code_official_thesis.pptx`.

These scripts read the CHPC paths listed at the top of each file; point them at your copy if it lives elsewhere.

---

## 7. Things that went wrong before (check these first)
- Claude Code's automatic version cleanup can delete the pinned 2.1.295 binary; launches then fail with an `execve` error.
- An expired login ended CLIO E2-05 Session B with 0 API calls (`ClaudeCodeSignedOutError`).
- Provider usage limits aborted baseline E1-04/04R and E2-02/04; the per-trial provider check exists for this.
- A transient CLI version probe failure made CLIO fall back to a newer CLI (CLIO E1-03); the CLIO supplement catches it.
- E3 boundary audit: CLIO reads its own blueprint skills and tool-output spill files outside the trial root. The
  own-runtime rule (`automation/clio/lib/e3_own_runtime_audit.py`) relabels only those reads (`runs/E3…/clio/README.md`).
- Never edit an automation script while a batch that uses it is running (`Thesis/automation/AUTOMATION_LIMITATIONS.md` §13).
- Morphorm job times depend on the node (about 10 min on notch351 vs 17–18 min on other nodes). Wall-time differences
  between arms partly reflect node assignment.
- `Thesis/automation/README.md` still names the original pin 2.1.292 in places; the counted runs used 2.1.295
  (`lib/common.sh`, researcher decision 2026-10-09).
