# Artifact selections — E3-clio-trial_04

Every candidate artifact examined, with the decision and reason. Collections: `e3-control` (snapshot in
`agent-inputs/control/`), `e3-private-source` (Globus collection 6dcea62e-130d-47a9-8b77-80fba6f58693, staged only
by `globus_stage_file.sh`), `e3-chpc-candidate-archive` (read-only POSIX). Nothing else was listed, searched or opened.

## e3-private-source (listed with `globus ls --recursive --long`; 15 entries, listing kept in `work/globus_ls_private_source.txt`)

| Artifact | Decision | How used / why |
|---|---|---|
| `documentation/curated_permitted_materials/software_contract.md` | **used** (staged) | approved software interface: loader path, Cubit/XMLGenerator/mpirun.source command forms; sourced in agent shell and in the job script |
| `documentation/curated_permitted_materials/compute_resources.md` | **used** (staged) | frozen Slurm resources copied verbatim into `jobs/morphorm_spc_run.sbatch` |
| `target_materials/symmetry_plane_cantilever/problem_specification.md` | **used** (staged) | verified byte-identical (SHA-256 f1bd0b56…) to `agent-inputs/control/task/frozen_task_specification.md`; the locked values were taken from it |
| `target_materials/symmetry_plane_cantilever/README.md` | **used** (staged) | confirms the target directory holds specification material only |
| `target_materials/symmetry_plane_cantilever/permitted_starting_materials/README.md` | **used** (staged) | confirms no starting deck/journal/mesh is provided; workflow must be constructed |
| `target_materials/symmetry_plane_cantilever/geometry_and_loading_figure.png` (500,087 B) | **not staged** | problem-statement figure only; every geometric and set definition it illustrates is given numerically in the locked specification, so it was not needed |
| `manuals/Morphorm_User_Manual.pdf` | **used** (staged) | converted once to text (`work/manual/user_manual.txt`) and searched for the filter, boundary-condition, output and study keywords; the two equivalent filter forms (filter block vs study-level keywords, Table 2.5.12) and `symmetry_plane_location_names` were confirmed here |
| `manuals/Morphorm_Theory_Manual.pdf` (1,556,172 B) | **not staged** | formulation background only; no keyword or value needed for this workflow comes from it |
| `README.md`, `documentation/curated_readme.md`, `documentation/version_provenance.yaml` | **used** (staged) | collection overview and version/provenance record (manual release 1.0.0, runtime/Cubit module identities) cited in the run summary |
| `documentation/MANIFEST_README.md`, `MANIFEST.tsv` | **not staged** | manifest descriptions; the manifest itself (`MANIFEST.sha256`) was transferred by the helper and used for verification |

## e3-chpc-candidate-archive (listed with `find -type f`; MANIFEST.sha256 verification PASS)

| Package | Decision | How used / why |
|---|---|---|
| `example_07/` (full 2x1x1 Helmholtz cantilever) | **adapted** — deck and journal staged; README, problem_card, provenance read | closest related workflow: same material, load, SIMP minimum, volume fraction, Helmholtz radius and sticking penalty, OC, 50 iterations. Its block structure and Cubit selection idioms were reused. Changes for the locked task: half domain z∈[0,0.5] (48x24x12), new sideset `ss_sym`, second boundary condition u_z=0 on `ss_sym`, `symmetry_plane_location_names ss_sym` on the filter, mesh name `mesh.exo`. No value was taken from it that the specification does not also fix. The geometry figure was not staged. |
| `example_01/` (bolted L-bracket, tet mesh, kernel filter) | **not used** — README and problem_card read only | different geometry, two blocks, traction loads, kernel filter; nothing beyond generic deck structure, which Example 7 already provides |
| `example_13/` (2-D L-bracket, Helmholtz) | **not used** — README and problem_card read only | 2-D QUAD4 problem; no symmetry plane; nothing needed beyond what Example 7 provides |
| `example_16_restart/` (two-stage restart) | **not used** — README and problem_card read only | restart workflow; the locked task is one uninterrupted 50-iteration run with no restart |

## e3-control

`task/frozen_task_specification.md`, `task/required_deliverables.md`, `task/task_prompt.md`, the catalog, the five artifact
cards, the four protocol files and the helper scripts were all read and used as the governing rules. `catalog/checksums.sha256`
verified: all 23 present files PASS; the listed `./.gitignore` is not part of the snapshot (reported, not an error of the task).
