# ACTION REQUIRED — ground-truth isolation is not technically verified

Status (2026-10-10 UTC): **E3 is not protected against ground-truth access. No counted trial may run.**

## What was achieved
A non-destructive bubblewrap sandbox prototype (`automation/sandbox/`) hides `Morphorm_ground_truth`, E3
`researcher_only/`, E1/E2, `ThesisExperiments`, other Daisy directories and all home directories from the **agent
process**. This was validated on the notchpeak1 login node with a harmless probe (`automation/sandbox/validation_record_login_node.txt`).
No original ground-truth directory was moved, deleted or altered.

## Exact limitation
1. **Slurm jobs run outside the sandbox.** The frozen specification (`E3-SPC-v1` §7) requires the optimisation to run as a
   Slurm batch job. With the scheduler exposed, munge authentication works from inside the sandbox (validated with a
   read-only `squeue`). Every job or step the agent creates (`sbatch`, `srun`, `salloc`) is started by Slurm daemons
   outside the agent's mount namespace and runs as the same Unix account with its full filesystem view. A job script
   written by the agent could therefore read `Morphorm_ground_truth/`, `Thesis/researcher_only/ground_truth/example_8/`,
   E3 `researcher_only/`, the completed Example 8 runs in the example-test collection, or the Example 8 deck in the
   Morphorm documentation tree, and copy content into the trial's outputs. Hiding the scheduler (`--scheduler none`)
   closes this but makes the task as specified impossible.
2. **Same Unix account.** Owner-only modes (`researcher_only/` 700, `globus_source_root/` now 700/600) do not stop a
   process running as the owner. Any process the agent can start outside the namespace has full access.
3. **Validated on a login node only.** The agent host runs on a compute node; bubblewrap/user namespaces, munge and ssh
   behaviour there have not been checked (requires a non-scored allocation; `setup/COMPUTE_NODE_QUALIFICATION_ACTION_REQUIRED.md`).
4. **Not integrated** into `run_baseline_e3_trial.sh` / the CLIO runner.
5. **Cubit licence** activation lives in the account home, which the sandbox does not mount.

## Minimum researcher/administrator decision needed (choose one)
| Option | What it needs | Effect |
|---|---|---|
| **A. Separate Unix account for agent trials** (recommended for strongest isolation) | CHPC account for a trial identity (administrator), in a group that has no read access to `Morphorm_ground_truth`, `Thesis/researcher_only`, E3 `researcher_only/`, E1/E2, `ThesisExperiments` and the example-test collection; read access to the E3 trial paths, candidate archive, E3 runtime copy; its own Claude/GitHub/Globus credentials and Cubit licence; Slurm account membership | Kernel permission checks apply to the agent **and to its Slurm jobs**. Requires changing group/other permissions on researcher-owned trees (a researcher decision; not done here). |
| **B. Same account + researcher-side job broker** | Implement and validate (plan steps B2–B7): the agent runs in the sandbox with `--scheduler none`; a broker outside the sandbox accepts job requests from the trial's `jobs/` directory and submits each with its script executed via `launch_e3_sandbox.sh --scheduler none` on the compute node; then validate on a compute node | Jobs are confined to the same mount view; protection depends on the broker being the only submission path, which must be verified. Researcher must accept it as the protocol's "Slurm batch job" mechanism (recorded deviation). |
| **C. Remove researcher-only reference material from storage mounted on CHPC during E3 trials** | Researcher moves (not deletes) the ground-truth and Example 8 reference material to storage not mounted on CHPC nodes for the duration of E3, and restores it afterwards; recorded with hashes | Simple, but alters the location of originals (explicitly not done by this remediation) and must cover every copy (ground-truth package, thesis ground truth, example-test Example 8, docs-tree Example 8 deck/journal/figures). |

Until one option is implemented and validated, `setup/E3_REMEDIATION_REPORT.md` and every trial manifest must state that
ground truth is **not** technically isolated, and no counted E3 trial may be run.
