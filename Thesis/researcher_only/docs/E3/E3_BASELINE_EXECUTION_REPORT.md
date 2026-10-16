# E3 baseline execution report

Researcher-side. Period 2026-10-10T05:20Z → 16:45Z (UTC). **E3 is baseline-complete: 5 valid trials (01, 03, 04, 05, 02R), all accepted.
The baseline-versus-CLIO comparison remains incomplete. CLIO was not run, modified or configured.**
Results and evaluation: `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/evaluation_figures/E3_baseline_prelim/E3_BASELINE_EVALUATION.md`.

## 1. Frozen configuration (`freeze/baseline_freeze.json`, sha256 `e13d2fd6846a2a8814a821c17808575a500073b7e17e434ec4b4d300a868ec35`, frozen 05:28:03Z)
| Item | Value |
|---|---|
| Task / prompt | `E3-SPC-v1`; prompt sha256 `63f84f79301da3a5362a457017d3df4ede1342c5ca5bd122b069f83424e91c20` (= `task/task_prompt.md` at the pin) |
| Control repository | `DaisyQuach/daisy-e3-distributed-context-control` (private), commit `62954055b4e848f2155258c5b8c628eab97c8586` (catalog v5) |
| Packet | generated fresh per trial at launch from the pin into `agent-inputs/` (read-only); no legacy inputs |
| Globus | source `6dcea62e-130d-47a9-8b77-80fba6f58693` (daisy-e3-private-source; MANIFEST.sha256 `d856bed2…cc53`), destination `7cf0baa1-…` limited to `staging-inbox/`; CLI 3.43.0 |
| Claude Code | 2.1.295, sha256 `4503bfe11a6c7fcc1e0b39b5e0d347c04248f750b03b0977b3ad6b531fe6f358`; model `claude-fable-5-1`; effort: harness default (CLAUDE* scrubbed, `--export=NONE`); timeout 6600 s |
| Runtime | `load_morphorm_e3.sh` sha256 `25b77e66…`; runtime tree fingerprint and Cubit manifest hashed in the freeze |
| Slurm contract | hochhalter-np, 1 node, 8 CPU, 32 GB, 2 h, `--export=NONE` |
| Audit / runner | `audit_boundary.sh` `05e49d4e…`; runner `b25d3c2d…`; all 37 automation files in `freeze/automation_files.sha256` (verified by every job before launch) |
| Scoring | `E3_SCORING_SCOPE.md` (frozen) + E1 rubric `ACCEPT-EX8-v1` by reference |

## 2. Jobs (`submission_manifest_all_attempts.tsv`)
| Label | Slurm job | Node | Window (UTC) | Slurm state | Terminal state | Decision |
|---|---|---|---|---|---|---|
| preflight (unscored) | 16173723 | notch204 | 05:30:01–05:30:54 | COMPLETED 0:0 | PASS 25/25 | – |
| trial_01 | 16173743 | notch274 | 05:38:04–06:09:53 | COMPLETED 0:0 | valid | accepted |
| trial_02 | 16173744 | notch274 | 06:09:59–06:38:11 | FAILED 12:0 | **audit_failed** | excluded |
| trial_03 | 16173745 | notch274 | 06:38:16–07:08:18 | COMPLETED 0:0 | valid | accepted |
| trial_04 | 16173746 | notch274 | 07:08:23–07:40:32 | COMPLETED 0:0 | valid | accepted |
| trial_05 | 16173748 | notch274 | 07:40:38–08:10:56 | COMPLETED 0:0 | valid | accepted |
| postprocess | 16173749 | notch204 | 08:11:08–08:12:06 | COMPLETED 0:0 | – | – |
| trial_06 = **02R** | 16176007 | notch272 | 14:58:59–15:31:48 | COMPLETED 0:0 | valid | accepted |
| postprocess_r1 (6 attempts) | 16176008 | notch272 | 15:31:54–15:33:06 | COMPLETED 0:0 | – | – |

Agent-submitted Morphorm jobs: 16173783, 16173993 (trial_02), 16174062, 16174185, 16174284, 16176085, all COMPLETED.
Trials ran one at a time (`afterany` chain), because the frozen audit fails a trial when anything else under the E3 root or in the
account's Globus task list changes during its window.

## 3. Where the evidence is
| What | Path |
|---|---|
| Freeze, hash lists, replacement addendum | `setup/baseline_execution/freeze/` |
| Preflight script, out/err, sacct, report | `setup/baseline_execution/preflight/` |
| Job scripts | `setup/baseline_execution/jobs/` (`e3_baseline_counted_trial.sh`; `_r1.sh` for 02R) |
| Per-job live records (start record, environment snapshot, runner log, Slurm out/err, artifact manifest, end record) | `.agent_runtime/baseline/E3-baseline-trial_NN/execution/` |
| Trial evidence (packet, session stream/transcript, staging, provenance, audit, verification, outputs) | `baseline/trial_NN/` (`TRIAL_STATUS.json` = terminal state) |
| Raw accounting exports and record copies | `Thesis/researcher_only/evaluation_figures/E3_baseline_prelim/raw/` (`slurm/sacct_*`, SHA256SUMS) |
| Figures, tables, scores | `Thesis/researcher_only/evaluation_figures/E3_baseline_prelim/`, `Thesis/researcher_only/evaluation_figures/E3-baseline-*.png`, `Thesis/researcher_only/scores/E3-baseline-*` (moved there 2026-10-10 at researcher request) |

## 4. Audit findings and protocol deviations
1. **trial_02 audit FAIL + session failure.** Claude OAuth refresh failed mid-session (exit 1, no deliverables). The audit also
   flagged two reads of the session's own persisted tool-output file under `.agent_runtime/.../claude_config/.../tool-results/`.
   Its content was permitted candidate-archive text. Retained as `audit_failed`; not scored; not rerun in place.
2. **Replacement 02R (researcher request).** Run in the new directory `trial_06`, because the frozen runner accepts only
   `trial_NN`. Before submission: a non-model `auth status` check passed (no token rotation), the token was valid for about 7.9 h,
   and a dry run passed. Same freeze, prompt, model, effort, pin, Globus, runtime, resources and audit. Changed execution scripts
   (`jobs/e3_baseline_counted_trial_r1.sh`, `postprocess_r1/`) and the workspace-parity note are in
   `freeze/replacement_addendum_r1.json`.
3. **Known audit gap (unchanged, for CLIO planning):** `audit_boundary.sh` treats the session's own `claude_config/` as forbidden,
   although the harness itself directs the agent there for large outputs. E1 corrected this after its trial 02; E3's frozen audit
   was deliberately not changed. A change would be a new, recorded researcher decision applied before CLIO, identically to both systems.
4. **Sequential execution** instead of five concurrent jobs (reason in §2).
5. **Scoring adapter:** the E3 completed verification was mapped to the E1 scorer's `packet_verification` field (evaluation §2).
6. **Figure re-layout:** after review, fig3 and fig5 of the six-attempt pass were re-laid-out from the same data; job originals kept.
7. **Results location (researcher request, 2026-10-10):** results moved to `Thesis/researcher_only/` (sha256-verified copy, then removed
   from the runs folder). The postprocessing job scripts (`postprocess/` and `postprocess_r1/e3_baseline_postprocess.sbatch`) now write to
   `Thesis/researcher_only/evaluation_figures/E3_baseline_prelim[_<UTC>]/`; only the `OUT=` line and its comment changed. The versions that
   actually ran (jobs 16173749, 16176008) are kept byte-identical in `postprocess*/as_run/` and match `freeze/execution_scripts*.sha256`.

8. **Documentation relocation (researcher request, 2026-10-10T17:3xZ):** 14 E3 reports moved byte-identical to `Thesis/researcher_only/docs/E3/`
   (`MOVED_FILES.tsv`); pointer files left at the old paths. Indexes added: `Thesis/researcher_only/docs/E3/README.md`, `Thesis/automation/E3_README.md`;
   `Thesis/README.md` and `Thesis/researcher_only/docs/E3_PLAN.md` updated (pre-update copies in `Thesis/researcher_only/docs/E3/pre_update_copies/`). E3 `automation/`,
   `setup/baseline_execution/`, data/hash files and CLIO documents stay in place (frozen paths). Post-move audit: frozen automation 37/37,
   freeze json, E3 tree (5007 files) and E1/E2/common trees unchanged; sources and originals PASS; all script-read `setup/` paths present;
   30 scripts parse; runner dry run passes every check up to workspace freshness; `verify --completed` PASS for 01/03/04/05/06; E1 preflight
   PASS; the frozen audit still classifies reads of the new and old report locations as FORBIDDEN and the loader as allowed.
   `postprocess_r1/make_figures.py` was edited after job 16176008 (figure re-layout); the as-run version, rebuilt by reversing that edit,
   matches the recorded hash: `setup/baseline_execution/postprocess_r1/as_run/make_figures.py`.
9. **Docs folder moved (researcher request, 2026-10-10):** `Thesis/docs/` (23 files incl. `E3/`) copied sha256-verified to
   `Thesis/researcher_only/docs/`; pointer files left in `Thesis/docs/` for the five E1/E2 documents; all E3 pointers and indexes updated.
   Agents are no more able or unable to read it (same account); the E1/E2 transcript audit pattern `researcher_only` now also covers it.

## 5. Integrity (2026-10-10T16:4xZ)
- E1, E2, ThesisExperiments, Morphorm, Morphorm_Full_Examples_Tests, Morphorm_ground_truth and morphorm_manuals all show **0
  differences** against the `setup/integrity/*.20261010T031425Z.snapshot` records (path, type, size, mode, mtime, ctime).
- `Thesis/researcher_only` and `Thesis/common`: 0 entries newer than the freeze. These were only read (scorer, spec, reference).
- E3 `clio/`: 0 entries newer than the freeze. No CLIO component, pilot, server, runner or local-PC component was touched.
- Source collections PASS, candidate archive has 0 write bits, originals 30/30 and 5/5 PASS (`verify_readonly_sources.sh --with-originals`).

## 6. Rule for any further attempt
No trial may be rerun or replaced except as a **new recorded attempt** under the protocol: a new fresh workspace, a new job, and a
manifest/addendum entry. Every earlier attempt stays as recorded. trial_02 remains part of the record as an excluded attempt.
