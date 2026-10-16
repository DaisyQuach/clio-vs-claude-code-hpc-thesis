# Run Summary — Trial E2-example16-clio-02 (Session A: Stage 1; Session B: Stage 2 continuation)

**STATUS: Stage 1 COMPLETE (Session A, job 16237845) and Stage 2 COMPLETE (Session B, job 16238332). Both stages reached their iteration caps (20 and 40; overall iteration 60); Stage 2 continued seamlessly from the Stage-1 iteration-20 `control` field (first Stage-2 compliance 2.360040e+05 = Stage-1 iteration-20 compliance). All deliverables of §9 are in place and `outputs/SHA256SUMS.txt` has been regenerated.** Session-A text is kept below unchanged; Session-B additions are the subsections marked "b" (3b–8b).

## 1. Trial identifier and assigned workflow
- Trial identifier (`THESIS_TRIAL_ID`): `E2-example16-clio-02`
- Frozen configuration: `FROZEN-EX16-v1` (`agent_inputs/FROZEN_CONFIG_SHA256.txt`: `a67d6cba7f0ce35ae6dc227f33b39056514be9494d6e15bc8e58524dfba1a86b`)
- Workflow: Full cantilever, two-stage restart (warm-start) workflow, `agent_inputs/scientific_problem_specification.md`. This session was instructed to construct the workflow, complete Stage 1 only, and stop.
- Software: approved interface `source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh` (Morphorm `approved-runtime`, Cubit `cubit-edu/2026.8`); only `agent_inputs/manuals/*.pdf` consulted (text copies under `work/manuals_txt/`).
- Facts log kept during the run: `work/notes.log`.

## 2. Mesh
- Generated with approved Coreform Cubit in batch mode: `cubit -batch -nographics -nojournal -input mesh.jou` in `work/mesh/` (log `work/mesh/cubit.log`, exit 0).
- Journal: `work/mesh/mesh.jou` → delivered as `outputs/mesh.jou`. Brick 2×1×1 moved to corner at origin; mapped scheme; uniform size 1/24; block 1 named `block_1` (HEX8); nodeset 1 = surface x=0 named `ns_fix`; nodeset 2 = curve x=2,y=0 named `ns_load`; `set exodus netcdf4 off`; `export mesh "mesh.exo" dimension 3`.
- Mesh file: `work/mesh/mesh.exo` → `outputs/mesh.exo` (SHA-256 `bb03d206dc6ed33e3a79131860dedb0d2aeca076a37945e1d34f72b5981b3248`); the identical file was used in the Stage-1 run directory (`cmp` verified).
- Verification (bundled `exo_summary.py`, record `work/verify/mesh.json` → `outputs/mesh_verification.json`, `expect_ok: true`): num_elem 27648, num_nodes 30625, num_dim 3, bbox [0,0,0]–[2.0,1.0,1.0], one block `block_1` HEX8 with 27648 elements, nodeset `ns_fix` 625 nodes, nodeset `ns_load` 25 nodes, no sidesets. All match §3 of the specification.

## 3. Input deck and generated runtime configuration (Stage 1)
- Deck: `work/stage1_run/input_deck.i` → `outputs/stage1/input_deck.i` (SHA-256 `69832ce8b31d95e3fd68bc791da8bdd85d4ad5e75463941f51df3cc94525968d`).
- Translation: `XMLGenerator input_deck.i` in `work/stage1_run/` (exit 0, 0 warnings; log `generated_config/xmlgen.log`). Generated files delivered in `outputs/stage1/generated_config/`: `interface.xml`, `engine_input_deck.xml`, `engine_operations.xml`, `analyze_2_input_deck.xml`, `analyze_2_operations.xml`, `analyze_helmholtz_input_deck.xml`, `analyze_helmholtz_operations.xml`, `mpirun.source`, `xmlgen.log`. The SHA-256 of each file as actually used by the job was printed by the job script into `outputs/stage1/run_logs/stage1_16237845.out` and equals the delivered copies.
- Verification record (bundled `xml_params.py`): `work/verify/stage1_generated_config.tsv`.

| Locked setting | Deck keyword(s) | Where it appears in the generated configuration (observed value) |
|---|---|---|
| Engine + analyze services, 1 processor each, single rank, no decomposition | `service 1 code engine number_processors 1`; `service 2 code analyze number_processors 1` | `mpirun.source`: `-np 1` PlatoMain, `-np 1` analyze_MPMD (analyze_2), `-np 1` analyze_MPMD (helmholtz); `interface.xml` Performers engine_1, analyze_2, analyze_helmholtz |
| Material E=1.0, ν=0.3 on `block_1` | `material 1 isotropic_elastic youngs_modulus 1.0 poissons_ratio 0.3`; `block 1 material_id 1 name block_1` | `analyze_2_input_deck.xml` Material Models/material_1: Youngs Modulus 1.0, Poissons Ratio 0.3; Spatial Model/Domains/block_1 → material_1 |
| Fixed support ns_fix ux=uy=uz=0 | `boundary_condition 1 fixed_value nodeset ns_fix dispx dispy dispz value 0 0 0` | `analyze_2_input_deck.xml` Essential Boundary Conditions: Displacement X/Y/Z, Type Fixed Value, Sides ns_fix, Value 0 (Index 0/1/2) |
| Load −1.0 per node on ns_load, direction y | `load 1 concentrated_load nodeset ns_load direction y value -1.0` | `analyze_2_input_deck.xml` Concentrated Loads: Dof 1, Value -1.0, Nodes ns_load; Natural BCs empty (no tractions) |
| Objective: weighted-sum, single compliance criterion, weight 1, analyze service | `criterion 1 mechanical_compliance`; `objective weighted_sum criterion_ids 1 service_ids 2 scenario_ids 1 weights 1` | `analyze_2_input_deck.xml` Criteria/My Objective: Internal Elastic Energy on {block_1}; `engine_operations.xml` Aggregator Weight 1; `interface.xml` Objective ValueStageName "Compute Objective Value" (analyze_2 computes) |
| Volume ≤ 15 %, less_than, engine service | `criterion 2 volume`; `constraint 1 criterion_id 2 relative_target 0.15 type less_than service_id 1` | `interface.xml` Constraint NormalizedTargetValue 0.15, ReferenceValueName Design Volume; `engine_operations.xml` ComputeVolume (engine_1, linear SIMP exponent 1.0 / min 0.0 for the volume measure) |
| Density discretization, uniform initial density 0.15 | `discretization density`, `initialize_method uniform`, `initial_density_value 0.15` | `engine_operations.xml` InitializeField Method Uniform Value 0.15; SetLower/UpperBounds Discretization density; `interface.xml` InitializationStage "Initial Guess" |
| SIMP single phase, exponent 3.0, minimum value 1e-3 | `material_interpolation 1 type single_phase model simp penalty_exponent 3.0 minimum_value 1e-3`, referenced by `residual 1 material_interpolation_id 1` | `analyze_2_input_deck.xml` Residual/Mechanical Residual: Material Interpolation Model Single-Phase, Penalty Function SIMP Exponent 3.0 Minimum Value 1e-3 |
| Compliance criterion minimum_ersatz_material_value 1e-3 | `criterion 1 minimum_ersatz_material_value 1e-3` | `analyze_2_input_deck.xml` Criteria/My Objective/Penalty Function: SIMP Exponent 3.0, Minimum Value 1e-3 |
| OC optimizer, default tolerances | `optimization_algorithm oc` | `interface.xml` Optimizer Package OC; tolerances left at generator defaults (log: control_stagnation 1e-4, objective_stagnation 1e-8, norm_gradient 1e-8) |
| normalize_in_aggregator false | `normalize_in_aggregator false` | no normalization element in `engine_operations.xml` Aggregator (generator default is false per manual Table 2.5.6) |
| update_problem true on engine, frequency 1 | `service 1 update_problem true update_problem_frequency 1` | `engine_operations.xml` Update Problem UpdateProblemFrequency 1; `interface.xml` Options ProblemUpdateFrequency 1 and stage "Update Problem" on engine_1 |
| Helmholtz filter, absolute radius 0.15, boundary-sticking 1.0, no symmetry plane | `filter_type helmholtz`, `filter_radius_absolute 0.15`, `boundary_sticking_penalty 1.0` (legacy study-level form) | `analyze_helmholtz_input_deck.xml` Physics "Helmholtz Filter": Length Scale 0.043301, Surface Length Scale 1.0; no symmetry sidesets. **Inference:** 0.043301 = 0.15/(2√3), i.e. the generator converts the radius to the PDE length scale ℓΩ; both the filter-block form and the legacy form produce the same value (compared in `work/try2_legacyfilter`), so the radius 0.15 is the value that reached the configuration. The manuals do not state this conversion explicitly. |
| Output: dispx dispy dispz from analyze; engine output of control and topology | `output 1 service_id 2 data dispx dispy dispz output_frequency 1` | `analyze_2_input_deck.xml` Output Plottable {displacement_x, displacement_y, displacement_z}; `analyze_2_operations.xml` OutputFrequency 1; `engine_operations.xml` PlatoMainOutput inputs `topology` and `control` (Nodal Field) |
| Stage-1 iteration cap 20 | `max_iterations 20` | `interface.xml` Convergence MaxIterations 20; `engine_operations.xml` PlatoMainOutput MaxIterations 20 |
| Restart-file writing / every-iteration engine output (21 states) | `write_restart_file true`; `isosurface_output_frequency 1` | `engine_operations.xml` PlatoMainOutput WriteRestart true, OutputFrequency 1 |

Comment lines in the deck are on their own lines. No Stage-2 restart keywords (`initial_guess_file_name`, `initial_guess_field_name`, `restart_iteration`) are present in the Stage-1 deck (fresh run; the generator log notes `initial_guess_field_name` unset, as expected).

### 3b. Stage-2 (continuation) input deck and generated configuration — Session B
- Deck: `work/stage2_run/input_deck.i` → `outputs/stage2/input_deck.i` (SHA-256 `135c501beff0952192476028931c1a0338a70fae59e82ad63c3e9a0efd929347`). It is the accepted Stage-1 deck with exactly four changes (verified by `diff`): header comments; `max_iterations 40`; and the three restart keywords of the manual §2.5.10 (Table 2.5.40) `initial_guess_file_name restart_input.exo`, `initial_guess_field_name control`, `restart_iteration 21`. `initialize_method uniform` / `initial_density_value 0.15` were left in place (the generator replaces the Uniform initialization by the restart initialization; see below). `write_restart_file true` and `isosurface_output_frequency 1` kept so Stage 2 also stores every iteration.
- Restart source: `work/stage2_run/restart_input.exo` = `cp -p` of `outputs/stage1/engine_output.exo`, `cmp`-identical (SHA-256 `58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8`), delivered as `outputs/stage2/restart_input.exo`.
- Translation: `XMLGenerator input_deck.i` in `work/stage2_run/` (exit 0, no warnings; `generated_config/xmlgen.log`). Generated files → `outputs/stage2/generated_config/`. SHA-256 of every input as used by the job is printed in `outputs/stage2/run_logs/stage2_16238332.out`.
- Verification (bundled `xml_params.py` → `work/verify/stage2_generated_config.tsv`, plus `diff` of every generated file against `outputs/stage1/generated_config/`): `analyze_2_input_deck.xml`, `analyze_2_operations.xml`, `analyze_helmholtz_input_deck.xml`, `analyze_helmholtz_operations.xml`, `engine_input_deck.xml` and `mpirun.source` are **byte-identical** to Stage 1 (material E=1.0/ν=0.3, SIMP exponent 3.0 / minimum 1e-3 in residual and compliance criterion, load −1.0 on ns_load, displacement X/Y/Z = 0 on ns_fix, Helmholtz Length Scale 0.043301 / Surface Length Scale 1.0, output frequency 1, 1 processor per service). Differences only:

| Locked Stage-2 setting | Deck keyword | Generated configuration (observed) |
|---|---|---|
| Iteration cap 40 | `max_iterations 40` | `interface.xml` Convergence MaxIterations 40; `engine_operations.xml` PlatoMainOutput MaxIterations 40 |
| Restart source file | `initial_guess_file_name restart_input.exo` | `engine_operations.xml` InitializeField: Method `FromFieldOnInputMesh`, Name `restart_input.exo` (replaces the Stage-1 `Uniform 0.15` block) |
| Restart field = control | `initial_guess_field_name control` | `engine_operations.xml` FromFieldOnInputMesh VariableName `control`; PlatoMainOutput RestartFieldName `control` |
| Saved state = iteration 20 | `restart_iteration 21` | `engine_operations.xml` FromFieldOnInputMesh Iteration `21` |
| Every-iteration engine output | `write_restart_file true`, `isosurface_output_frequency 1` | `engine_operations.xml` WriteRestart true, OutputFrequency 1 |

- **Restart index decision.** The manual says `restart_iteration` is "which iteration (time step) in the initial guess file" and does not state the base. The checkpoint stores 21 states with Exodus time values 1.0…21.0 for iterations 0…20, so the iteration-20 design is Exodus time step 21. A probe translation with `restart_iteration 20` (`work/try7_restart20_probe/`, translation only, not submitted) showed the generator passes the integer through unchanged (`<Iteration>20</Iteration>`), so the value is an engine time-step index. Value 21 was submitted and confirmed by the continuation evidence (§5): the first Stage-2 compliance equals the Stage-1 iteration-20 compliance exactly and the first Stage-2 `control` field is bit-identical to the Stage-1 iteration-20 `control` field (and differs from iteration 19 by up to 0.2). The index is therefore 1-based (time step), and no correction was needed.

## 4. Execution
All agent-host shells and the job script sourced the approved interface. Commands used (in order; see `work/notes.log` for timestamps):
1. `pdftotext -layout agent_inputs/manuals/Morphorm_User_Manual.pdf work/manuals_txt/user.txt` (and Theory manual) — permitted manuals to text for `grep`/`sed`.
2. `cd work/mesh && cubit -batch -nographics -nojournal -input mesh.jou` → exit 0.
3. `python3 SKILL/exo_summary.py work/mesh/mesh.exo --expect num_elem=27648 num_nodes=30625 block:block_1:type=HEX8 nodeset:ns_fix=625 nodeset:ns_load=25 bbox_max=2.0,1.0,1.0 bbox_min=0,0,0` → `expect_ok: true`.
4. `XMLGenerator input_deck.i` in `work/stage1` (attempt 1), `work/try2_legacyfilter`, `work/try3_legacy_outfreq`, `work/try4_isofreq`, `work/stage1_run` (attempt 2), `work/try5_minval_probe`, `work/try6_residual_interp`, and finally the accepted `work/stage1_run` — all exit 0 (translation probes only; no job submitted from the probe directories).
5. `python3 SKILL/xml_params.py work/stage1_run ...` → `work/verify/stage1_generated_config.tsv`.
6. `sbatch --parsable jobs/stage1_job_script.sbatch` → job ID **16237845** (recorded in `jobs/job_ids.txt`, `jobs/submissions.txt`). Submit time 2026-10-13T01:24:59-06:00.
7. `bash SKILL/wait_job.sh 16237845 ...` three bounded waits; `sacct -j 16237845` → `work/verify/stage1_sacct.txt`.
8. `python3 SKILL/diag_summary.py`, `exo_summary.py engine_output.exo`, `exo_summary.py iteration20.exo` → `work/verify/stage1_diag.json`, `stage1_engine_output.json`, `stage1_final_analyze_output.json`.
9. Copies to `outputs/`, `cmp` checks, `sha256sum` manifest + `sha256sum -c`.

- Job script: `jobs/stage1_job_script.sbatch` (copy `outputs/stage1/job_script.sbatch`). Resources exactly as frozen: account `hochhalter-np`, partition `hochhalter-np`, 1 node, 1 task, 8 CPUs/task, 32G, 02:00:00, no GPU. It sources the approved interface, `cd`s to `work/stage1_run`, prints the SHA-256 of every input, runs `bash mpirun.source > morphorm_stage1.log`, and exits with its code.
- Slurm jobs submitted in this trial: **16237845** only. `sacct`: State COMPLETED, ExitCode 0:0, Elapsed 00:17:24, node notch274, AllocCPUS 8, ReqMem 32G, partition/account hochhalter-np. Scheduler stdout/stderr: `logs/stage1_16237845.out`, `logs/stage1_16237845.err` (empty), copied to `outputs/stage1/run_logs/`. `mpirun.source exit code 0`.
- Morphorm was not run on the agent host; only Cubit, XMLGenerator and the Python verification checks ran there.

### 4b. Execution — Session B (Stage 2)
Session B is a new process with no record of Session A; it first re-verified the persistent Stage-1 state (`sha256sum -c outputs/SHA256SUMS.txt` OK; `cmp outputs/stage1/engine_output.exo work/stage1_run/engine_output.exo` identical; `diag_summary.py` 21 rows, iteration 20, stop at cap; `exo_summary.py` 21 time steps with `control`/`topology`; `sacct -j 16237845` COMPLETED 0:0). Commands (UTC timestamps in `work/notes.log`):
1. `mkdir work/stage2_run; cp -p outputs/mesh.exo work/stage2_run/mesh.exo; cp -p outputs/stage1/engine_output.exo work/stage2_run/restart_input.exo; cmp` (identical).
2. Stage-2 deck derived from `outputs/stage1/input_deck.i` with `sed` (changes listed in §3b), `diff` recorded.
3. `XMLGenerator input_deck.i` in `work/stage2_run` (exit 0, 2026-10-13T07:49Z) and probe `work/try7_restart20_probe` (exit 0, not submitted).
4. `python3 SKILL/xml_params.py work/stage2_run ...` → `work/verify/stage2_generated_config.tsv`; `diff` against Stage-1 generated files.
5. `jobs/stage2_job_script.sbatch` written from the Stage-1 script (job name `ex16_stage2`, run dir `work/stage2_run`, log `morphorm_stage2.log`, `module list` added to stdout, `restart_input.exo` added to the hashed inputs); resources exactly as frozen: account/partition `hochhalter-np`, 1 node, 1 task, 8 CPUs/task, 32G, 02:00:00, no GPU; sources the approved interface before any executable. Copy: `outputs/stage2/job_script.sbatch`.
6. `sbatch --parsable jobs/stage2_job_script.sbatch` → job ID **16238332** (submit 2026-10-13T01:50:38 MDT = 07:50:38Z; recorded in `jobs/job_ids.txt`, `jobs/submissions.txt`).
7. Once the first diagnostics row appeared (~1 min after start): `diag_summary.py --compare-first-to 2.360040e+05` → relative difference 0.0 (`work/verify/stage2_first_objective_check.json`); the run was allowed to continue. Then `bash SKILL/wait_job.sh 16238332 ...` in four bounded waits.
8. After completion: `sacct -j 16238332 ... -P` → `jobs/stage2_sacct_16238332.txt` (and `jobs/stage1_sacct_16237845.txt`); `diag_summary.py`, `exo_summary.py` on `engine_output.exo` and `iteration40.exo` → `work/verify/stage2_diag.json`, `stage2_engine_output.json`, `stage2_final_analyze_output.json`; `python3 -I work/verify/compare_restart_fields.py` → `work/verify/stage2_restart_field_comparison.json` (small field-comparison program written because the bundled checks cannot compare fields between two files).
9. Copies to `outputs/stage2/`, `cmp` checks, `sha256sum` manifest regenerated and `sha256sum -c` passed.

- Slurm jobs submitted in this trial: **16237845** (Stage 1, Session A) and **16238332** (Stage 2, Session B); no others. Job 16238332: State COMPLETED, ExitCode 0:0, Start 2026-10-13T01:50:43 MDT, End 02:24:09 MDT, Elapsed 00:33:26, node notch274, AllocCPUS 8, ReqMem 32G, MaxRSS 2.4 GB; `module list` in stdout: chpc/1.0, gcc/11.2.0, openmpi/5.0.3, morphorm/approved-runtime, cubit-edu/2026.8; `mpirun.source exit code 0`. Scheduler stdout/stderr: `logs/stage2_16238332.out`, `logs/stage2_16238332.err` (empty), copied to `outputs/stage2/run_logs/`.
- Morphorm was not run on the agent host (only XMLGenerator and Python checks).

## 5. Completed stages and iteration counts
- **Stage 1: complete.** Optimizer diagnostics `morphorm_oc_optimizer_diagnostics.txt`: 21 iteration rows, Iter 0 … 20 (F-count 1 … 21). Stopping message: `****** Optimization stopping due to exceeding maximum number of iterations. ******` (iteration cap 20 reached, as required). Objective F(X): iteration 0 = 4.893235e+06, iteration 20 = 2.360040e+05 (last-iteration compliance that Stage 2 must reproduce as its first evaluated compliance). Constraint H1(X) at iteration 20 = 3.964884e-13 (volume constraint active/feasible). `opt_criteria_history.csv` lists the same 21 objective values.
- Checkpoint: `work/stage1_run/engine_output.exo` → `outputs/stage1/engine_output.exo` (SHA-256 `58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8`, byte-identical copy verified with `cmp`; unmodified). Verified with `exo_summary.py` (`work/verify/stage1_engine_output.json`): 21 time steps (time values 1.0 … 21.0, i.e. iterations 0 … 20), nodal fields `control` and `topology`, 30625 nodes / 27648 elements, nodesets ns_fix/ns_load preserved. Note for Stage 2: the file holds 21 states; the iteration-20 design is the last state (time step 21 if 1-based, index 20 if 0-based) and must be read from the `control` field. The engine did not write a separate `engine_restart.exo` despite `WriteRestart true` in `engine_operations.xml`; the specification designates the engine output file as the checkpoint, so this does not block Stage 2 (the manual states `initial_guess_file_name` may be `engine_output.exo`).
- Final analyze output: `analyze_id_2_output_scenario_id_1/iteration20.exo` → `outputs/stage1/final_analyze_output.exo` (1 time step; nodal `displacement X/Y/Z`; record `work/verify/stage1_final_analyze_output.json`).
- Stage 2 (as of Session A): not started. *Superseded by §5b: Stage 2 was completed in Session B.*

### 5b. Stage 2 — completed (Session B) and continuation evidence
- **Stage 2: complete.** `outputs/stage2/morphorm_oc_optimizer_diagnostics.txt`: 41 iteration rows, local Iter 0 … 40 (F-count 1 … 41) = overall iterations 20 … 60. Stopping message: `****** Optimization stopping due to exceeding maximum number of iterations. ******` (cap 40 reached). Objective F(X): local iteration 0 = 2.360040e+05, local iteration 40 (overall 60) = 2.135584e+05; constraint H1(X) at the end = −7.552292e−14 (volume constraint active, feasible). `opt_criteria_history.csv` lists the same 41 values. Bundled record: `work/verify/stage2_diag.json`.
- Engine output `outputs/stage2/engine_output.exo`: 41 time steps (time values 1.0 … 41.0 = local iterations 0 … 40), nodal fields `control`, `topology` (`work/verify/stage2_engine_output.json`). Final analyze output `analyze_id_2_output_scenario_id_1/iteration40.exo` → `outputs/stage2/final_analyze_output.exo` (1 step, time 40.0; nodal `Topology`, `displacement X/Y/Z`; `work/verify/stage2_final_analyze_output.json`).
- **Continuation evidence** (`outputs/stage2/continuation_evidence.json`):
  - Checkpoint: `outputs/stage1/engine_output.exo` (SHA-256 `58dee776…3248`-prefixed value in manifest: `58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8`), 21 saved states; read by Stage 2 through the byte-identical copy `outputs/stage2/restart_input.exo` (same SHA-256).
  - Field: `control` (raw design variable), not `topology`. Saved state: Stage-1 iteration 20 = last state = Exodus time step 21 (`restart_iteration 21`).
  - Optimizer diagnostics: Stage-1 iteration 20 F(X) = **2.360040e+05**, Norm(F') = 1.191537e+04, H1 = 3.964884e−13; Stage-2 iteration 0 F(X) = **2.360040e+05**, Norm(F') = 1.191537e+04, H1 = 3.964884e−13 — identical (relative difference 0.0, `diag_summary.py --compare-first-to`). For contrast, Stage-1 iteration 19 F(X) = 2.388394e+05 ≠ Stage-2 iteration 0.
  - Saved fields (`work/verify/stage2_restart_field_comparison.json`): Stage-2 state 0 `control` vs Stage-1 state 20 `control`: max |Δ| = 0.0 over 30625 nodes (0 nodes differ); vs Stage-1 state 19: max |Δ| = 0.2. `topology` likewise max |Δ| = 0.0 vs state 20 (0.047 vs state 19). The closest Stage-1 state to the Stage-2 initial design is iteration 20 for both fields.
  - Conclusion: seamless restart from the iteration-20 design; the two stages together form one uninterrupted 60-iteration run. No restart correction was needed.

## 6. Key output files (outputs/) with SHA-256
Full manifest: `outputs/SHA256SUMS.txt` (verified with `sha256sum -c`; must be regenerated after Stage 2). Principal entries:
- `outputs/mesh.exo` `bb03d206dc6ed33e3a79131860dedb0d2aeca076a37945e1d34f72b5981b3248`
- `outputs/mesh.jou` `f800db8abb1ff7b7793091f1622301d5dd81e576159286f5f472a60e0c3f176f`
- `outputs/mesh_verification.json` `d99a3ab589cf294541beebc33e2fd084cdb97c1c029c0d28ffdc0f0e0eb39408`
- `outputs/stage1/input_deck.i` `69832ce8b31d95e3fd68bc791da8bdd85d4ad5e75463941f51df3cc94525968d`
- `outputs/stage1/job_script.sbatch` `2c961ff1f8ca6f1120ae63cadd7af01ca45c265411553906406aa2de3e8bda63`
- `outputs/stage1/generated_config/interface.xml` `2e2f1e9c750eb785bb3c6534df928b4bdd988cc0f53a4653ce142ec2a661dbb5`; `engine_operations.xml` `09dabcc015dd9e0ab88dbe54a8a2f0496ff19b9abfe94bf5c46107d6238fa40d`; `analyze_2_input_deck.xml` `998ee0d46d67b1eb726163d7064b22b57b7ac8c4295c03921456fd10bd1c8e6b`; `analyze_helmholtz_input_deck.xml` `c813b81a2c43cbac181b51c3ae12cad319473e7c2725afd29c2637fedec2dcbf` (others in the manifest)
- `outputs/stage1/morphorm_oc_optimizer_diagnostics.txt` `4aaeaa78e77e9f065e3e0ab91d0205a13cdf600a7c76d9f8fc492b06092772f1`
- `outputs/stage1/engine_output.exo` (checkpoint) `58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8`
- `outputs/stage1/final_analyze_output.exo` `1baf67b8cb33f9878f9d64e92529248ab924c4b04f32a6ba9500526c40aa116d`
- `outputs/stage1/run_logs/`: `stage1_16237845.out`, `stage1_16237845.err`, `morphorm_stage1.log`, performer logs `engine_1_0`, `analyze_2_1`, `analyze_helmholtz_2`, `opt_criteria_history.csv`, `iteration20_criteria_history.csv` (hashes in manifest)

### 6b. Stage-2 output files (outputs/stage2/) with SHA-256 — Session B
Manifest `outputs/SHA256SUMS.txt` regenerated over all 50 files under `outputs/` (excluding itself) and verified with `sha256sum -c`. Principal Stage-2 entries:
- `outputs/stage2/input_deck.i` `135c501beff0952192476028931c1a0338a70fae59e82ad63c3e9a0efd929347`
- `outputs/stage2/job_script.sbatch` `208da6cde776a6173bb4ce320efa1752d2db25a7f804b70d617ee357cfdc95bb`
- `outputs/stage2/restart_input.exo` `58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8` (= Stage-1 checkpoint)
- `outputs/stage2/morphorm_oc_optimizer_diagnostics.txt` `e206a8507f1c5233305540358ebbbb59df034d8b3219946bbbb097c71f0b2be1`
- `outputs/stage2/engine_output.exo` `ec46d954b50af857e3373fb8f716fd5e81a97efb13caa1d99088f9af5f71e9a6`
- `outputs/stage2/final_analyze_output.exo` `99f38f171ce7c3347f176230d50629d508a01a7dd062c7f26b9a920e7cfa6643`
- `outputs/stage2/continuation_evidence.json` `c44cc63eab2a3d95717c7ec029125e6e20ec3cffdd9dcf313136291a91c063eb`
- `outputs/stage2/generated_config/` (interface.xml, engine_input_deck.xml, engine_operations.xml, analyze_2_input_deck.xml, analyze_2_operations.xml, analyze_helmholtz_input_deck.xml, analyze_helmholtz_operations.xml, mpirun.source, xmlgen.log) and `outputs/stage2/run_logs/` (stage2_16238332.out/.err, morphorm_stage2.log, engine_1_0, analyze_2_1, analyze_helmholtz_2, opt_criteria_history.csv, iteration40_criteria_history.csv): hashes in the manifest.
- Stage-1 entries are unchanged (same hashes as in §6).

## 7. Failures, retries, cancelled jobs, deviations
- No job failed and no job was cancelled; a single submission (16237845) completed.
- Translation retries before submission (all kept under `work/`, none submitted):
  - `work/stage1_attempt1_filterblock_superseded/`: deck used a `begin filter 1 … end filter` block with `filter_ids 1`. Generated engine `OutputFrequency` was 5 (generator default `isosurface_output_frequency 5`), which would have stored only 5 states in `engine_output.exo` instead of 21. Superseded.
  - `work/try2_legacyfilter/`: legacy `filter_type/filter_radius_absolute/boundary_sticking_penalty` form; generated Helmholtz values identical to the block form (Length Scale 0.043301, Surface Length Scale 1.0) — used to confirm the radius propagated.
  - `work/try3_legacy_outfreq/`: study-level `output_frequency 1` — rejected by XMLGenerator as unrecognized (WARNING, ignored). Not used.
  - `work/try4_isofreq/`: `isosurface_output_frequency 1` (keyword name taken from XMLGenerator's own INFO line; it is not documented in the supplied manuals) → engine `OutputFrequency 1`, every other generated file unchanged. **Decision:** adopted, since the specification requires 21 saved states; the run confirmed 21 time steps.
  - `work/stage1_attempt2_matblock_interp_superseded/`: `material_interpolation_id 1` placed in the material block; `minimum_value 1e-3` did not reach the residual's SIMP block (probe `work/try5_minval_probe` with 1e-5 produced identical XML). Superseded.
  - `work/try6_residual_interp/`: `material_interpolation_id 1` moved to `residual 1` → residual Penalty Function now carries `Minimum Value 1e-3`. **Decision:** adopted as the Stage-1 deck (`work/stage1_run`).
- Assumptions/inferences: (a) Helmholtz Length Scale 0.043301 is taken to be the generator's conversion of radius 0.15 (= 0.15/(2√3)); (b) the engine volume operation's linear SIMP (exponent 1.0, minimum 0.0) is the generator's standard volume measure and is not the material SIMP of §6, which is verified in the analyze deck; (c) `normalize_in_aggregator false` leaves no explicit XML element and is taken as applied by default.
- Deviations from the specification: none known. No `engine_restart.exo` appeared (see §5), but the specification's checkpoint is `engine_output.exo`, which is present and complete.
- Unresolved issues: none for Stage 1. (Stage 2 was intentionally not started in Session A; completed in Session B, see §7b.)

### 7b. Session B failures, retries, deviations
- No job failed or was cancelled in Session B; one submission (16238332) completed. Translation probe `work/try7_restart20_probe/` (restart_iteration 20) was for inspection only and never submitted.
- Observation: Stage 2 wrote `engine_restart.exo` in the run directory, but it is a 0-byte file (SHA-256 of the empty string); Stage 1 wrote none. The specification's checkpoint is `engine_output.exo`, which is complete in both stages, so this does not affect the workflow. The empty file was copied to `outputs/stage2/engine_restart.exo` for completeness (not a required deliverable).
- The bundled checks cannot compare fields between two Exodus files, so one small verification program (`work/verify/compare_restart_fields.py`, run with `python3 -I` on the approved runtime's netCDF4/numpy) was written for the field-level continuation evidence.
- Assumption resolved by evidence: `restart_iteration` is the 1-based Exodus time-step index (21 = iteration 20); see §3b.
- Deviations from the specification: none known. Unresolved issues: none. No accepted Stage-1 deliverable was overwritten; the Session-A summary is preserved as `work/run_summary_sessionA_stage1_only.md`.

## 8. Final artifact paths
- Mesh: `outputs/mesh.jou`, `outputs/mesh.exo`, `outputs/mesh_verification.json`
- Stage 1: `outputs/stage1/input_deck.i`, `outputs/stage1/job_script.sbatch`, `outputs/stage1/generated_config/`, `outputs/stage1/morphorm_oc_optimizer_diagnostics.txt`, `outputs/stage1/engine_output.exo` (checkpoint, 21 states), `outputs/stage1/final_analyze_output.exo`, `outputs/stage1/run_logs/`
- Manifest: `outputs/SHA256SUMS.txt`
- Scheduler: `jobs/job_ids.txt`, `jobs/submissions.txt`, `jobs/stage1_job_script.sbatch`, `logs/stage1_16237845.out`, `logs/stage1_16237845.err`
- Working copies and verification records: `work/stage1_run/` (live run directory incl. all `iteration{0..20}.exo`), `work/mesh/`, `work/verify/`, `work/notes.log`, superseded attempts and probes under `work/stage1_attempt*`, `work/try*`
- Stage 2: see §8b.

### 8b. Stage-2 artifact paths (Session B)
- Stage 2: `outputs/stage2/input_deck.i`, `outputs/stage2/job_script.sbatch`, `outputs/stage2/generated_config/`, `outputs/stage2/restart_input.exo`, `outputs/stage2/morphorm_oc_optimizer_diagnostics.txt`, `outputs/stage2/engine_output.exo` (41 states), `outputs/stage2/final_analyze_output.exo` (local iteration 40 = overall 60), `outputs/stage2/continuation_evidence.json`, `outputs/stage2/run_logs/`
- Manifest: `outputs/SHA256SUMS.txt` (regenerated after Stage 2)
- Scheduler: `jobs/job_ids.txt` (16237845, 16238332), `jobs/submissions.txt`, `jobs/stage2_job_script.sbatch`, `jobs/stage1_sacct_16237845.txt`, `jobs/stage2_sacct_16238332.txt`, `logs/stage2_16238332.out`, `logs/stage2_16238332.err`
- Working copies and verification: `work/stage2_run/` (live run directory incl. all `iteration{0..40}.exo`), `work/verify/stage2_*.json|tsv`, `work/verify/compare_restart_fields.py`, `work/try7_restart20_probe/`, `work/notes.log`
