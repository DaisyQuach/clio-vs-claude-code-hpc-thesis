# E3 Phase 3 — harmless compute-node qualification (non-scored)

**Job:** 16172196 `e3-pilot-qual-nonscored`. Account and partition `hochhalter-np`; 1 node, 1 CPU, 2 GB, 15 min limit.
Node `notch204`. Ran 2026-10-10T03:40:36Z–03:41:02Z (26 s). State COMPLETED, exit 0:0.

**Evidence (disposable pilot root):** `Daisy/E3_access_pilot/phase3/`
- `job/e3_pilot_qual.sbatch`, with its `.sha256`
- `out/e3-pilot-qual-16172196.out` and `.err` (stderr is empty)
- `records/sacct_16172196.txt`, `records/job_id.txt`, `records/SHA256SUMS_16172196.txt`
- The output is redacted: the home path appears as `$HOME` and the account name as `<account>`, with 0 occurrences of
  the account name.

**What the job did not do:** call Claude for a model session, call CLIO, run Morphorm or Cubit, run an E3 runner, or read
an E3 research packet. The only file copied or transferred was the pilot file `phase3/input/hello.txt`. The approved
collection was only listed (6 entry names). The pinned GitHub commit was checked as an object only (blobless clone, no
checkout).

| Check | Result | Interpretation |
|---|---|---|
| Host, effective user, cwd | `notch204`, the researcher account, cwd = submit directory | ordinary user environment, as planned |
| `$SLURM_TMPDIR` | **unset** | **E3's staging design assumes it; a fixed node-local root must be chosen** (see below) |
| Slurm node-local config (login node, read-only) | `TmpFS=/scratch/local`, `JobContainerType=(null)`, `PrologFlags=Alloc,Contain` | there is no per-job private `/tmp`; `/scratch/local` was absent or not writable at its top level on `notch204` |
| `/tmp` on the node | writable, 98 GB free | node-local, but shared by every job on the node and not cleaned per job |
| Pilot-owned file read/write | yes | — |
| git / gh / Globus CLI | 2.43.7 / 2.0.0 / 3.43.0 (pinned venv) | available |
| Claude Code | `2.1.295 (Claude Code)`, SHA-256 `4503bfe1…f358`, all headless flags present | pin OK on the compute node (version/help only, no model call) |
| GitHub | `ls-remote` rc 0, `main` = `ab341a1…`; blobless clone rc 0; pin object `commit`; `gh auth status` rc 0 | authenticated, noninteractive read at the pin works from the compute node |
| Globus | `whoami` rc 0; guest collection `6dcea62e…` lists 6 entries; pilot transfer (mapped → mapped) `SUCCEEDED`, bytes identical | noninteractive Globus works from the compute node, including transfer submission and wait |
| Network | transfer API 404 (reachable), auth 302, **GCS manager 200**, guest HTTPS 307, github.com 200, api.github.com 200 | compute nodes reach the CHPC DMZ servers that login node notchpeak1 cannot |
| E3 loader | rc 0; 0 `ThesisExperiments` entries; `XMLGenerator`, `PlatoMain`, `analyze_MPMD` and `cubit` resolve to E3 runtime copies; modules `gcc/11.2.0 openmpi/5.0.3 morphorm/approved-runtime cubit-edu/2026.8` | loader works on the compute node (nothing executed) |
| Cubit licence location | `$HOME/.config/Coreform/` present on the node; `Cubit_ticket`, `cubit_creds`, `licenses` readable | the ordinary job environment sees the per-user licence. Whether Cubit actually accepts it is unproven, because Cubit was not launched |
| Retention record | not written | `$SLURM_TMPDIR` was unset, so no node-local probe dir was made |

## Consequences and open decisions
1. **Node-local staging root.** `$SLURM_TMPDIR` does not exist on these nodes. The runner, `init_node_local_staging.sh`,
   `staging_rules.md` and the qualification plan all assume it. One fixed root must be chosen and used identically for all
   ten trials: a `/scratch/local` per-job directory (needs a stat-only probe to confirm the layout), or
   `/tmp/e3/<system>/<trial_id>`. With the second, the runner records the listing before the job ends, and post-trial
   clean-up is a recorded step.
2. **How Globus files reach node-local storage.** The approved guest collection is read-only. A Globus transfer needs a
   destination collection, and the pilot shows the transfer, then copy, method works on a compute node. The catalog now
   forbids every collection except the guest one, so a destination has to be approved:
   - (a) the CHPC mapped collection, as destination only, limited to the trial's own inbox directory; or
   - (b) a second private guest collection, rooted at the trial directories and used only as a destination.
   A direct HTTPS download from the guest collection would need per-collection HTTPS consent and token handling by the
   agent, so it is not recommended.
3. **GitHub and Globus authentication at launch.** Both work noninteractively on the compute node with the researcher's
   stored credentials. The Globus high-assurance timeout is one year. A fixed pre-trial check (`whoami`, `ls-remote`)
   is already part of the runner.
4. **Cubit licence acceptance.** Only an actual `cubit -batch` run could prove it, and this task does not permit one.
   This stays open until the researcher allows the trivial check in `COMPUTE_NODE_QUALIFICATION_ACTION_REQUIRED.md` §2a.
5. **Side note:** the GCS manager is reachable from compute nodes. The researcher could still run
   `globus gcs collection update 6dcea62e-130d-47a9-8b77-80fba6f58693 --private` inside a short job, after the
   `globus login --gcs` consent, if a non-discoverable collection is wanted later.
