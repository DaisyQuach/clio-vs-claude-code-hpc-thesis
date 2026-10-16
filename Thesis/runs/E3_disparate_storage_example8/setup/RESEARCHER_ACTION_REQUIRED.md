# RESEARCHER ACTION REQUIRED — start the allocation and dedicated server for the CLIO access pilot (Phase 5.5)

Date: 2026-10-10 UTC. E3 is **NO-GO** until the pilot passes. Status: `setup/E3_BLOCKER_STATUS.yaml`.
Procedure: `setup/CLIO_RUNBOOK.md`.

Under your deployment definition you start the allocation and the CLIO service. The pilot runs entirely outside the
thesis repository, in `Daisy/E3_access_pilot/phase5_clio/`:
- a scratch E3 tree with pilot-only collections;
- one pilot file as the "Globus source";
- a pilot prompt (`phase5_clio/pilot_prompt.md`) that only prints host and environment, checks the pinned commit,
  stages the pilot file through the Globus helper, and writes a summary.

This is the one approved CLIO session. It makes model calls (`claude-fable-5-1`). There is no E3 task, no Morphorm or
Cubit, and no scientific job.

## Your action (CHPC login node)
```bash
salloc --account=hochhalter-np --partition=hochhalter-np --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=32G \
       --time=01:00:00 --job-name=e3-clio-pilot
hostname; echo "$SLURM_JOB_ID"                      # you should now be on a compute node
export E3_ROOT_OVERRIDE=/uufs/chpc.utah.edu/common/home/chet/Daisy/E3_access_pilot/phase5_clio/E3
$E3_ROOT_OVERRIDE/automation/clio/start_e3_clio_server.sh --trial-dir $E3_ROOT_OVERRIDE/clio/trial_01 --port 17861 --dry-run
$E3_ROOT_OVERRIDE/automation/clio/start_e3_clio_server.sh --trial-dir $E3_ROOT_OVERRIDE/clio/trial_01 --port 17861
```
Keep that shell open; the allocation must stay alive. Connecting the Desktop is optional. If you do connect, only watch:
send no message, and grant nothing.

## Verify (safe, read-only, in the same shell)
```bash
curl --noproxy '*' -s http://127.0.0.1:17861/v1/health; echo
cat $E3_ROOT_OVERRIDE/.agent_runtime/clio/E3-clio-trial_01/instance.json | head -20
```
Expected: a health response, and an instance record showing your node, the job ID and `clio_agent_version`.

## Then send
> E3 CLIO pilot server is running: job <JOBID>, port 17861. Resume E3 readiness.

## What I'll do next
1. Run the automated runner into your allocation with `srun --jobid=<JOBID> --overlap`, in test mode with the pilot
   prompt.
2. Retain the complete session record and audit it.
3. Report whether the CHPC-side agent reached the pinned GitHub commit and the Globus staging path, and that the
   Desktop played no data-access role.
4. Run the Phase 7 freeze only if every check passes.
