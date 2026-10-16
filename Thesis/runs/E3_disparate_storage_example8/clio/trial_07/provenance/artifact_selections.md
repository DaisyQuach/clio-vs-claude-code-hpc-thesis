# Artifact selections — trial E3-clio-trial_07

Every candidate artifact examined in the permitted collections, with the decision. Searched locations are in
`provenance/sources_searched.tsv`; staged copies in `staging-manifest/staged_files.tsv`.

## e3-control (snapshot in agent-inputs/control/, commit 62954055b4e848f2155258c5b8c628eab97c8586)
| Artifact | Decision | Why |
|---|---|---|
| task/frozen_task_specification.md (E3-SPC-v1) | USED (governing document) | every locked geometry/mesh/material/BC/filter/optimizer/output/execution value and deliverable path was taken from it |
| task/required_deliverables.md, task/task_prompt.md | USED | deliverable checklist and task statement |
| catalog/permitted_storage_catalog.yaml, artifact cards | USED | defined the only collections searched and gave the first relevance judgement of each package |
| protocol/*.md, scripts/non_destructive_preflight_helpers/ | USED | record-keeping rules; helpers used for every search/stage/return/hash record |

## e3-private-source (Globus collection 6dcea62e-130d-47a9-8b77-80fba6f58693)
| Artifact | Decision | Why |
|---|---|---|
| documentation/curated_permitted_materials/software_contract.md | USED | approved loader, command names (cubit batch flags, XMLGenerator, bash mpirun.source) |
| documentation/curated_permitted_materials/compute_resources.md | USED | frozen #SBATCH values copied verbatim into jobs/morphorm_spc_run2.sbatch |
| manuals/Morphorm_User_Manual.pdf | USED (reference) | converted to text once (work/manual/user_manual.txt); keyword syntax checked: filter block vs. legacy study-level keywords (Table 2.5.12/2.5.13), Helmholtz keywords (boundary_sticking_penalty, symmetry_plane_location_names), boundary_condition location_type, material_interpolation, output block, diagnostics file names (ch. 9) |
| manuals/Morphorm_Theory_Manual.pdf | NOT STAGED | formulation background only; no keyword needed from it, so not transferred |
| target_materials/symmetry_plane_cantilever/problem_specification.md | USED (cross-check) | byte-identical to the control specification (sha256 f1bd0b56…, diff empty) |
| target_materials/symmetry_plane_cantilever/README.md, permitted_starting_materials/README.md | USED (read) | confirmed no starting deck/journal/mesh is provided; workflow had to be constructed |
| target_materials/symmetry_plane_cantilever/geometry_and_loading_figure.png | NOT STAGED | the textual specification fully defines geometry, sets and loads; the figure was not needed |
| documentation/version_provenance.yaml, curated_readme.md, README.md, MANIFEST.sha256 | USED (read) | version record of the manuals/runtime; manifest used by globus_stage_file.sh to verify every transfer |

## e3-chpc-candidate-archive (read-only POSIX, MANIFEST verification PASS)
| Package | Decision | Why |
|---|---|---|
| example_07 (full 2x1x1 Helmholtz cantilever) | ADAPTED | closest related workflow: same load case, material, SIMP minimum, volume constraint 0.15, Helmholtz radius 0.15 with sticking penalty 1.0, OC, 50 iterations, update_problem. Its journal pattern (brick + mapped scheme + coordinate-filtered nodesets) and deck block structure were adapted to the half domain: z-extent 0.5, 48x24x12 elements, added sideset ss_sym, added boundary_condition 2 (dispz = 0 on ss_sym), added the filter symmetry plane, explicit SIMP exponent 3.0, explicit `type single_phase`/`model simp`. Nothing was copied unchanged except keyword forms; staged files README.md, problem_card.yaml, provenance.yaml, topology_mech_ex7.i, topology_mech_ex7.jou |
| example_16_restart (checkpoint/restart of the full cantilever) | NOT USED | restart workflow; the task is one uninterrupted 50-iteration run with no restart. README/problem card/provenance read only, nothing staged |
| example_01 (bolted L-bracket, tet mesh, kernel filter) | NOT USED | different geometry, tetrahedral mesh, non-design block, traction loads and kernel filter; none of its settings apply. README/problem card/provenance read only, nothing staged |
| example_13 (2-D L-bracket, Helmholtz) | NOT USED | 2-D problem with traction load; no setting needed beyond what example_07 and the manual provide. README/problem card/provenance read only, nothing staged |

## Not searched
No location outside the catalogued collections was listed, opened or used; the host path of the private source collection was not read directly.
