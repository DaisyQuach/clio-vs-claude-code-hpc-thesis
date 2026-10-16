# Source exclusions — material intentionally kept out of agent-visible E3 storage

Agent-visible E3 storage = `github_control_repo_worktree/` (and the private GitHub repository), `globus_source_root/`,
`chpc_candidate_archive/`, and the per-trial `agent-inputs/`. None of the following was copied into any of them.

## A. Completed Example 8 (target) materials — researcher-only, never copied anywhere in E3
Recorded by hash only in `researcher_only/example8_reference/`.
| Original | Category |
|---|---|
| `/uufs/chpc.utah.edu/common/home/chet/Daisy/Morphorm_Full_Examples_Tests/Example8_SymmetryPlane/` (126 files): `topology_mech_ex8.i`, `topology_mech_ex8.jou`, `topology_mech_ex8.exo`, `run_morphorm_ex8.sbatch`, `cubit_build.log`, `morphorm-ex8-groundtruth.16053535.out`, `README.md`, `renders/` (3 PNG), `run_16053535/` (generated XML, `engine_output.exo`, analyze outputs, diagnostics, criterion CSV) | completed deck, journal, mesh, job script, logs, result summary, topology renders, Exodus outputs, numerical histories |
| `/uufs/chpc.utah.edu/common/home/chet/Daisy/Morphorm_ground_truth/Example_08/` (178 files): original inputs, manual extracts, mesh generation, reference run, scalar results, figures, provenance | ground truth, validation, accepted reference results |
| `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/researcher_only/ground_truth/example_8/` | thesis reference package, acceptance spec (scoring) |
| `/uufs/chpc.utah.edu/common/home/chet/Daisy/Morphorm/docs/examples/input_decks/topology_optimization/mech/topology_mech_ex8.{i,jou}` | shipped completed deck and journal |
| `/uufs/chpc.utah.edu/common/home/chet/Daisy/Morphorm/docs/examples/topology_optimization/mech/examples_topology_optimization_mech_ex8.inc` | manual page with complete listings |
| `/uufs/chpc.utah.edu/common/home/chet/Daisy/Morphorm/docs/examples/figs/topology_optimization/mech/topology_opt_mech_ex8.png` | optimized-topology figure (result) |
| `/uufs/chpc.utah.edu/common/home/chet/Daisy/morphorm_manuals/examplesmanual.pdf` | Examples Manual (contains the completed Example 8 listings, §7.2.8) |

Only the problem-statement figure `topology_original_geom_mech_ex8.png` (domain, mesh, supports, load, symmetry plane; no result)
was copied, as `globus_source_root/target_materials/symmetry_plane_cantilever/geometry_and_loading_figure.png`.

## B. Result and evidence material of the candidate examples (1, 2, 7, 16) — not copied
| Original | Reason |
|---|---|
| `/uufs/chpc.utah.edu/common/home/chet/Daisy/Morphorm_Full_Examples_Tests/topology_mech_ex1.exo`, `.../Example7_Helmholtz/topology_mech_ex7.exo`, `.../Example7_ConventionalFilter/topology_mech_ex7.exo`, `.../Example16_Restart/topology_mech_ex16.exo` | meshes (regenerable from the shipped journals) |
| `run_16050140/`, `Example7_Helmholtz/run_16053278/`, `Example7_ConventionalFilter/run_16053495/`, `Example16_Restart/run_16053526/` | completed runs: generated XML, Exodus outputs, diagnostics, criterion histories |
| `renders/` (21 PNG), `Example7_*/renders/`, `Example16_Restart/renders/ex16_restart_compliance_history.png`, `webviewer_data/`, `*_optimized.stl` | topology renders, history plot, post-processed geometry |
| `morphorm-ex1-groundtruth.16050140.out`, `morphorm-ex7-*.out`, `morphorm-ex16-restart.16053526.out`, `cubit_build.log`, `authorization.log`, `tosca-ex1-compliance.16053079.out` | solver, mesher, Slurm and authorization logs |
| `README.md` files in `Morphorm_Full_Examples_Tests/` and its example directories | run result summaries |
| `run_morphorm_ex*.sbatch`, `env.sh` | run scripts tied to the earlier environment |
| `Example7_ConventionalFilter/topology_mech_ex7_conventional.i` | researcher-made variant (`boundary_sticking_penalty 0.0`), not a shipped example |
| `Example16_Restart/topology_mech_ex16_restart_from_topology.i` | researcher-made variant (`initial_guess_field_name topology`), not a shipped example |
| `topology_mech_ex1/`, `topology_mech_ex1.inp`, `.par`, `v0_design.txt`, `run_tosca_ex1.sbatch`, `*.py` helper scripts | Abaqus/Tosca comparison and post-processing for Example 1, outside the Morphorm workflow |
| `Example13_2D/` | unrelated example (not in E3 scope) |
| `/uufs/chpc.utah.edu/common/home/chet/Daisy/Morphorm_ground_truth/Example_16/`, `Experiment1/`, `Experiment2/`, `tools/`, audit/construction reports | ground truth, E1/E2 references, researcher tools |
| `/uufs/chpc.utah.edu/common/home/chet/Daisy/Morphorm/docs/examples/figs/.../topology_initial_geometry_mech_ex2.png`, `topology_results_mech_ex2.png`, `topology_opt_geom_mech_ex1_disp.png`, `topology_opt_*_mech_ex7.png`, `ex16/topology_restart_history_ex16.png` | result figures (the Example 2 "initial geometry" is an optimized Example 1 design) |
| `/uufs/chpc.utah.edu/common/home/chet/Daisy/Morphorm/docs/examples/topology_optimization/mech/examples_topology_optimization_mech_ex{1,2,7,16}.inc` | Examples Manual source pages: contain results sections; the thesis rule "never the Examples Manual" in agent-visible packets is kept. READMEs in each package describe the examples instead. |
| `runmorphorm.py` | execution driver not part of the approved software interface |

## C. Documentation
| Original | Reason |
|---|---|
| `/uufs/chpc.utah.edu/common/home/chet/Daisy/Morphorm/docs/` (690 MB, git commit `f07a712b`) | full documentation source tree stays private and uncopied; the two PDF manuals cover permitted syntax |
| `/uufs/chpc.utah.edu/common/home/chet/Daisy/morphorm_manuals/usermanual.pdf`, `theorymanual.pdf` | copied **only** into the private `globus_source_root/manuals/`; never into GitHub |

## D. Never placed in the GitHub repository
Manuals, any PDF, any Exodus file, any example deck/journal, ground truth, reference outputs, credentials or tokens
(`.gitignore` additionally blocks `*.pdf`, `*.exo`, `*.e`, `.credentials*`, `*.token`).
