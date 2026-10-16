# Artifact selections — E3-baseline-trial_05 (E3-SPC-v1)

Every candidate artifact examined, the decision, and the reason. Detail of locations in `sources_searched.tsv`;
copies in `../staging-manifest/staged_files.tsv`. No completed result, reference output or scoring material was sought or used.

## e3-control (control snapshot, commit 62954055b4e848f2155258c5b8c628eab97c8586)
| Artifact | Decision | Use / reason |
|---|---|---|
| `task/frozen_task_specification.md` (E3-SPC-v1) | **used** | the locked specification; every mesh, physics, filter, optimizer and deliverable value was taken from it |
| `task/required_deliverables.md`, `task/task_prompt.md` | used | deliverable checklist |
| `catalog/permitted_storage_catalog.yaml`, `catalog/artifact_cards/*.yaml` | used | discovery: which collections exist, which packages to examine; SHA-256 of cards matched the archive's problem cards |
| `protocol/*.md` | used | access, staging, cache and provenance rules followed |
| `scripts/non_destructive_preflight_helpers/*` | used | all record keeping, staging (POSIX and Globus), hashing |
| `catalog/checksums.sha256` | used | verified; all present files OK (`.gitignore` listed in the checksum file is absent from the snapshot — pre-existing packet condition, not a scientific input) |

## e3-private-source (Globus collection 6dcea62e-130d-47a9-8b77-80fba6f58693)
| Artifact | Decision | Use / reason |
|---|---|---|
| `README.md`, `documentation/curated_readme.md`, `documentation/MANIFEST_README.md` | staged, read | orientation; confirm which files are permitted documentation |
| `documentation/version_provenance.yaml` | staged, read | version record of manuals, runtime (engine 0d767ac7, analyze 60c5e37c), Cubit module cubit-edu/2026.8 |
| `documentation/curated_permitted_materials/software_contract.md` | staged, **used** | the approved software interface and commands (`cubit -batch -nographics -nojournal -input`, `XMLGenerator`, `bash mpirun.source`) |
| `documentation/curated_permitted_materials/compute_resources.md` | staged, **used** | frozen Slurm resources copied verbatim into the job script |
| `target_materials/symmetry_plane_cantilever/problem_specification.md` | staged, **used** | SHA-256 f1bd0b56… matches the artifact card; byte-identical (diff) to the control copy of the specification |
| `target_materials/symmetry_plane_cantilever/README.md`, `permitted_starting_materials/README.md` | staged, read | confirm no starting deck/journal/mesh is provided; workflow must be constructed |
| `target_materials/symmetry_plane_cantilever/geometry_and_loading_figure.png` | staged, not needed for construction | problem-statement figure; the text specification was sufficient (figure kept staged as part of the target package, not opened) |
| `manuals/Morphorm_User_Manual.pdf` | staged, **used** | deck syntax: filter block keywords (Table 2.5.12), Helmholtz `boundary_sticking_penalty` / `symmetry_plane_location_names` (Table 2.5.15), boundary_condition `location_type` (nodeset/sideset), `material_interpolation` block (type single_phase, model simp, penalty_exponent, minimum_value), service `update_problem`/`update_problem_frequency`, diagnostics file names (Ch. 9) |
| `manuals/Morphorm_Theory_Manual.pdf` | listed, **not staged / not read** | formulation background only; not needed to construct or verify the deck; staging rule: copy only what is needed |
| `MANIFEST.sha256`, `MANIFEST.tsv` | MANIFEST.sha256 transferred by the helper to the inbox for checksum verification of every staged file; MANIFEST.tsv not used | integrity only |

## e3-chpc-candidate-archive (read-only POSIX)
| Package | Decision | Use / reason |
|---|---|---|
| `example_07` (full 2x1x1 Helmholtz cantilever) | **adapted** (deck and journal staged) | closest relative of the target: same material, load type and magnitude, SIMP minimum 1e-3, volume fraction 0.15 on the engine service, Helmholtz radius 0.15 with sticking penalty 1.0, OC, 50 iterations, update_problem. Adaptations: journal width 1.0 → 0.5 (48×24×12), added sideset `ss_sym` on z = 0.5, export name; deck: added boundary_condition 2 (`ss_sym`, dispz = 0, location_type sideset), explicit `material_interpolation` block (single_phase simp, exponent 3.0, minimum 1e-3), `symmetry_plane_location_names ss_sym` on the filter (filter block and, because XMLGenerator only propagates the study-level form, also in the study block), `update_problem_frequency 1` moved to the engine service block, load value written as -1.0, mesh name `mesh.exo`. Not a completed solution; its full-domain problem differs from the half-domain target. |
| `example_16_restart` (two-stage restart of the same cantilever) | examined (read in place), **not used** | same physics as Example 7 but demonstrates restart (`write_restart_file`, `initial_guess_file_name`, `restart_iteration`), which the specification forbids (one uninterrupted 50-iteration run); nothing it adds is needed |
| `example_01` (bolted L-bracket, tets, kernel filter) | examined (read in place), **not used** | different geometry, tet mesh, fixed non-design block, traction loads, kernel filter, `normalize_in_aggregator true`, 100 iterations; only served as a syntax comparison for multi-BC decks |
| `example_13` (2-D L-bracket, Helmholtz) | examined (read in place), **not used** | 2-D QUAD4 problem with traction load; confirmed the Helmholtz filter-block syntax but contributed nothing beyond Example 7 |
| `*/problem_geometry_figure.png` | listed, not opened, not staged | figures of other problems; not needed |
| `*/README.md`, `problem_card.yaml`, `provenance.yaml`, archive `README.md`, `MANIFEST.sha256` | read in place | relevance judgement and integrity (manifest verification PASS) |

## Decision on the deck form (recorded finding)
With the symmetry plane declared only inside `begin filter 1 … end filter`, XMLGenerator produced a Helmholtz
configuration without `Symmetry Plane Sides` (kept as `work/xmlgen_tests/initial_block_only/`). Adding the documented
legacy study-level keyword `symmetry_plane_location_names ss_sym` (tests `work/xmlgen_tests/A_legacy`, `B_block_plus_study`)
produced `<Parameter name="Symmetry Plane Sides" … value="{ss_sym}"/>`. The accepted deck keeps the filter block and adds the
study-level keyword (variant B). All other generated settings were identical between the attempts.
