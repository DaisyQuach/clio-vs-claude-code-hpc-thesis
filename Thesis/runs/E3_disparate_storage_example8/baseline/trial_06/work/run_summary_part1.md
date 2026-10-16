# Run summary — E3-baseline-trial_06 (E3-SPC-v1, Symmetry-Plane Cantilever)

## 1. Identification

| Item | Value |
|---|---|
| Trial identifier (`$E3_TRIAL_ID`) | `E3-baseline-trial_06` |
| Node-local staging directory (`$E3_STAGING_DIR`) | `/scratch/local/u1282901/16176007/e3/baseline/E3-baseline-trial_06` (host notch272, Slurm per-job `$TMPDIR` of allocation 16176007; see `provenance/node_local_placement.txt`) |
| Control commit | `62954055b4e848f2155258c5b8c628eab97c8586` (snapshot `agent-inputs/control/`, catalog version 5; `catalog/checksums.sha256` verified PASS for all 24 snapshot files, `.gitignore` listed but not in the snapshot) |
| Assigned task | Specification `E3-SPC-v1`: minimum-compliance topology optimization of the half cantilever x∈[0,2], y∈[0,1], z∈[0,0.5] with symmetry plane z = 0.5; HEX8 48×24×12 mesh; E = 1, ν = 0.3; ns_fix clamped, ss_sym u_z = 0, −1 per node on ns_load; volume ≤ 15 %; SIMP p = 3, min 1e-3; OC, exactly 50 iterations; Helmholtz filter r = 0.15, sticking penalty 1.0, ss_sym as filter symmetry plane; engine + analyze, one processor each; Slurm job with the frozen resources |
| Agent host | notch272 (Slurm allocation 16176007); session started 2026-10-10T14:59:24Z |
| Approved software interface | `source .../automation/environment/load_morphorm_e3.sh` → modules chpc/1.0, gcc/11.2.0, openmpi/5.0.3, morphorm/approved-runtime (engine 0d767ac7, analyze 60c5e37c per `version_provenance.yaml`), cubit-edu/2026.8 |

## 2. Discovery (detail: `provenance/sources_searched.tsv`)

| Collection | How searched | What was found |
|---|---|---|
| `e3-control` (`agent-inputs/control/`) | read every file (README, task/, catalog/, artifact cards, protocol/, helper scripts) | task, specification, catalog, five artifact cards, protocol, helpers |
| `e3-private-source` (Globus 6dcea62e-130d-47a9-8b77-80fba6f58693) | `globus ls -r` of the collection root (13 files + MANIFEST); then `globus_stage_file.sh` for each needed file | manuals/ (User + Theory Manual), documentation/ (software contract, compute resources, version provenance, curated readme), target_materials/symmetry_plane_cantilever/ (specification, figure, READMEs, empty permitted_starting_materials/) |
| `e3-chpc-candidate-archive` (POSIX, read-only) | `find`, `verify_collection.sh` (MANIFEST PASS), then read README, problem_card, provenance, decks and journals of all four packages | example_01, example_07, example_13, example_16_restart |
| `e3-trial-inbox-destination` | used only as the Globus destination `staging-inbox/` (never listed or browsed) | 13 transferred files (`staging-manifest/globus_transfers.tsv`) |
| approved software interface | sourced the loader; `module list`; `which` of the contract's commands; `ls` of the runtime `bin/` placed on PATH (to confirm the executables; no documentation browsing) | cubit, XMLGenerator, PlatoMain, analyze_MPMD, mpiexec, python3 |

No other location was listed, searched or read. Source identifiers (`MORPHORM-*`) were not resolved.

## 3. Artifact selection (detail: `provenance/artifact_selections.md`)

- **example_07 — adapted.** Full-domain Helmholtz cantilever with every physical/optimizer value equal to the locked ones; its journal and deck were adapted to the half domain (width 0.5, 48×24×12, sideset `ss_sym`, symmetry displacement condition, filter symmetry plane). Nothing copied byte-for-byte.
- **example_16_restart — not used** (two-stage restart; the task requires one uninterrupted 50-iteration run).
- **example_01 — not used** (bracket, tets, kernel filter, tractions, fixed block).
- **example_13 — not used** (2-D L-bracket).
- **symmetry_plane_target (private source) — used**: the specification (byte-identical to the control copy, SHA-256 f1bd0b56…) and READMEs; the figure was staged but not needed.
- **Morphorm User Manual — used** for the filter keywords (`symmetry_plane_location_names`, Tables 2.5.12/2.5.15) and block syntax; **Theory Manual — not staged**.

## 4. Staging (detail: `staging-manifest/`)

- Staged by Globus from `e3-private-source` into `staging-inbox/` and then into `$E3_STAGING_DIR/e3-private-source/`: 12 files, 2,660,751 bytes (plus the collection `MANIFEST.sha256`, 1,482 bytes, transferred by the helper for verification). Every file matched `MANIFEST.sha256`; source and staged SHA-256 are identical for every row of `staging-manifest/staged_files.tsv`. 13 Globus tasks, all SUCCEEDED (`staging-manifest/globus_transfers.tsv`).
- Derived (not a source file): `$E3_STAGING_DIR/derived/user_manual.txt`, the `pdftotext -layout` extraction of the staged User Manual, used for keyword look-up.
- Nothing was copied from the candidate archive: its decks and journals were read in place and adapted into new files under `work/`, so `stage_file.sh` was not needed.
- Returned from staging to the trial workspace: **none** (`staging-manifest/returned_files.tsv` contains only the header). Everything the Slurm job needed (`work/run/`) was generated in the trial workspace; the staged documentation was consulted only on the agent host.

## 5. Mesh

- Journal `work/mesh/mesh.jou` (deliverable `outputs/mesh.jou`), adapted from the Example 7 journal: brick 2.0 × 1.0 × 0.5 moved to the origin corner, `scheme map`, size 0.0416667, HEX8, `block_1`, `ns_fix` (nodes of the x = 0 surface), `ns_load` (nodes with x > 2 − h/2 and y < h/2), `ss_sym` (surface with z > 0.5 − h/2), `export mesh "mesh.exo" dimension 3`.
- Generated on the agent host (permitted by `compute_resources.md`) with `cubit -batch -nographics -nojournal -input mesh.jou`, 2026-10-10T15:02:34Z–15:02:38Z, exit 0 (`outputs/run_logs/cubit_run.log`). Files: `work/mesh/mesh.exo` = `work/run/mesh.exo` = `outputs/mesh.exo`, SHA-256 `c396e719916fd594d9104512432cacf264d45b614452028dee061a7a50c76e77`.
- Verification (`work/scripts/verify_mesh.py` with the runtime python3/netCDF4, 2026-10-10T15:03:41Z; record `outputs/mesh_verification.json`): **ALL_PASS** —
  13,824 elements, 15,925 nodes, one block `block_1` (13,824 HEX8), bounding box x [0, 2] y [0, 1] z [0, 0.5], 49 × 25 × 13 node planes (h = 1/24, max deviation 6.7e-7),
  `ns_fix` 325 nodes all at x = 0, `ns_load` 13 nodes at x = 2, y = 0 spanning z ∈ [0, 0.5], `ss_sym` 1,152 faces all at z = 0.5.

## 6. Input deck and generated configuration

Deck `work/run/input_deck.i` (deliverable `outputs/input_deck.i`, SHA-256 `962da5c2534259b27de4bcc98c34e95f81ab4a7a5b949836921dcef1686d4aa1`), translated with `XMLGenerator input_deck.i` on the agent host at 2026-10-10T15:08:13Z (exit 0; `outputs/generated_config/xmlgenerator.log`). Generated files in `outputs/generated_config/`: `interface.xml`, `engine_input_deck.xml`, `engine_operations.xml`, `analyze_2_input_deck.xml`, `analyze_2_operations.xml`, `analyze_helmholtz_input_deck.xml`, `analyze_helmholtz_operations.xml`, `mpirun.source`. Verification record: `outputs/generated_config/generated_config_verification.txt` (28 checks, **ALL_PASS**, 2026-10-10T15:10Z).

| Locked setting | Deck | Generated configuration (where verified) |
|---|---|---|
| Services engine + analyze, 1 processor each, single-rank performers, no decomposition | `service 1 code engine number_processors 1`; `service 2 code analyze number_processors 1` | `interface.xml` performers engine_1, analyze_2, analyze_helmholtz; `mpirun.source` three `-np 1` launches, no `decomp` |
| Material E = 1.0, ν = 0.3 on block_1 | `material 1 isotropic_elastic youngs_modulus 1.0 poissons_ratio 0.3`; `block 1 name block_1 material_id 1` | `analyze_2_input_deck.xml` Material Models/material_1 Youngs Modulus 1.0, Poissons Ratio 0.3; Spatial Model Domains = {block_1 → material_1} |
| SIMP single phase, exponent 3.0 (default), minimum 1e-3; compliance criterion `minimum_ersatz_material_value 1e-3` | `material_interpolation 1 type single_phase model simp minimum_value 1e-3`; `criterion 1 mechanical_compliance minimum_ersatz_material_value 1e-3` | `analyze_2_input_deck.xml` Residual: Material Interpolation Model Single-Phase, Penalty Function SIMP Exponent 3.0 Minimum Value 1e-3; Criteria/My Objective (Internal Elastic Energy on {block_1}) Penalty Function SIMP Exponent 3.0 Minimum Value 1e-3 |
| ns_fix u = 0 | `boundary_condition 1 fixed_value nodeset ns_fix dispx dispy dispz 0 0 0` | Essential Boundary Conditions IDs 1–3: Sides ns_fix, Index 0/1/2, Value 0 |
| ss_sym u_z = 0 through the sideset | `boundary_condition 2 fixed_value location_type sideset location_name ss_sym dispz 0` | Essential Boundary Condition ID 4: Sides ss_sym, Index 2, Value 0 |
| Load −1.0 per node on ns_load (y), no other loads | `load 1 concentrated_load nodeset ns_load direction y value -1.0` | Concentrated Loads: Nodes ns_load, Dof 1, Value −1.0; Mechanical Natural Boundary Conditions empty |
| Objective weighted sum, single compliance criterion, weight 1, analyze service | `objective weighted_sum criterion_ids 1 service_ids 2 scenario_ids 1 weights 1` | `interface.xml` stage Compute Objective Value → analyze_2; `engine_operations.xml` Aggregator Weighting Value 1 |
| Volume ≤ 0.15, less_than, engine service | `constraint 1 criterion_id 2 relative_target 0.15 type less_than service_id 1` | `interface.xml` Constraint NormalizedTargetValue 0.15 referenced to Design Volume; Compute Constraint Value 1 → engine_1 |
| Density discretization, initial density 0.15 | `discretization density`, `initial_density_value 0.15` | `engine_operations.xml` InitializeField Uniform Value 0.15; SetLower/UpperBounds Discretization density |
| OC, default tolerances, `normalize_in_aggregator false`, `update_problem true`, frequency 1 | `optimization_algorithm oc`, `normalize_in_aggregator false`, service 1 `update_problem true`, `update_problem_frequency 1` | `interface.xml` Package OC, OCControlStagnationTolerance 1e-4, OCObjectiveStagnationTolerance 1e-8, OCGradientTolerance 1e-8, ProblemUpdateFrequency 1, UpdateProblemStage; Aggregator has no `<Normals>` element (a scratch translation with `normalize_in_aggregator true` adds one) |
| `max_iterations 50` | `max_iterations 50` | `interface.xml` MaxIterations 50; `engine_operations.xml` PlatoMainOutput MaxIterations 50 |
| Helmholtz filter r = 0.15, sticking penalty 1.0, ss_sym symmetry plane | `filter 1 type helmholtz radius_absolute 0.15 boundary_sticking_penalty 1.0`; study `symmetry_plane_location_names ss_sym` | `analyze_helmholtz_input_deck.xml` Parameters: Length Scale 0.043301 (= 0.15/(2√3)), Surface Length Scale 1.0, Symmetry Plane Sides {ss_sym} |
| Output dispx/dispy/dispz from analyze; engine output of control and topology | `output 1 service_id 2 output_data true data dispx dispy dispz` | `analyze_2_input_deck.xml` Output Plottable {displacement_x, displacement_y, displacement_z}; `interface.xml`/`engine_operations.xml` PlatoMainOutput inputs topology, control; `engine_input_deck.xml` output file engine_output |

Translation history: the first translation (keyword `symmetry_plane_location_names ss_sym` inside the filter block, the syntax of manual Table 2.5.12) exited 0 but produced a Helmholtz configuration **without** a symmetry-plane entry; it was rejected and kept in `work/xmlgen_tests/attempt0_filter_block_keyword/`. Moving the keyword to the study block (`work/xmlgen_tests/A_study_keyword/`) produced `Symmetry Plane Sides {ss_sym}` and was adopted; `B_both/` and `C_normalize_true/` are scratch translations used only for comparison. Only the adopted translation was run.
