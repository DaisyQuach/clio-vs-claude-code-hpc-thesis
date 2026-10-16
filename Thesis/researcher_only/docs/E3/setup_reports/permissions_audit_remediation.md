# Permissions audit — E3 remediation (step 5)

Change applied at 2026-10-10T00:51:44Z (UTC), as the owning account, with `chmod -R go-rwx globus_source_root` run from the E3 root.
Scope: **only** `globus_source_root/` (newly created E3 material: the private Globus-ready source tree and its manual
copies). No other permission was changed by this step: not the original manuals (`Daisy/morphorm_manuals/`, still
`644`/`755`), not any source root, not E1/E2, not shared thesis directories, not `chpc_candidate_archive/` (unchanged:
dirs `555`, files `444`).

Result: owner keeps read/write (files `600`) and traversal (dirs `700`); group `hochhalter` and other CHPC users have
no access. Entries with any group/other bit after the change: **0**. `sha256sum -c MANIFEST.sha256` after the change: PASS.

| Path (relative to `globus_source_root/`) | Before | After |
|---|---|---|
| `.` | `drwxr-xr-x (755)` | `drwx------ (700)` |
| `documentation` | `drwxr-xr-x (755)` | `drwx------ (700)` |
| `documentation/curated_permitted_materials` | `drwxr-xr-x (755)` | `drwx------ (700)` |
| `documentation/curated_permitted_materials/compute_resources.md` | `-rw-r--r-- (644)` | `-rw------- (600)` |
| `documentation/curated_permitted_materials/software_contract.md` | `-rw-r--r-- (644)` | `-rw------- (600)` |
| `documentation/curated_readme.md` | `-rw-r--r-- (644)` | `-rw------- (600)` |
| `documentation/MANIFEST_README.md` | `-rw-r--r-- (644)` | `-rw------- (600)` |
| `documentation/version_provenance.yaml` | `-rw-r--r-- (644)` | `-rw------- (600)` |
| `MANIFEST.sha256` | `-rw-r--r-- (644)` | `-rw------- (600)` |
| `MANIFEST.tsv` | `-rw-r--r-- (644)` | `-rw------- (600)` |
| `manuals` | `drwxr-xr-x (755)` | `drwx------ (700)` |
| `manuals/Morphorm_Theory_Manual.pdf` | `-rw-r--r-- (644)` | `-rw------- (600)` |
| `manuals/Morphorm_User_Manual.pdf` | `-rw-r--r-- (644)` | `-rw------- (600)` |
| `README.md` | `-rw-r--r-- (644)` | `-rw------- (600)` |
| `target_materials` | `drwxr-xr-x (755)` | `drwx------ (700)` |
| `target_materials/symmetry_plane_cantilever` | `drwxr-xr-x (755)` | `drwx------ (700)` |
| `target_materials/symmetry_plane_cantilever/geometry_and_loading_figure.png` | `-rw-r--r-- (644)` | `-rw------- (600)` |
| `target_materials/symmetry_plane_cantilever/permitted_starting_materials` | `drwxr-xr-x (755)` | `drwx------ (700)` |
| `target_materials/symmetry_plane_cantilever/permitted_starting_materials/README.md` | `-rw-r--r-- (644)` | `-rw------- (600)` |
| `target_materials/symmetry_plane_cantilever/problem_specification.md` | `-rw-r--r-- (644)` | `-rw------- (600)` |
| `target_materials/symmetry_plane_cantilever/README.md` | `-rw-r--r-- (644)` | `-rw------- (600)` |

## Limits of this protection
- **Owner-only permissions do not protect against an agent running under the same Unix account.** The baseline and CLIO
  agents run as the owning account, so they can read (and change the mode of) everything in this tree. Isolation from the
  agent is a separate problem; see `setup/GROUND_TRUTH_ISOLATION_ACTION_REQUIRED.md` and `automation/sandbox/`.
  *Update 2026-10-10:* E3 adopts the procedural E1/E2 policy (prohibited and audited, not technically enforced); the
  sandbox is optional and is not the runtime boundary (`setup/E3_PROCEDURAL_ACCESS_UPDATE.md`).
- A future Globus collection registered on this directory serves files as the owning account, so owner-only modes do not
  prevent the researcher's own Globus transfers.
- Other copies of the same manuals that this step did not touch (outside the step's scope) remain readable by group and
  other: the originals in `Daisy/morphorm_manuals/`; the pre-existing `baseline/trial_02..05/agent_inputs/manuals/`
  (`444`); and the legacy packet moved at remediation to
  `setup/preexisting_state/legacy_baseline_trial01_agent_inputs/manuals/` (`444`, modes preserved by the move). If those
  should also be private, that is a separate researcher decision.
- Parent directories (E3 root `755`, `Thesis/runs/` `755`) are unchanged; they reveal directory names, not file contents.

## Update 2026-10-10 (Globus configuration)
`chmod -R a-w globus_source_root` (dirs 700 -> 500, files 600 -> 400; pre-change modes in
`setup/preexisting_state/globus_source_root_modes.pre_readonly.txt`). Write bits remaining: 0, and `MANIFEST.sha256`
verifies. Reason: the guest collection `6dcea62e-130d-47a9-8b77-80fba6f58693` serves files as the owning account, and its
implicit owner rule is `rw`. With the filesystem read-only, a Globus `mkdir` probe on the collection returned
`EndpointPermissionDenied` (HTTP 403). The owner could still restore write bits; any change is detectable from the manifest.
