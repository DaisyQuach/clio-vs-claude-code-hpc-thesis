# Example 16 — Source Audit (Restart / Warm Start)

Researcher-only. Written 2026-10-09 (UTC) before any reference execution for the new `Thesis/` study.
All inspected locations were read only. Absolute paths below are under `/uufs/chpc.utah.edu/common/home/chet/Daisy/`
(`/uufs/chpc.utah.edu/common/home/u1282901/chet/Daisy/` resolves to the same directory).

## 1. Canonical manual section

| Item | Value |
|---|---|
| Manual file | `morphorm_manuals/examplesmanual.pdf` ("Examples Manual, Release 1.0.0", 716 PDF pages, created 2026-07-15) |
| Manual SHA-256 | `7fc32762247845fb89045c9eac9b422e57d49d4a68b1bdc0ed04864c9271c23d` |
| Section | §7.2.16 "Example 16: Restart (Warm Start)" (Chapter 7, §7.2 Mechanical) |
| Pages | PDF pages 551–558 = printed pages 545–552 (printed = PDF − 6); table of contents line 135 confirms printed p. 545 |
| Figures / listings | Fig. 7.2.36 (design domain = Example 7 geometry figure), Listing 7.2.18 (stage 1 deck), Listing 7.2.19 (stage 2 restart deck), Fig. 7.2.37 (compliance history across the restart; log axis; blue initial run, green `control` restart, orange dashed `topology` restart) |
| Dependency | §7.2.7 Example 7 (PDF 500–506) defines the 2 × 1 × 1 cantilever; the manual states "The model is the Example 7 cantilever" (p. 545) |
| Extracts kept | `manual_reference/examplesmanual_sec7.2.16_pdf551-558_printed545-552.txt`, page images `examplesmanual_page-55{1..8}.png`, Example 7 context text, User Manual pp. 29–30 |
| RST source | `Morphorm/docs/examples/topology_optimization/mech/examples_topology_optimization_mech_ex16.inc` (SHA-256 `b933d854da3c1e20fcafb01d8f08e99ebcd3cdb50581bc18237ccb6b789375e5`); it `literalinclude`s both decks below |

## 2. Canonical source files (selected)

| Role | Absolute path | SHA-256 | Bytes |
|---|---|---|---|
| **Canonical journal** | `Morphorm/docs/examples/input_decks/topology_optimization/mech/topology_mech_ex16.jou` | `b02676b90e219b460a1e4a5b9a5910438fea46198cfac4dbdeffa4a3c947fca5` | 1076 |
| **Canonical stage-1 deck** | `…/mech/topology_mech_ex16.i` | `4193f3b3981691499f13359369f6f419ea69c9a908f8c5285945ba51ca29112d` | 1731 |
| **Canonical stage-2 (restart) deck** | `…/mech/topology_mech_ex16_restart.i` | `951941cc684b444bd3c268c192eb7269ec964eb8b2579b6b8087b86575a32da6` | 1806 |
| Driver named by the manual | `Morphorm/engine/python/runmorphorm.py` | `70bd98cebb38bb77b3509b15d178bedd14bace8c775c004771b0217df782ae35` | 2678 |
| Manual Fig. 7.2.36 | `Morphorm/docs/examples/figs/topology_optimization/mech/topology_original_geom_mech_ex7.png` | `cf38e2f0eaadd07ecee27762e25679afdb59306d9f744ff8ac835c04e71b812a` | 697847 |
| Manual Fig. 7.2.37 | `Morphorm/docs/examples/figs/topology_optimization/mech/ex16/topology_restart_history_ex16.png` | `e61e3b1eb1a76dd52e530cdcd3bbf19059546129dd78e1cc9a6d7b00b8f8d028` | 72527 |
| Script that generated Fig. 7.2.37 | `Morphorm/docs/examples/_tools/gen_topology_restart_chart.py` | `a72e0f03ae2b1cac49343f7b27fea3977f68b53deedcce85d6cb3562ab319c6a` | 3396 |

Immutable copies are in `source_inputs/` (`source_inputs_sha256.tsv`). No mesh, criterion history or completed output for Example 16 exists in the
source tree; the run folders behind Fig. 7.2.37 (`/tmp/ex16run`, `/tmp/ex16ctrl`, `/tmp/ex16restart` per the generator script) were not preserved.

### 2a. Example 7 journal: relationship to Example 16 (task §3 requirement)

| File | SHA-256 |
|---|---|
| `…/mech/topology_mech_ex7.jou` | `2e5d0201ac23aea4533c007d44dd593713aae9533d73f800ec921034c70409ae` |
| `…/mech/topology_mech_ex16.jou` | `b02676b90e219b460a1e4a5b9a5910438fea46198cfac4dbdeffa4a3c947fca5` |

`diff topology_mech_ex7.jou topology_mech_ex16.jou` reports exactly one differing line, the export statement
(`export mesh "topology_mech_ex7.exo"` vs `export mesh "topology_mech_ex16.exo"`). Geometry (2 × 1 × 1), `esize 0.0416667` (48 × 24 × 24),
block, nodesets `ns_fix` / `ns_load` are byte-identical. The manual's Mesh Generation paragraph (printed p. 551) states the Example 16 mesh is
"generated from the Cubit journal `topology_mech_ex16.jou` (the Example 7 geometry)". **Conclusion:** the Example 7 journal is the geometric
origin, but Example 16 ships its own canonical journal that is required by the deck's `mesh name topology_mech_ex16.exo`. The rebuild uses
`topology_mech_ex16.jou`; `topology_mech_ex7.jou` is retained under `source_inputs/example7_evidence_only/` as corroborating evidence only and is **not executed**.
`diff topology_mech_ex7.i topology_mech_ex16.i`: only `max_iterations 50 → 20`, added `write_restart_file true`, and the mesh name differ,
confirming the manual's statement that "only the restart workflow is new".

## 3. Historical completed outputs (validation evidence only)

| Location | What | Use |
|---|---|---|
| `Morphorm_ground_truth/Example_16/` (2026-10-07, approved runtime, allocation 16068475 steps .19/.22/.28/.33) | stage 1 with the shipped deck (final F = 2.360040e5 at iteration 20); restart with shipped deck (`restart_iteration 20`, superseded: resumed from iteration 19); **corrected** restart (`restart_iteration 21`, researcher-authorized 2026-10-06): final F = 2.135584e5 at overall iteration 60 | numerical cross-check of all three rebuilt runs |
| `experiments_groundTruth/Example16_Restart/` (2026-10-04, developer runtime) | shipped decks; diagnostics reproduced line for line by the 2026-10-07 stage 1 | secondary cross-check |
| `Morphorm_ground_truth/Experiment2/reference_case` (2026-10-09, earlier session) | controlled thesis reference derived from Examples 7/16 with a 40 × 20 × 20 mesh, SIMP 1e-9, `single_criterion` | not the manual example; not used |
| `ThesisExperiments/runs/E2_interrupted_recovery/baseline/trial_0*` (pilot) | agent-built 40 × 20 × 20 workflows; all three agents discovered the off-by-one and used `restart_iteration 21` | preliminary evidence only |

## 4. Field-by-field configuration (manual vs shipped decks vs journal)

| Field | Manual statement (printed page) | Shipped value | Status |
|---|---|---|---|
| Geometry | 2 × 1 × 1 cantilever, Example 7 geometry (p. 545) | journal `len 2.0`, `ht 1.0`, `wd 1.0`, corner at origin | match |
| Mesh | structured HEX8 (p. 545, 551); no count printed | journal `esize 0.0416667` → 48 × 24 × 24 = 27,648 HEX8, 30,625 nodes; block `block_1` | journal supplies resolution |
| Fixed support | x = 0 face, `ns_fix`, all displacements (p. 545) | journal nodeset 1 (625 nodes); deck BC 1 dispx dispy dispz = 0 | match |
| Load | bottom-right edge x = 2, y = 0, `ns_load`, transverse −y line load (p. 545) | journal nodeset 2 (25 nodes); deck load 1 `concentrated_load`, direction y, value −1 per node | match |
| Symmetry | none (full-width model) | no symmetry BC, no filter symmetry keyword | match |
| Material | E = 1, ν = 0.3 (p. 545) | deck `isotropic_elastic` 1.0 / 0.3 | match |
| SIMP / interpolation | listings: `material_interpolation minimum_value 1e-3`, `minimum_ersatz_material_value 1e-3`; no exponent | deck identical; generated exponent 3.0 (default), Minimum Value 1e-3 | match |
| Objective | compliance minimization of Example 7 (p. 546): `weighted_sum`, criterion 1 `mechanical_compliance`, weight 1 | deck identical | match |
| Constraint | volume ≤ 15 %: `relative_target 0.15`, `less_than`, `service_id 1` (p. 546, 548) | deck identical | match |
| Filter | Helmholtz `radius_absolute 0.15`, `boundary_sticking_penalty 1.0` (p. 546) | deck filter block identical; generated Length Scale 0.043301, Surface Length Scale 1.0 (no symmetry sides, correct for this example) | match |
| Optimizer | OC, `discretization density`, `initial_density_value 0.15`, `normalize_in_aggregator false` (p. 546) | deck identical | match |
| **Stage 1** | `max_iterations 20`, `write_restart_file true` → `engine_output.exo` holds `control` and `topology` at every iteration (p. 546, 549) | deck identical; generated `PlatoMainOutput WriteRestart true`, `MaxIterations 20` | match |
| Carry-over | `cp engine_output.exo initialguess.exo` (p. 546, 551) | the reference build performs exactly this copy and records both hashes | match |
| **Stage 2** | `max_iterations 40`, `initial_guess_file_name initialguess.exo`, `initial_guess_field_name control`, `restart_iteration 20` = "the iteration to read from the checkpoint"; "resumes from the design saved at iteration 20"; "first restart iteration lands on the same compliance the initial run reached at iteration 20" (p. 545–546, 550–551) | deck identical to the listing; generated `InitializeField FromFieldOnInputMesh / Iteration 20` | **written identically, but see §5** |
| Iteration schedule | 20 + 40 = 60 total (p. 545) | decks 20 and 40 | match |
| Update frequency / ranks | listings print `problem_update_frequency 1`, `number_ranks 1` | decks: `update_problem_frequency 1`, no `number_ranks` (documented keywords) | documentation keyword difference only |
| Execution | `python runmorphorm.py topology_mech_ex16.i`; copy; `python runmorphorm.py topology_mech_ex16_restart.i` (p. 551) | driver copied | match |
| Published result | Fig. 7.2.37 only (log-scale history; iteration 0 ≈ 5e6, iteration 20 ≈ 2.4e5, iteration 60 ≈ 2.15e5 when pixel-read); "a cold start begins near 5 × 10⁶"; no final-topology figure; no printed numbers | — | approximate numeric target only |

## 5. Discrepancy carried forward (not concealed): `restart_iteration` semantics

Morphorm passes `restart_iteration` to `InitializeField` as a **1-based Exodus state** (`engine/src/operations/Plato_InitializeField.cpp` →
`read_defined_input_fields(state)`); state *s* of `engine_output.exo` holds the iteration *s* − 1 design (states 1–21 hold iterations 0–20).
Executed evidence (2026-10-07, `Morphorm_ground_truth/Example_16/failed_or_superseded/`): the shipped `restart_iteration 20` resumes from the
iteration-19 design (restart F₀ = 2.388394e5 = stage-1 iteration 19; 1.20 % above iteration 20's 2.360040e5) and repeats one iteration, so the
run ends at the equivalent of overall iteration 59. That contradicts the manual's stated semantics. With `restart_iteration 21` the restart's
initial `control` equals the iteration-20 checkpoint field exactly and F₀ = 2.360040e5 (difference 0). The researcher authorized this one-line
correction on 2026-10-06 (`Morphorm_ground_truth/Example_16/corrected_inputs/README.md`).

**Decision for the rebuild:** execute stage 1 with the unmodified shipped deck, then execute **both** restarts from that stage-1 checkpoint:
(a) `restart_iteration 21` (manual semantics, researcher-authorized correction; the primary candidate), and (b) the unmodified shipped
`restart_iteration 20` (manual listing as executed), so the scorer can classify an agent's continuation as resuming from iteration 20 or 19.
The accepted policy is recorded in `reference_case/ACCEPTANCE_SPEC.md` and flagged for researcher confirmation in `Thesis/BUILD_REPORT.md`.

## 6. Approved software and Slurm contract

Identical to Example 8's audit §6 (same approved runtime hashes, `cubit-edu/2026.8`, and the frozen contract
`--account=hochhalter-np --partition=hochhalter-np --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=32G --time=02:00:00`).

## 7. Conclusion

The canonical source for Example 16 is unambiguous: `topology_mech_ex16.jou`, `topology_mech_ex16.i`, `topology_mech_ex16_restart.i`,
`runmorphorm.py`, all hash-pinned above. The Example 7 journal is corroborating evidence only. Reference execution may proceed. The one
meaningful discrepancy (restart state indexing) is documented in §5 and handled by executing both restart variants from one stage-1 checkpoint.
