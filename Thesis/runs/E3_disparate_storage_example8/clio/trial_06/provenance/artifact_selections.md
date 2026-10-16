# Artifact selections — trial E3-clio-trial_06 (E3-SPC-v1)

Every candidate artifact examined, with the decision. Hashes are the collection-manifest / staged values recorded in
`staging-manifest/staged_files.tsv`; locations searched are in `provenance/sources_searched.tsv`.

## e3-control (snapshot `agent-inputs/control/`, commit 62954055b4e848f2155258c5b8c628eab97c8586)
| Artifact | Decision | How / why |
|---|---|---|
| `task/frozen_task_specification.md` (E3-SPC-v1) | USED | sole source of every locked value (geometry, mesh counts, sets, material, BCs, load, filter, optimizer, deliverable paths) |
| `task/required_deliverables.md`, `task/task_prompt.md` | USED | deliverable checklist and task statement |
| `catalog/permitted_storage_catalog.yaml`, `catalog/artifact_cards/*.yaml` | USED | defined the permitted collections, access methods and candidate packages; cards used to pre-judge relevance |
| `protocol/*.md` | USED | access, staging, cache and provenance rules followed throughout |
| `scripts/non_destructive_preflight_helpers/*` | USED | record_search, globus_stage_file, stage_file, return_file, record_node_placement, verify_collection, hash_outputs |

## e3-private-source (Globus collection 6dcea62e-130d-47a9-8b77-80fba6f58693; all reads by Globus transfer into `staging-inbox/`)
| Artifact | Decision | How / why |
|---|---|---|
| `MANIFEST.sha256`, `MANIFEST.tsv`, `README.md`, `documentation/MANIFEST_README.md`, `documentation/curated_readme.md` | USED (staged) | collection inventory; manifest check of every staged file |
| `documentation/version_provenance.yaml` | USED (staged) | recorded software/manual versions (engine 0d767ac7, analyze 60c5e37c, cubit-edu/2026.8) |
| `documentation/curated_permitted_materials/software_contract.md` | USED (staged) | approved commands: `cubit -batch -nographics -nojournal -input`, `XMLGenerator`, `bash mpirun.source` |
| `documentation/curated_permitted_materials/compute_resources.md` | USED (staged) | frozen `#SBATCH` resources copied verbatim into `jobs/morphorm_spc_run02.sbatch` |
| `manuals/Morphorm_User_Manual.pdf` | USED (staged; text copy in `work/manual_text/user_manual.txt`) | keyword confirmation: filter block vs legacy keywords (Table 2.5.12), `symmetry_plane_location_names`, `boundary_sticking_penalty`, `filter_radius_absolute`, boundary_condition/load/output blocks, `update_problem*`, comment syntax `//` |
| `manuals/Morphorm_Theory_Manual.pdf` | NOT USED (listed only, not staged) | formulation background only; the User Manual supplied every keyword needed, so it was not copied (stage only what is needed) |
| `target_materials/symmetry_plane_cantilever/problem_specification.md` | USED (staged) | confirmed byte-identical body to the control specification (sha256 f1bd0b56… matches the artifact card) |
| `target_materials/symmetry_plane_cantilever/README.md`, `permitted_starting_materials/README.md` | USED (staged) | confirmed no starting deck/journal/mesh is provided; workflow must be constructed |
| `target_materials/symmetry_plane_cantilever/geometry_and_loading_figure.png` | STAGED, not relied upon | problem-statement figure; the README's description (ns_fix red, ns_load blue, ss_sym green) was consistent with the specification, which was authoritative |

## e3-chpc-candidate-archive (read-only POSIX; manifest verified PASS)
| Artifact | Decision | How / why |
|---|---|---|
| `README.md`, `MANIFEST.sha256` | USED (read in place) | archive overview; manifest verification |
| `example_07/` (README, problem_card, provenance, `topology_mech_ex7.i`, `topology_mech_ex7.jou`) | ADAPTED (staged) | closest related workflow: full 2x1x1 Helmholtz cantilever, same E, nu, SIMP min 1e-3, same load and support names, same filter radius/penalty, OC, 50 iterations. Journal adapted to the half domain (wd 0.5 -> 48x24x12) plus sideset `ss_sym`; deck adapted with BC 2 (`ss_sym` dispz 0) and the filter symmetry plane. Figure not staged (not needed). |
| `example_16_restart/` (README, problem_card, provenance read in place) | NOT USED | restart-specific two-stage workflow; the specification requires one uninterrupted 50-iteration run, and its physics duplicates example_07 |
| `example_01/` (README, problem_card, provenance read in place) | NOT USED | tetrahedral bolted bracket with a non-design block, traction loads and kernel filter; no setting transfers beyond the general deck structure already present in example_07 |
| `example_13/` (README, problem_card, provenance read in place) | NOT USED | 2-D L-bracket with pave QUAD4 mesh and traction load; dimensionality and loading differ; its Helmholtz usage is already covered by example_07 |

## Translation decision (recorded, not an artifact)
run01 used the manual's filter-block form; `symmetry_plane_location_names` did not reach `analyze_helmholtz_input_deck.xml`.
run02 used the equivalent study-level keywords (Table 2.5.12); the generated file then contains `Symmetry Plane Sides {ss_sym}`.
All other generated files are byte-identical between run01 and run02. run02 is the submitted and accepted configuration.
