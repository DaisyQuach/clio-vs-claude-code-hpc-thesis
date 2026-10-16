# Run summary - Sessions A (Stage 1) and B (Stage 2 continuation)

**STATUS: Stage 1 COMPLETE (Session A, job 16242485, iterations 0-20) and Stage 2 COMPLETE (Session B, job 16243174, 40 further iterations, overall iteration 60). Both stages verified; seamless restart confirmed.** Session B (2026-10-13, 15:06-15:47 UTC) found Stage 1 complete and verified in this trial root, did not repeat it, and appended the subsections marked "B" below. The Session-A text is retained unchanged except for the two statements about Stage 2 not having been started, which are now superseded by sections 5B/8.

## 1. Trial identifier and assigned workflow
- Trial identifier (`THESIS_TRIAL_ID`): `E2-example16-clio-05R`
- Workflow: `FROZEN-EX16-v1` - full cantilever, two-stage restart (warm-start) workflow (`agent_inputs/scientific_problem_specification.md`; frozen hash `a67d6cba7f0ce35ae6dc227f33b39056514be9494d6e15bc8e58524dfba1a86b` per `FROZEN_CONFIG_SHA256.txt`).
- Session policy: Session A constructed the workflow and completed Stage 1 only, then stopped. Session B (a new process with no record of Session A) recovered the state from the persistent files of this trial root and completed Stage 2.
- Software: approved interface `source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh` (modules observed after sourcing, on the agent host and in the job stdout: `chpc/1.0, gcc/11.2.0, openmpi/5.0.3, morphorm/approved-runtime, cubit-edu/2026.8`).
- Documentation used: only `agent_inputs/manuals/Morphorm_User_Manual.pdf` and `Morphorm_Theory_Manual.pdf` (converted once with `pdftotext -layout` into `work/manuals_txt/`).

## 2. Mesh
- Generated on the agent host (permitted by `compute_resources.md`) with `cubit -batch -nographics -nojournal -input mesh.jou` (cwd `work/mesh`) at 2026-10-13T14:38Z, exit 0 (`work/mesh/cubit_stdout.log`; stderr empty).
- Journal: `work/mesh/mesh.jou` -> delivered as `outputs/mesh.jou`. Brick 2.0x1.0x1.0 moved to corner at the origin, mapped scheme, intervals 48 (curves longer than 1.5) / 24 (shorter curves), `block_1` HEX8 on volume 1, `ns_fix` = surface at x=0, `ns_load` = curve at x=2,y=0, export Exodus II dimension 3.
- Mesh file: `work/mesh/mesh.exo` -> `outputs/mesh.exo` (SHA-256 `892c8de1feb517864cf4de7fffebdbe99a342a494ad338b8e4892a1eaa7f5488`); the identical copy `work/stage1/run/mesh.exo` was read by the Stage-1 job (its hash is printed in `logs/stage1_16242485.out`).
- Verification (bundled `exo_summary.py`; record `work/verify/mesh.json` -> `outputs/mesh_verification.txt`; `expect_ok: true`, zero expectation failures): 27,648 HEX8 elements, 30,625 nodes, 3-D, bounding box [0,0,0]-[2.0,1.0,1.0], exactly one block named `block_1` (27,648 elements, 8 nodes/elem), nodesets `ns_fix` = 625 nodes, `ns_load` = 25 nodes, no sidesets. Cubit's executive summary agrees (1 block, 2 nodesets, 0 sidesets, 27648 elements, 30625 nodes).

## 3. Input deck and locked settings in the generated configuration
- Deck: `work/stage1/input_deck.i` -> `outputs/stage1/input_deck.i` (identical to `work/stage1/run/input_deck.i` used by the job).
- Translation: `XMLGenerator input_deck.i` in `work/stage1/run/` at 2026-10-13T14:40Z, exit 0. Generated files delivered under `outputs/stage1/generated_config/` together with the XMLGenerator stdout and the check record `verification_xml_params.txt` (bundled `xml_params.py` + grep of load/BC/initial-density entries).
- Locked setting -> where it appears in the generated configuration (all observed in the files listed):

| Locked setting | Deck keyword(s) | Generated configuration (file: path = value) |
|---|---|---|
| Material E=1.0, nu=0.3 on `block_1` | `material 1`; `block 1 name block_1` | `analyze_2_input_deck.xml`: Material Models/material_1/Isotropic Linear Elastic: Youngs Modulus=1.0, Poissons Ratio=0.3; Spatial Model/Domains/block_1 -> material_1 |
| Fixed support ns_fix ux=uy=uz=0 | `boundary_condition 1` fixed_value nodeset ns_fix dispx dispy dispz 0 0 0 | `analyze_2_input_deck.xml`: Essential Boundary Conditions: Displacement X/Y/Z, Index 0/1/2, Sides=ns_fix, Value=0 |
| Load -1.0 per node in y on ns_load (25 nodes, total -25.0); no other loads | `load 1` concentrated_load nodeset ns_load direction y value -1.0 | `analyze_2_input_deck.xml`: Concentrated Loads/Concentrated Load with ID 0: Dof=1 (y), Value=-1.0, Nodes=ns_load; Mechanical Natural Boundary Conditions empty; no body loads |
| Objective: weighted sum, single compliance criterion, weight 1, analyze service | `objective` weighted_sum criterion_ids 1 service_ids 2 scenario_ids 1 weights 1 | `analyze_2_input_deck.xml`: Criteria/My Objective Scalar Function Type=Internal Elastic Energy; `engine_operations.xml`: Aggregator Weighting/Weight/Value=1; `interface.xml`: objective value/gradient stages on analyze_2 |
| Constraint volume <= 0.15, less_than, engine service | `constraint 1` criterion_id 2 relative_target 0.15 type less_than service_id 1 | `interface.xml`: Optimizer/Constraint NormalizedTargetValue=0.15, ReferenceValueName=Design Volume; `engine_operations.xml`: ComputeVolume operations on engine_1 (SIMP exponent 1.0, min 0.0 = plain volume measure) |
| Density discretization; uniform initial density 0.15 | `discretization density`, `initialize_method uniform`, `initial_density_value 0.15` | `engine_operations.xml`: InitializeField Method=Uniform Value=0.15; bounds operations Discretization=density; `interface.xml`: InitializationStage=Initial Guess, BoundConstraint 0.0-1.0 |
| SIMP single phase, exponent 3.0, minimum 1e-3 | `material_interpolation 1` single_phase simp penalty_exponent 3.0 minimum_value 1e-3 (referenced from residual 1) | `analyze_2_input_deck.xml`: Residual/Mechanical Residual: Material Interpolation Model=Single-Phase, Penalty Function Type=SIMP Exponent=3.0 Minimum Value=1e-3 |
| Compliance criterion minimum_ersatz_material_value 1e-3 (exponent 3.0) | `criterion 1` mechanical_compliance material_penalty_exponent 3.0 minimum_ersatz_material_value 1e-3 | `analyze_2_input_deck.xml`: Criteria/My Objective/Penalty Function Type=SIMP Exponent=3.0 Minimum Value=1e-3 |
| OC optimizer, runtime default tolerances | `optimization_algorithm oc` | `interface.xml`: Optimizer/Package=OC; OCControlStagnationTolerance=1e-4, OCObjectiveStagnationTolerance=1e-8, OCGradientTolerance=1e-8 (defaults reported by XMLGenerator) |
| `normalize_in_aggregator false` | `normalize_in_aggregator false` | `engine_operations.xml`: Aggregator operation carries no normalization element (false) |
| `update_problem true`, frequency 1 on the engine service | service 1: `update_problem true`, `update_problem_frequency 1` | `engine_operations.xml`: Update Problem UpdateProblemFrequency=1; `interface.xml`: Update Problem stage, Optimizer/Options ProblemUpdateFrequency=1, UpdateProblemStage=Update Problem |
| Helmholtz filter, absolute radius 0.15, boundary-sticking penalty 1.0, no symmetry plane | `filter 1` type helmholtz radius_absolute 0.15 boundary_sticking_penalty 1.0; study `filter_ids 1` | `analyze_helmholtz_input_deck.xml`: Physics=Helmholtz Filter; Parameters: Length Scale=0.043301, Surface Length Scale=1.0; no symmetry sideset entries. 0.043301 = 0.15/(2*sqrt(3)) exactly; the legacy form (`filter_type helmholtz`, `filter_radius_absolute 0.15`, `boundary_sticking_penalty 1.0`) translated in a scratch directory gave byte-identical XML (section 7), so radius 0.15 was applied. The theory manual identifies the surface length scale with `boundary_sticking_penalty`. |
| Services: engine + analyze, one processor each, no decomposition | service 1 engine, service 2 analyze, number_processors 1 | `mpirun.source`: `-np 1` PlatoMain, `-np 1` analyze_MPMD (analyze_2), `-np 1` analyze_MPMD (Helmholtz filter service created by XMLGenerator) |
| Output: dispx dispy dispz from analyze; engine control + topology | `output 1` service_id 2 data dispx dispy dispz output_frequency 1 | `analyze_2_input_deck.xml`: Output Plottable={displacement_x, displacement_y, displacement_z}; `analyze_2_operations.xml`: Visualization OutputFrequency=1; `interface.xml`/`engine_operations.xml`: PlatoMainOutput inputs topology + control |
| Stage-1 iteration cap 20 | `max_iterations 20` | `interface.xml`: Optimizer/Convergence MaxIterations=20; `engine_operations.xml`: PlatoMainOutput MaxIterations=20 |
| Restart-file writing; engine output with every iteration saved (21 states) | `write_restart_file true`; `isosurface_output_frequency 1` (section 7) | `engine_operations.xml`: PlatoMainOutput WriteRestart=true, OutputFrequency=1; `engine_input_deck.xml`: output file `engine_output` (exodus) |

### 3B. Stage-2 input deck (Session B)
- Deck: `work/stage2/input_deck.i` -> `outputs/stage2/input_deck.i` (identical to `work/stage2/run/input_deck.i` read by the job). Derived from the accepted Stage-1 deck with exactly these changes: `max_iterations 20` -> `40`; `initialize_method uniform` and `initial_density_value 0.15` removed (the initial design now comes from the checkpoint); added the manual's restart keywords (User Manual 2.5.10, Table 2.5.40) `initial_guess_file_name restart_input.exo`, `initial_guess_field_name control`, `restart_iteration 21`; `write_restart_file true` and `isosurface_output_frequency 1` kept so every Stage-2 iteration is saved; comment lines updated. Every other block (services, scenario, residual, SIMP, load, BC, material, block, criteria, objective, constraint, filter, output, mesh) is byte-identical to Stage 1.
- Translation: `XMLGenerator input_deck.i` in `work/stage2/run/` at 2026-10-13T15:08:37Z, exit 0 (stdout/stderr kept in the run dir; stderr empty). Generated files delivered under `outputs/stage2/generated_config/` with `xmlgenerator_stdout.log` and the check record `verification_xml_params.txt` (bundled `xml_params.py`, exit 0; load/BC grep in `work/verify/stage2_xml_loads_bcs.txt`).
- Comparison with the Stage-1 generated configuration: `engine_input_deck.xml`, `analyze_2_input_deck.xml`, `analyze_2_operations.xml`, `analyze_helmholtz_input_deck.xml`, `analyze_helmholtz_operations.xml` and `mpirun.source` are byte-identical to Stage 1 (same SHA-256 in `outputs/SHA256SUMS.txt`), so material E=1.0/nu=0.3, SIMP exponent 3.0/min 1e-3 (residual and compliance criterion), load -1.0 in y on `ns_load`, displacement BCs on `ns_fix`, filter Length Scale 0.043301 (= 0.15/(2 sqrt 3)) / Surface Length Scale 1.0, analyze output dispx/dispy/dispz every iteration and the 1-rank performers are unchanged. Only `interface.xml` and `engine_operations.xml` differ:

| Locked Stage-2 setting | Deck keyword | Generated configuration |
|---|---|---|
| Iteration cap 40 | `max_iterations 40` | `interface.xml`: Optimizer/Convergence MaxIterations=40; `engine_operations.xml`: PlatoMainOutput MaxIterations=40 |
| Restart source file = copy of the Stage-1 checkpoint | `initial_guess_file_name restart_input.exo` | `engine_operations.xml`: InitializeField Method=FromFieldOnInputMesh, Name=restart_input.exo |
| Restart field `control` (not `topology`) | `initial_guess_field_name control` | `engine_operations.xml`: FromFieldOnInputMesh/VariableName=control; PlatoMainOutput RestartFieldName=control |
| Saved state = iteration-20 design | `restart_iteration 21` | `engine_operations.xml`: FromFieldOnInputMesh/Iteration=21 (= Exodus time step 21 = 21st saved state = iteration 20; confirmed by the continuation evidence, section 5) |
| Restart writing / all iterations saved | `write_restart_file true`, `isosurface_output_frequency 1` | `engine_operations.xml`: WriteRestart=true, OutputFrequency=1 |
| OC, volume 0.15 less_than, update_problem frequency 1, normalize false, weight 1 | unchanged | `interface.xml`: Package=OC, NormalizedTargetValue=0.15, ProblemUpdateFrequency=1; `engine_operations.xml`: UpdateProblemFrequency=1, Weight Value=1, no normalization element |

- Index-base check before submission: the same deck was translated with `restart_iteration 20` and `21` in the scratch directories `work/stage2/xlate_check_iter20/` and `xlate_check_iter21/` (translation only, never submitted). The only difference in the generated files is `<Iteration>20</Iteration>` vs `<Iteration>21</Iteration>`, i.e. XMLGenerator passes the integer straight to the engine. Because the checkpoint's 21 states are Exodus time steps 1..21 (time values 1.0..21.0) and the manual calls the keyword the "iteration (time step)", 21 was chosen as the time step holding iteration 20, with the mandatory empirical check of the first Stage-2 compliance (section 5) as the arbiter. The accepted translation in `work/stage2/run/` is byte-identical to `xlate_check_iter21/`.

## 4. Execution
All commands were run from the trial root after `source .../load_approved_software.sh`; the factual event log with UTC timestamps is `work/notes.log`.

| UTC | Command / event | Result |
|---|---|---|
| 14:36:19 | packet read; `pdftotext -layout` on both manuals -> `work/manuals_txt/` | ok |
| 14:38:21 | `cubit -batch -nographics -nojournal -input mesh.jou` (cwd `work/mesh`) | exit 0 |
| 14:38:48 | `python3 exo_summary.py work/mesh/mesh.exo --expect num_elem=27648 num_nodes=30625 block:block_1:type=HEX8 nodeset:ns_fix=625 nodeset:ns_load=25 bbox_max=2.0,1.0,1.0 bbox_min=0,0,0` | rc 0, expect_ok true |
| 14:38:57 | `XMLGenerator input_deck.i` (first translation, cwd `work/stage1/run`) | exit 0; engine OutputFrequency came out 5 (kept as `work/stage1/run_attempt0_translation_only/`, never submitted) |
| 14:40:14 | scratch translations `work/stage1/xlate_check_A` (legacy filter keywords) and `xlate_check_B` (`isosurface_output_frequency 1`) | both exit 0; A byte-identical to the first translation; B differs only in engine OutputFrequency 5 -> 1 |
| 14:40:41 | `XMLGenerator input_deck.i` (accepted translation, clean `work/stage1/run`, deck with `isosurface_output_frequency 1`) | exit 0 |
| 14:40 | `python3 xml_params.py work/stage1/run ...` -> `work/verify/stage1_xml_params.txt` (= `outputs/stage1/generated_config/verification_xml_params.txt`) | all locked values present (section 3) |
| 14:41:04 | `sbatch --parsable jobs/stage1_job_script.sbatch` | job **16242485** |
| 14:41:05-14:59:35 | job ran on `notch204`; inside: `bash mpirun.source > morphorm_stage1.log` | COMPLETED, ExitCode 0:0, Elapsed 00:18:30, MaxRSS 2.28 GB (`jobs/sacct_16242485.txt`) |
| 15:00 | `diag_summary.py`, `exo_summary.py engine_output.exo`, `exo_summary.py iteration20.exo` -> `work/verify/stage1_*.json` | see section 5 |
| 15:00:42 | delivery copies + `sha256sum` manifest + `sha256sum -c` | 30 entries, all OK |

- Job script: `jobs/stage1_job_script.sbatch` (copy at `outputs/stage1/job_script.sbatch`). SBATCH values exactly as frozen: account `hochhalter-np`, partition `hochhalter-np`, 1 node, 1 task, 8 CPUs/task, 32G, 02:00:00, no GPU. The script sources the approved interface, prints `module list` (visible in `logs/stage1_16242485.out`), hashes its inputs, runs `bash mpirun.source` in `work/stage1/run`.
- Scheduler: `jobs/job_ids.txt` = `16242485` (the only job submitted in this trial; nothing failed or cancelled). sacct record: `jobs/sacct_16242485.txt`. Slurm stdout/stderr: `logs/stage1_16242485.out` / `.err` (stderr is empty), copied to `outputs/stage1/run_logs/`.
- No Morphorm or Cubit was run on the agent host except Cubit meshing and XMLGenerator translation (both permitted).

### 4B. Stage-2 execution (Session B, 2026-10-13)
All commands run from the trial root after `source .../load_approved_software.sh`; event log `work/notes.log`.

| UTC | Command / event | Result |
|---|---|---|
| 15:06:53 | Session B start: read every file in `agent_inputs/`, `work/run_summary.md`, `work/notes.log`, `jobs/`, `logs/`, `outputs/`; `sha256sum -c outputs/SHA256SUMS.txt` (30 entries); `sha256sum` of `outputs/stage1/engine_output.exo` and `work/stage1/run/engine_output.exo`; bundled `exo_summary.py outputs/stage1/engine_output.exo` and `diag_summary.py outputs/stage1/morphorm_oc_optimizer_diagnostics.txt` | all OK; checkpoint 58dee776... intact, 21 states, control+topology; Stage 1 ended at iteration 20 with F=2.360040e+05 at the iteration cap -> Stage 1 accepted as complete, nothing repeated |
| 15:07 | `grep -n -i restart work/manuals_txt/user.txt`; `sed -n 3840,3930p` (User Manual 2.5.10 Restart) | keywords `initial_guess_file_name`, `initial_guess_field_name`, `restart_iteration` identified |
| 15:07:42 | `XMLGenerator input_deck.i` in `work/stage2/xlate_check_iter20/` and `.../xlate_check_iter21/` (scratch, translation only); `diff -r` of the two; diff against `outputs/stage1/generated_config/` | both exit 0; see section 3B |
| 15:08:37 | `cp outputs/mesh.exo work/stage2/run/mesh.exo`; `cp outputs/stage1/engine_output.exo work/stage2/run/restart_input.exo`; `XMLGenerator input_deck.i` (accepted translation, clean `work/stage2/run/`); `cmp` against `xlate_check_iter21`; `python3 xml_params.py work/stage2/run ...` -> `work/verify/stage2_xml_params.txt` | exit 0; all files identical to iter21; xml_params exit 0, all locked values present |
| 15:08:37 | `sbatch --parsable jobs/stage2_job_script.sbatch` | job **16243174** (recorded in `jobs/job_ids.txt`, `jobs/submissions.log`) |
| 15:08:48-15:44:47 | job ran on `notch204`; inside: `bash mpirun.source > morphorm_stage2.log` | COMPLETED, ExitCode 0:0, Elapsed 00:35:59, MaxRSS 2.36 GB (`jobs/sacct_16243174.txt`) |
| 15:11:59 | after 3 diagnostics rows: `diag_summary.py work/stage2/run/morphorm_oc_optimizer_diagnostics.txt --compare-first-to 2.360040e+05` -> `work/verify/stage2_first_objective_check.json` | rel diff 0.0 -> correct saved state; run allowed to continue (no cancellation) |
| 15:45:18 | `bash work/stage2/deliver_stage2.sh` (copies to `outputs/stage2/`, `sacct` record, bundled `diag_summary.py`, `exo_summary.py` on engine_output / final_analyze_output / restart_input -> `work/verify/stage2_*.json`) | all checks exit 0 |
| 15:45 | `python3 -I -c` netCDF4 field comparison (Stage-1 state 21 vs Stage-2 state 1, see section 5) -> `work/verify/stage2_field_continuation.txt` | identical arrays |
| 15:46:06 | `outputs/stage2/continuation_evidence.txt` written; `find ... | xargs sha256sum > outputs/SHA256SUMS.txt` (regenerated); `sha256sum -c` | 61 entries, all OK |

- Job script: `jobs/stage2_job_script.sbatch` (copy at `outputs/stage2/job_script.sbatch`). SBATCH values exactly as frozen: account `hochhalter-np`, partition `hochhalter-np`, 1 node, 1 task, 8 CPUs/task, 32G, 02:00:00, no GPU. It sources the approved interface, prints `module list` (visible in `logs/stage2_16243174.out`), hashes its inputs including `restart_input.exo`, runs `bash mpirun.source` in `work/stage2/run`.
- Scheduler: `jobs/job_ids.txt` = `16242485` (Stage 1, Session A) and `16243174` (Stage 2, Session B); no other job was submitted, nothing failed or was cancelled. sacct records: `jobs/sacct_16242485.txt`, `jobs/sacct_16243174.txt`. Slurm stdout/stderr: `logs/stage2_16243174.out` / `.err` (stderr empty), copied to `outputs/stage2/run_logs/`.
- Stage 2 was submitted only after Stage 1 was verified complete and its checkpoint preserved (hash unchanged before and after Stage 2).

## 5. Completed stages and iteration counts
- **Stage 1: COMPLETE.** Optimizer diagnostics `work/stage1/run/morphorm_oc_optimizer_diagnostics.txt` (delivered `outputs/stage1/morphorm_oc_optimizer_diagnostics.txt`): 21 iteration rows, Iter 0..20, F-count 1..21. `diag_summary.py`: first_iter 0, first_objective 4.893235e+06, last_iter 20, last_objective 2.360040e+05 (F(X) at iteration 20 = 2.360040e+05, Norm(F') 1.191537e+04, H1(X) 3.96e-13, abs(dX) 0.2). Stopping message: `****** Optimization stopping due to exceeding maximum number of iterations. ******` (i.e. stopped at the locked cap of 20).
- Checkpoint (engine output): `work/stage1/run/engine_output.exo` -> `outputs/stage1/engine_output.exo`, unmodified copy, SHA-256 `58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8` (identical for both copies). `exo_summary.py` (`outputs/stage1/run_logs/stage1_engine_output.json`): 21 time steps, time values 1.0..21.0, nodal fields `control` and `topology`, 30,625 nodes / 27,648 elements, nodesets ns_fix 625 / ns_load 25. Last state (iteration 20): control in [0.0, 1.0], topology in [5.48e-08, 0.9267]. **Mapping for Stage 2:** saved state k (1-based time step k, time value k) holds iteration k-1; the iteration-20 design is the 21st (last) saved state. The locked restart source field is `control`.
- Final analyze output: `work/stage1/run/analyze_id_2_output_scenario_id_1/iteration20.exo` -> `outputs/stage1/final_analyze_output.exo` (1 time step, time 20.0; nodal `Topology`, `displacement X/Y/Z`; element `My Objective`; record `outputs/stage1/run_logs/stage1_iteration20.json`). The topology min/max in it equal those of the last engine-output state.
- `opt_criteria_history.csv` (21 objective values, identical sequence to the diagnostics F(X) column) is delivered in `outputs/stage1/run_logs/`.
- Stage 2 status at the end of Session A: not started (superseded; see 5B below).

### 5B. Stage 2 (Session B)
- **Stage 2: COMPLETE.** Optimizer diagnostics `work/stage2/run/morphorm_oc_optimizer_diagnostics.txt` -> `outputs/stage2/morphorm_oc_optimizer_diagnostics.txt`: 41 iteration rows, local Iter 0..40, F-count 1..41 (overall iterations 20..60). `diag_summary.py` (`work/verify/stage2_diag_summary.json`): first_iter 0, first_objective 2.360040e+05, last_iter 40, last_objective 2.135584e+05 (Norm(F') 1.063277e+04, H1(X) -7.55e-14, abs(dX) 0.128). Stopping message: `****** Optimization stopping due to exceeding maximum number of iterations. ******` (stopped at the locked cap of 40). The overall workflow therefore reached iteration 60.
- **Continuation evidence** (full record: `outputs/stage2/continuation_evidence.txt`):
  - Checkpoint: `outputs/stage2/restart_input.exo`, byte-exact copy of `outputs/stage1/engine_output.exo` (both SHA-256 `58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8`; 21 saved states, `exo_summary.py` record `outputs/stage2/run_logs/stage2_restart_input.json`).
  - Field: `control` (raw design variable; generated `FromFieldOnInputMesh/VariableName=control`). Saved iteration: `restart_iteration 21` = Exodus time step 21 = iteration-20 design.
  - Diagnostics: Stage-1 iteration 20 F(X)=2.360040e+05, Norm(F')=1.191537e+04, H1=3.964884e-13; Stage-2 local iteration 0 F(X)=2.360040e+05, Norm(F')=1.191537e+04, H1=3.964884e-13 -> `first_vs_given_rel_diff 0.0` (`work/verify/stage2_first_objective_check.json`, taken while the job ran, and `stage2_diag_summary.json` after completion). Stage-1 iterations 19 (2.388394e+05) and 18 (2.422601e+05) are not matched.
  - Saved fields (`work/verify/stage2_field_continuation.txt`): `control` and `topology` arrays of Stage-1 state 21 (iteration 20) are identical (max|diff| 0.0) to Stage-2 engine-output state 1 (local iteration 0); against Stage-1 states 20/19 the control field differs by up to 0.200/0.377. `restart_input.exo` state 21 is identical to the Stage-1 engine output state 21. Mean control 0.168639 in both.
  - Nothing had to be corrected: the first chosen index (21) read the iteration-20 state.
- Stage-2 engine output: `work/stage2/run/engine_output.exo` -> `outputs/stage2/engine_output.exo` (`exo_summary.py`, `outputs/stage2/run_logs/stage2_engine_output.json`): 41 time steps (1.0..41.0), nodal `control` and `topology`, 30,625 nodes / 27,648 elements, nodesets ns_fix 625 / ns_load 25. Last state (local iteration 40 = overall 60): control in [0.0, 1.0], topology in [4.14e-08, 0.9338].
- Final analyze output: `work/stage2/run/analyze_id_2_output_scenario_id_1/iteration40.exo` -> `outputs/stage2/final_analyze_output.exo` (1 time step, time 40.0; nodal `Topology`, `displacement X/Y/Z`; element `My Objective`; record `outputs/stage2/run_logs/stage2_iteration40.json`). Its Topology min/max equal those of the last engine-output state.
- `opt_criteria_history.csv` (41 objective values) delivered in `outputs/stage2/run_logs/`.

## 6. Key output files (deliverables) and SHA-256
Full manifest: `outputs/SHA256SUMS.txt` (30 files, every file under `outputs/` except itself; verified with `sha256sum -c`).

| Path | SHA-256 |
|---|---|
| outputs/mesh.jou | eec2eb385a496973168fe36ae5b96a8e5f71a881da5af2677b6c6590438f5b49 |
| outputs/mesh.exo | 892c8de1feb517864cf4de7fffebdbe99a342a494ad338b8e4892a1eaa7f5488 |
| outputs/mesh_verification.txt | 66a11052672ff86b81079e0677dfaa601b873a93e871b47ddacb512f6c346991 |
| outputs/stage1/input_deck.i | 573725e91faa00ab239760339f47b957c3ee390c799cf81ebbd7e29ab6915941 |
| outputs/stage1/job_script.sbatch | 9714e07c32b3764b9e7edcbf73707aa9e93dbcffa5829d1c950b2c5fe23935f8 |
| outputs/stage1/generated_config/interface.xml | 6cb011ccd7be027a10a0295f96dbea688ec253fc28c322eef6290df9c3d90736 |
| outputs/stage1/generated_config/engine_operations.xml | 09dabcc015dd9e0ab88dbe54a8a2f0496ff19b9abfe94bf5c46107d6238fa40d |
| outputs/stage1/generated_config/engine_input_deck.xml | 7f3edc06119d4155981b3861c2c2263f268e6a3f56f7577cc0aa202f3b35169a |
| outputs/stage1/generated_config/analyze_2_input_deck.xml | 998ee0d46d67b1eb726163d7064b22b57b7ac8c4295c03921456fd10bd1c8e6b |
| outputs/stage1/generated_config/analyze_2_operations.xml | fbabf1a1c037533ce5dc1b1ba6a97ce9d70a795c1128735196a3e624aa73efa0 |
| outputs/stage1/generated_config/analyze_helmholtz_input_deck.xml | c813b81a2c43cbac181b51c3ae12cad319473e7c2725afd29c2637fedec2dcbf |
| outputs/stage1/generated_config/analyze_helmholtz_operations.xml | 402ffc30789914bd0c1c7bf429aa2f08ea22b0040960d015b9c71fd716404854 |
| outputs/stage1/generated_config/mpirun.source | 5f45e199f30722f60934996cf4b58b4ce832972c71a3ef0cbe97ae2f6469f3bc |
| outputs/stage1/morphorm_oc_optimizer_diagnostics.txt | 4aaeaa78e77e9f065e3e0ab91d0205a13cdf600a7c76d9f8fc492b06092772f1 |
| outputs/stage1/engine_output.exo (checkpoint, 21 states) | 58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8 |
| outputs/stage1/final_analyze_output.exo | 1baf67b8cb33f9878f9d64e92529248ab924c4b04f32a6ba9500526c40aa116d |
| outputs/stage1/run_logs/stage1_16242485.out | 836f9d09753df172f2ee471f1ed124f5e2c965cdf3a733890527c80aff0666b3 |
| outputs/stage1/run_logs/morphorm_stage1.log | 597b2a213ac90ef023b31aa8b56f825f7ba4ab3ec5dfbcbd43794c8a07ccec9a |

Other files in `outputs/stage1/run_logs/` (performer logs engine_1_0, analyze_2_1, analyze_helmholtz_2; opt_criteria_history.csv; iteration20_criteria_history.csv; sacct record; verification JSONs) and the generated_config extras (xmlgenerator_stdout.log, verification_xml_params.txt) are hashed in `outputs/SHA256SUMS.txt`.

### 6B. Stage-2 deliverables and SHA-256 (Session B)
Manifest regenerated after Stage 2: `outputs/SHA256SUMS.txt` (61 files, every file under `outputs/` except itself and the empty `.gitkeep`; `sha256sum -c` all OK). Stage-1 hashes in the table above are unchanged.

| Path | SHA-256 |
|---|---|
| outputs/stage2/input_deck.i | 74ae7450d4eb172077997dd92139c22987de7a0f0f2845bc420f34820e7bc02c |
| outputs/stage2/job_script.sbatch | b68192e10f8ce5312971f8dff793143ebb7f83c034f5cc4c59bd4000b68611ce |
| outputs/stage2/generated_config/interface.xml | 3582e3985d2dd3c4e34a29d3338c4b0de6a7b1e3e8a32e1e2cfa24ee1c88c7ef |
| outputs/stage2/generated_config/engine_operations.xml | de4341334d3c99814ea20139addc61561a25508268c3d2eebe97d80e819e9336 |
| outputs/stage2/generated_config/engine_input_deck.xml | 7f3edc06119d4155981b3861c2c2263f268e6a3f56f7577cc0aa202f3b35169a (= Stage 1) |
| outputs/stage2/generated_config/analyze_2_input_deck.xml | 998ee0d46d67b1eb726163d7064b22b57b7ac8c4295c03921456fd10bd1c8e6b (= Stage 1) |
| outputs/stage2/generated_config/analyze_2_operations.xml | fbabf1a1c037533ce5dc1b1ba6a97ce9d70a795c1128735196a3e624aa73efa0 (= Stage 1) |
| outputs/stage2/generated_config/analyze_helmholtz_input_deck.xml | c813b81a2c43cbac181b51c3ae12cad319473e7c2725afd29c2637fedec2dcbf (= Stage 1) |
| outputs/stage2/generated_config/analyze_helmholtz_operations.xml | 402ffc30789914bd0c1c7bf429aa2f08ea22b0040960d015b9c71fd716404854 (= Stage 1) |
| outputs/stage2/generated_config/mpirun.source | 5f45e199f30722f60934996cf4b58b4ce832972c71a3ef0cbe97ae2f6469f3bc (= Stage 1) |
| outputs/stage2/restart_input.exo (checkpoint copy) | 58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8 (= outputs/stage1/engine_output.exo) |
| outputs/stage2/morphorm_oc_optimizer_diagnostics.txt | e206a8507f1c5233305540358ebbbb59df034d8b3219946bbbb097c71f0b2be1 |
| outputs/stage2/engine_output.exo (41 states) | ec46d954b50af857e3373fb8f716fd5e81a97efb13caa1d99088f9af5f71e9a6 |
| outputs/stage2/final_analyze_output.exo | 99f38f171ce7c3347f176230d50629d508a01a7dd062c7f26b9a920e7cfa6643 |
| outputs/stage2/continuation_evidence.txt | 9236f49cac7c3c9535ba90782caee8be4d8d1d6b77df880edaa3afb3011fda6a |
| outputs/stage2/run_logs/stage2_16243174.out | 1258b92263093eea710420d77d0c5c61eaf7ae305174cc936677efa6967db5f1 |
| outputs/stage2/run_logs/morphorm_stage2.log | d37be3eb517f1b9b9c68b7e812ddf05586bac93b565ae9efa9ac7cb18985d85f |

Other files in `outputs/stage2/run_logs/` (performer logs engine_1_0, analyze_2_1, analyze_helmholtz_2; opt_criteria_history.csv; sacct record; stage2_16243174.err (empty); verification records stage2_diag_summary.json, stage2_engine_output.json, stage2_iteration40.json, stage2_restart_input.json, stage2_first_objective_check.json, stage2_field_continuation.txt) and the generated_config extras (xmlgenerator_stdout.log, verification_xml_params.txt) are hashed in `outputs/SHA256SUMS.txt`.

## 7. Failures, retries, cancelled jobs, unresolved issues, deviations
- Failures: none. Retries: none. Cancelled jobs: none. Job submissions: exactly one (16242485), successful.
- Translation decision (not a resubmission): the first translation put `OutputFrequency 5` on the engine PlatoMainOutput operation (the runtime default of the XMLGenerator parameter `isosurface_output_frequency`, reported in its INFO output). That would not satisfy the locked requirement of 21 saved states in the engine output file. The keyword `isosurface_output_frequency` is not documented in the supplied manuals; it was identified from XMLGenerator's own INFO message, tested by translation only in `work/stage1/xlate_check_B/` (diff against the first translation: the single change engine OutputFrequency 5 -> 1, every other generated file byte-identical), and then added to the accepted deck as `isosurface_output_frequency 1`. The first translation is preserved unsubmitted in `work/stage1/run_attempt0_translation_only/`. The run confirmed 21 saved states. This is the only keyword used that is not in the manuals; it is recorded here as a deviation-in-method, not a change of any locked value.
- Filter form check: XMLGenerator printed `filter_radius_absolute was not set` for the filter-block form, yet produced Length Scale 0.043301 (= 0.15/(2*sqrt(3))). The manual's equivalent legacy form (`work/stage1/xlate_check_A/`) produced byte-identical configuration files, so the radius was applied in both forms; the INFO line is a generator message about the legacy keyword, not an unapplied setting. Scratch directories A/B were translation-only, never submitted.
- Observation: although `WriteRestart true` is set, no separate `engine_restart.exo` file appeared in the run directory after completion; the engine wrote all 21 states to `engine_output.exo`, which the specification designates as the checkpoint, so the locked requirement is met by `engine_output.exo`. Stage 2 must read a copy of `outputs/stage1/engine_output.exo` (field `control`, iteration-20 design = last/21st saved state; the manual's `restart_iteration` keyword semantics must be checked against the first Stage-2 compliance = 2.360040e+05 as required by the specification).
- Unresolved issues: none for Stage 1. Deviations from the locked values: none.

### 7B. Session B
- Failures: none. Retries: none. Cancelled jobs: none. Job submissions in Session B: exactly one (16243174), successful. No accepted deliverable was overwritten; `outputs/SHA256SUMS.txt` was regenerated (as the specification requires after Stage 2) and now lists 61 files instead of 30; every Stage-1 hash is unchanged.
- Restart-index decision: `restart_iteration` is documented as an "iteration (time step)" without stating the base. Scratch translations with 20 and 21 (never submitted, kept under `work/stage2/xlate_check_iter20|21/`) showed the integer is passed verbatim to the engine. 21 (the Exodus time step holding iteration 20) was submitted and confirmed correct by the exact match of the first Stage-2 compliance and of the saved fields (section 5B). No correction was needed.
- Method note (same as Stage 1): the Stage-2 deck keeps `isosurface_output_frequency 1`, a keyword not in the supplied manuals (identified in Session A from XMLGenerator's own INFO output), so that every Stage-2 iteration is saved; no locked value was changed by it.
- Unresolved issues: none. Deviations from the locked values: none.

## 8. Final artifact paths
- `outputs/mesh.jou`, `outputs/mesh.exo`, `outputs/mesh_verification.txt`
- `outputs/stage1/input_deck.i`, `outputs/stage1/job_script.sbatch`, `outputs/stage1/generated_config/`
- `outputs/stage1/morphorm_oc_optimizer_diagnostics.txt`, `outputs/stage1/engine_output.exo` (checkpoint), `outputs/stage1/final_analyze_output.exo`, `outputs/stage1/run_logs/`
- `outputs/SHA256SUMS.txt`, `jobs/job_ids.txt`, `jobs/stage1_job_script.sbatch`, `jobs/sacct_16242485.txt`, `logs/stage1_16242485.{out,err}`
- Working state kept for inspection/continuation: `work/stage1/run/` (complete Stage-1 run directory incl. per-iteration `analyze_id_2_output_scenario_id_1/iteration0..20.exo`), `work/verify/`, `work/notes.log`, `work/manuals_txt/`.
- Session B additions: `outputs/stage2/input_deck.i`, `outputs/stage2/job_script.sbatch`, `outputs/stage2/generated_config/`, `outputs/stage2/restart_input.exo`, `outputs/stage2/morphorm_oc_optimizer_diagnostics.txt`, `outputs/stage2/engine_output.exo`, `outputs/stage2/final_analyze_output.exo`, `outputs/stage2/continuation_evidence.txt`, `outputs/stage2/run_logs/`; `outputs/SHA256SUMS.txt` (regenerated, 61 entries); `jobs/job_ids.txt` (2 ids), `jobs/stage2_job_script.sbatch`, `jobs/sacct_16243174.txt`, `jobs/submissions.log`; `logs/stage2_16243174.{out,err}`.
- Session B working state kept: `work/stage2/run/` (complete Stage-2 run directory incl. per-iteration `analyze_id_2_output_scenario_id_1/iteration0..40.exo`), `work/stage2/xlate_check_iter20/`, `work/stage2/xlate_check_iter21/` (translation-only scratch), `work/stage2/input_deck_template.i`, `work/stage2/deliver_stage2.sh`, `work/verify/stage2_*`, `work/summary_parts/`, `work/notes.log`.
