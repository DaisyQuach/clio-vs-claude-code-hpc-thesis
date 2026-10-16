# Run Summary — Trial E1-example8-baseline-02

## 1. Trial identifier and assigned workflow

- Trial identifier (THESIS_TRIAL_ID): `E1-example8-baseline-02`
- Frozen configuration: `FROZEN-EX8-v1` (hash `cf15ac52f018defeba40afbedc910d757c08609c6a9adaa4a1b0e0428a570b4d`)
- Assigned workflow: Frozen Workflow EX8 — half cantilever (2 × 1 × 0.5 brick, symmetry plane z = 0.5) with a Helmholtz symmetry-plane filter; minimum-compliance density topology optimization, OC optimizer, exactly 50 iterations.
- Agent host: Slurm job 16159111 on node notch351 (account/partition hochhalter-np, 8 CPUs, 32 GB, 02:00:00). Session start ≈ 2026-10-09T12:46Z; summary written 2026-10-09T13:07Z.
- Software: approved interface `source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/common/scripts/load_approved_software.sh` (SHA-256 of that script: `38848816a3798fbf939f235121898aa7624077e51a13716a1a03cc0e1d7843c0`). After sourcing, `module list` shows chpc/1.0, gcc/11.2.0, openmpi/5.0.3, morphorm/approved-runtime, cubit-edu/2026.8 (agent-host record: `logs/agent_host_software_load_check.log`; job record: `outputs/run_logs/slurm-16159127.out`). Only the two manuals in `agent_inputs/manuals/` were consulted (text extracted with `pdftotext -layout` into `work/manual_text/` for reading).

## 2. Mesh

- Generator: Coreform Cubit 2026.8 in batch mode on the agent host (permitted by compute_resources.md), command run from `work/mesh/`:
  `cubit -batch -nographics -nojournal -input mesh.jou` (exit 0). Start 2026-10-09T12:51:20Z, end 2026-10-09T12:51:26Z. Log: `work/mesh/cubit_run.log` (copied to `outputs/run_logs/cubit_run.log`).
- Journal: `work/mesh/mesh.jou` → deliverable `outputs/mesh.jou`. Procedure: `brick x 2.0 y 1.0 z 0.5`, translate by (1.0, 0.5, 0.25) so the corner is at the origin; curve intervals 48 (x-edges), 24 (y-edges), 12 (z-edges); `volume 1 scheme map`; `mesh volume 1`; block 1 = volume 1 named `block_1`, element type HEX8; nodeset 1 `ns_fix` = surface at x = 0; nodeset 2 `ns_load` = curve at x = 2, y = 0; sideset 1 `ss_sym` = surface at z = 0.5; `export mesh ... dimension 3 overwrite`.
- Mesh file: `work/mesh/mesh.exo` (SHA-256 `67a4ef5385e23dd80122b6cb86abf6cef40665aa18b8a40875fdb1fe32412880`), copied unchanged to the run directory `work/run1/mesh.exo` and to `outputs/mesh.exo` (byte-identical, verified with `cmp`).
- Verification (before any optimization, 2026-10-09T12:51Z): `python3 -I work/verify/verify_mesh.py work/mesh/mesh.exo` using the runtime's python3/netCDF4; record `work/verify/mesh_verification.json` → `outputs/mesh_verification.json`. Result: all 27 checks pass.

| Item | Locked | Measured |
|---|---|---|
| Dimension | 3 | 3 |
| Elements / nodes | 13,824 / 15,925 | 13,824 / 15,925 |
| Element type, block | HEX8, one block `block_1` with every element | HEX8, 1 block `block_1`, 13,824 elements |
| Bounding box | [0,2]×[0,1]×[0,0.5] | [0.0,2.0]×[0.0,1.0]×[0.0,0.5] |
| Uniform h | 1/24 | all element edges = 1/24 (max deviation < 1e-9); 49×25×13 distinct coordinates |
| `ns_fix` | 325 nodes on x = 0 | 325 nodes, all at x = 0, and every x = 0 node included |
| `ns_load` | 13 nodes on x = 2, y = 0, z ∈ [0,0.5] | 13 nodes at x = 2, y = 0, z from 0.0 to 0.5 |
| `ss_sym` | 1,152 faces on z = 0.5 | 1,152 unique faces, every face node at z = 0.5 |

## 3. Input deck and where each locked setting appears in the generated runtime configuration

- Accepted deck: `work/deck/input_deck.i` = `work/run1/input_deck.i` → `outputs/input_deck.i` (SHA-256 `eaffead3cdc3f30ac929a431f02f99f26bb2416a5d8bb88328648b8b013a7f48`).
- Translation: `XMLGenerator input_deck.i` in `work/run1/` (exit 0), 2026-10-09T12:52:55Z–12:52:58Z; log `work/run1/xmlgenerator.log` → `outputs/run_logs/xmlgenerator.log`. Generated files (all copied to `outputs/generated_config/`): `interface.xml`, `analyze_2_input_deck.xml`, `analyze_2_operations.xml`, `analyze_helmholtz_input_deck.xml`, `analyze_helmholtz_operations.xml`, `engine_input_deck.xml`, `engine_operations.xml`, `mpirun.source`.
- Generated-configuration verification (before submission, 2026-10-09T12:54Z): `python3 -I work/verify/verify_generated_config.py work/run1` → `work/verify/generated_config_verification.json` (copy in `outputs/verification/`). Result: all 74 checks pass.

| Locked setting | Deck (block / keyword) | Generated configuration (file: element → value) |
|---|---|---|
| Engine service, 1 processor, `update_problem true`, `update_problem_frequency 1` | `service 1`: `code engine`, `number_processors 1`, `update_problem true`, `update_problem_frequency 1` | `interface.xml`: Performer engine_1 (code engine); Optimizer/Options/ProblemUpdateFrequency = 1; UpdateProblemStage = "Update Problem". `engine_operations.xml`: Update Problem/UpdateProblemFrequency = 1. `mpirun.source`: `-np 1 ... PlatoMain engine_input_deck.xml` |
| Analyze service, 1 processor | `service 2`: `code analyze`, `number_processors 1` | `interface.xml`: Performer analyze_2 (analyze); `mpirun.source`: `-np 1 ... analyze_MPMD --input-config=analyze_2_input_deck.xml`; Helmholtz performer analyze_helmholtz also `-np 1`. No decomposition step in `mpirun.source`. |
| Mechanical scenario, 3-D | `scenario 1`: `type mechanical`, `dimensions 3` | `analyze_2_input_deck.xml`: Physics = Mechanical, PDE Constraint = Elliptic, Spatial Dimension = 3, Input Mesh = mesh.exo |
| Material E = 1.0, ν = 0.3 on `block_1` | `material 1`: `isotropic_elastic`, `youngs_modulus 1.0`, `poissons_ratio 0.3`; `block 1`: `name block_1`, `material_id 1` | `analyze_2_input_deck.xml`: Material Models/material_1/Isotropic Linear Elastic: Youngs Modulus = 1.0, Poissons Ratio = 0.3; Spatial Model/Domains/block_1: Element Block = block_1, Material Model = material_1 (only domain) |
| Fixed support `ns_fix` u_x = u_y = u_z = 0 | `boundary_condition 1`: `fixed_value`, nodeset `ns_fix`, `dispx dispy dispz`, `0.0 0.0 0.0` | `analyze_2_input_deck.xml`: Essential Boundary Conditions "Displacement X with ID 1" (Index 0), "Displacement Y with ID 2" (Index 1), "Displacement Z with ID 3" (Index 2): Type Fixed Value, Sides ns_fix, Value 0.0 |
| Symmetry `ss_sym` u_z = 0 through the sideset | `boundary_condition 2`: `fixed_value`, `location_type sideset`, `ss_sym`, `dispz`, `0.0` | `analyze_2_input_deck.xml`: "Displacement Z with ID 4": Type Fixed Value, Index 2, Sides ss_sym, Value 0.0 |
| Load: concentrated, direction y, −1.0 per node on `ns_load`; no other loads | `load 1`: `concentrated_load`, nodeset `ns_load`, `direction y`, `value -1.0` | `analyze_2_input_deck.xml`: Concentrated Loads/"Concentrated Load with ID 0": Dof = 1 (y), Value = −1.0, Nodes = ns_load; "Mechanical Natural Boundary Conditions" list empty (no tractions); no body loads |
| Objective: weighted sum, single compliance criterion, weight 1, analyze service | `criterion 1`: `mechanical_compliance`; `objective 1`: `weighted_sum`, `criterion_ids 1`, `service_ids 2`, `scenario_ids 1`, `weights 1` | `analyze_2_input_deck.xml`: Criteria/"My Objective": Scalar Function, Scalar Function Type = Internal Elastic Energy, Domains {block_1}. `interface.xml`: stage "Compute Objective Value" operation "Compute Objective Value" on analyze_2; `engine_operations.xml`: Aggregate Data with a single Weight 1 |
| Compliance `minimum_ersatz_material_value 1e-3` | `criterion 1`: `minimum_ersatz_material_value 1e-3` | `analyze_2_input_deck.xml`: Criteria/My Objective/Penalty Function: Type SIMP, Exponent 3.0, Minimum Value 1e-3 |
| SIMP single phase, exponent 3.0, minimum 1e-3 | `material_interpolation 1`: `single_phase`, `simp`, `penalty_exponent 3.0`, `minimum_value 1e-3`; referenced by `residual 1` | `analyze_2_input_deck.xml`: Residual/Mechanical Residual: Material Interpolation Model = Single-Phase, Response = Linear, Penalty Function Type SIMP, Exponent 3.0, Minimum Value 1e-3 |
| Constraint volume ≤ 0.15, `less_than`, engine service | `criterion 2`: `volume`; `constraint 1`: `criterion_id 2`, `relative_target 0.15`, `type less_than`, `service_id 1` | `interface.xml`: Optimizer/Constraint: NormalizedTargetValue = 0.15, ReferenceValueName = Design Volume, one Constraint block; stage "Compute Constraint Value 1" operation on engine_1 (`engine_operations.xml` ComputeVolume) |
| Density discretization, uniform initial density 0.15 | `study`: `discretization density`, `initialize_method uniform`, `initial_density_value 0.15` | `engine_operations.xml`: Initialize Field Method Uniform, Value 0.15; SetLower/UpperBounds Discretization density; `interface.xml` BoundConstraint 0.0–1.0 |
| OC optimizer, default tolerances, `normalize_in_aggregator false` | `study`: `optimization_algorithm oc`, `normalize_in_aggregator false` | `interface.xml`: Optimizer/Package = OC; OCControlStagnationTolerance 1e-4, OCObjectiveStagnationTolerance 1e-8, OCGradientTolerance 1e-8 (runtime defaults); `engine_operations.xml` Aggregate Data has no normalization element |
| `max_iterations 50` | `study`: `max_iterations 50` | `interface.xml`: Optimizer/Convergence/MaxIterations = 50; `engine_operations.xml`: PlatoMainOutput/MaxIterations = 50 |
| Helmholtz filter, absolute radius 0.15 | `study`: `filter_type helmholtz`, `filter_radius_absolute 0.15` | `analyze_helmholtz_input_deck.xml`: Physics = Helmholtz Filter; Parameters/Length Scale = 0.043301 (= 0.15 / (2√3), the generator's radius-to-length-scale conversion; verified numerically). Filter performer analyze_helmholtz applies "Filter Control"/"Filter Gradient" in every objective and constraint stage (`interface.xml`), `FilteredName` = Topology |
| Boundary-sticking penalty 1.0 | `study`: `boundary_sticking_penalty 1.0` | `analyze_helmholtz_input_deck.xml`: Parameters/Surface Length Scale = 1.0 (confirmed deck-driven, see §7 attempt 3) |
| `ss_sym` declared as filter symmetry plane | `study`: `symmetry_plane_location_names ss_sym` | `analyze_helmholtz_input_deck.xml`: Parameters/Symmetry Plane Sides = {ss_sym} |
| Output dispx, dispy, dispz from analyze; engine output of control and topology | `output 1`: `service_id 2`, `data dispx dispy dispz` | `analyze_2_input_deck.xml`: Output/Plottable = {displacement_x, displacement_y, displacement_z}; `analyze_2_operations.xml` Visualization OutputFrequency 1; `interface.xml` stage "Output To File": PlatoMainOutput inputs topology and control; `engine_input_deck.xml` output file engine_output |
| Mesh | `mesh`: `name mesh.exo` | Input Mesh = mesh.exo in both analyze decks and `engine_input_deck.xml` |

Notes on runtime defaults left untouched: linear solver tacho; engine PlatoMainOutput OutputFrequency 5 (the generator's `isosurface_output_frequency` default) — engine_output.exo nevertheless contains 51 time steps (iterations 0–50); engine volume evaluation uses the linear (exponent 1, minimum 0) volume measure.

## 4. Execution

Commands used (in order; all shells sourced the approved software interface first):
1. `pdftotext -layout agent_inputs/manuals/*.pdf work/manual_text/*.txt` (reading the permitted manuals).
2. `source .../load_approved_software.sh; module list; which cubit XMLGenerator PlatoMain analyze_MPMD mpiexec python3` → `logs/agent_host_software_load_check.log`.
3. `cd work/mesh && cubit -batch -nographics -nojournal -input mesh.jou` (exit 0).
4. `python3 -I work/verify/verify_mesh.py work/mesh/mesh.exo > work/verify/mesh_verification.json` (exit 0, all pass).
5. Translation attempts (see §7): `XMLGenerator input_deck.i` in `work/attempts/translate_attempt1_filter_block/` (12:51:38Z), `work/attempts/translate_attempt2_legacy_filter/` (12:52:27Z), `work/attempts/translate_attempt3_diagnostic_sticking_0p5/` (12:52Z, diagnostic only).
6. Accepted translation: `cp work/deck/input_deck.i work/run1/; cp work/mesh/mesh.exo work/run1/; cd work/run1 && XMLGenerator input_deck.i` (exit 0, 12:52:55Z–12:52:58Z).
7. `python3 -I work/verify/verify_generated_config.py work/run1 > work/verify/generated_config_verification.json` (exit 0, 74/74 pass, 12:54Z).
8. `sbatch jobs/job_script.sbatch` → "Submitted batch job 16159127" (submit 2026-10-09T12:54:49Z). Job ID appended to `jobs/job_ids.txt`; submission note in `jobs/submissions.log`.
9. Inside the job: `source .../load_approved_software.sh; module list; cd work/run1; bash mpirun.source > morphorm_run.log 2>&1` (job script `jobs/job_script.sbatch` = `outputs/job_script.sbatch`; `#SBATCH --account=hochhalter-np --partition=hochhalter-np --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=32G --time=02:00:00`, no GPU; OMP_NUM_THREADS=1).
10. Polling: `squeue -j 16159127`, `tail work/run1/morphorm_oc_optimizer_diagnostics.txt`.
11. `sacct -j 16159127 --format=JobID,JobName,State,ExitCode,Submit,Start,End,Elapsed,AllocCPUS,ReqMem,MaxRSS,NodeList -P > jobs/sacct_16159127.txt`.
12. `python3 -I work/verify/verify_results.py work/run1 > work/verify/results_verification.json` (exit 0, 35/35 pass).
13. Deliverable assembly with `cp -p` into `outputs/`, then `cd outputs && find . -type f ! -name SHA256SUMS.txt | sort | xargs sha256sum > SHA256SUMS.txt && sha256sum -c SHA256SUMS.txt`.

Slurm jobs submitted in this trial (also in `jobs/job_ids.txt`):

| Job ID | Script | Purpose | State | ExitCode | Submit (UTC) | Start (UTC) | End (UTC) | Elapsed | Node | MaxRSS |
|---|---|---|---|---|---|---|---|---|---|---|
| 16159127 | `jobs/job_script.sbatch` | accepted 50-iteration optimization, run dir `work/run1` | COMPLETED | 0:0 | 2026-10-09T12:54:49Z | 2026-10-09T12:54:56Z | 2026-10-09T13:04:38Z | 00:09:42 | notch351 | 1,388,664 K (batch step) |

(sacct prints local time, 06:54:49 MDT = 12:54:49 UTC.) Morphorm itself ran 2026-10-09T12:55:01Z–13:04:38Z, rc = 0. Scheduler stdout/stderr: `logs/slurm-16159127.out`, `logs/slurm-16159127.err` (empty), copies in `outputs/run_logs/`. The agent-host allocation is job 16159111 (not submitted by the agent; not listed in job_ids.txt).

## 5. Completed stages, iteration counts, stopping message

- Mesh generation: complete. Mesh verification: complete, all pass. Deck translation: complete. Generated-configuration verification: complete, all pass. Optimization job: complete.
- Iterations reached: the OC diagnostics (`outputs/morphorm_oc_optimizer_diagnostics.txt`) list iterations 0 through 50 (51 rows, F-count 1–51), i.e. the iteration cap `max_iterations 50` was reached. `engine_output.exo` holds 51 time steps (iterations 0–50); the analyze service wrote `iteration0.exo` … `iteration50.exo` (51 files) in `work/run1/analyze_id_2_output_scenario_id_1/`.
- Optimizer stopping message (last line of the diagnostics file): `****** Optimization stopping due to exceeding maximum number of iterations. ******` — the run did not stop early by any convergence criterion (no "converged" or "failed" message).
- Diagnostics at the ends of the history (F(X) = compliance objective, H1(X) = normalized volume constraint):

| Iter | F-count | F(X) | Norm(F') | H1(X) | abs(dX) | abs(dF) |
|---|---|---|---|---|---|---|
| 0 | 1 | 2.654786e+06 | 4.024583e+05 | −1.564817e−02 | 1.500000e−01 | 1.797693e+308 |
| 1 | 2 | 6.367926e+05 | 9.968606e+04 | 5.104328e−02 | 2.000000e−01 | 2.017994e+06 |
| 49 | 50 | 1.045363e+05 | 7.039483e+03 | 8.021361e−15 | 1.138896e−01 | 7.131218e+01 |
| 50 | 51 | 1.044701e+05 | 7.033815e+03 | −1.628697e−13 | 1.142971e−01 | 6.611695e+01 |

- Final-design sanity (from `outputs/verification/results_verification.json`): final `topology` field in [1.0e−08, 0.939], mean 0.1571 (volume constraint active, H1 ≈ 0); `final_analyze_output.exo` (iteration 50) contains nodal `Topology`, `displacement X/Y/Z` and element `My Objective`; u_y range [−21941.2, 0.0], all finite; run log and performer logs contain no error lines.

## 6. Key output files (deliverables in `outputs/`) with SHA-256

Full list in `outputs/SHA256SUMS.txt` (30 files, produced with `sha256sum`, verified with `sha256sum -c`).

| Deliverable | SHA-256 |
|---|---|
| `outputs/mesh.jou` | 30b658498ac6846313a69fed52fada86e41607c6510b5057b95407e5f918f3b9 |
| `outputs/mesh.exo` | 67a4ef5385e23dd80122b6cb86abf6cef40665aa18b8a40875fdb1fe32412880 |
| `outputs/mesh_verification.json` | f5535e8eb2c22496af6dd38d8e9c9709ec9b8e85d4282c46a7b8a5c6149c7fae |
| `outputs/input_deck.i` | eaffead3cdc3f30ac929a431f02f99f26bb2416a5d8bb88328648b8b013a7f48 |
| `outputs/job_script.sbatch` | a351a1ad9250736bb05ba773cfc4cba1401cf006c16bed0f71f2e52edf48f50d |
| `outputs/generated_config/interface.xml` | 2f545669f80885d182291e9aad47d74baf8403082364f79f67542f653a616885 |
| `outputs/generated_config/analyze_2_input_deck.xml` | 062429a12242027c1f6ec7871f893ae120475fbd547f64840f9fcd0158a4a39c |
| `outputs/generated_config/analyze_2_operations.xml` | fbabf1a1c037533ce5dc1b1ba6a97ce9d70a795c1128735196a3e624aa73efa0 |
| `outputs/generated_config/analyze_helmholtz_input_deck.xml` | e0b190ab3e8c71334d7b7ec5f0567dbcdae40f7a371b943a553d6eb54fae5436 |
| `outputs/generated_config/analyze_helmholtz_operations.xml` | 402ffc30789914bd0c1c7bf429aa2f08ea22b0040960d015b9c71fd716404854 |
| `outputs/generated_config/engine_input_deck.xml` | 7f3edc06119d4155981b3861c2c2263f268e6a3f56f7577cc0aa202f3b35169a |
| `outputs/generated_config/engine_operations.xml` | c5b07640e3f1427a5f763631a2f7f9c3ec1ea54e97160106efe598afc0c67c1b |
| `outputs/generated_config/mpirun.source` | 5f45e199f30722f60934996cf4b58b4ce832972c71a3ef0cbe97ae2f6469f3bc |
| `outputs/morphorm_oc_optimizer_diagnostics.txt` | 5bf3294ab40a1a55925134eb0ef493c7cb725e0964ae54cb3ce1ee62ae18e4f4 |
| `outputs/engine_output.exo` | 1aaed1e511062be4f851104be922563fc2efbb3f735cf87f3db19a779c05f200 |
| `outputs/final_analyze_output.exo` (= `work/run1/analyze_id_2_output_scenario_id_1/iteration50.exo`) | 37e132d17c1295ccb662ebba04d6217e1dc77ac03c443ac32103cde40227dca0 |
| `outputs/run_logs/slurm-16159127.out` | 7019476aacbf8aa4b0cfaa5cf52ffea95c2d26b614b53258dbf5260c3ac76de9 |
| `outputs/run_logs/slurm-16159127.err` (empty) | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| `outputs/run_logs/morphorm_run.log` | 24f51bf3b88158d9283abd03eca2f99f5418a3726091ea5e77b1dfc81695f555 |
| `outputs/run_logs/performer_log_engine_1_0.txt` | 0251658e45de22150ad3d5052e7ad8107c075731e60eae010c11292552d6c5c7 |
| `outputs/run_logs/performer_log_analyze_2_1.txt` | 3671439145de03e224a066ecb12822a827f277e50abd26c86d93766780af154e |
| `outputs/run_logs/performer_log_analyze_helmholtz_2.txt` | 3f9a09efa4481ab4e4c1da0dc51ada34af0c1a5e70882b1f6988bac8d0f04bec |
| `outputs/run_logs/xmlgenerator.log` | 8521bff2e3e3ec526f8537591ffac524b362510e8dc4a9ac7e273839c40cb712 |
| `outputs/run_logs/cubit_run.log` | 3573248c28c50691cb083e5202d20f647834e568376ac64a04e3f3252c80d56b |
| `outputs/run_logs/opt_criteria_history.csv` | fc58edec337c12168c1d4a61bd25900d1cc46c334323e0e1432061d82c9c24d0 |
| `outputs/run_logs/iteration50_criteria_history.csv` | fc58edec337c12168c1d4a61bd25900d1cc46c334323e0e1432061d82c9c24d0 |
| `outputs/run_logs/sacct_16159127.txt` | c58e12f7b905a02e8a662bc808f9c4d024c9d5d1f7af3e9ea369b53f175c2f30 |
| `outputs/verification/generated_config_verification.json` | 0e915ad262c0dfe5380fb8a95ebe72f689cab3553ce1c805268482d371592372 |
| `outputs/verification/results_verification.json` | 2f4706e02e14dadb87f71d594b4e8aec8201ce7ea4ad53a06eac1c786f5e7d08 |
| `outputs/.gitkeep` (pre-existing researcher placeholder, left in place) | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |

The performer log files are Morphorm's per-rank logs written as `engine_1_0`, `analyze_2_1`, `analyze_helmholtz_2` in the run directory; they were copied with a `performer_log_` prefix and `.txt` suffix. No deliverable was overwritten by a later attempt; `outputs/` was populated once, after the accepted run.

## 7. Failures, retries, cancelled jobs, unresolved issues, deviations

- **Translation attempt 1 (not used for any run):** the deck used the manual's recommended first-class `begin filter 1 … end filter` block (`type helmholtz`, `radius_absolute 0.15`, `boundary_sticking_penalty 1.0`, `symmetry_plane_location_names ss_sym`, referenced by `filter_ids 1`). XMLGenerator exited 0, but the generated `analyze_helmholtz_input_deck.xml` contained only Length Scale 0.043301 and Surface Length Scale 1.0 — **the symmetry-plane sideset was missing**. Per the specification such a run would not satisfy the frozen workflow, so no job was submitted from it. Files preserved in `work/attempts/translate_attempt1_filter_block/`.
- **Translation attempt 2 (adopted):** the same deck with the filter expressed through the manual's equivalent legacy study-level keywords (`filter_type helmholtz`, `filter_radius_absolute 0.15`, `boundary_sticking_penalty 1.0`, `symmetry_plane_location_names ss_sym` inside `begin study`). Generated Helmholtz configuration now contains Length Scale 0.043301, Surface Length Scale 1.0 and Symmetry Plane Sides {ss_sym}; all other generated files are byte-identical to attempt 1. Preserved in `work/attempts/translate_attempt2_legacy_filter/`; this deck became `work/deck/input_deck.i` and was re-translated in `work/run1/` (identical output) for the accepted run.
- **Translation attempt 3 (diagnostic only, never run):** XMLGenerator printed `INFO: Using default value of "1.0" for parameter "boundary_sticking_penalty"`, which made it unclear whether the 1.0 came from the deck. A copy of the attempt-2 deck with `boundary_sticking_penalty 0.5` was translated in `work/attempts/translate_attempt3_diagnostic_sticking_0p5/`; it produced Surface Length Scale 0.5, proving the deck keyword is honored. The accepted run uses 1.0 as locked.
- **Verification-script fixes (no effect on the run):** two of my own checker scripts initially mis-parsed names (the generated-config checker double-counted the nested penalty "Type" key as a second criterion; the results checker expected `displacement_x` but the analyze output names the field `displacement X`). Both were corrected and re-run; the generated configuration and run outputs were unchanged.
- No job failed, no job was cancelled, and only one Slurm job was submitted. The optimization ran uninterrupted for 50 iterations in a single job (elapsed 9 min 42 s).
- Deviations from the specification: **none**. Every locked value is present in the executed configuration (§3). The one interpretive point: the manual states that Dirichlet conditions are applied to nodesets, but the specification locks the symmetry condition "applied through the sideset"; the deck therefore uses `location_type sideset` with `location_name ss_sym`, XMLGenerator accepted it, and the generated analyze configuration carries the u_z = 0 condition with Sides = ss_sym exactly as the generator wrote it. Runtime defaults not locked by the specification (tacho linear solver, OC tolerances, engine PlatoMainOutput frequency 5) were left at their defaults.
- Unresolved issues: none.

## 8. Final artifact paths (relative to the trial root)

- `outputs/mesh.jou`, `outputs/mesh.exo`, `outputs/mesh_verification.json`
- `outputs/input_deck.i`, `outputs/job_script.sbatch`
- `outputs/generated_config/{interface.xml, analyze_2_input_deck.xml, analyze_2_operations.xml, analyze_helmholtz_input_deck.xml, analyze_helmholtz_operations.xml, engine_input_deck.xml, engine_operations.xml, mpirun.source}`
- `outputs/morphorm_oc_optimizer_diagnostics.txt`, `outputs/engine_output.exo`, `outputs/final_analyze_output.exo`
- `outputs/run_logs/` (Slurm stdout/stderr, Morphorm run log, three performer logs, XMLGenerator log, Cubit log, criteria-history CSVs, sacct record)
- `outputs/verification/{generated_config_verification.json, results_verification.json}`
- `outputs/SHA256SUMS.txt`
- `jobs/job_ids.txt`, `jobs/job_script.sbatch`, `jobs/submissions.log`, `jobs/sacct_16159127.txt`
- `logs/slurm-16159127.out`, `logs/slurm-16159127.err`, `logs/agent_host_software_load_check.log`
- `work/run1/` (complete accepted run directory, including all 51 `iteration*.exo` files), `work/mesh/`, `work/deck/`, `work/verify/` (verification scripts and records), `work/attempts/` (translation attempts 1–3), `work/manual_text/` (extracted manual text), `work/run_summary.md` (this file)
