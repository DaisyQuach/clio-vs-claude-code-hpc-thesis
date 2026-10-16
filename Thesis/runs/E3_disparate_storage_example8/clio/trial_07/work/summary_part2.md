
## 6. Input deck and generated configuration
- Accepted deck: `work/run2/input_deck.i` -> `outputs/input_deck.i` (sha256 `36ab98d6...`). The first translation `work/run/input_deck.i` used a `begin filter 1 ... end filter` block: XMLGenerator exit 0, but the generated `analyze_helmholtz_input_deck.xml` contained no symmetry-plane sideset (`work/verify/xml_params_run1_filter_block.tsv`: MISSING symmetry). Per the manual's Table 2.5.12 equivalence the filter was re-declared with the study-level keywords (`filter_type helmholtz`, `filter_radius_absolute 0.15`, `boundary_sticking_penalty 1.0`, `symmetry_plane_location_names ss_sym`) in a clean directory `work/run2/`; `interface.xml`, `engine_operations.xml`, `analyze_2_input_deck.xml` and `mpirun.source` were byte-identical between the two translations and the Helmholtz file gained `Symmetry Plane Sides {ss_sym}`. `work/run` was never submitted.
- Locked settings and where each appears in `outputs/generated_config/` (record `outputs/generated_config/generated_config_verification.tsv`, from `xml_params.py`):

| Locked setting | Deck block | Generated configuration |
|---|---|---|
| E = 1.0, nu = 0.3 on block_1 | material 1, block 1 | `analyze_2_input_deck.xml` Material Models/material_1: Youngs Modulus 1.0, Poissons Ratio 0.3; Spatial Model/Domains/block_1 |
| SIMP exponent 3.0, minimum 1e-3; criterion minimum_ersatz 1e-3 | material_interpolation 1, criterion 1 | `analyze_2_input_deck.xml` Residual/Penalty Function Exponent 3.0, Minimum Value 1e-3; Criteria/My Objective/Penalty Function Exponent 3.0, Minimum Value 1e-3 |
| ns_fix u_x = u_y = u_z = 0 | boundary_condition 1 (nodeset) | Essential Boundary Conditions: Displacement X/Y/Z with ID 1/2/3, Sides ns_fix, Value 0 |
| ss_sym u_z = 0 through the sideset | boundary_condition 2 (`location_type sideset`) | Essential Boundary Conditions: Displacement Z with ID 4, Index 2, Sides ss_sym, Value 0 |
| load -1.0 in y on every node of ns_load | load 1 concentrated_load | Concentrated Loads: Dof 1, Value -1.0, Nodes ns_load |
| weighted-sum compliance objective, weight 1, analyze service | objective | `interface.xml` objective stage; `analyze_2_input_deck.xml` Criteria/My Objective Internal Elastic Energy |
| volume <= 0.15, less_than, engine service | constraint 1 | `interface.xml` Optimizer/Constraint NormalizedTargetValue 0.15 |
| density, initial 0.15 | study | `interface.xml` OptimizationVariables InitializationStage Initial Guess; `engine_operations.xml` initialize value 0.15 |
| OC, default tolerances, normalize_in_aggregator false, update_problem true, frequency 1 | service 1, study | `interface.xml` Package OC, OC tolerances 1e-4/1e-8/1e-8, ProblemUpdateFrequency 1; `engine_operations.xml` UpdateProblemFrequency 1 |
| max_iterations 50 | study | `interface.xml` Convergence/MaxIterations 50; `engine_operations.xml` MaxIterations 50 |
| Helmholtz radius 0.15, sticking penalty 1.0, symmetry plane ss_sym | study (legacy keywords) | `analyze_helmholtz_input_deck.xml` Length Scale 0.043301 (= 0.15/(2 sqrt 3), the generator's conversion of the absolute radius), Surface Length Scale 1.0, Symmetry Plane Sides {ss_sym} |
| engine + analyze, 1 processor each, no decomposition | service 1, 2 | `mpirun.source`: `-np 1` PlatoMain, `-np 1` analyze_MPMD (scenario), `-np 1` analyze_MPMD (Helmholtz filter service, generated automatically) |
| dispx dispy dispz from analyze; engine control/topology | output 1 | `analyze_2_input_deck.xml` Output Plottable {displacement_x, displacement_y, displacement_z}; `engine_input_deck.xml` output file engine_output |

## 7. Execution
- Commands (all after `source .../load_morphorm_e3.sh`; agent host unless stated): `cubit -batch -nographics -nojournal -input mesh.jou`; `python3 exo_summary.py ...`; `XMLGenerator input_deck.i` (in `work/run`, then `work/run2`); `python3 xml_params.py ...`; `sbatch --parsable jobs/morphorm_spc_run2.sbatch` (2026-10-13T19:28:46Z); `wait_job.sh 16253073 500 ...` (two waits); `sacct -j 16253073 ...`; `python3 diag_summary.py ...`; `python3 exo_summary.py` on `iteration50.exo` and `engine_output.exo`; `hash_outputs.sh`. Timeline with UTC stamps: `work/notes.log`.
- Slurm job **16253073** (`jobs/job_ids.txt`; script `jobs/morphorm_spc_run2.sbatch` = `outputs/job_script.sbatch`; resources exactly as `compute_resources.md`: hochhalter-np, 1 node, 1 task, 8 CPUs, 32G, 02:00:00). State COMPLETED, ExitCode 0:0, node notch273, Submit 13:28:46, Start 13:28:47, End 13:45:58 (local), Elapsed 00:17:11, MaxRSS 1.76 GB (`jobs/sacct_16253073.txt`). `module list` is recorded in `outputs/run_logs/slurm-16253073.out` (gcc/11.2.0, openmpi/5.0.3, morphorm/approved-runtime, cubit-edu/2026.8). The job ran `bash mpirun.source` in `work/run2/`; `morphorm_rc=0`. The optimization was not run on the agent host.
- Only this one job was submitted; none failed or was cancelled.

## 8. Stages completed and iterations reached
- Mesh generation, mesh verification, deck translation (twice; second accepted), generated-configuration verification, one uninterrupted optimization, output verification, delivery: all completed.
- `outputs/morphorm_oc_optimizer_diagnostics.txt`: 51 iteration rows, Iter 0 ... 50 (F(X) 2.654786e+06 at iteration 0 -> 1.044701e+05 at iteration 50; H1(X) about -1.6e-13 at iteration 50, i.e. the volume constraint is active and satisfied). Stopping message: `****** Optimization stopping due to exceeding maximum number of iterations. ******` (`outputs/run_logs/diagnostics_summary.json`). The required iteration count 50 was reached; no early convergence stop.
- `outputs/engine_output.exo`: 51 time steps, nodal fields `control` and `topology`, 15,925 nodes / 13,824 elements. `outputs/final_analyze_output.exo` (= `analyze_id_2_output_scenario_id_1/iteration50.exo`): time 50, nodal `Topology` (min 1.0e-8, max 0.939), `displacement X/Y/Z`, element `My Objective`.

## 9. Key output files (all SHA-256 in `outputs/SHA256SUMS.txt`, 32 entries)
| File | SHA-256 |
|---|---|
| outputs/mesh.jou | cf87de245decc55fbe0fa8977606ee4fa4efc57ea9114ee0ec9db59074548ae4 |
| outputs/mesh.exo | 9f73c9c32e2b53c513e9235311a866b693fe63c29dfbc80d7d8c6646fd351571 |
| outputs/mesh_verification.json | d37ca675238200df81f9cfb4b3243d5560df87ccaae1764061504a6c2998d619 |
| outputs/input_deck.i | 36ab98d6068668e476eb438c986d1a01a5148f2c23fff81af7f2a9df3983d5c2 |
| outputs/job_script.sbatch | b90d1abf830ee97bbe88d072559e265d32bb71340933643983cf19a46f490f9d |
| outputs/generated_config/interface.xml | 2f545669f80885d182291e9aad47d74baf8403082364f79f67542f653a616885 |
| outputs/generated_config/analyze_2_input_deck.xml | 9bc13ac9c61c0d8b3c7c73b5c0bce38e31c7d35b53e45483c2fd5238bea222e8 |
| outputs/generated_config/analyze_helmholtz_input_deck.xml | e0b190ab3e8c71334d7b7ec5f0567dbcdae40f7a371b943a553d6eb54fae5436 |
| outputs/generated_config/mpirun.source | 5f45e199f30722f60934996cf4b58b4ce832972c71a3ef0cbe97ae2f6469f3bc |
| outputs/morphorm_oc_optimizer_diagnostics.txt | 5bf3294ab40a1a55925134eb0ef493c7cb725e0964ae54cb3ce1ee62ae18e4f4 |
| outputs/engine_output.exo | 9b053a7c2d14ab5200f97efc1b927f3c6a5c787e754ddbd16e6212a1a988f7c9 |
| outputs/final_analyze_output.exo | 7b9510366799145234e5d149e7916485b20f3ed58138e1f7d6d62f12afb7ceb7 |

## 10. Failures, retries, cancelled jobs, deviations
- Failed, retried or cancelled jobs: none. Deviations from the specification: none; every locked value was realized and verified in the generated configuration, and the run reached iteration 50 with the iteration-cap stop.
- Noted, not deviations: (a) the filter-block form of the deck did not propagate `symmetry_plane_location_names` into the generated Helmholtz configuration; the accepted deck uses the manual's equivalent study-level keyword form (section 6). (b) The manual says essential boundary conditions must always be applied to nodesets, yet `location_type sideset` for `ss_sym` was accepted by XMLGenerator and appears in the generated analyze configuration as `Sides ss_sym`, exactly as the specification requires. (c) The control snapshot lacks the `./.gitignore` listed in its checksum file. (d) `generated_config_verification.tsv` reports MISSING for value-only search terms (`ss_sym`, `ns_fix`, `ns_load`, `concentrated`, `displacement`, `algorithm`) because `xml_params.py` matches parameter names; those values are present (section 6 and the files themselves).
- Unresolved issues: none.

## 11. Final artifact paths (relative to the trial root)
`outputs/mesh.jou`, `outputs/mesh.exo`, `outputs/mesh_verification.json`, `outputs/input_deck.i`, `outputs/job_script.sbatch`, `outputs/generated_config/` (8 XMLGenerator files + `generated_config_verification.tsv`), `outputs/morphorm_oc_optimizer_diagnostics.txt`, `outputs/engine_output.exo`, `outputs/final_analyze_output.exo`, `outputs/opt_criteria_history.csv`, `outputs/run_logs/` (Slurm stdout/stderr, `morphorm_run.log`, performer logs, XMLGenerator and Cubit logs, bundled-check summaries), `outputs/SHA256SUMS.txt`, `jobs/job_ids.txt`, `jobs/morphorm_spc_run2.sbatch`, `jobs/sacct_16253073.txt`, `jobs/job_submissions.tsv`, `work/run_summary.md`, `work/notes.log`, `provenance/sources_searched.tsv`, `provenance/artifact_selections.md`, `provenance/node_local_placement.txt`, `provenance/control_and_source_versions.txt`, `staging-manifest/staged_files.tsv`, `staging-manifest/globus_transfers.tsv`, `staging-manifest/returned_files.tsv`. Working copies: `work/mesh/`, `work/run/` (first translation, not run), `work/run2/` (accepted run directory), `work/verify/`, `work/manual/`.
