# Artifact selections — E3-baseline-trial_02 (E3-SPC-v1)

Every candidate artifact examined, with the decision and reasons. Collections: `e3-control` (snapshot in `agent-inputs/control/`),
`e3-private-source` (Globus collection `6dcea62e-130d-47a9-8b77-80fba6f58693`), `e3-chpc-candidate-archive` (read-only POSIX).
Staged copies are listed in `staging-manifest/staged_files.tsv`; search order in `provenance/sources_searched.tsv`.

## e3-control (read in place, not staged)

| Artifact | Decision | Use / reason |
|---|---|---|
| `task/frozen_task_specification.md` (E3-SPC-v1) | USED | the locked specification; every mesh, physics, filter, optimizer and deliverable value was taken from it |
| `task/required_deliverables.md`, `task/task_prompt.md` | USED | deliverable checklist |
| `catalog/permitted_storage_catalog.yaml`, `catalog/artifact_cards/*.yaml` | USED | discovery of the three collections and their access methods; card summaries guided which packages to examine first |
| `protocol/*.md` | USED | access, staging, cache and provenance rules followed throughout |
| `scripts/non_destructive_preflight_helpers/*` | USED | record_search.sh, globus_stage_file.sh, stage_file.sh, verify_collection.sh, record_node_placement.sh, hash_outputs.sh, return_file.sh |
| `catalog/checksums.sha256` | USED | verified; all files PASS except `./.gitignore`, which is not part of the snapshot |

## e3-private-source (staged by Globus, 12 of 13 files)

| Artifact | Decision | Use / reason |
|---|---|---|
| `README.md`, `documentation/curated_readme.md`, `documentation/MANIFEST_README.md` | USED (read) | orientation: what the collection contains and that the User Manual is the only permitted syntax reference |
| `documentation/curated_permitted_materials/software_contract.md` | USED | approved commands: `cubit -batch -nographics -nojournal -input`, `XMLGenerator <deck>`, `bash mpirun.source`; runtime python3 with netCDF4 for verification |
| `documentation/curated_permitted_materials/compute_resources.md` | USED | the frozen `#SBATCH` block copied verbatim into `jobs/job_script.sbatch`; rule that the optimization must run through sbatch |
| `documentation/version_provenance.yaml` | USED (read) | manual/runtime version record for the run summary |
| `manuals/Morphorm_User_Manual.pdf` | USED | text extracted with pdftotext into `work/manual_text/`; consulted for: filter block keywords (Table 2.5.12), Helmholtz keywords `boundary_sticking_penalty` and `symmetry_plane_location_names` (§2.5), boundary-condition block (§3.3; sideset example in §1), load block (§3.2), output block (§5.1, control/topology always written), material_interpolation keywords (§6.10), diagnostics file names (§9) |
| `manuals/Morphorm_Theory_Manual.pdf` | STAGED, NOT USED | extracted for completeness; the User Manual's Helmholtz section (Eq. 2.5.4) already explained the surface term; no theory question required it |
| `target_materials/symmetry_plane_cantilever/problem_specification.md` | USED (cross-check) | SHA-256 f1bd0b56... identical to the control copy of the specification (and to the card's `specification_sha256`) |
| `target_materials/symmetry_plane_cantilever/README.md`, `permitted_starting_materials/README.md` | USED (read) | confirm that no starting deck/journal/mesh is provided and that the workflow must be constructed |
| `target_materials/symmetry_plane_cantilever/geometry_and_loading_figure.png` | STAGED, NOT OPENED | the specification text fully defines geometry, sets and loads; the figure was not needed |
| `MANIFEST.sha256` | USED | transferred by `globus_stage_file.sh` into `staging-inbox/`; its SHA-256 equals the catalog's `manifest_sha256`; every staged file verified against it |
| `MANIFEST.tsv` | NOT STAGED | redundant with MANIFEST.sha256 |

## e3-chpc-candidate-archive (examined in place; example_07 staged)

| Package | Decision | Use / reason |
|---|---|---|
| `example_07/` (full 2x1x1 Helmholtz cantilever, HEX8 48x24x24, OC, 50 it.) | ADAPTED (deck + journal staged; README and problem_card staged as the record of what was adapted) | closest workflow: same physics, material, load type, filter type/radius/penalty, constraint, OC settings and iteration count. Journal adapted: width 1.0 -> 0.5 (12 elements), added `sideset 1 ... "ss_sym"` on z = 0.5, output name `mesh.exo`. Deck adapted: added boundary_condition 2 (`fixed_value`, `location_type sideset`, `ss_sym`, `dispz` = 0) referenced from the residual; added `symmetry_plane_location_names ss_sym` to the Helmholtz filter block and, because XMLGenerator did not propagate the filter-block form, also as the equivalent study-level keyword (manual Table 2.5.12); material_interpolation written explicitly (`type single_phase`, `model simp`, `penalty_exponent 3.0`, `minimum_value 1e-3`); `update_problem_frequency 1` on the engine service; mesh name `mesh.exo`. Its `problem_geometry_figure.png` was not staged (full-domain figure, not needed). |
| `example_16_restart/` (two-stage restart of the same cantilever) | NOT USED | restart-specific workflow (20 + 40 iterations with `write_restart_file`/`initial_guess_file_name`); the task requires one uninterrupted 50-iteration run. Its stage-1 deck and journal are otherwise identical to example_07, so it added nothing; read in place for comparison only. |
| `example_13/` (2-D L-bracket, QUAD4, traction, Helmholtz) | NOT USED | 2-D, pave mesh, traction load on a sideset; confirmed sideset naming syntax in a journal (`sideset 1 add curve ...`) but nothing was taken from it. |
| `example_01/` (bolted bracket, tet mesh, kernel filter, fixed blocks) | NOT USED | different geometry, tet mesh, kernel filter, non-design blocks, traction loads; irrelevant to a structured HEX8 Helmholtz cantilever. Read in place only. |
| `README.md`, `MANIFEST.sha256` | USED | package overview; manifest verified PASS with verify_collection.sh |

## Decisions that were not taken from any artifact
- The `symmetry_plane_location_names` keyword was discovered in the User Manual; no candidate uses a symmetry plane.
- The generated-configuration check (`work/scripts/verify_generated_config.py`) and mesh check (`work/scripts/verify_mesh.py`) were written for this trial.
- XMLGenerator variant tests are kept under `work/xmlgen_tests/` (A: filter-block keyword only -> no `Symmetry Plane Sides`; B: legacy study-level keywords only -> present; C = accepted deck: filter block plus study-level keyword -> present; all other generated files byte-identical between A and C).
