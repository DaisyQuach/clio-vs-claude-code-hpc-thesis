# Artifact selections — E3-baseline-trial_04 (E3-SPC-v1 Symmetry-Plane Cantilever)

Every candidate artifact examined, with the decision and reasons. Collections and paths are those of
`catalog/permitted_storage_catalog.yaml`; the full ordered access log is `provenance/sources_searched.tsv`.

## e3-control (snapshot at commit 62954055b4e848f2155258c5b8c628eab97c8586)
| Artifact | Decision | How / why |
|---|---|---|
| `task/frozen_task_specification.md` (E3-SPC-v1) | USED | the locked problem definition; every mesh, physics, filter, optimizer and deliverable value was taken from it |
| `task/required_deliverables.md`, `task/task_prompt.md` | USED | deliverable checklist and task statement |
| `catalog/permitted_storage_catalog.yaml`, `catalog/artifact_cards/*.yaml` | USED | to find the permitted collections and judge candidate relevance before opening packages |
| `protocol/*.md` | USED | access, staging, cache and provenance rules followed throughout |
| `scripts/non_destructive_preflight_helpers/*` | USED | record_search.sh, globus_stage_file.sh, verify_collection.sh, record_node_placement.sh, hash_outputs.sh produced the provenance and staging records |
| `catalog/checksums.sha256` | USED | verified the snapshot (all 27 present files PASS; `.gitignore` is not part of the snapshot) |

## e3-private-source (Globus collection 6dcea62e-130d-47a9-8b77-80fba6f58693; staged by Globus only)
| Artifact | Decision | How / why |
|---|---|---|
| `target_materials/symmetry_plane_cantilever/problem_specification.md` | USED (staged) | SHA-256 f1bd0b56… matches the artifact card and is byte-identical to the control copy; confirmed no additional values beyond the control specification |
| `target_materials/symmetry_plane_cantilever/README.md`, `permitted_starting_materials/README.md` | USED (staged) | confirm that no starting deck/journal/mesh is provided and the workflow must be constructed |
| `target_materials/symmetry_plane_cantilever/geometry_and_loading_figure.png` | STAGED, NOT NEEDED | problem-statement figure; staged for completeness of the target package, but the textual specification already fixed every geometric and set definition, so it was not opened |
| `documentation/curated_permitted_materials/software_contract.md` | USED (staged) | approved software interface, exact Cubit/XMLGenerator/mpirun commands, rule not to use other installations |
| `documentation/curated_permitted_materials/compute_resources.md` | USED (staged) | frozen `#SBATCH` resources copied verbatim into `jobs/morphorm_run.sbatch` |
| `documentation/curated_readme.md`, `documentation/version_provenance.yaml`, `documentation/MANIFEST_README.md`, `README.md`, `MANIFEST.tsv` | USED (staged) | orientation inside the collection, expected manual versions/hashes (User Manual sha256 46c0b655… matched after staging) |
| `manuals/Morphorm_User_Manual.pdf` | USED (staged; text extracted with pdftotext into `work/manual_text/`) | deck syntax: filter-block keyword table (Table 2.5.12), Helmholtz keywords incl. `symmetry_plane_location_names` (§2.5), `boundary_condition` keywords and the sideset `fixed_value` example (§3.3), `material_interpolation` keywords/defaults (§6.10), service `update_problem`/`update_problem_frequency` (§2.2), output block (§5.1), output file layout (§9) |
| `manuals/Morphorm_Theory_Manual.pdf` | NOT STAGED | listed in the Globus listing only; the task is fully specified numerically and the User Manual documents the Helmholtz boundary term and keywords, so the theory background was not needed |

## e3-chpc-candidate-archive (read-only POSIX; manifest verification PASS)
| Package | Decision | How / why |
|---|---|---|
| `example_07/` (full 2×1×1 Helmholtz cantilever: `topology_mech_ex7.i`, `.jou`, README, problem card, provenance) | ADAPTED (read in place; not copied to staging, not copied into the workspace) | closest related workflow: same material, load type, SIMP minimum, volume fraction, Helmholtz radius/penalty, OC and 50 iterations. Its journal idiom (brick + `scheme map` + coordinate-based nodesets) and its deck block layout were followed when writing my own `mesh.jou` and `input_deck.i`. Everything specific to this task was changed or added: half domain (z-width 0.5, 48×24×12), sideset `ss_sym` on z = 0.5, sideset `fixed_value` condition u_z = 0, explicit `material_interpolation` block (single_phase SIMP, exponent 3.0, minimum 1e-3), `symmetry_plane_location_names ss_sym`, `update_problem_frequency 1` on the engine service, mesh name `mesh.exo`. Its figure was not opened. |
| `example_16_restart/` (two-stage restart of the full Helmholtz cantilever) | NOT USED | same physics as example_07 but split into 20 + 40 iterations with restart files; the specification requires one uninterrupted 50-iteration run and no restart, so nothing from it was needed beyond confirming that its stage-1 deck matches example_07 |
| `example_13/` (2-D L-bracket, Helmholtz filter, QUAD4, traction load, 30 iterations) | NOT USED | 2-D, traction-loaded, different geometry, filter radius, volume fraction and iteration count; offered no syntax beyond what example_07 and the manual already provided |
| `example_01/` (bolted L-bracket, tet mesh, fixed non-design block, kernel filter, 100 iterations) | NOT USED | different mesh type, kernel filter, fixed blocks, sideset tractions, steel properties; incompatible with every locked setting of this task |
| archive `README.md`, `MANIFEST.sha256` | USED | package overview; manifest verified PASS with `verify_collection.sh` |

## Not used anywhere
No completed run, numerical output, reference result, scoring/validation material, other trial or external reference was
sought or used. No candidate file was copied into the node-local staging directory; the candidate packages were read in
place (POSIX, read-only) and only their structure/idioms were reused in files written under `work/`.
