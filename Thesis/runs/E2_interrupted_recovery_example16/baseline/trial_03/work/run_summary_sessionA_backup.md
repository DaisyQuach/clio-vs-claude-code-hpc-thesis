# Run summary — Session A (Stage 1 only)

## 1. Trial identifier and assigned workflow
- **Trial identifier:** `E2-example16-baseline-03` (environment variable `THESIS_TRIAL_ID`).
- **Frozen configuration:** `FROZEN-EX16-v1` (hash `a67d6cba7f0ce35ae6dc227f33b39056514be9494d6e15bc8e58524dfba1a86b`).
- **Workflow:** full cantilever, two-stage restart (warm-start) minimum-compliance topology optimization (`agent_inputs/scientific_problem_specification.md`).
- **Session:** Session A, fully headless. **Stage 1 is COMPLETE and verified. Stage 2 has NOT been started**: no Stage-2 or continuation deck, job script, translation or job was created, submitted or run in this session.
- **Agent host:** Slurm job 16165551 (account/partition hochhalter-np, 1 node, 8 CPUs, 32 GB, 02:00:00) on notch351. Software interface sourced on the agent host and in the job script: `source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh` (modules loaded: chpc/1.0, gcc/11.2.0, openmpi/5.0.3, morphorm/approved-runtime, cubit-edu/2026.8; see `logs/env_check_agent_host.log` and the job stdout).
- Documentation used: only `agent_inputs/manuals/Morphorm_User_Manual.pdf` and `Morphorm_Theory_Manual.pdf` (text extracted with pdftotext into `work/manual_text/`). No external reference meshes, decks, runs, outputs or scoring material were sought or used; nothing outside the trial root was modified.

## 2. Mesh
- **Generation:** Coreform Cubit 2026.8 in batch mode on the agent host (mesh generation on the agent host is permitted by `compute_resources.md`): `cubit -batch -nographics -nojournal -input mesh.jou` run in `work/mesh/` (log: `work/mesh/cubit_run.log`, copied to `outputs/stage1/run_logs/cubit_mesh_generation.log`). Mesh generation UTC 2026-10-09T20:22:42Z – 20:22:45Z, exit 0.
- **Journal:** `outputs/mesh.jou` (= `work/mesh/mesh.jou`): brick 2.0×1.0×1.0 translated so the corner is at the origin; `volume 1 scheme map`, `curve all interval 24`, `curve with length > 1.5 interval 48`; `block 1` = volume 1, named `block_1`, element type HEX8; `nodeset 1` = surface x=0 named `ns_fix`; `nodeset 2` = curve x=2,y=0 named `ns_load`; `export mesh "mesh.exo" dimension 3 overwrite`.
- **Files:** `outputs/mesh.exo` (sha256 `ceeed3bbaca41c84f1d568fdde66c4d810a685467fe83a27351dca70d851fcaf`), `outputs/mesh_verification.json` (verification record), script `work/scripts/verify_mesh.py` (approved runtime python3 + netCDF4, run with `python3 -I`).
- **Verification result (UTC 2026-10-09T20:23:4xZ, all 25 checks PASS):** elements 27648, nodes 30625, blocks 1 (block_1, HEX8), nodesets {'ns_fix': 625, 'ns_load': 25}, sidesets 0, bbox [0.0, 2.0, 0.0, 1.0, 0.0, 1.0], checks passed 25/25. Additional checks: every node lies on the h = 1/24 lattice (49×25×25 planes), all 12 edges of every HEX8 equal h (max deviation 1.5e-15), ns_fix contains every node with x = 0 (625), ns_load contains every node with x = 2 and y = 0 (25 nodes spanning z ∈ [0,1]), element count × h³ = 2.0 = domain volume.
- First attempt of the verification script crashed (floating-point noise in coordinates broke a naive unique-count); the script was corrected to snap coordinates to the h-lattice with a 1e-9 tolerance and rerun. The mesh itself was generated once and never regenerated.

## 3. Input deck and generated runtime configuration (Stage 1)
- **Deck:** `outputs/stage1/input_deck.i` (= `work/stage1/input_deck.i`, sha256 `3d865e33ef7a86e05fe24111e4898259aa9cf1e72e811a29c9a0493869042e8d`).
- **Translation:** `XMLGenerator input_deck.i` in `work/stage1/` (the Stage-1 run directory). Two translations were made: attempt 1 (UTC 20:24:05Z, kept under `work/stage1/translation_attempt1/`) showed the engine output operation with `OutputFrequency 5`, which would not guarantee a saved state at every iteration; attempt 2 (UTC 20:26:53Z–20:26:54Z, exit 0, log `outputs/stage1/generated_config/xmlgenerator.log`) is the configuration actually run, after adding `isosurface_output_frequency 1` to the study block (see §7). Generated files kept in `outputs/stage1/generated_config/`: `interface.xml`, `engine_input_deck.xml`, `engine_operations.xml`, `analyze_2_input_deck.xml`, `analyze_2_operations.xml`, `analyze_helmholtz_input_deck.xml`, `analyze_helmholtz_operations.xml`, `mpirun.source`.
- **Automated verification of the generated configuration:** `work/scripts/verify_generated_config.py 1 work/stage1` → `outputs/stage1/generated_config/generated_config_verification.json`, 52/52 checks PASS (UTC 2026-10-09T20:26:5xZ). Locked settings and where each appears in the *generated* configuration:

| Locked setting | Deck keyword(s) | Generated configuration (file → element) |
|---|---|---|
| Design domain / mesh | `mesh 1: name mesh.exo` | `engine_input_deck.xml` `<mesh>mesh.exo`; `analyze_2_input_deck.xml` and `analyze_helmholtz_input_deck.xml` `Input Mesh = mesh.exo`, `Spatial Dimension = 3` |
| One block `block_1`, E = 1.0, ν = 0.3 isotropic elastic | `block 1 name block_1 material_id 1`; `material 1 isotropic_elastic youngs_modulus 1.0 poissons_ratio 0.3` | `analyze_2_input_deck.xml` Spatial Model/Domains/block_1 → Material Model material_1; Material Models/material_1/Isotropic Linear Elastic: Youngs Modulus 1.0, Poissons Ratio 0.3 |
| Fixed support ns_fix, u_x=u_y=u_z=0 | `boundary_condition 1 fixed_value nodeset ns_fix dispx dispy dispz 0 0 0` | `analyze_2_input_deck.xml` Essential Boundary Conditions: Displacement X/Y/Z with ID 1/2/3, Type Fixed Value, Index 0/1/2, Sides ns_fix, Value 0.0 |
| Load: concentrated nodal load, every node of ns_load, direction y, −1.0 per node (25 nodes → −25.0 total); no tractions/body forces | `load 1 concentrated_load nodeset ns_load direction y value -1.0` | `analyze_2_input_deck.xml` Concentrated Loads/Concentrated Load with ID 0: Dof 1, Value −1.0, Nodes ns_load; Mechanical Natural Boundary Conditions empty; no body loads |
| Objective: weighted-sum, single compliance criterion, weight 1, evaluated by analyze | `criterion 1 mechanical_compliance`; `objective 1 weighted_sum criterion_ids 1 service_ids 2 scenario_ids 1 weights 1` | `analyze_2_input_deck.xml` Criteria/My Objective: Scalar Function Type Internal Elastic Energy; `interface.xml` stage Compute Objective Value performed by analyze_2, Aggregator (engine) weight 1 |
| SIMP single phase, exponent 3.0, minimum 1e-3; compliance `minimum_ersatz_material_value 1e-3` | `material_interpolation 1 single_phase simp penalty_exponent 3.0 minimum_value 1e-3` (referenced from residual 1 and material 1); `criterion 1 minimum_ersatz_material_value 1e-3` | `analyze_2_input_deck.xml` Residual/Mechanical Residual: Material Interpolation Model Single-Phase, Penalty Function SIMP Exponent 3.0 Minimum Value 1e-3; Criteria/My Objective/Penalty Function SIMP Exponent 3.0 Minimum Value 1e-3 |
| Constraint volume ≤ 15 %, relative_target 0.15, less_than, evaluated by engine | `criterion 2 volume`; `constraint 1 criterion_id 2 relative_target 0.15 type less_than service_id 1` | `interface.xml` Optimizer/Constraint: NormalizedTargetValue 0.15, ReferenceValueName Design Volume, value/gradient stages performed by engine_1; `engine_operations.xml` ComputeVolume operations |
| Density discretization, uniform initial density 0.15 | `study: discretization density, initialize_method uniform, initial_density_value 0.15` | `engine_operations.xml` InitializeField Method Uniform Value 0.15; SetLower/UpperBounds Discretization density; `interface.xml` BoundConstraint Lower 0.0 Upper 1.0 |
| Optimizer OC, default tolerances, max_iterations 20 | `study: optimization_algorithm oc, max_iterations 20` | `interface.xml` Optimizer Package OC, MaxIterations 20, OCControlStagnationTolerance 1e-4, OCObjectiveStagnationTolerance 1e-8, OCGradientTolerance 1e-8 |
| `normalize_in_aggregator false` | `study: normalize_in_aggregator false` | `engine_operations.xml` Aggregator has a single weight 1 and no normalization element |
| `update_problem true`, `update_problem_frequency 1` on the engine service | `service 1 update_problem true update_problem_frequency 1` | `engine_operations.xml` Update Problem UpdateProblemFrequency 1; `interface.xml` ProblemUpdateFrequency 1 and UpdateProblemStage "Update Problem" |
| Helmholtz filter, absolute radius 0.15, boundary-sticking penalty 1.0, no symmetry plane | `filter 1 helmholtz radius_absolute 0.15 boundary_sticking_penalty 1.0`; `study filter_ids 1` | `analyze_helmholtz_input_deck.xml` Physics Helmholtz Filter, **Length Scale 0.043301** (= 0.15/(2√3), the runtime's radius→length-scale conversion; proven by a scratch translation with radius 0.30 → 0.086603, kept in `work/scratch_xmlgen_checks/A_filter_values/`), **Surface Length Scale 1.0** (= boundary_sticking_penalty, proven by the same scratch test: 0.5 → 0.5; the Theory Manual §Helmholtz states boundary_sticking_penalty sets ℓΓ); no symmetry entries |
| Services engine + analyze, one processor each, single-rank performers, no decomposition | `service 1 engine number_processors 1`, `service 2 analyze number_processors 1` | `mpirun.source`: `-np 1` for PlatoMain (engine_1), analyze_MPMD (analyze_2) and analyze_MPMD (analyze_helmholtz, auto-wired filter service); no decomposition step |
| Output dispx dispy dispz from analyze; engine output of control and topology | `output 1 service_id 2 data dispx dispy dispz` | `analyze_2_input_deck.xml` Output Plottable {displacement_x, displacement_y, displacement_z}; `engine_operations.xml` PlatoMainOutput inputs topology + control |
| Stage 1: restart-file writing enabled, every iteration saved (21 states) | `study: write_restart_file true`, `isosurface_output_frequency 1` | `engine_operations.xml` PlatoMainOutput WriteRestart true, OutputFrequency 1, MaxIterations 20 |
| Stage 1 is a fresh run | no `restart_iteration`/`initial_guess_*` keywords | XMLGenerator log: restart_iteration default 0; InitializeField is Uniform (no field read from file) |

- Note: in the XMLGenerator INFO log the lines "filter_radius_absolute was not set" and "Using default value of 1.0 for boundary_sticking_penalty" refer to the legacy study-level keywords; the filter-block values were applied, as proven above (length scale changes with `radius_absolute`, surface length scale changes with `boundary_sticking_penalty`).

## 4. Execution
Commands used (agent host unless stated; the approved interface was sourced before each):
1. `pdftotext -layout agent_inputs/manuals/Morphorm_User_Manual.pdf work/manual_text/user_manual.txt` (and the Theory Manual) — reading the permitted documentation.
2. `source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh; module list; which cubit XMLGenerator PlatoMain analyze_MPMD mpiexec python3` → `logs/env_check_agent_host.log`; `squeue/sinfo/scontrol` → `logs/slurm_check_agent_host.log`.
3. `cd work/mesh && cubit -batch -nographics -nojournal -input mesh.jou` (UTC 20:22:42Z–20:22:45Z, exit 0).
4. `cd work/mesh && python3 -I ../scripts/verify_mesh.py mesh.exo > mesh_verification.json` (first run crashed on a script bug, script fixed, second run exit 0, UTC ~20:23:4xZ).
5. `cp work/mesh/mesh.exo work/stage1/mesh.exo; cd work/stage1 && XMLGenerator input_deck.i` (attempt 1, UTC 20:24:05Z–20:24:06Z, exit 0; attempt 2 after adding `isosurface_output_frequency 1`, UTC 20:26:53Z–20:26:54Z, exit 0).
6. Scratch translations in `work/scratch_xmlgen_checks/{A,B,C,D}*/` (XMLGenerator only, nothing run) to prove the keyword→configuration mappings (see §3 and §7).
7. `python3 -I work/scripts/verify_generated_config.py 1 work/stage1 > work/stage1/generated_config_verification.json` (exit 0, 52/52 PASS).
8. `sbatch jobs/stage1_job.sbatch` → **Submitted batch job 16165768** (submission UTC 2026-10-09T20:27:25Z; also recorded in `jobs/job_ids.txt` and `jobs/submissions.log`).
9. Inside the job (`jobs/stage1_job.sbatch` = `outputs/stage1/job_script.sbatch`): frozen resources `--account=hochhalter-np --partition=hochhalter-np --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=32G --time=02:00:00`, no GPU; sources the approved interface, prints `module list`, `cd work/stage1`, sha256 of all inputs, `export OMP_NUM_THREADS=1` (one processor per single-rank performer), `bash mpirun.source > morphorm_stage1.log 2>&1`.
10. Polling with `squeue -j 16165768`; after completion `sacct -j 16165768 --format=JobID,JobName,State,ExitCode,Submit,Start,End,Elapsed,AllocCPUS,ReqMem,MaxRSS,NodeList -P > jobs/sacct_16165768.txt`.
11. `python3 -I work/scripts/verify_stage1_results.py work/stage1 > work/stage1/stage1_results_verification.json` (first run flagged two over-strict checks of my own script — see §7 — script corrected, second run exit 0, 17/17 PASS, UTC ~20:48Z).
12. Copy of deliverables to `outputs/` (cp; sha256 of each copy compared to its original — all MATCH), `cd outputs && find . -type f ! -name SHA256SUMS.txt | sort | xargs sha256sum > SHA256SUMS.txt && sha256sum -c SHA256SUMS.txt` (OK, UTC 2026-10-09T20:48:07Z).

Slurm jobs submitted in this trial (all in `jobs/job_ids.txt`):

| Job ID | Script | Host | State | ExitCode | Submit (local) | Start | End | Elapsed | MaxRSS |
|---|---|---|---|---|---|---|---|---|---|
| 16165768 | `jobs/stage1_job.sbatch` | notch272 | COMPLETED | 0:0 | 2026-10-09T14:27:25 (20:27:25Z) | 14:27:29 (20:27:29Z) | 14:46:03 (20:46:03Z) | 00:18:34 | 2.4 GB |

Job timestamps from its stdout: JOB START UTC 2026-10-09T20:27:33Z, MORPHORM START UTC 20:27:39Z, MORPHORM END UTC 20:46:03Z, MORPHORM EXIT CODE 0, JOB END UTC 20:46:03Z. `module list` output is in the job stdout (`outputs/stage1/run_logs/slurm_16165768.out`). Stderr is empty. No job was cancelled or re-submitted.

## 5. Completed stages and iteration counts
- **Stage 1: COMPLETE.** Optimizer diagnostics (`outputs/stage1/morphorm_oc_optimizer_diagnostics.txt`) contain iterations 0–20 (21 rows, F-count 1–21) and end with the stopping message `****** Optimization stopping due to exceeding maximum number of iterations. ******` (max_iterations 20 reached, as required). Volume constraint H1(X) ≈ 4e-13 at iteration 20 (active, feasible). Full diagnostics:

```
Iter   F-count          F(X)        Norm(F')         H1(X)         abs(dX)        abs(dF)
0         1        4.893235e+06   5.288704e+05  -1.564817e-02   1.500000e-01  1.797693e+308
1         2        8.715305e+05   1.190725e+05   9.426307e-02   2.000000e-01   4.021705e+06
2         3        9.153247e+05   7.076490e+04   4.184032e-02   2.000000e-01   4.379426e+04
3         4        5.932948e+05   3.922089e+04   4.846958e-02   2.000000e-01   3.220299e+05
4         5        7.157917e+05   5.052073e+04   1.676062e-02   2.000000e-01   1.224969e+05
5         6        5.716814e+05   3.791666e+04   1.721705e-02   2.000000e-01   1.441103e+05
6         7        6.161091e+05   4.085972e+04  -4.378164e-13   2.000000e-01   4.442771e+04
7         8        5.220660e+05   3.312145e+04  -6.858403e-14   2.000000e-01   9.404305e+04
8         9        4.470169e+05   2.693147e+04  -2.564338e-13   2.000000e-01   7.504918e+04
9        10        3.893516e+05   2.243726e+04  -3.237688e-13   2.000000e-01   5.766529e+04
10        11        3.481402e+05   1.935145e+04   6.715462e-13   2.000000e-01   4.121135e+04
11        12        3.179639e+05   1.725104e+04   5.812573e-13   2.000000e-01   3.017632e+04
12        13        2.957322e+05   1.572357e+04  -3.227973e-14   2.000000e-01   2.223172e+04
13        14        2.794783e+05   1.464060e+04   5.512257e-14   2.000000e-01   1.625391e+04
14        15        2.674795e+05   1.385789e+04  -5.665746e-13   2.000000e-01   1.199873e+04
15        16        2.585237e+05   1.328678e+04  -7.141510e-14   2.000000e-01   8.955873e+03
16        17        2.516773e+05   1.285511e+04  -1.626754e-13   2.000000e-01   6.846314e+03
17        18        2.464064e+05   1.252720e+04   4.223843e-13   2.000000e-01   5.270959e+03
18        19        2.422601e+05   1.227652e+04  -3.567702e-13   2.000000e-01   4.146265e+03
19        20        2.388394e+05   1.207748e+04   4.834189e-13   2.000000e-01   3.420762e+03
20        21        2.360040e+05   1.191537e+04   3.964884e-13   2.000000e-01   2.835402e+03


****** Optimization stopping due to exceeding maximum number of iterations. ******
```

- **Checkpoint preserved:** `outputs/stage1/engine_output.exo` (unmodified copy of `work/stage1/engine_output.exo`, identical sha256 `58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8`), 21 Exodus time steps (time values 1…21 = iterations 0…20), nodal fields `control` and `topology`, 30,625 nodes / 27,648 elements. Verified (`outputs/stage1/stage1_results_verification.json`): saved state 0 control is uniform 0.15; all 21 control states finite in [0,1]; consecutive states differ (max change 0.2 = OC move limit); the last saved state (time step 21 = iteration 20) is the non-uniform iteration-20 design (control min 0, max 1, mean 0.1686; topology mean 0.1435). Pointer file for Session B: `work/stage1/CHECKPOINT.txt`.
- **Stage-1 compliance at iteration 20** (the value Stage 2's first evaluated compliance must reproduce): **F(X) = 2.360040e+05** (diagnostics; `opt_criteria_history.csv`: 2.3600395811001546e+05).
- The runtime did not write a separate `engine_restart.exo`; the restart states live in `engine_output.exo`, which is exactly the file the specification designates as the checkpoint (§7 of the spec: "the Stage-1 engine output file is the checkpoint").
- Final analyze output: `outputs/stage1/final_analyze_output.exo` = copy of `work/stage1/analyze_id_2_output_scenario_id_1/iteration20.exo` (fields Topology, displacement X/Y/Z).
- **Stage 2: NOT STARTED.** No Stage-2 deck, job script, translation or job exists. For Session B: Stage 2 must copy the checkpoint to `outputs/stage2/restart_input.exo`, read the **iteration-20** design from the **`control`** field (not `topology`) — in Exodus terms the last of the 21 time steps — and run `max_iterations 40`; its first evaluated compliance must equal 2.360040e+05.

## 6. Key output files (deliverables) and SHA-256
See `outputs/SHA256SUMS.txt` (covers every file under `outputs/` except itself; verified with `sha256sum -c`). Main entries:

| Path | SHA-256 |
|---|---|
| outputs/mesh.jou | 6b4c6c7c577cf5cc4bb1691079105e3555e7c5bd574f8d2e36c90a04a22c5f84 |
| outputs/mesh.exo | ceeed3bbaca41c84f1d568fdde66c4d810a685467fe83a27351dca70d851fcaf |
| outputs/mesh_verification.json | a46f101a05493db25356830563e68e3e9b8858d9343cf6f4498fa1cd4e3f705c |
| outputs/stage1/input_deck.i | 3d865e33ef7a86e05fe24111e4898259aa9cf1e72e811a29c9a0493869042e8d |
| outputs/stage1/job_script.sbatch | c826085d90a9862b4420615a8b2eace9faa0409748b969d1665b8dd0ac42743e |
| outputs/stage1/generated_config/interface.xml | 5a5069736df8b3ba8ff727c07ae73515f8803f069b460a3b24d7783dcb8ec669 |
| outputs/stage1/generated_config/engine_operations.xml | 09dabcc015dd9e0ab88dbe54a8a2f0496ff19b9abfe94bf5c46107d6238fa40d |
| outputs/stage1/generated_config/analyze_2_input_deck.xml | a6f7d5bf3d61607bec82781d3afad5231a493e602331ea7a3b54f7e9b3c162d5 |
| outputs/stage1/generated_config/analyze_helmholtz_input_deck.xml | c813b81a2c43cbac181b51c3ae12cad319473e7c2725afd29c2637fedec2dcbf |
| outputs/stage1/generated_config/mpirun.source | 5f45e199f30722f60934996cf4b58b4ce832972c71a3ef0cbe97ae2f6469f3bc |
| outputs/stage1/morphorm_oc_optimizer_diagnostics.txt | 4aaeaa78e77e9f065e3e0ab91d0205a13cdf600a7c76d9f8fc492b06092772f1 |
| outputs/stage1/engine_output.exo (checkpoint) | 58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8 |
| outputs/stage1/final_analyze_output.exo | 1baf67b8cb33f9878f9d64e92529248ab924c4b04f32a6ba9500526c40aa116d |
| outputs/stage1/run_logs/slurm_16165768.out | 13e78bbd37e062cbb68232c5d4799d83e18adc2826833c60e29c5fb18f89e867 |
| outputs/stage1/run_logs/morphorm_stage1.log | 24f51bf3b88158d9283abd03eca2f99f5418a3726091ea5e77b1dfc81695f555 |

## 7. Failures, retries, cancelled jobs, unresolved issues, deviations
- **No failed, cancelled or re-submitted Slurm jobs.** One job (16165768) was submitted and completed with exit 0.
- **Retry 1 (agent-host script bug, no deliverable affected):** the first run of `verify_mesh.py` crashed on a naive unique-coordinate count; fixed (snap to h-lattice) and rerun.
- **Retry 2 (deck translation, before any submission):** translation attempt 1 (`work/stage1/translation_attempt1/`) produced `OutputFrequency 5` in the engine output operation. Scratch translations (`work/scratch_xmlgen_checks/`, translation only) showed the documented output-block `output_frequency` controls only the analyze visualization frequency, while the study-level keyword `isosurface_output_frequency` (named in XMLGenerator's own INFO log, not documented in the User Manual) sets the engine output operation's OutputFrequency. `isosurface_output_frequency 1` was added to the study block so the engine output file stores every iteration; the result (21 saved states) confirms the locked requirement is met. This keyword changes no locked value; it only realizes the locked "every iteration / 21 saved states" requirement.
- **Retry 3 (result-verification script, no deliverable affected):** two checks in my own `verify_stage1_results.py` were wrong (expected the manual's iteration-per-row CSV layout and a separate `engine_restart.exo`); the runtime writes `opt_criteria_history.csv` as one row of 21 values (verified equal to the diagnostics) and stores restart states in `engine_output.exo`. Checks corrected and rerun (17/17 PASS).
- **Environment choice:** `OMP_NUM_THREADS=1` set in the job script (consistent with one processor per service); 8 CPUs were allocated per the frozen contract.
- **Deviations from the specification:** none. All locked values were used exactly; the generated configuration was verified setting by setting before submission.
- **Unresolved issues:** none for Stage 1.

## 8. Final artifact paths
- Mesh: `outputs/mesh.jou`, `outputs/mesh.exo`, `outputs/mesh_verification.json`
- Stage 1: `outputs/stage1/input_deck.i`, `outputs/stage1/job_script.sbatch`, `outputs/stage1/generated_config/` (8 generated files + `xmlgenerator.log` + `generated_config_verification.json`), `outputs/stage1/morphorm_oc_optimizer_diagnostics.txt`, `outputs/stage1/engine_output.exo` (checkpoint), `outputs/stage1/final_analyze_output.exo`, `outputs/stage1/stage1_results_verification.json`, `outputs/stage1/run_logs/` (Slurm stdout/stderr, Morphorm log, performer logs engine_1_0/analyze_2_1/analyze_helmholtz_2, criteria histories, sacct record, Cubit log)
- Manifest: `outputs/SHA256SUMS.txt`
- Scheduler evidence: `jobs/job_ids.txt`, `jobs/stage1_job.sbatch`, `jobs/submissions.log`, `jobs/sacct_16165768.txt`, `logs/stage1_16165768.out`, `logs/stage1_16165768.err`, `logs/env_check_agent_host.log`, `logs/slurm_check_agent_host.log`
- Working copies / provenance: `work/mesh/` (journal, mesh, Cubit log, verification), `work/stage1/` (run directory with all raw outputs incl. `analyze_id_2_output_scenario_id_1/iteration0..20.exo`, `translation_attempt1/`, `CHECKPOINT.txt`), `work/scratch_xmlgen_checks/` (translation-only keyword tests), `work/scripts/` (verify_mesh.py, verify_generated_config.py, verify_stage1_results.py), `work/manual_text/` (extracted manual text)
- Stage 2 artifacts: **none exist** (Stage 2 not started in this session).

Session A ended after Stage 1 (summary written UTC 2026-10-09T20:50:18Z).
