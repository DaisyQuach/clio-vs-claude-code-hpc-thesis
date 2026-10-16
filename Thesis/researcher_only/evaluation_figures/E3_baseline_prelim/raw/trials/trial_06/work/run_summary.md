# Run summary — E3-baseline-trial_06 (E3-SPC-v1, Symmetry-Plane Cantilever)

## 1. Identification

| Item | Value |
|---|---|
| Trial identifier (`$E3_TRIAL_ID`) | `E3-baseline-trial_06` |
| Node-local staging directory (`$E3_STAGING_DIR`) | `/scratch/local/u1282901/16176007/e3/baseline/E3-baseline-trial_06` (host notch272, Slurm per-job `$TMPDIR` of allocation 16176007; see `provenance/node_local_placement.txt`) |
| Control commit | `62954055b4e848f2155258c5b8c628eab97c8586` (snapshot `agent-inputs/control/`, catalog version 5; `catalog/checksums.sha256` verified PASS for the 23 snapshot files it lists that are present; `.gitignore` is listed but not in the snapshot) |
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

## 7. Execution

Commands used (all on the agent host unless noted; the loader was sourced first in every shell):

```
sha256sum -c --quiet catalog/checksums.sha256                       # control snapshot (in agent-inputs/control)
record_node_placement.sh ; verify_collection.sh <candidate archive> ; record_search.sh ...
globus ls -r 6dcea62e-130d-47a9-8b77-80fba6f58693:/                  # discovery of the private source
globus_stage_file.sh <path>   (x12; each: globus transfer -> staging-inbox/, MANIFEST check, cp -p -> $E3_STAGING_DIR)
pdftotext -layout <staged User Manual> $E3_STAGING_DIR/derived/user_manual.txt
cubit -batch -nographics -nojournal -input mesh.jou                  # work/mesh, 15:02:34Z-15:02:38Z, exit 0
python3 -I work/scripts/verify_mesh.py work/mesh/mesh.exo            # 15:03:41Z, ALL_PASS
XMLGenerator input_deck.i                                            # work/run, accepted translation 15:08:13Z, exit 0
python3 -I work/scripts/verify_generated_config.py work/run          # 28 checks ALL_PASS (final record 15:10Z)
sbatch jobs/morphorm_oc50_symplane.sbatch                            # 15:10:11Z -> job 16176085
   (inside the job, on notch272:  source load_morphorm_e3.sh; module list; bash mpirun.source > morphorm_run.log)
sacct -j 16176085 --format=JobID,JobName,State,ExitCode,Submit,Start,End,Elapsed,AllocCPUS,ReqMem,MaxRSS,NodeList -P
python3 -I (netCDF4) check of iteration50.exo and engine_output.exo   # outputs/run_logs/final_output_check.txt
bash work/scripts/finalize_outputs.sh 16176085 <iteration50.exo>; hash_outputs.sh
```

Slurm jobs submitted in this trial (also `jobs/job_ids.txt`):

| Job ID | Script | Resources | State | Exit | Submit / Start / End (UTC) | Elapsed | Node | MaxRSS |
|---|---|---|---|---|---|---|---|---|
| 16176085 | `jobs/morphorm_oc50_symplane.sbatch` (= `outputs/job_script.sbatch`) | account/partition hochhalter-np, 1 node, 1 task, 8 CPUs, 32G, 02:00:00 (frozen contract, verbatim) | COMPLETED | 0:0 | 15:10:11 / 15:10:13 / 15:27:51 | 00:17:38 | notch272 | 1,675,112 K (batch step) |

`sacct` record: `jobs/sacct_16176085.txt`. Scheduler stdout/stderr: `logs/slurm-16176085.out` / `.err` (copies in `outputs/run_logs/`; stderr is empty). The job's stdout contains `module list` after sourcing the approved interface, the SHA-256 of every input it used (identical to the verified files in `outputs/`), and the timestamps `morphorm_start_utc 15:10:29Z`, `morphorm_end_utc 15:27:50Z`, `morphorm_exit=0`. No job was cancelled or failed; only this one job was submitted. The optimization was not run on the agent host (the job ran under its own allocation 16176085; the scheduler placed it on notch272, the same node as the agent allocation 16176007).

## 8. Completed stages and iteration count

- Discovery, staging, mesh generation, mesh verification, deck translation, generated-configuration verification, Slurm optimization, output verification, deliverable placement: all completed.
- Optimizer: `outputs/morphorm_oc_optimizer_diagnostics.txt` lists iterations 0 … **50** (51 rows, F-count 51). The analyze visualization directory holds `iteration0.exo` … `iteration50.exo` (51 files); `engine_output.exo` holds 51 time steps.
- Stopping message (end of the diagnostics file and of `morphorm_run.log`):
  `****** Optimization stopping due to exceeding maximum number of iterations. ******`
  i.e. the run reached the locked cap of 50 iterations; no convergence stop occurred earlier.
- Iteration history (from the diagnostics): F(X) 2.654786e+06 at iteration 0 → 1.044701e+05 at iteration 50; abs(dX) 1.142971e-01 and abs(dF) 6.611695e+01 at the last iteration (well above the default stagnation tolerances, consistent with the cap-based stop).
- Final fields (`outputs/run_logs/final_output_check.txt`): `final_analyze_output.exo` (= `iteration50.exo`) contains the nodal fields Topology (density; min 1.0e-08, max 0.939, mean 0.157) and displacement X/Y/Z, plus the element field My Objective; `engine_output.exo` contains the nodal fields control and topology at 51 steps (final mean control 0.185, topology 0.157 ≈ the 15 % volume target).

## 9. Key output files (`outputs/`, SHA-256 in `outputs/SHA256SUMS.txt`)

| File | SHA-256 |
|---|---|
| `outputs/mesh.jou` | 145d8641fff412740c85a0a1ea8a9fcd1a390539bffbe5718e6d04acf2c597d4 |
| `outputs/mesh.exo` | c396e719916fd594d9104512432cacf264d45b614452028dee061a7a50c76e77 |
| `outputs/mesh_verification.json` | fe6925bff13ff37c959b4afc8c11f79ceab08f4b2bd5d1033e4e0e41ee4045b0 |
| `outputs/input_deck.i` | 962da5c2534259b27de4bcc98c34e95f81ab4a7a5b949836921dcef1686d4aa1 |
| `outputs/job_script.sbatch` | 46ca650c0c37fa216cb03a7536ef45a316305fdd4733191ac84e1cb2eb78e74b |
| `outputs/generated_config/interface.xml` | 2f545669f80885d182291e9aad47d74baf8403082364f79f67542f653a616885 |
| `outputs/generated_config/engine_input_deck.xml` | 7f3edc06119d4155981b3861c2c2263f268e6a3f56f7577cc0aa202f3b35169a |
| `outputs/generated_config/engine_operations.xml` | c5b07640e3f1427a5f763631a2f7f9c3ec1ea54e97160106efe598afc0c67c1b |
| `outputs/generated_config/analyze_2_input_deck.xml` | 9bc13ac9c61c0d8b3c7c73b5c0bce38e31c7d35b53e45483c2fd5238bea222e8 |
| `outputs/generated_config/analyze_2_operations.xml` | fbabf1a1c037533ce5dc1b1ba6a97ce9d70a795c1128735196a3e624aa73efa0 |
| `outputs/generated_config/analyze_helmholtz_input_deck.xml` | e0b190ab3e8c71334d7b7ec5f0567dbcdae40f7a371b943a553d6eb54fae5436 |
| `outputs/generated_config/analyze_helmholtz_operations.xml` | 402ffc30789914bd0c1c7bf429aa2f08ea22b0040960d015b9c71fd716404854 |
| `outputs/generated_config/mpirun.source` | 5f45e199f30722f60934996cf4b58b4ce832972c71a3ef0cbe97ae2f6469f3bc |
| `outputs/morphorm_oc_optimizer_diagnostics.txt` | 5bf3294ab40a1a55925134eb0ef493c7cb725e0964ae54cb3ce1ee62ae18e4f4 |
| `outputs/engine_output.exo` | 9b053a7c2d14ab5200f97efc1b927f3c6a5c787e754ddbd16e6212a1a988f7c9 |
| `outputs/final_analyze_output.exo` (iteration 50) | 7b9510366799145234e5d149e7916485b20f3ed58138e1f7d6d62f12afb7ceb7 |
| `outputs/run_logs/` | slurm-16176085.out/.err, morphorm_run.log, cubit_run.log, opt_criteria_history.csv, performer logs, final_output_check.txt (hashes in SHA256SUMS.txt) |

The generated-config SHA-256 values equal those printed by the job (`slurm-16176085.out`), proving the job ran the verified configuration.

## 10. Failures, retries, cancelled jobs, unresolved issues, deviations

- **Translation retry (before any run):** the first XMLGenerator translation (symmetry keyword in the filter block) did not carry the symmetry-plane sideset into the Helmholtz configuration; it was discarded (kept for the record in `work/xmlgen_tests/attempt0_filter_block_keyword/`) and the deck was corrected (keyword in the study block). The generated files in `work/run/` were replaced before submission; only the corrected configuration was ever run. No Slurm job was affected.
- **Control checksum:** `catalog/checksums.sha256` lists `.gitignore`, which the snapshot archive does not contain; the other 23 entries verified. Not a scientific input.
- **Deliverable replacement:** `outputs/SHA256SUMS.txt` was regenerated once after adding `outputs/run_logs/final_output_check.txt`; no scientific deliverable was overwritten.
- **Manual vs specification:** the User Manual states that essential boundary conditions must be on nodesets; the specification (locked) requires u_z = 0 through the sideset `ss_sym`. The deck follows the specification and XMLGenerator produced an Essential Boundary Condition with `Sides = ss_sym` (analyze accepted it and ran). Reported for transparency; no locked value was changed.
- No cancelled or failed jobs; no deviation from §1–§7 of the specification; **none** unresolved.

## 11. Final artifact paths

- Scientific: `outputs/mesh.jou`, `outputs/mesh.exo`, `outputs/mesh_verification.json`, `outputs/input_deck.i`, `outputs/job_script.sbatch`, `outputs/generated_config/` (8 XMLGenerator files + `generated_config_verification.txt` + `xmlgenerator.log`), `outputs/morphorm_oc_optimizer_diagnostics.txt`, `outputs/engine_output.exo`, `outputs/final_analyze_output.exo`, `outputs/run_logs/`, `outputs/SHA256SUMS.txt`, `jobs/job_ids.txt`, `jobs/morphorm_oc50_symplane.sbatch`, `jobs/sacct_16176085.txt`, `jobs/submissions.log`, `work/run_summary.md`.
- Distributed context: `provenance/sources_searched.tsv`, `provenance/artifact_selections.md`, `staging-manifest/staged_files.tsv`, `staging-manifest/globus_transfers.tsv`, `staging-manifest/returned_files.tsv` (header only; nothing was returned), `provenance/node_local_placement.txt`, `provenance/control_and_source_versions.txt`.
- Working copies (kept, unmodified after the run): `work/mesh/`, `work/run/` (full run directory incl. `analyze_id_2_output_scenario_id_1/iteration0..50.exo`), `work/scripts/`, `work/xmlgen_tests/`, `logs/staging/`, `staging-inbox/` (Globus transfer record), `$E3_STAGING_DIR` (left in place).
