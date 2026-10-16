# E3 baseline — evaluation and preliminary results (baseline only)

Location: `Thesis/researcher_only/evaluation_figures/E3_baseline_prelim/` (moved from the E3 runs folder 2026-10-10 at researcher request).
Paths below: `scores/` = `Thesis/researcher_only/scores/`; per-trial figures = `Thesis/researcher_only/evaluation_figures/`; `baseline_prelim_r1_all_attempts/` = this folder; `baseline_prelim/` = `superseded_first_pass_5_attempts/` here.

Researcher-only. Evaluated 2026-10-10 UTC. Configuration: `E3-BASELINE-FREEZE-v1` (freeze sha256 `e13d2fd6…ec35`), unchanged
for all six attempts. CLIO was not run; **nothing here is a baseline-versus-CLIO comparison.**

## 1. Outcome at a glance
| Attempt | Directory | Slurm job | Terminal state | Scientific decision (E1 rubric `ACCEPT-EX8-v1`) |
|---|---|---|---|---|
| 01 | `baseline/trial_01` | 16173743 | valid | **accepted** |
| 02 | `baseline/trial_02` | 16173744 | **audit_failed — excluded** | not scored |
| 03 | `baseline/trial_03` | 16173745 | valid | **accepted** |
| 04 | `baseline/trial_04` | 16173746 | valid | **accepted** |
| 05 | `baseline/trial_05` | 16173748 | valid | **accepted** |
| 02R | `baseline/trial_06` (replacement for 02) | 16176007 | valid | **accepted** |

**5 valid and accepted trials (01, 03, 04, 05, 02R); 1 excluded attempt (02), shown in every operational table and figure.**
Combined table: `scores/E3_baseline_scores_and_telemetry.csv`.

## 2. How the evaluation was done
- **Scorer and rubric unchanged from E1** (as `E3_SCORING_SCOPE.md` §1 requires): `Thesis/researcher_only/ground_truth/tools/score_trial.py`
  with `Thesis/researcher_only/ground_truth/example_8/reference_case/acceptance_spec.json` (`ACCEPT-EX8-v1`, reference policy
  `symmetry_honored_variant`; accept tolerances: final-compliance rel. diff ≤ 1e-6, density max abs diff ≤ 1e-6). Both read only.
- Python: the E3 runtime copy (`automation/environment/runtime/morphorm/python`, numpy 2.3.1, netCDF4 1.7.2), bytecode writing off.
  The obsolete `ThesisExperiments` runtime the E1 wrapper used was not used.
- Each trial was scored through a read-only scratch view (symlinks + a one-line manifest giving the run ID). No trial file was changed by scoring.
- **Adapter (recorded):** the E1 scorer reads E1's `logs/packet_verification.json`. E3 records the equivalent completed-trial
  verification in `provenance/verification.txt` (36 checks, verdict PASS for every valid trial). A first pass without the adapter
  gave `needs_review` with that single reason and every scientific check passing; it is kept in
  `scores/<run>/pass1_without_E3_verification_adapter/`. The second pass maps the E3 verdict to `result: verified`
  (`scores/<run>/packet_verification_adapter.json`, with the source file's sha256).
- Only the decision word was written to each trial manifest (`e3dc_scoring_decision: accepted`, `e3dc_status: scored`; pre-scoring
  copies in `scores/<run>/manifest.pre_scoring.yaml`), as in E1. trial_02 was not scored and its manifest was not changed.

## 3. Scientific results (valid trials only)

Final topology was checked node by node (nodes matched by coordinates) against both researcher-side Example 8 reference runs: the accepted
`symmetry_honored_variant` (max |Δ density| 0.0, mean 0.0 for every valid trial) and the `canonical_shipped_deck` (max 0.93, mean 0.21 — expected,
that full-domain deck lacks the required symmetry treatment).

| Attempt | Iterations | Final compliance F | Rel. diff vs reference | Max nodal density diff | Generated config | Symmetry plane in filter | Mesh checks |
|---|---|---|---|---|---|---|---|
| 01 | 0–50 (stop message present) | 104 470.1 | 0.0 | 0.0 | 34/34 | yes | 8/8 |
| 03 | 0–50 | 104 470.1 | 0.0 | 0.0 | 34/34 | yes | 8/8 |
| 04 | 0–50 | 104 470.1 | 0.0 | 0.0 | 34/34 | yes | 8/8 |
| 05 | 0–50 | 104 470.1 | 0.0 | 0.0 | 34/34 | yes | 8/8 |
| 02R | 0–50 | 104 470.1 | 0.0 | 0.0 | 34/34 | yes | 8/8 |

- Every valid trial **reproduces the E1 symmetry-honored reference exactly**: identical compliance history at all 51 iterations and
  identical final density field. This is the same scientific outcome E1 obtained, now reached with the documentation, specification
  and related examples distributed across a private Globus collection, a POSIX candidate archive and a private GitHub repository.
- Symmetry treatment (scoring scope §3.2) is correct in all five: half-domain mesh with `ss_sym`, symmetry boundary condition, and the
  symmetry plane present in the generated Helmholtz filter configuration.
- Figures: `evaluation_figures/E3-baseline-<run>_final_iteration50_vs_symmetry_honored_variant.png` (trial vs reference, E1 render
  script), `baseline_prelim_r1_all_attempts/figures/fig1_E3_compliance_history_valid_trials` and `fig6_E3_topology_grid`.

## 4. Operational observations (all six attempts)
Means over the 5 valid trials (range in brackets):
| Measure | E3 baseline | E1 baseline (for context only) |
|---|---|---|
| Agent session wall time | 30.9 min (29.5–32.2) | 22.0 min |
| Model reasoning & writing share | 37.7 % | 52.9 % |
| Slurm submit & wait share | 56.8 % | 43.1 % |
| Agent-submitted Morphorm job run time | 17.2 min (17.0–17.6) | 9.7 min |
| Turns / output tokens / reported cost | 49 / 52.3 k / $7.40 | 53 / 55.7 k / $7.98 |
| Files staged (private source via Globus / candidate archive) | 14.8 (12.2 / 2.6) | – |
| Globus transfers, bytes, summed transfer time | 13.2, 3.3 MB, 246 s | – |
| Agent time in Globus/staging commands | 66 s (3.6 % of session) | – |
| Agent-host job CPU time / peak RSS | 1.4 min / 0.60 GB (8 CPU, 32 GB allocated) | – |

- **The agent's own time is about the same as E1; the longer session comes from the Morphorm run.** The model's API time
  (mean 699 s) is close to E1's, but the agent-submitted Morphorm job took about 17 min instead of about 10 min with the same
  8-CPU request. The E3 runs were on notch272–274, E1's on notch351. The cause was not investigated; this is not attributed
  to E3's distributed storage.
- **Globus staging is a small cost.** Each valid trial staged 11–13 private-source files by Globus (every one hash-checked
  against the collection manifest) and 0–6 candidate-archive files. "Summed transfer time" adds up the per-transfer submit-to-finish
  intervals, which can overlap. Per scoring scope §4, these are recorded for completeness; no staging-performance claim is made.
- **Selection varied while the result did not.** Trials 04 and 02R staged nothing from the candidate archive; trial 03 staged 6 files.
  The final design was identical either way.
- Scheduling: trials ran one at a time (dependency wait shows as queue in fig2), with 5–12 s queue time once eligible. 02R ran later
  that day on notch272.
- Descriptive only (tokens, cost, turns), as in E1/E2.
- Figures: `fig2_E3_execution_timeline`, `fig3_E3_time_breakdown_by_trial`, `fig4_E3_gantt_representative_trial` (trial 01, by the
  fixed rule "lowest-numbered valid trial"), `fig5_E3_resource_telemetry`; tables in `baseline_prelim_r1_all_attempts/tables/tables.md`.

## 5. Excluded attempt 02 (shown, not counted)
- **Session failed:** after about 28 min the session ended with `Failed to authenticate: OAuth session expired and could not be
  refreshed` (session exit 1). Before that it had staged 16 files (13 Globus transfers) and submitted Morphorm job 16173993, which
  completed (16.9 min). The session never collected the outputs, so there are no deliverables and the completed verification FAILed.
- **Audit FAIL (frozen policy):** two tool calls read the session's own persisted tool-output file under
  `.agent_runtime/.../claude_config/.../tool-results/`. The harness had written it there and pointed the agent to it. The content
  was permitted candidate-archive text, not researcher-only material. This is the same false-positive class E1 corrected for its
  trial 02; the frozen E3 audit lacks that correction. It remains `audit_failed`. It cannot be counted in any case, because of the
  authentication failure.
- Telemetry for 02 (turns 1, output tokens 0) reflects the error result record, not the work done; its transcript-based time
  breakdown is shown in fig3.

## 6. What cannot yet be concluded
- No baseline-versus-CLIO comparison: CLIO trials have not been run. CLIO must use this same frozen configuration.
- No staging-performance claim (scoring scope §4).
- n = 5 valid trials; telemetry is descriptive.

## 7. Files
| Path (see location note at top) | Content |
|---|---|
| `scores/E3-baseline-{01,03,04,05,02R}/` | `score.json`, `score.md`, scorer stdout, generated-config check, adapter record, pass-1 record, pre-scoring manifest |
| `scores/E3_baseline_scores_and_telemetry.csv` | one row per attempt (decision + measured values + telemetry) |
| `evaluation_figures/` | per-trial final topology vs reference (5 PNG) |
| `baseline_prelim_r1_all_attempts/` | six-attempt postprocessing (job 16176008): `raw/` (sacct exports and record copies, SHA256SUMS), `data/`, `tables/`, `figures/` (fig3 and fig5 re-laid-out after review; job originals in `figures/as_produced_by_job_16176008/`), `renders/`, `analysis/` |
| `baseline_prelim/` | first five-attempt postprocessing (job 16173749), kept unchanged |
