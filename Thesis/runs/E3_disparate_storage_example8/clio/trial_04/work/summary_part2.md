
## 7. Execution
Commands (agent host, all after `source …/load_morphorm_e3.sh`; UTC):
1. 17:51:04 `record_node_placement.sh`; `sha256sum -c catalog/checksums.sha256`; `verify_collection.sh <candidate archive>`; `find <candidate archive> -type f`
2. 17:51:14 `globus ls 6dcea62e-130d-47a9-8b77-80fba6f58693:/ --recursive --long`
3. 17:51:34–17:52:48 `globus_stage_file.sh <9 paths>`; 17:52:36 `stage_file.sh` ×2 (Example 7 deck and journal)
4. 17:5x `pdftotext -layout Morphorm_User_Manual.pdf work/manual/user_manual.txt`; `grep -n`/`sed -n` on the filter, boundary-condition, output and study sections
5. 17:54:11 `cubit -batch -nographics -nojournal -input mesh.jou` (in `work/mesh/`); 17:54:27 `python3 exo_summary.py work/mesh/mesh.exo --expect …`
6. 17:54:50 `XMLGenerator input_deck.i` (attempt 1, filter-block form, `work/run_attempt1_filter_block/`, not run); 17:55:37 `XMLGenerator input_deck.i` (accepted, `work/run/`); `python3 xml_params.py work/run …`
7. 17:56:25 `sbatch --parsable jobs/morphorm_spc_run.sbatch` → job **16247887**; waits with `wait_job.sh 16247887 500 …` (two calls)
8. 18:07:01 `sacct -j 16247887 … -P` → `jobs/sacct_16247887.txt`; `diag_summary.py`, `exo_summary.py` on the outputs; copies to `outputs/`; `hash_outputs.sh`; `sha256sum -c outputs/SHA256SUMS.txt`

Slurm jobs (`jobs/job_ids.txt`, `jobs/submissions.tsv`):
| Job ID | Script | Resources | State | ExitCode | Submit / Start / End (local) | Elapsed | Node |
|---|---|---|---|---|---|---|---|
| 16247887 | `jobs/morphorm_spc_run.sbatch` (= `outputs/job_script.sbatch`) | account/partition hochhalter-np, 1 node, 1 task, 8 cpus, 32G, 02:00:00, no GPU | COMPLETED | 0:0 | 11:56:25 / 11:56:54 / 12:06:40 | 00:09:46 | notch351 |

The job sourced the approved loader (module list recorded in `outputs/run_logs/morphorm_16247887.out`: gcc/11.2.0, openmpi/5.0.3, morphorm/approved-runtime, cubit-edu/2026.8), hashed its inputs, ran `bash mpirun.source` in `work/run/` (utc 17:57:07Z–18:06:40Z, mpirun exit 0), and read only the trial workspace and the approved interface. Scheduler stderr is empty. Only one job was submitted; none failed or was cancelled.

## 8. Completed stages and iteration count
- Optimizer diagnostics (`outputs/morphorm_oc_optimizer_diagnostics.txt`, `diag_summary.py` record in `outputs/run_logs/diagnostics_verification.json`): 51 iteration rows, iterations 0 … **50**, objective 2.654786e+06 at iteration 0 → 1.044701e+05 at iteration 50; constraint H1(X) ≈ 0 (−1.63e-13) at the last row.
- Stopping message: `****** Optimization stopping due to exceeding maximum number of iterations. ******` — the run reached the locked cap of 50 iterations; no early convergence stop.
- `outputs/engine_output.exo`: 51 time steps, nodal fields `control` and `topology` (last step: topology ∈ [1.0e-08, 0.939]).
- `outputs/final_analyze_output.exo` (= `work/run/analyze_id_2_output_scenario_id_1/iteration50.exo`): nodal `Topology`, `displacement X/Y/Z`, element `My Objective`; its criteria history (`outputs/run_logs/iteration50_criteria_history.csv`) lists 51 objective values ending at 1.0447014e+05.

## 9. Key output files (full list and hashes: `outputs/SHA256SUMS.txt`, 31 entries, verified with `sha256sum -c`)
| File | SHA-256 |
|---|---|
| `outputs/mesh.jou` | 8b0c1d5016d27dbf5952f4f9401c6a5ff6ad018de2cb6521d701e0ef59add577 |
| `outputs/mesh.exo` | dc533f251640add8957a0950a490810f42f083745837f5cde7b959da0b8be70f |
| `outputs/mesh_verification.json` | d37ca675238200df81f9cfb4b3243d5560df87ccaae1764061504a6c2998d619 |
| `outputs/input_deck.i` | 7cf05672516f0c5bcedba024e6bb82aee565efe0a61fc2898138731f6dc4fb75 |
| `outputs/job_script.sbatch` | ab3e29d657aed668329438111e9e4db14f5711bff115c0953a1675d7fa40ff96 |
| `outputs/generated_config/interface.xml` | 2f545669f80885d182291e9aad47d74baf8403082364f79f67542f653a616885 |
| `outputs/generated_config/analyze_2_input_deck.xml` | 9bc13ac9c61c0d8b3c7c73b5c0bce38e31c7d35b53e45483c2fd5238bea222e8 |
| `outputs/generated_config/analyze_helmholtz_input_deck.xml` | e0b190ab3e8c71334d7b7ec5f0567dbcdae40f7a371b943a553d6eb54fae5436 |
| `outputs/generated_config/engine_input_deck.xml` | 7f3edc06119d4155981b3861c2c2263f268e6a3f56f7577cc0aa202f3b35169a |
| `outputs/generated_config/engine_operations.xml` | c5b07640e3f1427a5f763631a2f7f9c3ec1ea54e97160106efe598afc0c67c1b |
| `outputs/generated_config/analyze_2_operations.xml` | fbabf1a1c037533ce5dc1b1ba6a97ce9d70a795c1128735196a3e624aa73efa0 |
| `outputs/generated_config/analyze_helmholtz_operations.xml` | 402ffc30789914bd0c1c7bf429aa2f08ea22b0040960d015b9c71fd716404854 |
| `outputs/generated_config/mpirun.source` | 5f45e199f30722f60934996cf4b58b4ce832972c71a3ef0cbe97ae2f6469f3bc |
| `outputs/morphorm_oc_optimizer_diagnostics.txt` | 5bf3294ab40a1a55925134eb0ef493c7cb725e0964ae54cb3ce1ee62ae18e4f4 |
| `outputs/engine_output.exo` | 9b053a7c2d14ab5200f97efc1b927f3c6a5c787e754ddbd16e6212a1a988f7c9 |
| `outputs/final_analyze_output.exo` | 7b9510366799145234e5d149e7916485b20f3ed58138e1f7d6d62f12afb7ceb7 |
| `outputs/run_logs/morphorm_16247887.out` | 1aae4ed06eb26dcf04407fe47c555624d65f598c15c1e99a6127e0641ac89377 |

`outputs/run_logs/` also holds the empty scheduler stderr, `morphorm_run.log`, the performer logs `engine_1_0`, `analyze_2_1`, `analyze_helmholtz_2`, `opt_criteria_history.csv`, `cubit_batch.log`, `xmlgenerator.log` (in `generated_config/`) and the bundled-check verification records. The pre-existing empty `outputs/.gitkeep` is also listed in the manifest.

## 10. Failures, retries, cancelled jobs, unresolved issues, deviations
- Failed/cancelled jobs: none. Retries of the optimization: none (one submission, one uninterrupted 50-iteration run).
- Translation retry (not an execution): the filter-block form of the deck did not carry `symmetry_plane_location_names` into the generated Helmholtz configuration; per the specification's generated-configuration requirement that version was not run and the deck was re-expressed with the manual's equivalent study-level keywords (preserved: `work/run_attempt1_filter_block/`). The accepted configuration contains the symmetry plane.
- Control-snapshot checksum list names `./.gitignore`, which is not present in `agent-inputs/control/`; all 23 present files verify. Reported, no effect on the task.
- `normalize_in_aggregator false`: the generated `interface.xml` contains no normalization element; the manual states false as the default, so the locked value is in effect, but it is not visible as an explicit keyword in the generated files. Noted for transparency.
- Spatial note: Cubit's `sideset … add surface with z_coord > …` selected the single surface at z = 0.5 (1,152 faces, verified) and the symmetry BC is applied as `location_type sideset` exactly as the specification requires; XMLGenerator emitted it as an essential boundary condition on `ss_sym`.
- Deviations from the specification: none.

## 11. Final artifact paths (relative to the trial root)
`outputs/mesh.jou`, `outputs/mesh.exo`, `outputs/mesh_verification.json`, `outputs/input_deck.i`, `outputs/job_script.sbatch`, `outputs/generated_config/` (interface.xml, analyze_2_input_deck.xml, analyze_helmholtz_input_deck.xml, engine_input_deck.xml, analyze_2_operations.xml, analyze_helmholtz_operations.xml, engine_operations.xml, mpirun.source, xmlgenerator.log, generated_config_verification.tsv), `outputs/morphorm_oc_optimizer_diagnostics.txt`, `outputs/engine_output.exo`, `outputs/final_analyze_output.exo`, `outputs/run_logs/`, `outputs/SHA256SUMS.txt`, `jobs/job_ids.txt`, `jobs/morphorm_spc_run.sbatch`, `jobs/sacct_16247887.txt`, `jobs/submissions.tsv`, `logs/morphorm_16247887.out`, `logs/morphorm_16247887.err`, `provenance/sources_searched.tsv`, `provenance/artifact_selections.md`, `provenance/node_local_placement.txt`, `provenance/control_and_source_versions.txt`, `staging-manifest/staged_files.tsv`, `staging-manifest/returned_files.tsv`, `staging-manifest/globus_transfers.tsv`, `work/run_summary.md`, `work/notes.log` (event log), `work/run/` (accepted run directory), `work/run_attempt1_filter_block/` (untested translation), `work/mesh/`, `work/verify/`, `work/manual/user_manual.txt`.
