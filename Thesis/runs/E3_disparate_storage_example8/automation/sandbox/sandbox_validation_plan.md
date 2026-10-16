# E3 sandbox validation plan

**Status (2026-10-10 UTC, procedural-access update):** technical isolation is *not adopted for the current E3 protocol*.
Section A remains a record of the login-node visibility check. Section B is no longer a prerequisite for a counted E3
trial. It lists what would be needed if technical isolation were adopted later. E3 uses the procedural researcher-only
policy of E1/E2 (`setup/E3_PROCEDURAL_ACCESS_UPDATE.md`). The sandbox does not technically isolate Slurm jobs submitted
under the same account (A10).

Every validation step is non-scored and harmless: no model call for a trial, no Morphorm or Cubit execution, no
scientific output. The probe (`sandbox_probe.sh`) only stats and lists paths and, with `--with-loader`, loads modules.

## A. Done (2026-10-10, notchpeak1 login node, no allocation) — record: `validation_record_login_node.txt`
| # | Check | Result |
|---|---|---|
| A1 | bubblewrap runs unprivileged (OS package, not setuid) | PASS |
| A2 | permitted E3 paths visible: trial dir, `agent-inputs/`, `work/`, candidate archive incl. `example_13`, E3 loader | PASS |
| A3 | `agent-inputs/` not writable; `work/` writable (access(2) checks only) | PASS |
| A4 | not visible: E3 `researcher_only/`, E3 `setup/`, other E3 automation, `Morphorm_ground_truth`, E1, E2, `ThesisExperiments`, `Morphorm_Full_Examples_Tests`, Morphorm source/docs, original manuals, `Thesis/researcher_only`, legacy `agent_inputs/`, other trials | PASS |
| A5 | listings: Daisy shows only `Thesis`; `Thesis/runs` only E3; E3 root only `automation baseline chpc_candidate_archive`; no other home directories; `HOME` is a tmpfs | PASS |
| A6 | E3 loader works inside: Morphorm runtime and Cubit resolve to E3 copies, CHPC `mpiexec`; no `ThesisExperiments` entry; `ldd`: 0 missing libraries | PASS |
| A7 | pinned Claude Code visible at `/opt/e3/bin/claude`, `--version` = 2.1.295 | PASS |
| A8 | `--scheduler none`: no `sbatch`, no munge socket, no Slurm tree | PASS |
| A9 | launcher refuses: trial without `agent-inputs/`; `researcher_only` as a mount; Daisy root (ancestor of ground truth); account home | PASS |
| A10 | `--scheduler direct`: read-only `squeue` authenticates from inside | observed — **this is the escape path** (limitation 1) |
| A11 | outbound ssh to a login node from inside (batch mode, no keys) | refused (rc 255) |

## B. Only if technical isolation is adopted later (not done; not required for the current E3 protocol)
| # | Step | Pass criterion |
|---|---|---|
| B1 | Researcher decision on job isolation (`setup/GROUND_TRUTH_ISOLATION_ACTION_REQUIRED.md`) | a recorded decision |
| B2 | If the broker design is chosen: implement a researcher-side submission broker outside the sandbox; agent runs with `--scheduler none`; the broker submits each agent job with its batch script executed through `launch_e3_sandbox.sh --scheduler none` on the compute node | probe run as a broker-submitted job shows A2–A5 and no munge/Slurm inside the job |
| B3 | Repeat A1–A9 and A11 inside a non-scored agent-host allocation (frozen account/partition, short time) on a compute node | same results as A |
| B4 | Inside that allocation: `$SLURM_TMPDIR`-based staging dir mounted read-write via `--staging-dir` | visible, writable; nothing else under `$SLURM_TMPDIR` visible |
| B5 | Decide Cubit licensing inside the sandbox (mount `$HOME/.config/Coreform` read-only, or mesh outside the agent's sandbox) and validate `cubit -batch` on a trivial non-scientific journal | licensed batch run exits 0 |
| B6 | Integrate the launcher into `run_baseline_e3_trial.sh` (and the CLIO runner) and re-run the plumbing tests on a scratch copy with the test double | audit PASS, sources unchanged |
| B7 | Negative test inside the integrated sandbox (test double): attempt to read `Morphorm_ground_truth`, `researcher_only/`, E1 | path does not exist (ENOENT), audit records it |

B1 is resolved by the 2026-10-10 researcher decision: technical isolation is not adopted and E3 uses the procedural policy.
B2–B7 are not planned. No E3 document claims technical isolation, and none may unless B2–B7 are implemented and pass.
