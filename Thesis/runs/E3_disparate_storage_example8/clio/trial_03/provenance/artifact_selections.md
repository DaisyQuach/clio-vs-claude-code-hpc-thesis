# Artifact selections — trial E3-clio-trial_03

Every candidate artifact examined, with the decision and reason. Collections: `e3-control` (snapshot in `agent-inputs/control/`),
`e3-private-source` (Globus collection 6dcea62e-130d-47a9-8b77-80fba6f58693, staged by `globus_stage_file.sh`),
`e3-chpc-candidate-archive` (read-only POSIX). Searches: `provenance/sources_searched.tsv`; copies: `staging-manifest/`.

## e3-control (read in place; authoritative task definition)
| Artifact | Decision | Use / reason |
|---|---|---|
| `task/frozen_task_specification.md` (E3-SPC-v1) | USED | the locked specification every setting was taken from |
| `task/required_deliverables.md`, `task/task_prompt.md` | USED | deliverable checklist |
| `catalog/permitted_storage_catalog.yaml`, `catalog/artifact_cards/*.yaml` | USED | discovery of the permitted collections and candidate packages |
| `protocol/*.md` | USED | access, staging, cache and provenance rules followed |
| `scripts/non_destructive_preflight_helpers/*` | USED | record-keeping/staging helpers (record_search, globus_stage_file, stage_file, record_node_placement, verify_collection, hash_outputs) |
| `catalog/checksums.sha256` | USED | snapshot verified (`sha256sum -c`, all OK) |

## e3-private-source (staged by Globus into `$E3_STAGING_DIR/e3-private-source/`)
| Artifact | Decision | Use / reason |
|---|---|---|
| `documentation/curated_permitted_materials/software_contract.md` | USED | approved software interface: loader to source, `cubit -batch -nographics -nojournal -input`, `XMLGenerator`, `bash mpirun.source` |
| `documentation/curated_permitted_materials/compute_resources.md` | USED | frozen `#SBATCH` resources copied verbatim into `jobs/morphorm_spc_run2.sbatch` |
| `manuals/Morphorm_User_Manual.pdf` | USED | converted to text (`work/manual_text/user_manual.txt`); keywords confirmed: filter block vs. study-level filter keywords (Table 2.5.12), `filter_radius_absolute`, `boundary_sticking_penalty`, `symmetry_plane_location_names` (Table 2.5.15), boundary_condition core keywords (§3.3), material_interpolation block (`type single_phase`, `model simp`, `penalty_exponent`, `minimum_value`), output block, diagnostics file names (§9) |
| `manuals/Morphorm_Theory_Manual.pdf` | STAGED, NOT NEEDED | converted to text but no theory question arose; the User Manual answered every keyword question |
| `target_materials/symmetry_plane_cantilever/problem_specification.md` | USED (cross-check) | `diff` against `task/frozen_task_specification.md`: identical |
| `target_materials/symmetry_plane_cantilever/geometry_and_loading_figure.png` | STAGED, NOT NEEDED | the text specification fully defined geometry, sets and load; the figure was not consulted |
| `target_materials/symmetry_plane_cantilever/README.md`, `permitted_starting_materials/README.md` | USED (orientation) | confirm no starting deck/journal/mesh exists for the task |
| `README.md`, `documentation/curated_readme.md`, `documentation/MANIFEST_README.md`, `documentation/version_provenance.yaml` | USED (orientation/provenance) | collection layout; manual SHA-256 values (46c0b655… user, e60bf7f2… theory) matched the staged copies |
| `MANIFEST.sha256` | USED | transferred by the helper; SHA-256 d856bed2…cc53 equals the catalog's `manifest_sha256`; every staged file matched its manifest entry |

## e3-chpc-candidate-archive (read in place; two files staged)
| Package | Decision | Use / reason |
|---|---|---|
| `example_07/` (full 2x1x1 Helmholtz cantilever, HEX8 48x24x24, OC, 50 it.) | ADAPTED | closest related workflow. `topology_mech_ex7.jou` and `topology_mech_ex7.i` were staged and used as structural templates only. Journal adapted: width 1.0 -> 0.5 (half domain), sideset `ss_sym` added on z = 0.5, export name `mesh.exo`. Deck adapted: added `boundary_condition 2` (`ss_sym`, `dispz` = 0, `location_type sideset`), explicit `material_interpolation` (`type single_phase`, `model simp`, `penalty_exponent 3.0`, `minimum_value 1e-3`), `symmetry_plane_location_names ss_sym`, mesh name. Its filter-block form was tried first (work/run) and replaced by the study-level keyword form (work/run2) because the block form did not propagate the symmetry plane to `analyze_helmholtz_input_deck.xml`. Every numerical value came from E3-SPC-v1, not from the example. `problem_geometry_figure.png` NOT USED (full-domain figure, not needed). |
| `example_16_restart/` (two-stage checkpoint/restart cantilever) | NOT USED | the task is one uninterrupted 50-iteration run; restart keywords (`write_restart_file`) are not part of the specification. Deck/journal read for comparison only (identical structure to example_07 apart from the restart keywords). |
| `example_13/` (2-D L-bracket, QUAD4, Helmholtz, 30 it.) | NOT USED | 2-D, traction load, different geometry; only confirmed the Helmholtz filter-block syntax already seen in example_07 |
| `example_01/` (bolted bracket, tet mesh, kernel filter, fixed block) | NOT USED | kernel filter, fixed non-design block, traction loads, `single_criterion` objective: none applies to this specification |
| `README.md`, `MANIFEST.sha256` | USED | package overview; manifest verification (25/25 listed files OK; the listed `./.gitignore` is absent, see `provenance/control_and_source_versions.txt`) |
