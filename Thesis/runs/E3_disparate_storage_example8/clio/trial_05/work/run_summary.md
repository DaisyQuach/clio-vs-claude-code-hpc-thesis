# Run summary — E3 Symmetry-Plane Cantilever (E3-SPC-v1)

## 1. Trial identity
| Item | Value |
|---|---|
| Trial identifier (`$E3_TRIAL_ID`) | `E3-clio-trial_05` |
| Staging directory (`$E3_STAGING_DIR`) | `/scratch/local/u1282901/16248146/e3/clio/E3-clio-trial_05` (host notch204, Slurm allocation 16248146; `provenance/node_local_placement.txt`) |
| Control commit | `62954055b4e848f2155258c5b8c628eab97c8586` (snapshot `agent-inputs/control/`, catalog version 5; `sha256sum -c catalog/checksums.sha256`: all listed files OK, `.gitignore` absent from the snapshot) |
| Assigned task | Construct and run the Symmetry-Plane Cantilever minimum-compliance topology optimization exactly as locked in `task/frozen_task_specification.md` (E3-SPC-v1): half 2×1×0.5 cantilever, HEX8 48×24×12, Helmholtz filter with symmetry plane, OC, 50 iterations, Slurm with frozen resources, deliverables with SHA-256 manifest. |
| Agent host | notch204 (no Morphorm optimization executed on it; only Cubit meshing, XMLGenerator translation and Python verification, as permitted by `compute_resources.md`). |

## 2. Discovery
Collections searched (detail: `provenance/sources_searched.tsv`, 11 records):
- `e3-control` — `agent-inputs/control/` snapshot: README, task/, catalog/ (storage catalog, 5 artifact cards, checksums), protocol/ (4 files), helper scripts. Read in full.
- `e3-chpc-candidate-archive` — `ls`/`find` of the whole archive root (4 packages, `README.md`, `MANIFEST.sha256`); README.md and problem_card.yaml of every package read by POSIX; `verify_collection.sh` → PASS (manifest sha 3c89c503… = catalog value).
- `e3-private-source` — `globus ls -r` of the collection root via collection `6dcea62e-130d-47a9-8b77-80fba6f58693` only (manuals/, documentation/, target_materials/). Files staged by `globus_stage_file.sh` into `staging-inbox/` through destination collection `7cf0baa1-…` and then into `$E3_STAGING_DIR` (12 Globus tasks incl. MANIFEST.sha256, all SUCCEEDED; `staging-manifest/globus_transfers.tsv`). The host path `globus_source_root` was never read.
- No other location was listed, searched or opened. `e3-trial-inbox-destination` was used only as the Globus destination.

## 3. Artifact selection
Detail: `provenance/artifact_selections.md`. Summary:
- **used**: `target_materials/symmetry_plane_cantilever/problem_specification.md` (byte-identical to the control spec — verified by `diff`), `software_contract.md`, `compute_resources.md`, `version_provenance.yaml`, curated READMEs, `manuals/Morphorm_User_Manual.pdf` (keyword reference, converted once to `work/manual/user_manual.txt`).
- **adapted**: `example_07` (full Helmholtz cantilever deck and Cubit journal) — the closest workflow; halved width, added `ss_sym` sideset, u_z = 0 sideset BC, explicit SIMP material interpolation, filter symmetry plane, `update_problem_frequency 1`.
- **examined, not used**: `example_16_restart` (restart workflow irrelevant to one uninterrupted run; stage-1 files staged only as a keyword cross-check), `example_01` (tet bracket, kernel filter), `example_13` (2-D). `Morphorm_Theory_Manual.pdf` and the two figures were listed but not staged (not needed).

## 4. Staging
Detail: `staging-manifest/staged_files.tsv` (16 files, 2,167,418 bytes; source and staged SHA-256 match on every line) and `staging-manifest/returned_files.tsv` (5 files, 14,269 bytes copied from staging into `work/reference/` for traceability of the adapted/used sources). Staged: 11 private-source files by Globus (10 documentation/specification files + User Manual 2,142,345 B) and 5 candidate-archive files by `stage_file.sh` (`cp -p`). Nothing in any source collection or in `staging-inbox/` was modified. The Slurm job read no staged file: it ran entirely from `work/run2/` in the trial workspace.

## 5. Mesh
- Journal `outputs/mesh.jou` (= `work/mesh/mesh.jou`), adapted from the example_07 journal: brick 2.0 × 1.0 × 0.5 moved so the corner is at the origin, `scheme map`, size 0.0416667, `block_1` HEX8, `ns_fix` (nodes in surface with x < h/2), `ns_load` (nodes with x > 2 − h/2 and y < h/2), `ss_sym` (surface with z > 0.5 − h/2), `export mesh "mesh.exo" dimension 3`.
- Command (agent host, 2026-10-13T18:20:42Z, after sourcing the approved loader): `cubit -batch -nographics -nojournal -input mesh.jou` → exit 0 (`outputs/run_logs/cubit.log`).
- Verification (`exo_summary.py --expect …`, record `outputs/mesh_verification.json`, `expect_ok: true`): 13,824 elements, 15,925 nodes, dim 3, bbox [0,0,0]–[2.0,1.0,0.5], one block `block_1` HEX8 with 13,824 elements, `ns_fix` 325 nodes, `ns_load` 13 nodes, `ss_sym` 1,152 faces — all equal to the locked values. `outputs/mesh.exo` (SHA-256 1a0b3ea8…) is byte-identical to the copy the job used (`cmp`).

## 6. Input deck and generated configuration
Accepted deck: `outputs/input_deck.i` (= `work/run2/input_deck.i`). A first translation (`work/run/input_deck.i`, filter declared as a `begin filter 1 … end filter` block with `filter_ids 1`) produced a Helmholtz configuration **without** the symmetry plane (`xml_params.py`: `MISSING symmetry`), so following the manual's statement that the filter block and the study-level keywords are equivalent (User Manual §2.5, Table 2.5.12 and "General Filter Keywords" note) the deck was re-translated once in a clean directory with the study-level form. The analyze deck, `interface.xml` and `engine_operations.xml` are byte-identical between the two translations; only `analyze_helmholtz_input_deck.xml` gained `Symmetry Plane Sides`. The first (not submitted) translation is kept in `work/run/`.

Locked settings and where each appears in the generated runtime configuration (`outputs/generated_config/`; machine record `outputs/run_logs/generated_config_params.tsv`):
| Locked setting | Deck | Generated configuration |
|---|---|---|
| Material E = 1.0, ν = 0.3 on `block_1` | `material 1`, `block 1` | `analyze_2_input_deck.xml` Material Models/material_1: Youngs Modulus 1.0, Poissons Ratio 0.3; Domains/block_1 → material_1 |
| SIMP single phase, exponent 3.0, minimum 1e-3 | `material_interpolation 1` (type single_phase, model simp, minimum_value 1e-3; exponent left at runtime default) | `analyze_2_input_deck.xml` Residual Penalty Function: Type SIMP, Exponent 3.0, Minimum Value 1e-3; Material Interpolation Model Single-Phase |
| Compliance criterion `minimum_ersatz_material_value 1e-3` | `criterion 1` | `analyze_2_input_deck.xml` Criteria/My Objective: Internal Elastic Energy, Penalty Function SIMP, Exponent 3.0, Minimum Value 1e-3 |
| Fixed support `ns_fix` u_x=u_y=u_z=0 | `boundary_condition 1` | Essential Boundary Conditions: Displacement X/Y/Z with ID 1/2/3, Sides ns_fix, Value 0 |
| Symmetry `ss_sym` u_z = 0 via sideset | `boundary_condition 2` (location_type sideset) | Essential Boundary Conditions: Displacement Z with ID 4, Index 2, Sides ss_sym, Value 0 |
| Load: concentrated, direction y, −1.0 per node on `ns_load` | `load 1` | Concentrated Loads: Dof 1, Value −1.0, Nodes ns_load; Natural Boundary Conditions empty (no tractions, no body forces) |
| Objective: weighted sum, single compliance criterion, weight 1, analyze service | `objective` | `interface.xml` objective stages use service 2 (analyze) operations; `engine_operations.xml` aggregator weight 1 |
| Constraint volume ≤ 0.15, less_than, engine service | `constraint 1` (service_id 1) | `interface.xml` Optimizer/Constraint NormalizedTargetValue 0.15; volume computed by PlatoMain (engine) operations |
| Density discretization, initial density 0.15 | `study` | `engine_operations.xml` Initialize Field: Method Uniform, Value 0.15; `interface.xml` InitializationStage "Initial Guess" |
| OC, default tolerances, `normalize_in_aggregator false` | `study` | `interface.xml` Optimizer Package OC, OCControlStagnationTolerance 1e-4, OCObjectiveStagnationTolerance 1e-8, OCGradientTolerance 1e-8 (runtime defaults as printed by XMLGenerator) |
| `update_problem true`, frequency 1 | `service 1` | `interface.xml` ProblemUpdateFrequency 1 and UpdateProblemStage; `engine_operations.xml` UpdateProblemFrequency 1 |
| `max_iterations 50` | `study` | `interface.xml` Convergence/MaxIterations 50; `engine_operations.xml` MaxIterations 50 |
| Helmholtz filter, radius 0.15, sticking penalty 1.0, symmetry plane `ss_sym` | `study`: filter_type helmholtz, filter_radius_absolute 0.15, boundary_sticking_penalty 1.0, symmetry_plane_location_names ss_sym | `analyze_helmholtz_input_deck.xml` Parameters: Length Scale 0.043301 (= 0.15/(2√3), the generator's conversion of the absolute radius; same value in both translations, whereas the default radius 1.0 would give 0.2887), Surface Length Scale 1.0, Symmetry Plane Sides {ss_sym} |
| Services: engine + analyze, 1 processor each, single rank, no decomposition | `service 1`, `service 2` | `mpirun.source`: `-np 1` PlatoMain, `-np 1` analyze_MPMD (mechanical), `-np 1` analyze_MPMD (Helmholtz filter service generated by XMLGenerator); no decomp step |
| Output dispx dispy dispz from analyze; engine output of control and topology | `output 1` | `analyze_2_input_deck.xml` Output Plottable {displacement_x, displacement_y, displacement_z}; `engine_operations.xml` PlatoMainOutput with arguments topology and control; `engine_input_deck.xml` output file engine_output |
No deck setting was found absent from the generated configuration after the second translation. `xml_params.py` reports `MISSING sticking` only because the generated name of the boundary-sticking term is "Surface Length Scale" (present, 1.0).

## 7. Execution
All commands were run from the trial root after `source …/automation/environment/load_morphorm_e3.sh` (modules chpc/1.0, gcc/11.2.0, openmpi/5.0.3, morphorm/approved-runtime, cubit-edu/2026.8; `module list` is printed in the job stdout). Chronological log with UTC timestamps: `work/notes.log`.
- Discovery/staging: `record_node_placement.sh`; `sha256sum -c catalog/checksums.sha256`; `ls`/`find` of the candidate archive; `verify_collection.sh <archive>`; `globus ls -r --long 6dcea62e-…:/`; 11 × `globus_stage_file.sh <path>`; 5 × `stage_file.sh <archive file>`; `record_search.sh` after each listing/read; `pdftotext -layout <User Manual> work/manual/user_manual.txt` (one conversion; then `grep -n`/`sed -n`).
- Mesh: `cubit -batch -nographics -nojournal -input mesh.jou` in `work/mesh/` (18:20:42Z); `python3 SKILL_ROOT/scripts/exo_summary.py work/mesh/mesh.exo --expect …`.
- Translation: `XMLGenerator input_deck.i` in `work/run/` (18:21:04Z, filter-block form, rejected) and in `work/run2/` (18:21:47Z, accepted); `python3 SKILL_ROOT/scripts/xml_params.py <dir> …`; `diff` of generated files between the two directories.
- Submission: `sbatch --parsable jobs/morphorm_e3_spc_v1.sbatch` at 2026-10-13T18:22:16Z → **job 16248958** (the only job submitted; `jobs/job_ids.txt`, `jobs/submissions.tsv`). Script: `jobs/morphorm_e3_spc_v1.sbatch` (copy `outputs/job_script.sbatch`), resources exactly as `compute_resources.md`: account/partition hochhalter-np, 1 node, 1 task, 8 cpus-per-task, 32G, 02:00:00, no GPU; it sources the approved loader, prints `module list`, `cd work/run2`, hashes its inputs, and runs `bash mpirun.source`.
- Wait: `wait_job.sh 16248958 540 work/run2/morphorm_oc_optimizer_diagnostics.txt` (two calls).
- Job record (`jobs/sacct_16248958.txt`): State COMPLETED, ExitCode 0:0, Submit 12:22:16, Start 12:23:28, End 12:40:39 (local), Elapsed 00:17:11, AllocCPUS 8, ReqMem 32G, MaxRSS 1,393,356 K, node notch273. stderr empty; stdout `outputs/run_logs/morphorm_16248958.out` (utc_start 18:23:32Z, mpirun_rc=0).
- Delivery: `cp -p` of run files into `outputs/`, `hash_outputs.sh` (30 files hashed), 5 × `return_file.sh`.

## 8. Completed stages and iteration count
One uninterrupted optimization. `outputs/morphorm_oc_optimizer_diagnostics.txt`: 51 iteration rows (Iter 0 … 50), first objective F(X) = 2.654786e+06 (uniform density 0.15), last row `50 51 1.044701e+05 7.033815e+03 -1.628697e-13 1.142971e-01 6.611695e+01`. Stopping message: `****** Optimization stopping due to exceeding maximum number of iterations. ******` — the run reached the locked iteration cap of 50; no convergence stop occurred before it (`outputs/run_logs/diagnostics_summary.json`). The volume constraint value H1(X) at iteration 50 is −1.6e-13 (constraint active, satisfied). `opt_criteria_history.csv` lists 51 objective values, 2.6548e+06 → 1.0447e+05.

## 9. Key outputs (SHA-256 in `outputs/SHA256SUMS.txt`, 30 entries incl. a pre-existing empty `outputs/.gitkeep`)
| File | SHA-256 (first 16) | Note |
|---|---|---|
| `outputs/mesh.jou` | b5a3e43454edf719 | Cubit journal |
| `outputs/mesh.exo` | 1a0b3ea85a2e17df | 1,052,996 B, verified §5 |
| `outputs/mesh_verification.json` | d37ca675238200df | exo_summary expect record |
| `outputs/input_deck.i` | a57be55d082816da | accepted deck |
| `outputs/job_script.sbatch` | f75600648a032000 | = jobs/morphorm_e3_spc_v1.sbatch |
| `outputs/generated_config/interface.xml` | 2f545669f80885d1 | plus engine_input_deck.xml, engine_operations.xml, analyze_2_input_deck.xml, analyze_2_operations.xml, analyze_helmholtz_input_deck.xml, analyze_helmholtz_operations.xml, mpirun.source, xmlgenerator.log — all XMLGenerator files used by job 16248958 (hashes also printed in the job stdout) |
| `outputs/morphorm_oc_optimizer_diagnostics.txt` | 5bf3294ab40a1a55 | 51 iterations |
| `outputs/engine_output.exo` | 9b053a7c2d14ab52 | 14,073,528 B; 51 time steps; nodal fields `control`, `topology` (exo_summary: `outputs/run_logs/engine_output_summary.json`) |
| `outputs/final_analyze_output.exo` | 7b9510366799145234 | = `work/run2/analyze_id_2_output_scenario_id_1/iteration50.exo`; time 50; nodal fields Topology (min 1.0e-08, max 0.939), displacement X/Y/Z; element field My Objective (`outputs/run_logs/final_analyze_output_summary.json`) |
| `outputs/run_logs/` | — | Slurm stdout/err, morphorm_run.log, engine_1_0.log, analyze_2_1.log, analyze_helmholtz_2.log, opt_criteria_history.csv, cubit.log, verification JSON/TSV |

## 10. Failures, retries, cancelled jobs, deviations
- No job failed or was cancelled; one submission only.
- Retry of translation only: the filter-block form did not propagate `symmetry_plane_location_names` to `analyze_helmholtz_input_deck.xml`; the deck was re-translated once with the manual's equivalent study-level form before any submission (§6). Not a deviation from the specification; both decks are kept.
- Observations, not deviations: (a) `engine_operations.xml` PlatoMainOutput OutputFrequency is the runtime default 5, which the specification does not lock; the delivered `engine_output.exo` nevertheless contains 51 time steps. (b) XMLGenerator adds a third single-rank performer (the Helmholtz filter analyze service) to `mpirun.source`; the deck declares exactly the two locked services, one processor each. (c) The SIMP exponent was left at the runtime default and verified as 3.0 in the generated analyze deck, as the specification states. (d) `.gitignore` listed in the control checksums is absent from the snapshot (not an input to this task).
- Unresolved issues: none. Deviations from E3-SPC-v1: none identified.

## 11. Final artifact paths (relative to the trial root)
`outputs/mesh.jou`, `outputs/mesh.exo`, `outputs/mesh_verification.json`, `outputs/input_deck.i`, `outputs/job_script.sbatch`, `outputs/generated_config/` (9 files), `outputs/morphorm_oc_optimizer_diagnostics.txt`, `outputs/engine_output.exo`, `outputs/final_analyze_output.exo`, `outputs/run_logs/` (12 files), `outputs/SHA256SUMS.txt`; `jobs/job_ids.txt`, `jobs/morphorm_e3_spc_v1.sbatch`, `jobs/sacct_16248958.txt`, `jobs/submissions.tsv`; `logs/morphorm_16248958.out`, `logs/morphorm_16248958.err`; `provenance/sources_searched.tsv`, `provenance/artifact_selections.md`, `provenance/node_local_placement.txt`, `provenance/control_and_source_versions.txt`; `staging-manifest/staged_files.tsv`, `staging-manifest/returned_files.tsv`, `staging-manifest/globus_transfers.tsv`; `work/run_summary.md`, `work/notes.log`, `work/run2/` (accepted run directory, incl. all 51 per-iteration analyze outputs), `work/run/` (rejected first translation), `work/mesh/`, `work/verify/`, `work/manual/user_manual.txt`, `work/reference/`.
