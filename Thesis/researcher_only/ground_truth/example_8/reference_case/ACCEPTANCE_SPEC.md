# Example 8 — Acceptance Specification (researcher-only; machine-readable twin: `acceptance_spec.json`, id `ACCEPT-EX8-v1`)

Applies to every E1 (and future E3) baseline trial scored with `automation/score_researcher_only.sh`. Predeclared before any counted trial.

## A. Gates (any failure → `rejected`)
1. Packet verification (`verify_trial_packet.sh --completed`) did not fail: locked deliverables present, `outputs/SHA256SUMS.txt` verifies, job ids and
   sacct present, session record with pinned executable 2.1.292, no resume/continue/fork, no restricted paths in the transcript.
2. Mesh equals the frozen discretization: 48 × 24 × 12 HEX8 (13,824 elements, 15,925 nodes), bbox [0,2]×[0,1]×[0,0.5], single block `block_1`,
   `ns_fix` 325 nodes, `ns_load` 13 nodes, sideset `ss_sym` 1,152 faces.
3. Generated configuration (the agent's XMLGenerator output) matches the frozen formulation: Helmholtz Length Scale 0.043301 (= 0.15/(2√3)),
   Surface Length Scale 1.0, E = 1, ν = 0.3, SIMP exponent 3 and minimum 1e-3 (residual and objective), one concentrated load Dof 1 value −1 on `ns_load`,
   u = 0 on `ns_fix`, u_z = 0 on `ss_sym`, OC, MaxIterations 50, NormalizedTargetValue 0.15 vs Design Volume, uniform initial density 0.15,
   update frequency 1, three single-rank performers. Under the `symmetry_honored_variant` policy, `Symmetry Plane Sides {ss_sym}` must be present.
4. The optimizer reached iteration 50 with the stop message present.

## B. Reference match (which variant the trial reproduces)
The trial's compliance history and final density field are compared with both reference runs; the variant with the smaller final-compliance
relative difference is the `matched_variant`.

| Measure | accept | needs_review | rejected |
|---|---|---|---|
| final compliance relative difference vs matched variant | ≤ 1e-6 | ≤ 1e-2 | > 1e-2 (matches neither) |
| final `Topology` field, node-matched by coordinates, max abs diff | ≤ 1e-6 | ≤ 0.05 | > 0.05 |
| final density field not node-comparable (different mesh) | — | always | — |

## C. Policy (researcher decision, `reference_policy`)
- `undecided` (build default): every trial → `needs_review`. **Decided 2026-10-09: `symmetry_honored_variant`** (see `../../../RESEARCHER_DECISIONS.md`).
- `symmetry_honored_variant` (recommended; the frozen specification requires the filter symmetry plane in the generated configuration):
  a trial matching the canonical-as-executed result is `rejected`.
- `canonical_shipped_deck`: a trial matching the symmetry-honored result is `rejected`.

## D. Non-gating, recorded
Deliverables found by search instead of at their locked paths (→ at most `needs_review`); `packet_verification: ambiguous` (→ at most `needs_review`);
process exit code, timeout flag, token/tool counts (descriptive only).

## E. Reference values (private)
Canonical: F₅₀ = 1.468985e5, F₀ = 2.837864e6, volume fraction 0.150000, max |u| 2.8635e4. Symmetry-honored: F₅₀ = 1.044701e5, F₀ = 2.654786e6,
volume fraction 0.150000, max |u| 2.2969e4. Full histories: `results/*_criterion_history.csv`; final fields: `run_*/analyze_id_2_output_scenario_id_1/iteration50.exo`.
