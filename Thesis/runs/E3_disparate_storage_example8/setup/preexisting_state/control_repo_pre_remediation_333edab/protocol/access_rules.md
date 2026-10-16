# Access rules

## Permitted
| Access | Scope |
|---|---|
| read | the collections listed in `catalog/permitted_storage_catalog.yaml`, through the access method listed there |
| read | `agent-inputs/` of your own trial (read-only; never modify) |
| read/write | your own trial root: `work/`, `jobs/`, `logs/`, `outputs/`, `provenance/`, `staging-manifest/` |
| read/write | the node-local staging directory in `$E3_STAGING_DIR` (created fresh for this trial) |
| execute | the approved software interface (`documentation/curated_permitted_materials/software_contract.md` in the private source collection), Slurm commands for your own jobs |

## Not permitted
1. Any storage location not listed in the catalog. Original locations quoted in `problem_card.yaml` / `provenance.yaml`
   files are provenance records, **not** access paths; do not open them.
2. Directories adjacent to the permitted collections that are not themselves listed (for example parent directories,
   researcher records, other trials' workspaces, other experiments).
3. Software source/installation trees, their documentation trees, example or test trees, and any completed run outputs,
   reference results, histories, tolerances or scoring criteria.
4. Writing, renaming, moving, deleting or changing permissions of anything in a source collection.
5. Web search, downloads, or external reference retrieval. Network use is limited to the model provider, CHPC scheduler and
   module access, and (if the catalog lists it) noninteractive access to the private control repository and Globus collection.
6. Credentials: never print, copy, or store tokens or credential files.

Any access to a non-permitted location is detectable from the session record and disqualifies the trial.
