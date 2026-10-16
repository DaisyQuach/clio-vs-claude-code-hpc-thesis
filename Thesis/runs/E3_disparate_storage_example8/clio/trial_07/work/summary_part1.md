# Run summary — E3 Symmetry-Plane Cantilever (E3-SPC-v1)

## 1. Trial identity
- Trial identifier (`$E3_TRIAL_ID`): `E3-clio-trial_07`
- Trial root: `/uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/clio/trial_07`
- Node-local staging directory (`$E3_STAGING_DIR`): `/scratch/local/u1282901/16252784/e3/clio/E3-clio-trial_07` (host notch204, agent allocation 16252784; `provenance/node_local_placement.txt`)
- Control commit: `62954055b4e848f2155258c5b8c628eab97c8586` (`agent-inputs/CONTROL_COMMIT.txt`); snapshot checksums: all 23 present files PASS, `./.gitignore` is listed in `catalog/checksums.sha256` but absent from the snapshot (`provenance/control_and_source_versions.txt`)
- Assigned task: construct and complete the Symmetry-Plane Cantilever topology-optimization workflow exactly as locked in `task/frozen_task_specification.md` (half 2x1x1 cantilever, z in [0, 0.5], HEX8 48x24x12, Helmholtz filter with symmetry plane `ss_sym`, OC, exactly 50 iterations, frozen Slurm resources), with every deliverable of section 8 and the distributed-context provenance.

## 2. Discovery (detail: `provenance/sources_searched.tsv`, 17 records)
| Collection | Method | What was listed/read |
|---|---|---|
| e3-control | POSIX read of `agent-inputs/control/` | README, task prompt, frozen specification, deliverables, catalog, 5 artifact cards, 4 protocol files, helper scripts |
| e3-private-source (Globus `6dcea62e-130d-47a9-8b77-80fba6f58693`) | `globus ls --recursive`, then `globus_stage_file.sh` per file | top level: `manuals/`, `documentation/`, `target_materials/`, `MANIFEST.sha256`, `MANIFEST.tsv`, `README.md` (21 entries). Host path never read directly |
| e3-chpc-candidate-archive (POSIX, MANIFEST verification PASS) | `find`, POSIX read | `README.md`, `MANIFEST.sha256`, and the README/problem_card/provenance of `example_01`, `example_07`, `example_13`, `example_16_restart` |
| e3-trial-inbox-destination | Globus destination only (`staging-inbox/`) | never listed or used as a source |

No other location was searched, listed or opened.

## 3. Artifact selection (detail: `provenance/artifact_selections.md`)
- USED: frozen specification (control; byte-identical copy in the private source, sha256 `f1bd0b56...`), `software_contract.md`, `compute_resources.md`, Morphorm User Manual (keyword reference, converted once to `work/manual/user_manual.txt`), `version_provenance.yaml`, the target-materials READMEs (confirm no starting materials).
- ADAPTED: `example_07` (full-domain Helmholtz cantilever): journal pattern and deck block structure adapted to the half domain; symmetry sideset, symmetry displacement condition, filter symmetry plane and explicit SIMP exponent added from the specification.
- NOT USED: `example_01` (tet L-bracket, kernel filter), `example_13` (2-D), `example_16_restart` (restart workflow): read their cards only, nothing staged. NOT STAGED: Theory Manual, geometry figures (not needed).

## 4. Staging (detail: `staging-manifest/`)
- 14 files, 2,167,707 bytes staged into `$E3_STAGING_DIR` (`staged_files.tsv`): 9 from e3-private-source by Globus (10 transfers incl. `MANIFEST.sha256`, all SUCCEEDED, `globus_transfers.tsv`; every file matched the collection manifest, sha256 of manifest `d856bed2...` = catalog value) and 5 from e3-chpc-candidate-archive by `stage_file.sh` (source/copy SHA-256 equal).
- Returned files: none (`returned_files.tsv` header only). The journal and deck were written from scratch under `work/`; no staged file was copied into the workspace. The Slurm job read only `work/run2/` (shared file system) and the approved loader.

## 5. Mesh
- Journal `work/mesh/mesh.jou` -> `outputs/mesh.jou`; run on the agent host (permitted for meshing) with `cubit -batch -nographics -nojournal -input mesh.jou` (exit 0, 2026-10-13T19:26:50Z; logs in `outputs/run_logs/cubit_stdout.log`). Half brick 2.0x1.0x0.5 at the origin, `scheme map`, size 0.0416667, `block_1` HEX8, `ns_fix` (x = 0 surface nodes), `ns_load` (x = 2 and y = 0 nodes), `ss_sym` (surface z = 0.5), `export mesh mesh.exo dimension 3`.
- Mesh file: `outputs/mesh.exo` (sha256 `9f73c9c3...`, byte-identical to the file read by the job, hashed inside the job stdout).
- Verification (`exo_summary.py`, record `outputs/mesh_verification.json`, `expect_ok: true`): 13,824 elements, 15,925 nodes, dim 3, bbox [0,0,0]-[2.0,1.0,0.5], one block `block_1` HEX8 (13,824 elems), `ns_fix` 325, `ns_load` 13, `ss_sym` 1,152 faces. All locked values met.
