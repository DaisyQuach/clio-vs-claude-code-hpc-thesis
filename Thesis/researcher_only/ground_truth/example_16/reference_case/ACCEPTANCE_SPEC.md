# Example 16 — Acceptance Specification (researcher-only; machine-readable twin: `acceptance_spec.json`, id `ACCEPT-EX16-v1`)

Applies to every E2 baseline trial scored with `automation/score_researcher_only.sh`. Predeclared before any counted trial.

## A. Gates (any failure → `rejected`)
1. Packet verification (`verify_trial_packet.sh --completed`) did not fail: locked deliverables for both stages, `outputs/SHA256SUMS.txt` verifies,
   job ids and sacct present, **two** session records with distinct ids and distinct config dirs, pinned executable 2.1.292, no resume/continue/fork,
   Session A ended before Session B started, no restricted paths in either transcript.
2. Mesh equals the frozen discretization: 48 × 24 × 24 HEX8 (27,648 elements, 30,625 nodes), bbox [0,2]×[0,1]×[0,1], `block_1`, `ns_fix` 625, `ns_load` 25.
3. Generated configurations match the frozen formulation (Helmholtz Length Scale 0.043301, Surface Length Scale 1.0, no symmetry sides, E = 1, ν = 0.3,
   SIMP 3 / 1e-3, load Dof 1 value −1 on `ns_load`, u = 0 on `ns_fix`, OC, NormalizedTargetValue 0.15, update frequency 1, single-rank performers);
   Stage 1: `MaxIterations 20`, `WriteRestart true`, uniform initial density 0.15; Stage 2: `MaxIterations 40`, `InitializeField FromFieldOnInputMesh`
   with field `control`.
4. Stage 1 reached iteration 20 with 21 saved states holding `control` and `topology`; Stage 2 reached local iteration 40 with the stop message.
5. Stage 2's initial `control` field equals some saved Stage-1 state exactly (max abs diff ≤ 1e-12); otherwise it is not a restart from the checkpoint.

## B. Which semantics the trial realized (`matched_variant`)
From the saved state the Stage-2 initial design matches: iteration 20 → `manual_semantics_iteration_20`; iteration 19 → `shipped_listing_iteration_19`;
anything else → `rejected`. The Stage-2 history and final density are then compared with the matching reference run.

| Measure | accept | needs_review | rejected |
|---|---|---|---|
| Stage-1 compliance history, max relative difference vs reference | ≤ 1e-6 | ≤ 1e-2 | > 1e-2 |
| Stage-2 final compliance relative difference vs matched reference | ≤ 1e-6 | ≤ 1e-2 | > 1e-2 |
| Stage-2 final `Topology`, node-matched by coordinates, max abs diff | ≤ 1e-6 | ≤ 0.05 | > 0.05 |

## C. Policy (researcher decision, `reference_policy`)
- `undecided` (build default): every trial → `needs_review`. **Decided 2026-10-09: `manual_semantics_iteration_20`** (see `../../../RESEARCHER_DECISIONS.md`).
- `manual_semantics_iteration_20` (recommended; the frozen specification requires resumption from the iteration-20 design with seamless compliance):
  a trial that resumed from iteration 19 is `rejected`.
- `shipped_listing_iteration_19`: a trial that resumed from iteration 20 is `rejected`.

## D. Non-gating, recorded
Deliverables found by search instead of at locked paths; ambiguous packet verification; Stage-2 deck mtime vs Session A end; exit codes, timeouts,
token/tool counts (descriptive only).

## E. Reference values (private)
Stage 1: F₀ = 4.893235e6, F₂₀ = 2.360040e5. Restart from iteration 20: F₀ = 2.360040e5, F₄₀ = 2.135584e5 (overall 60). Shipped restart:
F₀ = 2.388394e5, F₄₀ = 2.136843e5 (overall 59). Histories: `results/*_criterion_history.csv`; final fields: `*/analyze_id_2_output_scenario_id_1/iteration{20,40}.exo`.

## Amendment log
- **2026-10-09T18:20Z (ACCEPT-EX16-v1 → v1.1):** removed the Stage-2 check `PlatoMainOutput WriteRestart == false` from `generated_config_args.stage2`.
  Reason: the frozen specification locks restart-file writing for Stage 1 only and says nothing about Stage 2; `write_restart_file` controls only what the
  engine output file stores (an output setting), not the physics or optimizer. Trial E2-01 kept it enabled in Stage 2 and otherwise matched the reference
  exactly (Stage-1 history, continuation state, Stage-2 history and final density all with difference 0.0), so rejecting on this check would penalize a
  setting the agents were never asked to lock. The pre-amendment spec is kept as `acceptance_spec.v1_2026-10-09T07.json`; E2-01 was re-scored under v1.1
  and its first score kept as `scores/E2-example16-baseline-01/score_v1_before_amendment/`.
