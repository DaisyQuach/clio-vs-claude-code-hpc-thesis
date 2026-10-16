# Run summary — E3-clio-trial_04 (Symmetry-Plane Cantilever, E3-SPC-v1)

## 1. Identification
- Trial identifier (`$E3_TRIAL_ID`): `E3-clio-trial_04`
- Staging directory (`$E3_STAGING_DIR`): `/scratch/local/u1282901/16247644/e3/clio/E3-clio-trial_04` (host notch204, Slurm allocation 16247644; `provenance/node_local_placement.txt`)
- Trial root: `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/clio/trial_04`
- Control commit: `62954055b4e848f2155258c5b8c628eab97c8586` (`agent-inputs/CONTROL_COMMIT.txt`; checksum verification in `provenance/control_and_source_versions.txt`)
- Assigned task: construct and complete the half-domain minimum-compliance topology optimization locked in `task/frozen_task_specification.md` (E3-SPC-v1): Cubit HEX8 mesh 48×24×12, Morphorm deck, XMLGenerator translation, verification of mesh and generated configuration, one 50-iteration OC run under the frozen Slurm resources, deliverables with SHA-256 manifest.

## 2. Discovery (detail: `provenance/sources_searched.tsv`)
| UTC | Collection | What was done |
|---|---|---|
| 17:51:04 | e3-control | read the whole snapshot `agent-inputs/control/` (task, catalog, cards, protocol, helpers); `sha256sum -c catalog/checksums.sha256`: 23 files OK, listed `./.gitignore` absent from the snapshot |
| 17:51:04 | e3-chpc-candidate-archive | `find -type f` (26 files, listing in `work/archive_listing.tsv`); `verify_collection.sh` MANIFEST.sha256 → PASS |
| 17:51:14 | e3-private-source | `globus ls --recursive --long` of collection `6dcea62e-130d-47a9-8b77-80fba6f58693` (15 entries, `work/globus_ls_private_source.txt`); nothing read by POSIX path |
| 17:51–17:52 | e3-chpc-candidate-archive | read README and `problem_card.yaml` of all four packages; read `example_07` provenance, deck and journal |

No other location was listed, searched or opened. The Globus destination collection was used only as transfer target for `staging-inbox/`.

## 3. Artifact selection (detail: `provenance/artifact_selections.md`)
- **Used (private source):** `software_contract.md`, `compute_resources.md`, `problem_specification.md` (byte-identical to the control specification, SHA-256 `f1bd0b56…`), the target README and `permitted_starting_materials/README.md`, `Morphorm_User_Manual.pdf` (keyword reference), collection `README.md`, `curated_readme.md`, `version_provenance.yaml`.
- **Not staged:** `geometry_and_loading_figure.png` (figure only; all definitions are numeric in the spec), `Morphorm_Theory_Manual.pdf` (background only), `MANIFEST_README.md`, `MANIFEST.tsv`.
- **Adapted:** `example_07` (full-domain Helmholtz cantilever): deck block structure and Cubit selection idioms reused; half domain, `ss_sym` sideset, u_z=0 symmetry BC and `symmetry_plane_location_names ss_sym` added; every value comes from the locked specification.
- **Not used:** `example_01` (bracket, tet, kernel filter), `example_13` (2-D), `example_16_restart` (restart workflow) — examined via README/problem card only.

## 4. Staging (detail: `staging-manifest/`)
- 11 files, 2,161,721 bytes staged into `$E3_STAGING_DIR` (`staging-manifest/staged_files.tsv`): 9 from e3-private-source by Globus (`globus_stage_file.sh`; 10 transfer tasks incl. `MANIFEST.sha256`, all SUCCEEDED, `staging-manifest/globus_transfers.tsv`; each file matched the collection manifest and the inbox→staging copy matched again), 2 from e3-chpc-candidate-archive by `stage_file.sh` (`topology_mech_ex7.i`, `topology_mech_ex7.jou`; source/copy SHA-256 equal).
- Returned files: none. No staged file was copied into the trial workspace; the mesh, deck and job script were written in `work/` from the specification, so `staging-manifest/returned_files.tsv` holds the header only. The manual was converted to text under `work/manual/` (derived file, not a copy).
- Staged originals were not modified.

## 5. Mesh
- Generated on the agent host (permitted by `compute_resources.md`) with the approved Cubit (`cubit-edu/2026.8`, loader sourced): `cubit -batch -nographics -nojournal -input mesh.jou` at 17:54:11Z, exit 0 (`outputs/run_logs/cubit_batch.log`).
- Journal `work/mesh/mesh.jou` → `outputs/mesh.jou`; mesh `work/mesh/mesh.exo` → `work/run/mesh.exo` (used by the run) → `outputs/mesh.exo` (byte-identical, `cmp` checked).
- Verification (`exo_summary.py`, 17:54:27Z, record `outputs/mesh_verification.json`): 13,824 elements, 15,925 nodes, dim 3, bbox [0,0,0]–[2.0,1.0,0.5], one block `block_1` HEX8 (13,824 elements), `ns_fix` 325 nodes, `ns_load` 13 nodes, `ss_sym` 1,152 faces — all expectations met (`expect_ok: true`).

## 6. Input deck and generated configuration
- Deck: `work/run/input_deck.i` → `outputs/input_deck.i` (SHA-256 `7cf05672…`). Translated at 17:55:37Z with `XMLGenerator input_deck.i` (exit 0) in the clean directory `work/run/`; generated files copied to `outputs/generated_config/` (hashes printed by the job in `outputs/run_logs/morphorm_16247887.out` equal those in `outputs/SHA256SUMS.txt`, so these are the files the accepted run used).
- First translation attempt used the manual's `begin filter … end filter` form; its `analyze_helmholtz_input_deck.xml` lacked the symmetry-plane sideset, so it was **not** run; it is preserved unchanged in `work/run_attempt1_filter_block/`. The accepted deck uses the equivalent study-level keywords (`filter_type helmholtz`, `filter_radius_absolute 0.15`, `boundary_sticking_penalty 1.0`, `symmetry_plane_location_names ss_sym`; manual Table 2.5.12). All other generated files were byte-identical between the two attempts.

| Locked setting | Deck | Generated configuration (`outputs/generated_config/`) |
|---|---|---|
| E = 1.0, ν = 0.3 on block_1 | material 1, block 1 | `analyze_2_input_deck.xml` Material Models/material_1 Youngs Modulus 1.0, Poissons Ratio 0.3; Spatial Model/Domains/block_1 |
| SIMP single phase, exponent 3.0, minimum 1e-3 | material_interpolation 1 minimum_value 1e-3 | `analyze_2_input_deck.xml` Residual Penalty Function SIMP, Exponent 3.0, Minimum Value 1e-3; Material Interpolation Model Single-Phase |
| compliance criterion minimum_ersatz 1e-3, weight 1, analyze service | criterion 1, objective weighted_sum | `analyze_2_input_deck.xml` Criteria/My Objective Internal Elastic Energy, Penalty Function Minimum Value 1e-3; `interface.xml` Objective stage on performer analyze |
| ns_fix u_x=u_y=u_z=0 | boundary_condition 1 (nodeset) | Essential Boundary Conditions: Displacement X/Y/Z with ID 1/2/3, Sides ns_fix, Value 0 |
| ss_sym u_z=0 (through the sideset) | boundary_condition 2 (location_type sideset) | Essential Boundary Conditions: Displacement Z with ID 4, Index 2, Sides ss_sym, Value 0 |
| load −1.0 per node, direction y, ns_load | load 1 concentrated_load | Concentrated Loads: Dof 1, Value −1.0, Nodes ns_load (13 nodes → total −13.0) |
| volume ≤ 0.15 relative, less_than, engine service | constraint 1 | `interface.xml` Constraint NormalizedTargetValue 0.15, ReferenceValueName Design Volume, stages on engine |
| density, initial 0.15 | discretization density, initial_density_value 0.15 | `engine_operations.xml` InitializeField Uniform Value 0.15 |
| OC, default tolerances, update_problem true, frequency 1 | optimization_algorithm oc, update_problem true, update_problem_frequency 1 | `interface.xml` Optimizer Package OC, ProblemUpdateFrequency 1, UpdateProblemStage; `engine_operations.xml` UpdateProblemFrequency 1; default tolerances (XMLGenerator log) |
| normalize_in_aggregator false | study keyword | no normalization option emitted in `interface.xml` (manual default is false; generated aggregator stage carries no normalize flag) |
| max_iterations 50 | study | `interface.xml` Convergence MaxIterations 50; `engine_operations.xml` MaxIterations 50 |
| Helmholtz, radius 0.15, sticking penalty 1.0, symmetry plane ss_sym | study-level keywords | `analyze_helmholtz_input_deck.xml` Length Scale 0.043301 (= 0.15/(2√3)), Surface Length Scale 1.0, **Symmetry Plane Sides {ss_sym}** |
| services: engine ×1, analyze ×1 (+ Helmholtz analyze performer), single rank, no decomposition | service 1/2 number_processors 1 | `mpirun.source`: `-np 1` PlatoMain, `-np 1` analyze_MPMD (analyze_2), `-np 1` analyze_MPMD (helmholtz) |
| output dispx dispy dispz; engine control+topology | output 1 | `analyze_2_input_deck.xml` Output Plottable {displacement_x, displacement_y, displacement_z}; `engine_operations.xml` PlatoMainOutput inputs topology, control |

Verification record: `outputs/generated_config/generated_config_verification.tsv` (`xml_params.py`; its only MISSING token, "algorithm", is a search word — the OC choice appears as `Package OC`).
