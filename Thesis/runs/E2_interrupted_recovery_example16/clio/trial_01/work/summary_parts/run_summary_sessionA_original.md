# Run summary — Session A (Stage 1 only)

**STATUS: Stage 1 is COMPLETE and verified. Stage 2 has NOT been started** (no Stage-2 deck, generated configuration, job script or job was created, translated, submitted or run in this session). Everything a later process needs for Stage 2 is in `outputs/`, `jobs/`, `logs/` and `work/`.

## 1. Trial identifier and assigned workflow

- Trial identifier: `E2-example16-clio-01` (from `THESIS_TRIAL_ID`); trial root `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E2_interrupted_recovery_example16/clio/trial_01`.
- Assigned workflow: `FROZEN-EX16-v1` — full cantilever (no symmetry), minimum-compliance density topology optimization, two-stage restart (warm-start) workflow. Stage 1 = 20 OC iterations from uniform density 0.15 with the engine output file as the checkpoint; Stage 2 (not run here) = 40 further iterations resuming from the iteration-20 `control` field.
- Session policy: Session A (this process) constructs the workflow and completes Stage 1 only, then stops.
- Software: approved interface `source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh` (modules observed after sourcing, on the agent host and inside the job: `chpc/1.0`, `gcc/11.2.0`, `openmpi/5.0.3`, `morphorm/approved-runtime`, `cubit-edu/2026.8`). Documentation used: only `agent_inputs/manuals/Morphorm_User_Manual.pdf` and `Morphorm_Theory_Manual.pdf` (converted once with `pdftotext -layout` to `work/manuals/user.txt`, `work/manuals/theory.txt`).
- Chronological facts log (UTC, one line per event): `work/notes.log`.

## 2. Mesh

- Generated on the agent host (permitted by `compute_resources.md`) with the approved Cubit in batch mode, 2026-10-13T06:15:03Z–06:15:06Z: `cubit -batch -nographics -nojournal -input mesh.jou` run in `work/mesh/` (exit code 0; Cubit log `work/mesh/cubit_mesh.log`; the RLM licensing notice in the log is informational, the batch run completed normally).
- Journal: `work/mesh/mesh.jou` → delivered as `outputs/mesh.jou`. Procedure: `brick x 2 y 1 z 1`, moved so the corner is at the origin; `volume 1 scheme map`; intervals 48 on the x-curves (length 2) and 24 on the y/z-curves (length 1) → uniform h = 1/24; `block 1` = volume 1, named `block_1`, element type HEX8; `nodeset 1` = all nodes with x < 1e-6, named `ns_fix`; `nodeset 2` = all nodes with x > 1.999999 and y < 1e-6, named `ns_load`; no sidesets; `export mesh ... dimension 3`.
- Mesh file: `work/mesh/mesh.exo` → `outputs/mesh.exo` (SHA-256 `71b221cd4af5d917e80fd2d12635e675807f7f53feeb22818b0125de90c174b0`); the identical file was copied to the Stage-1 run directory `work/stage1/run/mesh.exo`.
- Verification (before any optimization; `morphorm` skill script `exo_summary.py --expect ...`, 2026-10-13T06:15:19Z, exit 0, `expect_ok: true`), record `outputs/mesh_verification.txt` (also `work/verify/mesh.json`, `work/verify/mesh_nodeset_coords.txt`):
  - num_elem 27648, num_nodes 30625, num_dim 3;
  - bbox_min (0,0,0), bbox_max (2.0, 1.0, 1.0);
  - exactly one block, name `block_1`, type HEX8, 27648 elements (8 nodes/elem);
  - nodeset `ns_fix` 625 nodes, all at x = 0 spanning y in [0,1], z in [0,1];
  - nodeset `ns_load` 25 nodes, all at x = 2, y = 0, spanning z in [0,1];
  - no sidesets; unique node coordinates 49 x 25 x 25 with spacing 0.041666–0.041667 in x, y, z (h = 1/24).

## 3. Input deck and generated runtime configuration (Stage 1)

- Deck: `work/stage1/input_deck.i` → `outputs/stage1/input_deck.i` (SHA-256 `ff31180564abd7cffa148a0cbf4cc920f7a7d189c4c76ae2a324d6edf90a4f52`). Every keyword was taken from the User Manual (filter block Table 2.5.12; restart 2.5.10; concentrated_load 3.2.2; material_interpolation 6.10; output block 5.1).
- Translation: `XMLGenerator input_deck.i` in the clean run directory `work/stage1/run/` at 2026-10-13T06:16:15Z, exit 0 (`work/stage1/run/xmlgenerator.log`). Generated files (copied unmodified to `outputs/stage1/generated_config/`): `interface.xml`, `engine_input_deck.xml`, `engine_operations.xml`, `analyze_2_input_deck.xml`, `analyze_2_operations.xml`, `analyze_helmholtz_input_deck.xml`, `analyze_helmholtz_operations.xml`, `mpirun.source`, plus `xmlgenerator.log` and the check output `xml_params_verification.txt` (`xml_params.py`, also `work/verify/stage1_xml_params.txt`).
- Locked setting → deck keyword → where it appears in the generated configuration (all read from the generated files before submission):

| Locked setting | Deck | Generated configuration (Stage 1) |
|---|---|---|
| Mesh `mesh.exo`, one block `block_1` | `begin mesh / name mesh.exo`; `begin block 1 / name block_1 / material_id 1` | `engine_input_deck.xml` mesh `mesh.exo`, block index 1 material 1; `analyze_2_input_deck.xml` Spatial Model/Domains/`block_1` (Element Block `block_1`, Material `material_1`) |
| Material E = 1.0, nu = 0.3 on `block_1` | `material 1`: `isotropic_elastic`, `youngs_modulus 1.0`, `poissons_ratio 0.3` | `analyze_2_input_deck.xml` Material Models/material_1/Isotropic Linear Elastic: `Youngs Modulus 1.0`, `Poissons Ratio 0.3` |
| Fixed support `ns_fix`, u_x=u_y=u_z=0 | `boundary_condition 1`: `fixed_value`, nodeset `ns_fix`, `degree_of_freedom dispx dispy dispz`, `value 0 0 0` | `analyze_2_input_deck.xml` Essential Boundary Conditions: Displacement X/Y/Z (Index 0/1/2), Type Fixed Value, Sides `ns_fix`, Value 0 |
| Load -1.0 in y on every node of `ns_load` (total -25.0); no other loads | `load 1`: `concentrated_load`, nodeset `ns_load`, `direction y`, `value -1.0` (no `weight`, no `index`) | `analyze_2_input_deck.xml` Concentrated Loads / Concentrated Load with ID 0: `Dof 1` (y), `Value -1.0`, `Nodes ns_load`; Mechanical Natural Boundary Conditions empty (no tractions); no body loads |
| Objective: weighted sum, single compliance criterion, weight 1, analyze service | `criterion 1 type mechanical_compliance`; `objective type weighted_sum, criterion_ids 1, service_ids 2, scenario_ids 1, weights 1` | `analyze_2_input_deck.xml` Criteria/My Objective: Scalar Function `Internal Elastic Energy`, Domains `{block_1}`; `engine_operations.xml` Aggregator with one `Weight 1`; `interface.xml` objective value/gradient stages on performer `analyze_2` |
| Constraint: volume <= 15 %, `less_than`, engine service | `criterion 2 type volume`; `constraint 1: criterion_id 2, relative_target 0.15, type less_than, service_id 1, scenario_id 1` | `interface.xml` Optimizer/Constraint `NormalizedTargetValue 0.15`, `ReferenceValueName Design Volume`; `engine_operations.xml` `ComputeVolume` operations (Compute Constraint Value/Gradient 1) on performer `engine_1` (volume unpenalized: SIMP exponent 1.0, minimum 0.0) |
| Density discretization, uniform initial density 0.15 | `study`: `discretization density`, `initial_density_value 0.15`, `method topology` | `engine_operations.xml` InitializeField `Method Uniform`, `Value 0.15`; Set Lower/Upper Bounds `Discretization density`; `interface.xml` InitializationStage `Initial Guess`, bounds 0.0/1.0 |
| SIMP single phase, exponent 3.0, minimum 1e-3 | `material_interpolation 1`: `type single_phase`, `model simp`, `minimum_value 1e-3`, `penalty_exponent 3.0`, referenced by `residual 1 material_interpolation_id 1` | `analyze_2_input_deck.xml` Residual/Mechanical Residual: `Material Interpolation Model Single-Phase`, Penalty Function `SIMP`, `Exponent 3.0`, `Minimum Value 1e-3` |
| Compliance criterion `minimum_ersatz_material_value 1e-3` | `criterion 1 minimum_ersatz_material_value 1e-3` | `analyze_2_input_deck.xml` Criteria/My Objective/Penalty Function `SIMP`, `Exponent 3.0`, `Minimum Value 1e-3` |
| Optimizer OC, default tolerances; `normalize_in_aggregator false`; `update_problem true`, frequency 1 (engine service) | `study optimization_algorithm oc`, `normalize_in_aggregator false`; `service 1 (engine) update_problem true, update_problem_frequency 1` | `interface.xml` Optimizer `Package OC`, Options OCControlStagnationTolerance 1e-4, OCObjectiveStagnationTolerance 1e-8, OCGradientTolerance 1e-8 (runtime defaults, per XMLGenerator log), `ProblemUpdateFrequency 1`, `UpdateProblemStage Update Problem`; `engine_operations.xml` `Update Problem / UpdateProblemFrequency 1`; the Aggregator carries no normalization element (deck value `false` is the manual default; XMLGenerator emits no element for it) |
| Helmholtz filter, absolute radius 0.15, boundary-sticking penalty 1.0, no symmetry plane | `filter 1`: `type helmholtz`, `radius_absolute 0.15`, `boundary_sticking_penalty 1.0`; `study filter_ids 1`; no `symmetry_plane_location_names` | `analyze_helmholtz_input_deck.xml` Physics `Helmholtz Filter`, Parameters `Length Scale 0.043301`, `Surface Length Scale 1.0`; `analyze_helmholtz_operations.xml` ApplyHelmholtz / ApplyHelmholtzGradient; `interface.xml` performer `analyze_helmholtz`, Filter Control / Filter Gradient operations; no symmetry sideset anywhere. Note: 0.043301 = 0.15/(2*sqrt(3)) = 0.0433013, i.e. XMLGenerator converts the absolute radius 0.15 into the PDE length scale l0 = r/(2*sqrt(3)); the Surface Length Scale 1.0 is the boundary-sticking penalty. The XMLGenerator INFO line that `filter_radius_absolute` was not set refers to the legacy study-level keyword; the filter-block value did reach the generated configuration, so no re-translation with the legacy form was needed. |
| Services: engine + analyze, one processor each, single-rank performers, no decomposition | `service 1 code engine number_processors 1`; `service 2 code analyze number_processors 1` | `mpirun.source`: `-np 1 PlatoMain engine_input_deck.xml : -np 1 analyze_MPMD analyze_2 : -np 1 analyze_MPMD analyze_helmholtz` (the Helmholtz service is wired automatically by Morphorm, User Manual 2.5 note); no decomposition step |
| Output: dispx/dispy/dispz from analyze; engine output of `control` and `topology` | `output 1 service_id 2 data dispx dispy dispz` | `analyze_2_input_deck.xml` Output/Plottable `{displacement_x, displacement_y, displacement_z}`; `analyze_2_operations.xml` Visualization `OutputFrequency 1` (every iteration); `engine_operations.xml` PlatoMainOutput inputs `topology` and `control` (Nodal Field); `interface.xml` stage `Output To File` |
| Stage 1 `max_iterations 20` | `study max_iterations 20` | `interface.xml` Optimizer/Convergence `MaxIterations 20`; `engine_operations.xml` PlatoMainOutput `MaxIterations 20` |
| Restart-file writing enabled (Stage 1) | `study write_restart_file true` | `engine_operations.xml` PlatoMainOutput `WriteRestart true` |
| Restart source (Stage 2 only) | not set (fresh run; `restart_iteration` default 0) | `initial_guess_field_name` not set (XMLGenerator INFO), as required for a Stage-1 fresh run |

- Translation observation (not a deviation): `engine_operations.xml` PlatoMainOutput carries `OutputFrequency 5`, which XMLGenerator reports as the default of an `isosurface_output_frequency` parameter (not documented in the manuals). A scratch re-translation with an explicit `output_frequency 1` in the output block (`work/stage1/xmltest_outfreq/`, 2026-10-13T06:17:23Z, never submitted) left this value unchanged while the analyze `OutputFrequency` stayed 1 and `interface.xml` was byte-identical, so the submitted deck is the original one (output-block `output_frequency` default = 1 per manual 5.1.1). The manual states engine_output.exo stores every major iteration (9.3.4); this was verified after the run: 21 time steps (see section 5).

## 4. Execution

Commands used (all run from the trial root unless noted; the approved interface was sourced in every shell that called Cubit/Morphorm/python3 and inside the job script; SKILL_ROOT = the bundled check scripts of the `morphorm` / `hpc-batch-jobs` skills):

1. `pdftotext -layout agent_inputs/manuals/Morphorm_User_Manual.pdf work/manuals/user.txt` and the same for the Theory Manual (06:13:29Z); keyword lookups with `grep -n` / `sed -n` on those text copies.
2. `source .../load_approved_software.sh`; `which cubit XMLGenerator PlatoMain analyze_MPMD mpiexec python3`; `module list`.
3. `cd work/mesh && cubit -batch -nographics -nojournal -input mesh.jou > cubit_mesh.log 2>&1` (rc 0, 06:15:03Z–06:15:06Z).
4. `python3 SKILL_ROOT/scripts/exo_summary.py work/mesh/mesh.exo --expect num_elem=27648 num_nodes=30625 block:block_1:type=HEX8 nodeset:ns_fix=625 nodeset:ns_load=25 bbox_max=2.0,1.0,1.0 bbox_min=0,0,0` (rc 0, 06:15:19Z) and a short netCDF4 `python3 -I -c` nodeset-coordinate/spacing check (06:15:48Z, `work/verify/mesh_nodeset_coords.txt`).
5. `cp work/mesh/mesh.exo work/stage1/run/mesh.exo; cp work/stage1/input_deck.i work/stage1/run/; cd work/stage1/run && XMLGenerator input_deck.i > xmlgenerator.log 2>&1` (rc 0, 06:16:15Z).
6. `python3 SKILL_ROOT/scripts/xml_params.py work/stage1/run <search terms>` (06:16:42Z; exit 1 only because some of my free-text search terms such as radius / ersatz / algorithm are not literal XML parameter names; every locked value was then confirmed by reading the generated files with `cat`, see section 3).
7. Scratch translation test in `work/stage1/xmltest_outfreq/` (06:17:23Z, see section 3; never submitted).
8. `sbatch --parsable jobs/stage1_job_script.sbatch` → job **16236766** (submitted 2026-10-13T06:17:38Z UTC = 00:17:38 local). Job script: `jobs/stage1_job_script.sbatch` (copy: `outputs/stage1/job_script.sbatch`). SBATCH values exactly as frozen: account `hochhalter-np`, partition `hochhalter-np`, nodes 1, ntasks 1, cpus-per-task 8, mem 32G, time 02:00:00, no GPU. The script sources the approved interface, prints `module list` to the job stdout, changes to `work/stage1/run`, sets `OMP_NUM_THREADS=1`, and runs `bash mpirun.source > morphorm_stage1.log 2>&1`.
9. Waits with `bash SKILL_ROOT/scripts/wait_job.sh 16236766 <=540 work/stage1/run/morphorm_oc_optimizer_diagnostics.txt` (three bounded waits: 06:22:51Z RUNNING at iteration 4; 06:31:58Z RUNNING at iteration 16; 06:35:34Z left queue, COMPLETED).
10. `sacct -j 16236766 --format=JobID,JobName,State,ExitCode,Submit,Start,End,Elapsed,AllocCPUS,ReqMem,MaxRSS,NodeList -P > jobs/sacct_16236766.txt`.
11. `diag_summary.py morphorm_oc_optimizer_diagnostics.txt`; `exo_summary.py engine_output.exo --expect time_steps=21 num_nodes=30625`; `exo_summary.py analyze_id_2_output_scenario_id_1/iteration20.exo` (06:36:11Z; records in `work/verify/`).
12. `cp` of deliverables to `outputs/` (06:17:50Z for mesh/deck/config/job script; 06:36:23Z for run results), `cmp` of the checkpoint copy, then `cd outputs && find . -type f ! -name SHA256SUMS.txt | sort | xargs sha256sum > SHA256SUMS.txt && sha256sum -c SHA256SUMS.txt` (0 non-OK lines).

Slurm jobs submitted in this trial (also in `jobs/job_ids.txt`, one per line, and `jobs/submissions.txt`):

| Job ID | Stage | Script | Submit (local) | Start | End | Elapsed | State | ExitCode | Node | MaxRSS |
|---|---|---|---|---|---|---|---|---|---|---|
| 16236766 | Stage 1 | `jobs/stage1_job_script.sbatch` | 2026-10-13T00:17:38 | 00:17:48 | 00:35:02 | 00:17:14 | COMPLETED | 0:0 | notch274 | 2264552K (batch step) |

`sacct` record: `jobs/sacct_16236766.txt`. Job stdout/stderr: `logs/stage1_16236766.out` (contains the `module list` output, RUN_DIR, MORPHORM_START_UTC 06:17:58Z, MORPHORM_END_UTC 06:35:02Z rc=0) and `logs/stage1_16236766.err` (empty); copies in `outputs/stage1/run_logs/`. No job was cancelled; no job failed; no resubmission.

## 5. Completed stages and iteration counts

- **Stage 1: COMPLETE.** Optimizer diagnostics `work/stage1/run/morphorm_oc_optimizer_diagnostics.txt` (delivered as `outputs/stage1/morphorm_oc_optimizer_diagnostics.txt`): 21 iteration rows, Iter 0 … Iter 20 (F-count 1 … 21); objective F(X) at iteration 0 = 4.893235e+06 (uniform density 0.15, H1 = -1.564817e-02); objective at iteration 20 = **2.360040e+05** (Norm(F') 1.191537e+04, H1 3.964884e-13, abs(dX) 2.0e-01). The volume constraint is satisfied/active (H1 ~ 0) from iteration 6 on.
  Stopping message (verbatim): `****** Optimization stopping due to exceeding maximum number of iterations. ******` — i.e. the run stopped at the locked iteration cap of 20, as required.
  Criteria history (`opt_criteria_history.csv`, 21 values) agrees with the diagnostics: last value 2.3600395811001546e+05.
- **Checkpoint preserved:** the Stage-1 engine output `work/stage1/run/engine_output.exo` (12,383,296 bytes, unmodified since the job wrote it at 00:34 local) copied byte-identically (`cmp` OK) to **`outputs/stage1/engine_output.exo`**, SHA-256 `9f9616771441ca2de1d98bb44ccd81daedaa2b0bc305a2d0733d2402f6addee9`. Verified with `exo_summary.py` (`work/verify/stage1_engine_output.json`, `expect_ok: true`): **21 time steps** (time values 1.0 … 21.0 = saved states for iterations 0–20; the iteration-20 design is the 21st = last time step), nodal fields **`control`** and **`topology`**, 30625 nodes, 27648 HEX8 elements, nodesets `ns_fix` (625) / `ns_load` (25) carried through; last-step ranges: control [0.0, 1.0], topology [5.48e-08, 0.9267]. For Stage 2 the manual's restart keywords are `initial_guess_file_name`, `initial_guess_field_name` (= `control`) and `restart_iteration` (User Manual 2.5.10); which index value selects the 21st saved state (0- vs 1-based) must be established by the Stage-2 process and proven by comparing its first compliance with 2.360040e+05 (spec section 7).
  Note: although `write_restart_file true` was translated to `WriteRestart true`, no separate `engine_restart.exo` file appeared in the run directory after the job (checked with `ls | grep -i restart`); the spec designates `engine_output.exo` as the checkpoint, and it holds all 21 states, so Stage 1 meets its locked requirement.
- Final analyze output: `work/stage1/run/analyze_id_2_output_scenario_id_1/iteration20.exo` (one of 21 per-iteration files iteration0 … iteration20.exo, written at every iteration) → **`outputs/stage1/final_analyze_output.exo`**, 1 time step (time 20.0), nodal fields `Topology`, `displacement X/Y/Z` (`work/verify/stage1_final_analyze_output.json`).
- **Stage 2: NOT STARTED.** No Stage-2 deck, configuration, job script, job or `outputs/stage2/` directory exists. Continuation evidence (spec section 7) therefore does not exist yet; the reference value for it is the Stage-1 compliance at iteration 20 = 2.360040e+05.

## 6. Key output files (deliverables) and SHA-256

Full manifest: `outputs/SHA256SUMS.txt` (28 files = every file under `outputs/` except itself, including the pre-existing empty `outputs/.gitkeep`; produced with `sha256sum`; `sha256sum -c` all OK). Key entries:

| Deliverable | SHA-256 |
|---|---|
| `outputs/mesh.jou` | 3c576b45f3935cabac87bf104b04911dbaab7de3d23201cc71e4b22411ee4c63 |
| `outputs/mesh.exo` | 71b221cd4af5d917e80fd2d12635e675807f7f53feeb22818b0125de90c174b0 |
| `outputs/mesh_verification.txt` | e22d1516375c5c231bdfddb9eef10e90744b1943adf5968d9c03c6458b7d6d19 |
| `outputs/stage1/input_deck.i` | ff31180564abd7cffa148a0cbf4cc920f7a7d189c4c76ae2a324d6edf90a4f52 |
| `outputs/stage1/job_script.sbatch` | e9d5805e96cfc3c4de4a90f1ac58d8b9d24c06c501a8a53bf7e2be9c95b51627 |
| `outputs/stage1/generated_config/interface.xml` | 2e2f1e9c750eb785bb3c6534df928b4bdd988cc0f53a4653ce142ec2a661dbb5 |
| `outputs/stage1/generated_config/engine_operations.xml` | 0d9b5d12f1ac587977b4ab7dfbb92de77ddb2bf9636be2e38869752c4f7b26ec |
| `outputs/stage1/generated_config/analyze_2_input_deck.xml` | 998ee0d46d67b1eb726163d7064b22b57b7ac8c4295c03921456fd10bd1c8e6b |
| `outputs/stage1/generated_config/analyze_helmholtz_input_deck.xml` | c813b81a2c43cbac181b51c3ae12cad319473e7c2725afd29c2637fedec2dcbf |
| `outputs/stage1/morphorm_oc_optimizer_diagnostics.txt` | 4aaeaa78e77e9f065e3e0ab91d0205a13cdf600a7c76d9f8fc492b06092772f1 |
| `outputs/stage1/engine_output.exo` (checkpoint, 21 saved states) | 9f9616771441ca2de1d98bb44ccd81daedaa2b0bc305a2d0733d2402f6addee9 |
| `outputs/stage1/final_analyze_output.exo` | 58a7704efef44e95fc192ed1f209381d0b8f419415a03ea0488720c67f597cac |
| `outputs/stage1/run_logs/stage1_16236766.out` | 1592f1670d851640e1848e75d6b14a20b78324f933454f47a88f90de54504664 |

## 7. Failures, retries, cancelled jobs, unresolved issues, deviations

- Failures: none. Retries: none. Cancelled jobs: none. Only one job (16236766) was submitted; no deliverable was replaced by a later attempt.
- Deviations from the specification: none. Every locked value was realized as written in section 3 and verified in the generated configuration before submission.
- Observations recorded for the record (not deviations): (a) the engine-side `OutputFrequency 5` in `engine_operations.xml` is an undocumented isosurface default and did not affect the design history (21 states verified); (b) no separate `engine_restart.exo` was produced although `WriteRestart true` was generated — the designated checkpoint `engine_output.exo` is complete; (c) the `xml_params.py` call exited 1 only because some free-text search terms are not literal XML parameter names — every locked value was confirmed directly in the generated files; (d) the scratch translation under `work/stage1/xmltest_outfreq/` is an unsubmitted test kept for provenance.
- Unresolved issues: none for Stage 1. Open for Stage 2 (deliberately not addressed in this session per the session policy): the `restart_iteration` index convention (0- or 1-based) for selecting the iteration-20 state must be established and proven by the seamless-restart check of spec section 7 (first Stage-2 compliance must equal 2.360040e+05).

## 8. Final artifact paths

- Mesh: `outputs/mesh.jou`, `outputs/mesh.exo`, `outputs/mesh_verification.txt` (working copies `work/mesh/`, checks `work/verify/mesh.json`, `work/verify/mesh_nodeset_coords.txt`).
- Stage 1: `outputs/stage1/input_deck.i`, `outputs/stage1/job_script.sbatch`, `outputs/stage1/generated_config/` (8 XMLGenerator files + `xmlgenerator.log` + `xml_params_verification.txt`), `outputs/stage1/morphorm_oc_optimizer_diagnostics.txt`, `outputs/stage1/engine_output.exo` (**checkpoint, 21 saved states, fields control and topology**), `outputs/stage1/final_analyze_output.exo`, `outputs/stage1/run_logs/` (Slurm stdout/stderr, `morphorm_stage1.log`, performer logs `engine_1_0`, `analyze_2_1`, `analyze_helmholtz_2`, `opt_criteria_history.csv`, `iteration20_criteria_history.csv`, `sacct_16236766.txt`).
- Manifest: `outputs/SHA256SUMS.txt` (to be regenerated after Stage 2).
- Scheduler: `jobs/job_ids.txt`, `jobs/submissions.txt`, `jobs/stage1_job_script.sbatch`, `jobs/sacct_16236766.txt`; `logs/stage1_16236766.out`, `logs/stage1_16236766.err`.
- Work area: `work/stage1/run/` (complete untouched Stage-1 run directory incl. all 21 `analyze_id_2_output_scenario_id_1/iteration*.exo`), `work/stage1/xmltest_outfreq/` (unsubmitted scratch translation), `work/verify/` (all check outputs), `work/manuals/` (text copies of the manuals), `work/notes.log` (facts log), `work/run_summary.md` (this file).
- Stage 2 artifacts: none exist (`outputs/stage2/` not created). **Stage 1 complete; Stage 2 not started.**
