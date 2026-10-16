# Example 16 — Reference Validation

Compares the rebuilt reference (2026-10-09, jobs 16154331–16154334) with (a) the Examples Manual §7.2.16 and (b) valid historical evidence (read-only):
`Morphorm_ground_truth/Example_16` (2026-10-07: stage 1, corrected restart, superseded shipped restart) and
`experiments_groundTruth/Example16_Restart` (2026-10-04, developer runtime; stage 1 only was cross-checked by the 2026-10-07 package).

## 1. Exact source / formulation identity (no tolerance)

| Item | Result |
|---|---|
| Journal, decks, driver | byte-identical to the canonical files and to the 2026-10-07 `original_inputs/` (`b02676b9…7fca5`, `4193f3b3…9112d`, `951941cc…2da6`, `70bd98ce…2ae35`); corrected deck identical to the 2026-10-07 `corrected_inputs/` deck (`ab736535…c77`, one line changed) |
| Formulation vs manual Listings 7.2.18/7.2.19 | identical except the documentation-keyword spellings (`number_ranks 1`, `problem_update_frequency 1`) — `../SOURCE_AUDIT.md` §4 |
| Example 7 journal relationship | `topology_mech_ex7.jou` differs from `topology_mech_ex16.jou` only in the export file name (`../SOURCE_AUDIT.md` §2a); not executed |
| Mesh | 7/7 checks; node coordinates and connectivity identical (max abs diff 0.0) to the 2026-10-07 mesh |
| Generated configurations | Stage 1 33/33 (`WriteRestart true`); both restarts 36/36 in their own mode (`Iteration 21` vs `Iteration 20`); run-time translations identical to preflight (8/8 each) |
| Checkpoint handling | `initialguess.exo` byte-identical to `stage1/engine_output.exo` in both restarts (`results/*_restart_evidence.json`) |

## 2. Byte-identical artifacts
- `stage1/morphorm_oc_optimizer_diagnostics.txt` ↔ 2026-10-07 `reference_stage_1/`: **identical**.
- `stage1/engine_output.exo` ↔ 2026-10-07 `reference_stage_1/engine_output.exo`: **identical** (SHA-256 `10ceb645…a00b`; the engine output carries no time stamps).
- `restart_corrected_21/morphorm_oc_optimizer_diagnostics.txt` ↔ 2026-10-07 `reference_restart/`: **identical**.
- `restart_shipped_20/morphorm_oc_optimizer_diagnostics.txt` ↔ 2026-10-07 `failed_or_superseded/reference_restart_shipped_deck_restart_iteration20/`: **identical**.

## 3. Expected non-byte-identical derived artifacts
`mesh/topology_mech_ex16.exo` (QA/time-stamp records; numerically identical), analyze `iteration*.exo` outputs, performer logs, `time_v.txt`, `timestamps.txt`, Slurm logs.

## 4. Numerical comparisons (with tolerances)

| Quantity | Rebuilt | 2026-10-07 | Difference | Verdict (tol 1e-6 rel / 1e-6 abs on fields) |
|---|---|---|---|---|
| Stage-1 F₂₀ | 2.360040e5 | 2.360040e5 | 0 | match |
| Checkpoint state 21 `control`, `topology` | — | — | max abs diff 0.0 | match |
| Corrected restart F₀ / F₄₀ | 2.360040e5 / 2.135584e5 | same | 0 | match |
| Corrected final `Topology`, displacements X/Y/Z | — | — | max abs diff 0.0 | match |
| Shipped restart F₀ / F₄₀ | 2.388394e5 / 2.136843e5 | same (superseded run) | 0 | match |
| Shipped final `Topology` | — | — | max abs diff 0.0 | match |

## 5. Comparison with the manual (the manual prints no numbers; Fig. 7.2.37 is pixel-readable only)

| Manual statement (printed p. 545–552) | Restart from iteration 20 (`restart_iteration 21`) | Shipped `restart_iteration 20` |
|---|---|---|
| "resumes from the design saved at iteration 20" | **reproduced** (initial `control` = state 21 = iteration-20 design, diff 0) | **not reproduced** (iteration-19 design) |
| "first restart iteration lands on the same compliance the initial run reached at iteration 20" | **reproduced** (2.360040e5, diff 0) | not reproduced (2.388394e5, +1.20 %) |
| 20 + 40 iterations, "as if it had never been interrupted" | reproduced (overall 60; same trajectory as shipped shifted by one) | one iteration repeated (overall 59) |
| cold start "near 5 × 10⁶" | 4.893235e6 (Stage 1) | same |
| Fig. 7.2.37 (figure-read, ≈0.6 %/px): F₂₀ ≈ 2.4e5, F₆₀ ≈ 2.15e5 | 2.360e5, 2.136e5: within figure resolution | 2.388e5 at the restart point: also within figure resolution — the figure cannot distinguish the two |
| Restart from `topology` (dashed curve) | not run (no shipped deck; out of scope) | — |
| Final topology | no manual figure for Example 16; same truss family as Example 7's Fig. 7.2.18 description (`figures/`) | — |

## 6. Verdict
- Stage 1 and both restarts reproduce the historical executions bit for bit and all stated manual values within figure resolution.
- **Exact manual agreement holds for the corrected restart and fails for the shipped listing** on the one field the manual states explicitly (resume
  iteration). This discrepancy is fully documented; the accepted semantics for E2 scoring (`acceptance_spec.json: reference_policy`) is a researcher
  decision required before the first counted E2 trial. Recommendation: `manual_semantics_iteration_20`.
