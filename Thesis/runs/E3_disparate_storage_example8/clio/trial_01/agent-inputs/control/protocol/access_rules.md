# Access rules

## Access model
E3 uses the same access model as Experiments 1 and 2. Researcher-only material is excluded from the agent-visible task
packet, and agents are instructed and audited not to access it. Because experimental agents and their Slurm jobs run
under the researcher's account, this separation is procedural rather than a technically enforced filesystem security
boundary. File permissions are therefore not a guide to what is allowed: a location that can be read is still
prohibited unless it is listed under "Permitted" below. This applies equally to the agent session and to every Slurm
job or job step it submits.

## Permitted
| Access | Scope |
|---|---|
| read | the collections listed in `catalog/permitted_storage_catalog.yaml`, through the access method listed there |
| read | `agent-inputs/` of your own trial (read-only; never modify) |
| read/write | your own trial root: `work/`, `jobs/`, `logs/`, `outputs/`, `provenance/`, `staging-manifest/` |
| Globus destination | your own trial's `staging-inbox/` only, through the destination collection listed in the catalog, for transfers from the private source collection (`globus_stage_file.sh`) |
| read/write | the node-local staging directory in `$E3_STAGING_DIR` (created fresh for this trial) |
| execute | the approved software interface (`documentation/curated_permitted_materials/software_contract.md` in the private source collection): source its loader `load_morphorm_e3.sh` and use what it puts on `PATH`; Slurm commands for your own jobs; the pinned Globus CLI named in `agent-inputs/globus_access.txt` |

## Not permitted
1. Any storage location not listed in the catalog. Source identifiers such as `MORPHORM-CANDIDATE-EX07` in artifact cards,
   `problem_card.yaml` and `provenance.yaml` are logical identifiers, **not** paths; do not try to resolve or locate them.
   The approved software's own directories are used only through the loader, not browsed as documentation.
2. Directories adjacent to the permitted collections that are not themselves listed (for example parent directories,
   researcher records, other trials' workspaces, other experiments).
3. Software source/installation trees, their documentation trees, example or test trees, and any completed run outputs,
   reference results, histories, tolerances or scoring criteria.
4. Writing, renaming, moving, deleting or changing permissions of anything in a source collection.
5. Web search, downloads, or external reference retrieval. Network use is limited to the model provider, CHPC scheduler and
   module access, and (if the catalog lists it) noninteractive access to the private control repository and Globus collection.
6. Credentials: never print, copy, or store tokens or credential files.
7. Researcher-only material of any kind: researcher records, completed reference packages or runs of the target problem,
   scoring records, validation records and acceptance criteria. This includes reading such material from a Slurm job
   script or from staging, not only from the agent session.

## Audit
Every path used in the session's tool calls, the job scripts under `jobs/`, the job logs, the staging records and the
provenance records are kept and audited after the trial. Any access to a non-permitted location is detectable from these
records and disqualifies the trial.
