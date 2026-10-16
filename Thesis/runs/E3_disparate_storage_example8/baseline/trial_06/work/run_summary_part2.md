
## 7. Execution

Commands used (all on the agent host unless noted; the loader was sourced first in every shell):

```
sha256sum -c --quiet catalog/checksums.sha256                       # control snapshot (in agent-inputs/control)
record_node_placement.sh ; verify_collection.sh <candidate archive> ; record_search.sh ...
globus ls -r 6dcea62e-130d-47a9-8b77-80fba6f58693:/                  # discovery of the private source
globus_stage_file.sh <path>   (x12; each: globus transfer -> staging-inbox/, MANIFEST check, cp -p -> $E3_STAGING_DIR)
pdftotext -layout <staged User Manual> $E3_STAGING_DIR/derived/user_manual.txt
cubit -batch -nographics -nojournal -input mesh.jou                  # work/mesh, 15:02:34Z-15:02:38Z, exit 0
python3 -I work/scripts/verify_mesh.py work/mesh/mesh.exo            # 15:03:41Z, ALL_PASS
XMLGenerator input_deck.i                                            # work/run, accepted translation 15:08:13Z, exit 0
python3 -I work/scripts/verify_generated_config.py work/run          # 28 checks ALL_PASS (final record 15:10Z)
sbatch jobs/morphorm_oc50_symplane.sbatch                            # 15:10:11Z -> job 16176085
   (inside the job, on notch272:  source load_morphorm_e3.sh; module list; bash mpirun.source > morphorm_run.log)
sacct -j 16176085 --format=JobID,JobName,State,ExitCode,Submit,Start,End,Elapsed,AllocCPUS,ReqMem,MaxRSS,NodeList -P
python3 -I (netCDF4) check of iteration50.exo and engine_output.exo   # outputs/run_logs/final_output_check.txt
bash work/scripts/finalize_outputs.sh 16176085 <iteration50.exo>; hash_outputs.sh
```

Slurm jobs submitted in this trial (also `jobs/job_ids.txt`):

| Job ID | Script | Resources | State | Exit | Submit / Start / End (UTC) | Elapsed | Node | MaxRSS |
|---|---|---|---|---|---|---|---|---|
| 16176085 | `jobs/morphorm_oc50_symplane.sbatch` (= `outputs/job_script.sbatch`) | account/partition hochhalter-np, 1 node, 1 task, 8 CPUs, 32G, 02:00:00 (frozen contract, verbatim) | COMPLETED | 0:0 | 15:10:11 / 15:10:13 / 15:27:51 | 00:17:38 | notch272 | 1,675,112 K (batch step) |

`sacct` record: `jobs/sacct_16176085.txt`. Scheduler stdout/stderr: `logs/slurm-16176085.out` / `.err` (copies in `outputs/run_logs/`; stderr is empty). The job's stdout contains `module list` after sourcing the approved interface, the SHA-256 of every input it used (identical to the verified files in `outputs/`), and the timestamps `morphorm_start_utc 15:10:29Z`, `morphorm_end_utc 15:27:50Z`, `morphorm_exit=0`. No job was cancelled or failed; only this one job was submitted. The optimization was not run on the agent host (the job ran under its own allocation 16176085; the scheduler placed it on notch272, the same node as the agent allocation 16176007).

## 8. Completed stages and iteration count

- Discovery, staging, mesh generation, mesh verification, deck translation, generated-configuration verification, Slurm optimization, output verification, deliverable placement: all completed.
- Optimizer: `outputs/morphorm_oc_optimizer_diagnostics.txt` lists iterations 0 … **50** (51 rows, F-count 51). The analyze visualization directory holds `iteration0.exo` … `iteration50.exo` (51 files); `engine_output.exo` holds 51 time steps.
- Stopping message (end of the diagnostics file and of `morphorm_run.log`):
  `****** Optimization stopping due to exceeding maximum number of iterations. ******`
  i.e. the run reached the locked cap of 50 iterations; no convergence stop occurred earlier.
- Iteration history (from the diagnostics): F(X) 2.654786e+06 at iteration 0 → 1.044701e+05 at iteration 50; abs(dX) 1.142971e-01 and abs(dF) 6.611695e+01 at the last iteration (well above the default stagnation tolerances, consistent with the cap-based stop).
- Final fields (`outputs/run_logs/final_output_check.txt`): `final_analyze_output.exo` (= `iteration50.exo`) contains the nodal fields Topology (density; min 1.0e-08, max 0.939, mean 0.157) and displacement X/Y/Z, plus the element field My Objective; `engine_output.exo` contains the nodal fields control and topology at 51 steps (final mean control 0.185, topology 0.157 ≈ the 15 % volume target).

## 9. Key output files (`outputs/`, SHA-256 in `outputs/SHA256SUMS.txt`)

| File | SHA-256 |
|---|---|
| `outputs/mesh.jou` | 145d8641fff412740c85a0a1ea8a9fcd1a390539bffbe5718e6d04acf2c597d4 |
| `outputs/mesh.exo` | c396e719916fd594d9104512432cacf264d45b614452028dee061a7a50c76e77 |
| `outputs/mesh_verification.json` | fe6925bff13ff37c959b4afc8c11f79ceab08f4b2bd5d1033e4e0e41ee4045b0 |
| `outputs/input_deck.i` | 962da5c2534259b27de4bcc98c34e95f81ab4a7a5b949836921dcef1686d4aa1 |
| `outputs/job_script.sbatch` | 46ca650c0c37fa216cb03a7536ef45a316305fdd4733191ac84e1cb2eb78e74b |
| `outputs/generated_config/interface.xml` | 2f545669f80885d182291e9aad47d74baf8403082364f79f67542f653a616885 |
| `outputs/generated_config/engine_input_deck.xml` | 7f3edc06119d4155981b3861c2c2263f268e6a3f56f7577cc0aa202f3b35169a |
| `outputs/generated_config/engine_operations.xml` | c5b07640e3f1427a5f763631a2f7f9c3ec1ea54e97160106efe598afc0c67c1b |
| `outputs/generated_config/analyze_2_input_deck.xml` | 9bc13ac9c61c0d8b3c7c73b5c0bce38e31c7d35b53e45483c2fd5238bea222e8 |
| `outputs/generated_config/analyze_2_operations.xml` | fbabf1a1c037533ce5dc1b1ba6a97ce9d70a795c1128735196a3e624aa73efa0 |
| `outputs/generated_config/analyze_helmholtz_input_deck.xml` | e0b190ab3e8c71334d7b7ec5f0567dbcdae40f7a371b943a553d6eb54fae5436 |
| `outputs/generated_config/analyze_helmholtz_operations.xml` | 402ffc30789914bd0c1c7bf429aa2f08ea22b0040960d015b9c71fd716404854 |
| `outputs/generated_config/mpirun.source` | 5f45e199f30722f60934996cf4b58b4ce832972c71a3ef0cbe97ae2f6469f3bc |
| `outputs/morphorm_oc_optimizer_diagnostics.txt` | 5bf3294ab40a1a55925134eb0ef493c7cb725e0964ae54cb3ce1ee62ae18e4f4 |
| `outputs/engine_output.exo` | 9b053a7c2d14ab5200f97efc1b927f3c6a5c787e754ddbd16e6212a1a988f7c9 |
| `outputs/final_analyze_output.exo` (iteration 50) | 7b9510366799145234e5d149e7916485b20f3ed58138e1f7d6d62f12afb7ceb7 |
| `outputs/run_logs/` | slurm-16176085.out/.err, morphorm_run.log, cubit_run.log, opt_criteria_history.csv, performer logs, final_output_check.txt (hashes in SHA256SUMS.txt) |

The generated-config SHA-256 values equal those printed by the job (`slurm-16176085.out`), proving the job ran the verified configuration.

## 10. Failures, retries, cancelled jobs, unresolved issues, deviations

- **Translation retry (before any run):** the first XMLGenerator translation (symmetry keyword in the filter block) did not carry the symmetry-plane sideset into the Helmholtz configuration; it was discarded (kept for the record in `work/xmlgen_tests/attempt0_filter_block_keyword/`) and the deck was corrected (keyword in the study block). The generated files in `work/run/` were replaced before submission; only the corrected configuration was ever run. No Slurm job was affected.
- **Control checksum:** `catalog/checksums.sha256` lists `.gitignore`, which the snapshot archive does not contain; the other 24 entries verified. Not a scientific input.
- **Deliverable replacement:** `outputs/SHA256SUMS.txt` was regenerated once after adding `outputs/run_logs/final_output_check.txt`; no scientific deliverable was overwritten.
- **Manual vs specification:** the User Manual states that essential boundary conditions must be on nodesets; the specification (locked) requires u_z = 0 through the sideset `ss_sym`. The deck follows the specification and XMLGenerator produced an Essential Boundary Condition with `Sides = ss_sym` (analyze accepted it and ran). Reported for transparency; no locked value was changed.
- No cancelled or failed jobs; no deviation from §1–§7 of the specification; **none** unresolved.

## 11. Final artifact paths

- Scientific: `outputs/mesh.jou`, `outputs/mesh.exo`, `outputs/mesh_verification.json`, `outputs/input_deck.i`, `outputs/job_script.sbatch`, `outputs/generated_config/` (8 XMLGenerator files + `generated_config_verification.txt` + `xmlgenerator.log`), `outputs/morphorm_oc_optimizer_diagnostics.txt`, `outputs/engine_output.exo`, `outputs/final_analyze_output.exo`, `outputs/run_logs/`, `outputs/SHA256SUMS.txt`, `jobs/job_ids.txt`, `jobs/morphorm_oc50_symplane.sbatch`, `jobs/sacct_16176085.txt`, `jobs/submissions.log`, `work/run_summary.md`.
- Distributed context: `provenance/sources_searched.tsv`, `provenance/artifact_selections.md`, `staging-manifest/staged_files.tsv`, `staging-manifest/globus_transfers.tsv`, `staging-manifest/returned_files.tsv` (header only; nothing was returned), `provenance/node_local_placement.txt`, `provenance/control_and_source_versions.txt`.
- Working copies (kept, unmodified after the run): `work/mesh/`, `work/run/` (full run directory incl. `analyze_id_2_output_scenario_id_1/iteration0..50.exo`), `work/scripts/`, `work/xmlgen_tests/`, `logs/staging/`, `staging-inbox/` (Globus transfer record), `$E3_STAGING_DIR` (left in place).
