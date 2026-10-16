# Run summary — E3-clio-trial_02 (Symmetry-Plane Cantilever, E3-SPC-v1)

## 1. Identification
| Item | Value |
|---|---|
| Trial identifier (`$E3_TRIAL_ID`) | `E3-clio-trial_02` |
| Trial root | `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/clio/trial_02` |
| Staging directory (`$E3_STAGING_DIR`) | `/scratch/local/u1282901/16244752/e3/clio/E3-clio-trial_02` (host notch204, agent allocation 16244752; `provenance/node_local_placement.txt`) |
| Control commit | `62954055b4e848f2155258c5b8c628eab97c8586` (snapshot `agent-inputs/control/`, catalog version 5) |
| Assigned task | construct and complete the Symmetry-Plane Cantilever topology-optimization workflow exactly as locked in `task/frozen_task_specification.md` (E3-SPC-v1): half cantilever 2 × 1 × 0.5, HEX8 48 × 24 × 12, Helmholtz filter with symmetry plane `ss_sym`, OC, exactly 50 iterations, deliverables at the locked paths |
| Facts log | `work/notes.log` (one line per event, UTC) |

## 2. Discovery (detail: `provenance/sources_searched.tsv`)
| UTC | Collection | What |
|---|---|---|
| 16:01:00Z | `e3-control` | read the whole pinned snapshot (task, specification, deliverables, catalog, 5 artifact cards, protocol, helpers); `sha256sum -c catalog/checksums.sha256`: every provided file PASS; the listed `./.gitignore` is not part of the snapshot and could not be checked |
| 16:01:00Z | `e3-chpc-candidate-archive` | `verify_collection.sh` PASS (manifest sha256 3c89c503… = catalog); `find -type f` listed 4 packages (27 files) |
| 16:01:07Z | `e3-private-source` | `globus ls --recursive --long` of collection `6dcea62e-130d-47a9-8b77-80fba6f58693` (18 entries: manuals/, documentation/, target_materials/, MANIFEST.sha256, MANIFEST.tsv, README.md); the host path was never read directly |
| 16:01:31–16:01:32Z | `e3-chpc-candidate-archive` | README and the text files of example_01, example_07, example_13, example_16_restart staged and read |

No other location was listed, searched or read. The destination collection `7cf0baa1-…` was used only as the transfer target `staging-inbox/`.

## 3. Artifact selection (detail: `provenance/artifact_selections.md`)
| Candidate | Decision |
|---|---|
| `e3-private-source`: `software_contract.md`, `compute_resources.md`, `Morphorm_User_Manual.pdf`, README/curated_readme/version_provenance/MANIFEST_README, target `problem_specification.md` (+2 READMEs) | **used** (contract, frozen resources, deck syntax; `problem_specification.md` sha256 f1bd0b56… identical to the control snapshot's specification) |
| `e3-private-source`: `Morphorm_Theory_Manual.pdf`, `geometry_and_loading_figure.png` | not staged — formulation background / figure not needed, every value is locked numerically |
| `example_07` (full Helmholtz cantilever) | **adapted**: journal → half domain + `ss_sym`; deck → sideset symmetry BC, explicit SIMP block, Helmholtz symmetry plane |
| `example_16_restart`, `example_13`, `example_01` | examined, **not used** (restart workflow / 2-D / unrelated bracket); figures not staged |

## 4. Staging (detail: `staging-manifest/`)
- `staged_files.tsv`: 32 files, 2,199,657 bytes — `e3-private-source` 10 files, 2,159,049 bytes (by Globus, each checked against the collection `MANIFEST.sha256`, source and copy SHA-256 equal); `e3-chpc-candidate-archive` 22 files, 40,608 bytes (`stage_file.sh`, source and copy SHA-256 equal).
- `globus_transfers.tsv`: 11 Globus tasks (MANIFEST.sha256 + 10 files), all `SUCCEEDED`, 2,160,531 bytes into `staging-inbox/`.
- `returned_files.tsv`: header only — no staged file was copied byte-for-byte into the workspace. Derived files were written under `work/` (the manual converted once to `work/manual/user_manual.txt`; the ex7 journal and deck adapted into `work/mesh/mesh.jou` and `work/run02/input_deck.i`). The Slurm job needed nothing from staging.
- No file in any source collection was modified, moved or deleted.

## 5. Mesh
- Generated on the agent host (permitted by `compute_resources.md`) with `cubit -batch -nographics -nojournal -input mesh.jou` in `work/mesh/` (16:05:50Z, exit 0; log `outputs/run_logs/cubit_mesh.log`). Journal `work/mesh/mesh.jou` → `outputs/mesh.jou`; mesh `work/mesh/mesh.exo` (byte-identical copy used in the run) → `outputs/mesh.exo` (sha256 9dc06848…).
- Verification (`exo_summary.py` with `--expect`, 16:06:16Z; record `outputs/mesh_verification.json`, `expect_ok: true`): 13,824 HEX8 elements, 15,925 nodes, dim 3, bounding box [0,0,0]–[2.0,1.0,0.5], exactly one block `block_1` (13,824 elements), `ns_fix` 325 nodes, `ns_load` 13 nodes, `ss_sym` 1,152 faces. All values equal §3 of the specification.

## 6. Input deck and generated configuration
Accepted deck: `work/run02/input_deck.i` → `outputs/input_deck.i` (sha256 4ce1b535…). Translated with `XMLGenerator input_deck.i` (16:07:44Z, exit 0) in `work/run02/`; the files used by the run are in `outputs/generated_config/` (interface.xml, analyze_2_input_deck.xml, analyze_2_operations.xml, analyze_helmholtz_input_deck.xml, analyze_helmholtz_operations.xml, engine_input_deck.xml, engine_operations.xml, mpirun.source, xmlgenerator.log). The job's stdout records the SHA-256 of these files at run time; they equal `outputs/SHA256SUMS.txt`.

| Locked setting | Deck | Generated configuration (file: path = value) |
|---|---|---|
| E = 1.0, ν = 0.3 on block_1 | `material 1`, `block 1 name block_1` | `analyze_2_input_deck.xml`: Material Models/material_1/Isotropic Linear Elastic: Youngs Modulus 1.0, Poissons Ratio 0.3; Spatial Model/Domains/block_1 |
| SIMP exponent 3.0, minimum 1e-3 | `material_interpolation 1` (single_phase, simp, 1e-3, 3.0) | `analyze_2_input_deck.xml`: Residual/Mechanical Residual/Penalty Function: SIMP, Exponent 3.0, Minimum Value 1e-3 |
| compliance criterion, `minimum_ersatz_material_value 1e-3` | `criterion 1` | `analyze_2_input_deck.xml`: Criteria/My Objective: Internal Elastic Energy, Penalty Function SIMP, Exponent 3.0, Minimum Value 1e-3 |
| fixed support `ns_fix` u_x=u_y=u_z=0 | `boundary_condition 1` (nodeset) | `analyze_2_input_deck.xml`: Essential Boundary Conditions: Displacement X/Y/Z with ID 1/2/3, Sides ns_fix, Value 0 |
| symmetry `ss_sym` u_z=0 through the sideset | `boundary_condition 2` (`location_type sideset`, `dispz`) | `analyze_2_input_deck.xml`: Displacement Z with ID 4, Index 2, Sides ss_sym, Value 0 |
| load −1.0 per node in y on `ns_load` (13 nodes, total −13) | `load 1` concentrated_load | `analyze_2_input_deck.xml`: Concentrated Load with ID 0: Dof 1, Value −1.0, Nodes ns_load; no natural BCs |
| objective weighted sum, weight 1, analyze service | `objective` | `interface.xml` Optimizer/Objective; `engine_operations.xml` Aggregator Weight Value 1 |
| volume ≤ 0.15, less_than, engine service | `constraint 1` | `interface.xml`: Optimizer/Constraint NormalizedTargetValue 0.15, ReferenceValueName Design Volume |
| density, initial 0.15 | `study` | `engine_operations.xml`: Initial Guess Uniform Value 0.15 |
| OC, default tolerances | `optimization_algorithm oc` | `interface.xml`: Package OC; OCControlStagnationTolerance 1e-4, OCObjectiveStagnationTolerance 1e-8, OCGradientTolerance 1e-8 (runtime defaults, not set in the deck) |
| `normalize_in_aggregator false` | `study` | `engine_operations.xml` Aggregate Data: no normalization element present (the translator emits none for `false`) |
| `update_problem true`, frequency 1 | `service 1`, `study` | `interface.xml`: UpdateProblemStage Update Problem, ProblemUpdateFrequency 1; `engine_operations.xml` UpdateProblemFrequency 1 |
| `max_iterations 50` | `study` | `interface.xml`: Convergence/MaxIterations 50; `engine_operations.xml` MaxIterations 50 |
| Helmholtz, radius 0.15, sticking penalty 1.0, symmetry plane `ss_sym` | `study`: `filter_type helmholtz`, `filter_radius_absolute 0.15`, `boundary_sticking_penalty 1.0`, `symmetry_plane_location_names ss_sym` | `analyze_helmholtz_input_deck.xml`: Length Scale 0.043301 (= 0.15/(2√3), the translator's conversion of the radius), Surface Length Scale 1.0, Symmetry Plane Sides {ss_sym} |
| services engine + analyze, 1 processor each, no decomposition | `service 1/2` | `mpirun.source`: three `-np 1` performers (PlatoMain, analyze_MPMD mechanical, analyze_MPMD helmholtz) |
| output dispx dispy dispz; engine control/topology | `output 1` | `analyze_2_input_deck.xml`: Output/Plottable {displacement_x, displacement_y, displacement_z}; `engine_input_deck.xml` output file engine_output |

Filter-form note: the first translation (`work/run01`, filter-block form `begin filter 1 … symmetry_plane_location_names ss_sym`) produced Length Scale and Surface Length Scale but **no** symmetry-plane sideset; it was rejected before any submission and kept for the record. The study-level form (User Manual Table 2.5.12) produced the sideset; every other generated file was byte-identical between run01 and run02 (`diff`). Verification records: `work/verify/xml_params_run01.txt`, `work/verify/xml_params_run02.txt` (= `outputs/run_logs/xml_params_run02.txt`).

## 7. Execution
Commands (all after `source …/load_morphorm_e3.sh`, modules gcc/11.2.0, openmpi/5.0.3, morphorm/approved-runtime, cubit-edu/2026.8 — `module list` is in the job stdout):
1. `cubit -batch -nographics -nojournal -input mesh.jou` (agent host, `work/mesh/`).
2. `python3 SKILL_ROOT/scripts/exo_summary.py work/mesh/mesh.exo --expect …` → `work/verify/mesh.json`.
3. `XMLGenerator input_deck.i` in `work/run01/` (rejected) and `work/run02/` (accepted); `python3 SKILL_ROOT/scripts/xml_params.py work/run02 …`.
4. `sbatch --parsable jobs/morphorm_run02.sbatch` at 2026-10-13T16:08:27Z → job **16245034** (`jobs/job_ids.txt`). The script contains the frozen resources verbatim (`--account=hochhalter-np --partition=hochhalter-np --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=32G --time=02:00:00`, no GPU), sources the approved interface, prints `module list` and input hashes, runs `bash mpirun.source > morphorm_run.log` in `work/run02/`. Copy of the script: `outputs/job_script.sbatch`.
5. Waited with `wait_job.sh 16245034 …` (three bounded waits); `sacct` record in `jobs/sacct_16245034.txt`.

| Job ID | Script | State | ExitCode | Submit → Start → End (local) | Elapsed | Node | MaxRSS |
|---|---|---|---|---|---|---|---|
| 16245034 | `jobs/morphorm_run02.sbatch` | COMPLETED | 0:0 | 10:08:27 → 10:08:35 → 10:26:39 | 00:18:04 | notch204 | 1,646,696 K |

Only this one job was submitted; none failed or was cancelled. Slurm placed it on notch204 (the same node that hosts the agent allocation) — it ran inside its own Slurm allocation with the frozen resources, not in the agent process. The job's `mpirun_rc=0`; stderr is empty.

## 8. Completed stages and iterations
- Mesh generation, mesh verification, deck translation, generated-configuration verification, optimization, output verification: all completed.
- Optimizer: 51 diagnostic rows (iterations 0–50), first objective 2.654786e+06 (uniform 0.15 design), last objective 1.044701e+05 at iteration 50; constraint H1 ≈ 0 (volume at the 15 % target) from iteration 4 on. Stop message: `****** Optimization stopping due to exceeding maximum number of iterations. ******` — the run reached the locked iteration cap of 50 (`diag_summary.py` record: `outputs/run_logs/diag_run02.json`).
- Output checks (`exo_summary.py`): `engine_output.exo` has 51 time steps with nodal fields `control` and `topology`; `final_analyze_output.exo` (= `analyze_id_2_output_scenario_id_1/iteration50.exo`) has one step (time 50) with nodal `Topology`, `displacement X/Y/Z`, Topology range 1.0e-08 … 0.939.
- Boundary-condition check on the final field (`outputs/run_logs/symmetry_bc_check_iteration50.txt`): |u_z| = 0.0 on all 1,225 nodes of the cut plane z = 0.5 (max |u_z| elsewhere 2.14e+03) and |u| = 0.0 on all 325 nodes of x = 0 — the sideset-based symmetry condition and the fixed support are enforced.

## 9. Key deliverables (`outputs/`, hashes in `outputs/SHA256SUMS.txt`, 31 entries)
| File | SHA-256 |
|---|---|
| `outputs/mesh.jou` | 0e616b09b228fc68ffb06fe181a6d31f98cdf5f4a40f2857fd8075245a7505b0 |
| `outputs/mesh.exo` | 9dc06848308c57dca629ba2f54911e0d73d0de23c84e7025daaaeca7c4106124 |
| `outputs/mesh_verification.json` | d37ca675238200df81f9cfb4b3243d5560df87ccaae1764061504a6c2998d619 |
| `outputs/input_deck.i` | 4ce1b535b7c4a16d49ccde56a642d46a25bf1aee4a019b1eb3644af91a5bc2d1 |
| `outputs/job_script.sbatch` | 98b7e4842ac76a275b765fe7e0652880dd4331a589aa0ef857de8c9c6048f31c |
| `outputs/generated_config/interface.xml` | 2f545669f80885d182291e9aad47d74baf8403082364f79f67542f653a616885 |
| `outputs/generated_config/analyze_2_input_deck.xml` | 9bc13ac9c61c0d8b3c7c73b5c0bce38e31c7d35b53e45483c2fd5238bea222e8 |
| `outputs/generated_config/analyze_helmholtz_input_deck.xml` | e0b190ab3e8c71334d7b7ec5f0567dbcdae40f7a371b943a553d6eb54fae5436 |
| `outputs/generated_config/engine_input_deck.xml` | 7f3edc06119d4155981b3861c2c2263f268e6a3f56f7577cc0aa202f3b35169a |
| `outputs/generated_config/mpirun.source` | 5f45e199f30722f60934996cf4b58b4ce832972c71a3ef0cbe97ae2f6469f3bc |
| `outputs/morphorm_oc_optimizer_diagnostics.txt` | 5bf3294ab40a1a55925134eb0ef493c7cb725e0964ae54cb3ce1ee62ae18e4f4 |
| `outputs/engine_output.exo` | 9b053a7c2d14ab5200f97efc1b927f3c6a5c787e754ddbd16e6212a1a988f7c9 |
| `outputs/final_analyze_output.exo` | 7b9510366799145234e5d149e7916485b20f3ed58138e1f7d6d62f12afb7ceb7 |
| `outputs/run_logs/` (Slurm stdout/stderr, `morphorm_run.log`, performer logs `engine_1_0.log`, `analyze_2_1.log`, `analyze_helmholtz_2.log`, `cubit_mesh.log`, verification records) | see `outputs/SHA256SUMS.txt` |
Also delivered: `outputs/opt_criteria_history.csv`, `outputs/generated_config/{analyze_2_operations,analyze_helmholtz_operations,engine_operations}.xml`, `outputs/generated_config/xmlgenerator.log`.

## 10. Failures, retries, cancelled jobs, deviations
- No failed, retried or cancelled job; no deliverable was overwritten.
- Translation attempt 1 (`work/run01`, filter-block form) did not carry the filter symmetry plane into the generated Helmholtz configuration; it was rejected before submission (no job) and replaced by the study-level form (`work/run02`). This is the only re-translation.
- `catalog/checksums.sha256` lists `./.gitignore`, which the snapshot does not contain; every other file verified.
- The User Manual (§3.3) states Dirichlet conditions are applied to nodesets; the specification locks the symmetry condition "applied through the sideset". The sideset form was used as locked, translated, and verified in the final field (u_z = 0 on every cut-plane node). Not a deviation; recorded as a documentation/specification difference.
- Deviations from the specification: **none**.

## 11. Final artifact paths (relative to the trial root)
- Scientific: `outputs/mesh.jou`, `outputs/mesh.exo`, `outputs/mesh_verification.json`, `outputs/input_deck.i`, `outputs/job_script.sbatch`, `outputs/generated_config/`, `outputs/morphorm_oc_optimizer_diagnostics.txt`, `outputs/engine_output.exo`, `outputs/final_analyze_output.exo`, `outputs/run_logs/`, `outputs/SHA256SUMS.txt`, `jobs/job_ids.txt`, `jobs/morphorm_run02.sbatch`, `jobs/sacct_16245034.txt`, `jobs/submissions.log`, `logs/morphorm_run02_16245034.{out,err}`, `work/run_summary.md`.
- Distributed context: `provenance/sources_searched.tsv`, `provenance/artifact_selections.md`, `provenance/node_local_placement.txt`, `provenance/control_and_source_versions.txt`, `staging-manifest/staged_files.tsv`, `staging-manifest/globus_transfers.tsv`, `staging-manifest/returned_files.tsv`, `staging-inbox/` (Globus transfer record, untouched).
- Working material: `work/notes.log`, `work/mesh/`, `work/run01/` (rejected translation), `work/run02/` (accepted run directory, all per-iteration outputs), `work/verify/`, `work/manual/user_manual.txt`.
