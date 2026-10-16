# Artifact selections — E3-clio-trial_02

Every candidate artifact examined, the decision, and the reason. Collections: `e3-control` (pinned snapshot in
`agent-inputs/control/`), `e3-private-source` (Globus collection 6dcea62e-130d-47a9-8b77-80fba6f58693, staged only
through `globus_stage_file.sh`), `e3-chpc-candidate-archive` (read-only POSIX, staged with `stage_file.sh`).
Staged copies live under `$E3_STAGING_DIR/<alias>/...`; see `staging-manifest/staged_files.tsv`.

## e3-control (read in place, not staged)
| Artifact | Decision | Use / reason |
|---|---|---|
| `task/task_prompt.md`, `task/frozen_task_specification.md` (E3-SPC-v1), `task/required_deliverables.md` | used | the task and every locked value (§1–§9) |
| `catalog/permitted_storage_catalog.yaml`, `catalog/artifact_cards/*.yaml`, `catalog/checksums.sha256` | used | discovery of the permitted collections and candidate packages; snapshot checksums verified (all PASS; `./.gitignore` listed in the checksum file is absent from the snapshot and could not be checked) |
| `protocol/*.md`, `scripts/non_destructive_preflight_helpers/*` | used | access/staging/provenance rules; helpers used for every record |

## e3-private-source (Globus)
| Artifact | Decision | Use / reason |
|---|---|---|
| `MANIFEST.sha256` | staged (inbox, by the helper) | manifest check of every staged file; sha256 d856bed2… matches the catalog |
| `documentation/curated_permitted_materials/software_contract.md` | staged, used | approved software interface, commands (`cubit -batch …`, `XMLGenerator`, `bash mpirun.source`) |
| `documentation/curated_permitted_materials/compute_resources.md` | staged, used | frozen `#SBATCH` resources copied verbatim into `jobs/morphorm_run02.sbatch` |
| `manuals/Morphorm_User_Manual.pdf` | staged, used | converted once to `work/manual/user_manual.txt`; keyword reference for filter blocks vs. study-level filter keywords (Table 2.5.12, §2.5 Helmholtz keywords incl. `symmetry_plane_location_names`), boundary-condition keywords (§3.3), material_interpolation block (§6.10), output block (§5.1), output directory layout (§9.1) |
| `manuals/Morphorm_Theory_Manual.pdf` | examined in listing only, not staged | formulation background only; every setting needed is locked by the specification and the User Manual gives the deck syntax |
| `README.md`, `documentation/curated_readme.md`, `documentation/version_provenance.yaml`, `documentation/MANIFEST_README.md` | staged, read | collection overview and version provenance (manual release 1.0.0, runtime identifiers) recorded for the summary |
| `target_materials/symmetry_plane_cantilever/problem_specification.md` | staged, verified | sha256 f1bd0b56… identical to the control snapshot's `frozen_task_specification.md`; confirms the specification is the same in both collections |
| `target_materials/symmetry_plane_cantilever/README.md`, `permitted_starting_materials/README.md` | staged, read | confirms no starting deck/journal/mesh is provided and that the workflow must be constructed |
| `target_materials/symmetry_plane_cantilever/geometry_and_loading_figure.png` | not staged | problem-statement figure only; every geometric/loading value is given numerically in the locked specification, so the figure was not needed |

## e3-chpc-candidate-archive (POSIX)
| Package | Decision | Use / reason |
|---|---|---|
| `README.md`, `MANIFEST.sha256` | read / verified | collection overview; `verify_collection.sh` PASS (manifest sha256 3c89c503… matches the catalog) |
| `example_07` (full Helmholtz cantilever: README, problem_card, provenance, `topology_mech_ex7.i`, `topology_mech_ex7.jou`) | staged, **adapted** | closest related workflow: same material, load, filter type/radius/penalty, OC, 50 iterations, 15 % volume, h = 1/24. The journal was adapted to the half domain (`wd = 0.5`, 48×24×12) and extended with the `ss_sym` sideset; the deck was adapted with the second (sideset, dispz) boundary condition, explicit SIMP values, and the Helmholtz symmetry plane. The figure (`problem_geometry_figure.png`) was not staged (not needed). |
| `example_16_restart` (README, problem_card, provenance, stage-1 and restart decks, journal) | staged, examined, **not used** | restart-specific workflow; the task is a single uninterrupted 50-iteration run. Confirmed the same deck structure as example_07; no restart keywords are needed. |
| `example_13` (2-D L-bracket: README, problem_card, provenance, deck, journal) | staged, examined, **not used** | 2-D, traction load, different geometry; only confirmed the Helmholtz filter-block syntax. Figure not staged. |
| `example_01` (bolted bracket: README, problem_card, provenance, deck, journal) | staged, examined, **not used** | tetrahedral mesh, non-design block, kernel filter, tractions — not relevant to the locked problem. Figure not staged. |

## Decisions that depended on the examined material
1. Filter declaration: the filter-block form (as in example_07/13/16) translated without the symmetry-plane sideset
   (`work/run01`, rejected before submission). The User Manual's equivalent study-level keywords
   (`filter_type helmholtz`, `filter_radius_absolute`, `boundary_sticking_penalty`, `symmetry_plane_location_names`)
   produced `Symmetry Plane Sides {ss_sym}` in `analyze_helmholtz_input_deck.xml` (`work/run02`, accepted).
2. Symmetry displacement condition: declared on the sideset `ss_sym` (`location_type sideset`, `dispz`), as locked by
   the specification §5, and confirmed present in the generated analyze configuration as `Displacement Z with ID 4`,
   `Sides ss_sym`. (The User Manual §3.3 states that Dirichlet conditions are applied to nodesets; the translator
   accepted the sideset form and the runtime result is recorded in `work/run_summary.md`.)
