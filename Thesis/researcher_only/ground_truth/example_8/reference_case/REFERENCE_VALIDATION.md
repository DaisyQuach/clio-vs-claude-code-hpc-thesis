# Example 8 — Reference Validation

Compares the rebuilt reference (2026-10-09, jobs 16154328/16154329/16154330) with (a) the Examples Manual §7.2.8 and (b) valid historical
Example 8 evidence (read-only): `Morphorm_ground_truth/Example_08` (2026-10-07, approved runtime) and
`experiments_groundTruth/Example8_SymmetryPlane/run_16053535` (2026-10-04, developer runtime).

## 1. Exact source / formulation identity (no tolerance)

| Item | Result |
|---|---|
| Journal, deck, driver | byte-identical to the canonical files in `Morphorm/docs/...` and to the 2026-10-07 package's `original_inputs/` (SHA-256 `cd852856…c46a6`, `01a76bf2…6a5ff`, `70bd98ce…2ae35`) |
| Formulation vs manual Listing 7.2.10 | identical except the documentation-keyword spellings (`number_ranks 1` ×2, `problem_update_frequency 1` are not parsed keys; the deck uses `update_problem_frequency 1`) — see `../SOURCE_AUDIT.md` §4 |
| Mesh vs manual/journal | 48 × 24 × 12 HEX8, 15,925 nodes, bbox [0,2]×[0,1]×[0,0.5], `ns_fix` 325, `ns_load` 13, `ss_sym` 1,152 faces: all 8 checks pass; node coordinates and connectivity **identical** (max abs diff 0.0) to the 2026-10-07 mesh |
| Generated configuration (canonical) | 34/34 checks in the "symmetry absent" mode; 33/34 in the "symmetry required" mode — the single failure is the missing `Symmetry Plane Sides`, i.e. the frozen software does not apply the manual's filter symmetry plane (documented defect, `../SOURCE_AUDIT.md` §5) |
| Generated configuration (variant) | 34/34 with `Symmetry Plane Sides {ss_sym}`; all other generated files byte-identical to the canonical translation |
| Run-time translation vs preflight | 8/8 generated files byte-identical, both runs |

## 2. Byte-identical artifacts
- `inputs/*` (canonical copies) ↔ source tree and 2026-10-07 `original_inputs/`: identical.
- `run_canonical/morphorm_oc_optimizer_diagnostics.txt` ↔ 2026-10-07 `reference_run/morphorm_oc_optimizer_diagnostics.txt`: **identical** (`diff` empty).
- `run_canonical/morphorm_oc_optimizer_diagnostics.txt` ↔ 2026-10-04 developer-runtime `run_16053535/morphorm_oc_optimizer_diagnostics.txt`: **identical**.

## 3. Expected non-byte-identical derived artifacts
- `mesh/topology_mech_ex8.exo` (SHA-256 `46dd51a8…f0f3`) vs 2026-10-07 mesh (`0a0a3a7d…0ab4`): Exodus files carry QA/time-stamp records, so the
  bytes differ while coordinates and connectivity are identical (verified numerically).
- `*.exo` outputs, `engine_*`/`analyze_*` performer logs, `time_v.txt`, `timestamps.txt`, Slurm logs: run-specific metadata; compared numerically, not by hash.

## 4. Numerical comparisons (with tolerances)

| Quantity | Rebuilt canonical | 2026-10-07 package | Difference | Tolerance / verdict |
|---|---|---|---|---|
| Final compliance F₅₀ | 1.468985e5 | 1.468985e5 | 0 (7 significant digits; full histories identical) | ≤ 1e-6 rel: **match** |
| Final `Topology` field (iteration50.exo), node-wise | — | — | max abs diff **0.0** | ≤ 1e-6: **match** |
| Final displacements X/Y/Z, node-wise | — | — | max abs diff **0.0** | **match** |
| Volume fraction | 0.150000 | 0.150000 | 1.7e-13 from 0.15 | ≤ 1e-6: **match** |
| Max displacement magnitude | 2.8635e4 | 2.8635e4 | 0 | **match** |

The symmetry-honored variant has no historical counterpart on this mesh (the earlier `Experiment1/reference_case` used a 40 × 20 × 10 mesh,
SIMP floor 1e-9 and a `single_criterion` objective, so it is not comparable); its validity rests on the generated-configuration check and on the
qualitative agreement below.

## 5. Comparison with the manual's stated result (qualitative; the manual prints no numbers for Example 8)

| Manual statement (printed p. 500–504) | Canonical as executed | Symmetry-honored variant |
|---|---|---|
| "Mirroring it across z = 0.5 recovers the full cantilever of Example 7" | **not reproduced**: mean density 0.0137 on the cut plane (material avoids the cut); the mirrored design is two separate trusses (`figures/Example_08_canonical_shipped_deck_final_iteration50.png`) | **reproduced qualitatively**: mean density 0.506 on the cut; the mirrored half forms one connected full-width design (`figures/Example_08_symmetry_honored_variant_final_iteration50.png`) |
| "the design near the cut matches the full-domain result rather than developing the artificial boundary layer" | not reproduced (boundary-sticking penalty acts on the cut) | reproduced (sticking penalty excluded on `ss_sym`) |
| Fig. 7.2.20: half design, displacement color bar up to ≈ 2.9e4 (figure-read) | max |u| 2.8635e4: consistent | max |u| 2.2969e4: lower (the cut-plane material stiffens the half) |
| Example 7 context: consistent-boundary full design ≈ 2.2e5 at 15 % | half-model values are not directly comparable to the full model | — |

## 6. Verdict
- **Exact manual agreement cannot be claimed for either run.** The canonical run reproduces the manual's listing, mesh, boundary conditions,
  iteration count and volume constraint exactly and the historical executions bit for bit, but not the manual's central symmetry-plane claim
  (software defect). The variant reproduces the manual's described behaviour but uses a documented one-block rewrite of the deck.
- This is a meaningful, fully documented discrepancy. It does **not** block the suite build (both references are complete, validated and hashed),
  but the choice of accepted variant (`acceptance_spec.json: reference_policy`) is a researcher decision required before the first counted E1 trial.
