# E3 remediation report

Window: 2026-10-10T00:32Z → 2026-10-10T00:58Z (UTC), login node notchpeak1, no allocation.
**No scored trial was run, no model was called for a trial, no Slurm job was submitted, Morphorm and Cubit were not
executed, and no scientific result was created.** The setup report `setup/E3_SETUP_REPORT.md` and its evidence files are
unchanged.

**Verdict: E3 is NOT ready for a counted trial.** Ground-truth isolation is not technically verified (§7, §12).

## 1. Every file/directory moved, created or edited
Complete path-level list: `setup/remediation/E3_REMEDIATION_CHANGED_PATHS.txt` (E3-tree snapshot before vs after).
SHA-256 of every created or edited file (outside `.git/` and the runtime copies): `setup/remediation/E3_REMEDIATION_SHA256SUMS.txt`.
Before any edit of a pre-existing file, a copy was kept under `setup/preexisting_state/`.

**Moved (not deleted; hashes and modes verified identical after the move)**
| From | To | Content |
|---|---|---|
| `baseline/trial_01/agent_inputs/` | `setup/preexisting_state/legacy_baseline_trial01_agent_inputs/` | 15 files (legacy pre-E3 packet + 2 manuals), 00:37:26Z. Dir was `555`; `u+w` set on it only for the rename and restored to `555`. |
| `chpc_candidate_archive/example_02/` | `setup/preexisting_state/example_02_incomplete_candidate/` | 4 files, 00:37:55Z. Archive root and package temporarily `u+w`, restored to `555`. |
| `github_control_repo_worktree/catalog/artifact_cards/example_02.yaml` | removed from the worktree with `git rm` (single file) | preserved in git history (`333edab`) and in `setup/preexisting_state/control_repo_pre_remediation_333edab/` |

**Created**
- `automation/environment/`: `load_morphorm_e3.sh`, `load_morphorm_e3.sha256`, `README.md`, `environment_inventory.txt`,
  `modulefiles/Core/{morphorm/approved-runtime.lua, cubit-edu/2026.8.lua}`, `runtime/morphorm/` (2,064 files, 1.2 GB),
  `runtime/coreform_cubit/` (30,819 files, 5.3 GB), `runtime_manifests/coreform_cubit.sha256`, `.copy_started_utc`, `.copy_finished_utc`.
- `automation/sandbox/`: `README.md`, `launch_e3_sandbox.sh`, `allowed_paths.txt`, `denied_paths.txt`, `sandbox_probe.sh`,
  `sandbox_validation_plan.md`, `validation_record_login_node.txt`.
- `chpc_candidate_archive/example_13/` (README, problem card, provenance, 3 source files).
- `github_control_repo_worktree/catalog/artifact_cards/example_13.yaml`.
- `baseline/trial_01/README.md`.
- `researcher_only/evaluation/E3_SCORING_SCOPE.md`; `researcher_only/provenance/{README.md, agent_visible_to_canonical_source_map.tsv}` (mode 600, dir 700).
- `setup/`: this report, `permissions_audit_remediation.md`, `GROUND_TRUTH_ISOLATION_ACTION_REQUIRED.md`,
  `COMPUTE_NODE_QUALIFICATION_ACTION_REQUIRED.md`, `remediation/{sanitize_candidate_archive.py, remediation_source_inventory.csv,
  remediation_source_inventory.sha256, claude_2.1.295_help.txt, E3_REMEDIATION_CHANGED_PATHS.txt, E3_REMEDIATION_SHA256SUMS.txt}`.
- `setup/preexisting_state/` copies: `baseline_trial_01_manifest.pre_remediation.yaml`, `E3_README.md.pre_remediation`,
  `access_qualification_plan.pre_remediation.md`, `automation_pre_remediation/` (6 files), `globus_source_root_pre_remediation/`
  (4 files), `control_repo_pre_remediation_333edab/` (9 files), `candidate_archive_pre_remediation/` (8 files; the regenerated
  cards had been overwritten in place, so byte-identical originals were recovered from the setup session's scratch test tree and
  each was verified against `setup/E3_SETUP_SHA256SUMS.txt` before being kept).

**Edited (pre-existing E3 files)**
| File | Change |
|---|---|
| `README.md` | remediation status, new layout, Examples 1/7/13/16 |
| `baseline/trial_01/manifest.yaml` | `e3rem_*` fields **appended**; all earlier fields unchanged |
| `automation/lib/e3_common.sh` | adds `E3_ENV_LOADER`, `E3_SOFTWARE_ROOTS` |
| `automation/audit_boundary.sh` | software roots counted as allowed (loader, modulefiles, runtime only) |
| `automation/baseline/prepare_baseline_trial.sh` | `agent-inputs/trial_context.md` names the E3 loader instead of the thesis loader |
| `automation/verify_readonly_sources.sh` | `--with-originals` also checks the Example 13 originals |
| `automation/baseline/baseline_e3_config.env` | `E3_CONTROL_COMMIT` → `c3b87369…e3b7` (old value kept in a comment); `.example` unchanged |
| `automation/baseline/README.md` | current blockers |
| `setup/access_qualification_plan.md` | pinned commit updated |
| `chpc_candidate_archive/`: `README.md`, `MANIFEST.sha256`, `example_{01,07,16_restart}/{problem_card,provenance}.yaml` | regenerated with logical identifiers (§5) |
| `globus_source_root/`: `documentation/version_provenance.yaml`, `documentation/curated_permitted_materials/software_contract.md`, `MANIFEST.tsv`, `MANIFEST.sha256` | logical identifiers; E3 loader; regenerated manifests |
| control repo: `README.md`, `catalog/permitted_storage_catalog.yaml`, `catalog/checksums.sha256`, cards `example_01/07/16_restart`, `symmetry_plane_target`, `protocol/access_rules.md` | §9 |

## 2. Legacy agent inputs
`baseline/trial_01/agent_inputs/` no longer exists. `trial_01` now holds only the E3 packet directory `agent-inputs/`
(empty until preparation), the standard workspace directories, `manifest.yaml` and a README stating that `agent-inputs/` is
the only valid agent-visible input packet. `--accept-legacy-agent-inputs` was not used or enabled. In the sandbox the archived
packet is not visible (probe: `legacy_agent_inputs not visible`). `verify_baseline_trial.sh --planned`: PASS.

**trial_02 … trial_05 (inspected, not changed):** each holds an `agent_inputs/` identical to trial_01's legacy packet
(`diff -r`: identical), including `E3_PLANNED_NOT_EXECUTABLE.md`, which labels the packet "E3" and names the frozen
Example 8 configuration (`FROZEN-EX8-v1`) with the two manuals; manifests differ only in `run_id`, `paired_block`,
`created_utc`. **Reported ambiguity:** these are E3-labelled legacy packets that would conflict with an E3 `agent-inputs/`
if those trials are converted. They have no `agent-inputs/` yet, so no adjacency exists today. Before converting any of
them, move its `agent_inputs/` out as was done for trial_01 (researcher decision). The sandbox launcher refuses a trial
directory that contains `agent_inputs/` or lacks `agent-inputs/`.

## 3. Candidate archive and Example 2
`chpc_candidate_archive/` now contains `example_01/`, `example_07/`, `example_13/`, `example_16_restart/`, `README.md` and
`MANIFEST.sha256` (25 files, manifest SHA-256 `3c89c503…7dac`). All entries are write-protected (0 write bits). Verification passes.
Example 2 is archived at `setup/preexisting_state/example_02_incomplete_candidate/` (unchanged; not agent-visible) and is
listed as withdrawn in the researcher-only source map. Its control-repo card is withdrawn.

## 4. Replacement candidate: Example 13 (`chpc_candidate_archive/example_13/`, `MORPHORM-CANDIDATE-EX13`)
Search (read-only): every mech deck in the Morphorm documentation tree except Example 8, and the user's working-example
collection (`Example13_2D`, the only example there not yet used). Excluded: Ex 2/4/5 (no journal; 4 reuses the Ex 1 mesh, 5
needs a target CSV and a mesh), Ex 16 restart (already present), Ex 17 (declares a symmetry location; too close to the target
for a replacement), Abaqus material, researcher variant decks. Docs-tree Examples 3, 6, 9–12, 14, 15 have journals and
showed no external-file dependency in a keyword screen, but were not chosen because the instructions prefer the user's
existing working examples; they were not inspected further.
**Selected: Example 13**, a 2-D L-bracket with a Helmholtz filter. The journal draws the geometry and exports the 2-D mesh
the deck reads (`topology_mech_ex13.exo`). There are no initial-guess, restart, CSV or other-example dependencies and no
symmetry plane. It is not a completed result: the package holds only the shipped deck, the journal and the manual's
problem-statement figure, which was checked visually and shows the mesh, the clamped edge and the loaded edge. The
working copies in `Example13_2D` are byte-identical to the documentation-tree deck and journal (verified). Scientific role
(truthful, in the card): a self-contained general 2-D Helmholtz-filter workflow. Its geometry, dimension, supports and load
type all differ from the 3-D target. One noted discrepancy: the journal's header comment says "structured", but its mesh
scheme is `pave`.
Files: `topology_mech_ex13.i` (sha256 `d1cd04ae…e691`), `topology_mech_ex13.jou`, `problem_geometry_figure.png` (`33380568…bbb2`);
originals verified unchanged (`remediation original sources: PASS (5 files)`, counting the identical copies).

## 5. No canonical absolute paths in agent-visible files
- Example 7 is retained as the near-miss candidate. Its card still describes it truthfully as a full-domain Helmholtz
  cantilever with no symmetry plane.
- Every `problem_card.yaml` / `provenance.yaml` now carries `source_identifier` / `source_file_identifier` values
  (`MORPHORM-CANDIDATE-EX01|07|13|16/<role>`). Each card states explicitly that these are logical identifiers, not
  filesystem paths and not original locations. The Globus provenance uses `MORPHORM-MANUAL-USER-V1`,
  `MORPHORM-MANUAL-THEORY-V1`, `MORPHORM-TARGET-SUPPORT-V1/problem_figure` and `MORPHORM-DOCS-SOURCE-V1`.
- Complete canonical paths and the mapping are only in `researcher_only/provenance/agent_visible_to_canonical_source_map.tsv`
  (17 rows) and in researcher-side `setup/` records.
- Final scan of `chpc_candidate_archive/`, `globus_source_root/`, `github_control_repo_worktree/` (excluding `.git`),
  `baseline/trial_01`, `clio/trial_01` and the loader/modulefiles finds no original source path, no `Morphorm_Full_Examples_Tests`,
  `Morphorm_ground_truth`, `ThesisExperiments`, `docs/examples`, Example 8 file or directory name, or account name. The only
  absolute paths left are E3 access locations: the loader (3 occurrences), and the `posix_root` of the two collections in the catalog.
- Checksums, manifests and cards were all regenerated and verify. The new control-repo checksum list also passes in a fresh clone of the pinned commit.
- Residual (not changed, reported): the byte-identical runtime copies' own `PROVENANCE.md` files (Morphorm and Cubit), which
  are readable through the loader-visible runtime, name the account as their assembler. That is an account name, not a path,
  and no ground truth. Editing them would break the verified runtime identity, so this is left as a researcher decision (the
  sandbox could mask them).

## 6. Permissions (only inside E3)
`globus_source_root/`: dirs 755→700, files 644→600 (owner keeps access; group/other none; 0 entries with group/other bits).
Manifest verifies afterwards. Record: `setup/permissions_audit_remediation.md`. The temporary `u+w` used for the two moves
and the archive regeneration was restored (archive: dirs 555, files 444). No permission was changed on any original, source
root, E1/E2 or shared thesis path. **Owner-only modes do not protect against an agent running under the same Unix account.**
Copies of the manuals outside `globus_source_root/` (originals; trial_02..05 legacy packets; the moved trial_01 legacy packet)
remain group/world-readable. They were outside this step's scope and are reported in the audit.

## 7. Sandbox status — ground truth is NOT technically isolated
Mechanism: `/usr/bin/bwrap` (bubblewrap 0.4.0, RHEL 8 OS package, not setuid, unprivileged user namespaces). Prototype:
`automation/sandbox/`. Harmless validation on notchpeak1 (`validation_record_login_node.txt`):
- Permitted E3 paths are visible: trial dir, `agent-inputs/` (read-only), candidate archive including `example_13`, E3 loader.
- Not visible: E3 `researcher_only/` and `setup/`, `Morphorm_ground_truth`, E1, E2, `ThesisExperiments`,
  `Morphorm_Full_Examples_Tests`, the Morphorm source/docs tree, the original manuals, `Thesis/researcher_only`, other trials,
  other Daisy directories, and every home directory.
- The loader works inside the sandbox; the pinned Claude Code is visible at `/opt/e3/bin/claude`.
- The launcher refuses mounts that would expose denied roots.

**Not isolated for a trial**, for these reasons:
- Slurm authentication works from inside the sandbox, and the specification requires a Slurm batch job. Jobs run outside
  the namespace with full access.
- Validated on a login node only.
- Not wired into the runner.
- No Cubit licence inside the sandbox.

Decision needed: `setup/GROUND_TRUTH_ISOLATION_ACTION_REQUIRED.md`. Options: a separate Unix account (recommended), a
researcher-side job broker with sandboxed job scripts, or moving reference material off CHPC-mounted storage for the
duration of E3.

## 8. Environment loader
`automation/environment/load_morphorm_e3.sh` (sha256 `25b77e66…5b9a`, `bash -n` PASS). It references no `ThesisExperiments`
path and no account path. It uses CHPC Lmod, `gcc/11.2.0`, `openmpi/5.0.3` and E3-local byte-identical copies of the
approved runtime and Cubit:
- Morphorm `SHA256SUMS` passes 2064/2064, and its hash `fa0d97b9…e4d2` equals the frozen-configuration value.
- Cubit: all 30,819 file hashes are identical.

Loading succeeds in an empty shell, a login shell and the sandbox. Executables resolve to the E3 copies, there are 0
obsolete-tree entries in `PATH`/`LD_LIBRARY_PATH`/`MODULEPATH`, and `ldd` reports 0 missing libraries.

Deviations, documented in its README:
- Root paths are new.
- Guards are added.
- When Lmod is absent, the loader initialises CHPC Lmod. The original fallback, Tcl modules, cannot load the Lua modulefiles.
- Modulefile hashes are new.

Not reproducible in the sandbox: Cubit licence activation (account home). `ENVIRONMENT_ACTION_REQUIRED.md` was not needed:
no shared environment, licence, module or source tree was changed. Agent-visible documents now point to the E3 loader:
`software_contract.md`, `version_provenance.yaml`, the catalog, and `trial_context.md` via `prepare_baseline_trial.sh`.

## 9. GitHub
- Repository: https://github.com/DaisyQuach/daisy-e3-distributed-context-control (SSH `git@github.com:DaisyQuach/daisy-e3-distributed-context-control.git`).
- New commit **`c3b87369b51ee9e33f66c55f9608a16e447ab3e7`** (parent `333edab`), pushed; `git ls-remote` confirms `main` = `c3b8736`.
- Privacy: API `private: true`, `visibility: private`; unauthenticated `GET api.github.com/repos/…` → HTTP 404.
- Changed files: `README.md`; `catalog/permitted_storage_catalog.yaml` (v2: manifests `d856bed2…`/`3c89c503…`, Example 13 in,
  Example 2 out, identifier note, E3 loader); `catalog/checksums.sha256`; cards `example_01`, `example_07`, `example_16_restart`
  (identifier + new card hash), `example_13` (added), `example_02` (deleted), `symmetry_plane_target` (identifier);
  `protocol/access_rules.md`.
- Pre-push scan: no manuals, binaries, completed examples, original source paths, account name, credentials or ground truth.
- The pinned commit now used by the baseline config is `c3b8736`. A fresh clone at the pin verifies its checksums, and its
  prompt and specification are byte-identical to the E3 copies.

## 10. Globus
Unchanged: **not configured** (no collection, no CLI session). `globus_source_root/` is ready (manifest `d856bed2…`, now
owner-only). See `setup/GLOBUS_ACTION_REQUIRED.md`. The baseline dry run still stops at `globus_not_configured` (exit 3,
nothing written).

## 11. Claude Code 2.1.295 pin
Present and unchanged at `$HOME/.local/share/claude/versions/2.1.295` (regular file; `$HOME` = account home, whose literal
path is withheld by the path policy).
- `--version`: `2.1.295 (Claude Code)`.
- SHA-256 `4503bfe11a6c7fcc1e0b39b5e0d347c04248f750b03b0977b3ad6b531fe6f358`.
- All required headless flags are present (list and full `--help` in `COMPUTE_NODE_QUALIFICATION_ACTION_REQUIRED.md` §3 and
  `setup/remediation/claude_2.1.295_help.txt`).
- `~/.local/bin/claude` → 2.1.296 was not followed. `CLAUDE_VERSION_ACTION_REQUIRED.md` was not needed.
- Risk: the file sits in the auto-updater's versions directory.

## 12. Blockers before any counted E3 trial
1. **Ground-truth isolation** is not technically verified: Slurm jobs escape the sandbox, and the sandbox is not integrated
   or compute-node-validated → `setup/GROUND_TRUTH_ISOLATION_ACTION_REQUIRED.md` (researcher/administrator decision), then
   `automation/sandbox/sandbox_validation_plan.md` B1–B7.
2. **Compute-node qualification** (`$SLURM_TMPDIR` existence/path/ownership/writability/account-name, staging clearing and
   retention, loader and sandbox on the compute node) → `setup/COMPUTE_NODE_QUALIFICATION_ACTION_REQUIRED.md`.
3. **Globus** not configured → `setup/GLOBUS_ACTION_REQUIRED.md`. The alternative is a recorded `posix_readonly_fallback`
   decision, with no staging-performance claim (`researcher_only/evaluation/E3_SCORING_SCOPE.md` §4).
4. **Cubit licence inside the sandbox** (researcher decision; sandbox plan B5).
5. **trial_02..05 legacy packets** must be moved out before those trials are converted (§2).
6. Decide on the account name in the runtime copies' `PROVENANCE.md` (§5; mask, or accept).

Resolved by this remediation:
- The agent-visible packet for trial_01 is unambiguous.
- The candidate archive is clean (no incomplete package, no canonical paths).
- The environment no longer depends on the obsolete tree.
- The Claude pin is verified.
- The scoring scope is frozen (`researcher_only/evaluation/E3_SCORING_SCOPE.md`).

## 13. E1, E2, originals and ThesisExperiments unchanged
Method: `find -printf '%p %y %s %m %T@ %C@'` snapshots at 00:32:58Z (before any write) and 00:57:16Z, compared line by line.
| Tree | Entries before / after | Differences |
|---|---|---|
| `Thesis/runs/E1_uninterrupted_example8` | 1757 / 1757 | **0** |
| `ThesisExperiments` | 39897 / 39897 | **0** (read only: loader, modulefiles, runtime/tool trees copied) |
| `Morphorm_Full_Examples_Tests` | 1255 / 1255 | **0** |
| `Morphorm_ground_truth` | 1073 / 1073 | **0** (never opened) |
| `Morphorm` (source/docs) | 130855 / 130855 | **0** |
| `morphorm_manuals` | 4 / 4 | **0** |
| `Thesis/common` | 36 / 36 | **0** |
| `Thesis/runs/E2_interrupted_recovery_example16` | 2474 / 2532 | 72 lines, all under `baseline/trial_05/work/` — written by the researcher's concurrently running E2 jobs (`agent_E2-example16-baseline-05_session_b` 16169529, `ex16_stage2` 16169770); this remediation wrote nothing there |

Original source content also verifies: `setup/source_inventory.sha256` 30/30 PASS, Example 13 originals 5/5 PASS.
No path containing the account name was created. Inside E3 and every protected tree, `rm -rf`, `git reset` and
`git checkout` were not used; the only deletion was the single-file `git rm` (§1). **Disclosure:** outside E3, in the
session scratchpad, I ran `rm -rf -- <scratchpad>/pinclone` (a no-op: the directory did not exist yet) immediately before
creating a throwaway verification clone there, and `git checkout --detach c3b8736` inside that scratch clone (to verify the
pin, §9). Neither touched E3 or any protected path, but both fall outside the letter of the instructions. Two temporary
manifest files briefly created inside `globus_source_root/` (`MANIFEST.tsv.new`, `MANIFEST.sha256.new`) were renamed onto the
manifests, which were then regenerated cleanly. No stray file remains.
