# E3 filesystem sandbox — prototype (not yet protecting any trial)

Purpose: the baseline and CLIO agents run under the same Unix account that can read `Morphorm_ground_truth`, E3
`researcher_only/`, E1/E2 and the obsolete `ThesisExperiments` tree. File permissions cannot separate them, and a prompt
prohibition is not access control. This prototype gives the agent process a private mount namespace in which those
locations simply do not exist.

**Status: prototype only.** It is not wired into `automation/baseline/run_baseline_e3_trial.sh`, it has been validated on
a login node only, and it does **not** isolate Slurm jobs the agent submits (see Limitations). Ground truth is therefore
**not** technically isolated for a counted trial: `setup/GROUND_TRUTH_ISOLATION_ACTION_REQUIRED.md`.

## Mechanism
- `/usr/bin/bwrap` — bubblewrap 0.4.0 from the RHEL 8 OS package `bubblewrap-0.4.0-2.el8_10` (owned by root, **not**
  setuid). It runs unprivileged using kernel user namespaces (`/proc/sys/user/max_user_namespaces` = 384706 on notchpeak1).
  No elevated privilege was requested or used.
- CHPC also provides Apptainer modules (`apptainer/1.0.3` … `1.4.0`). Apptainer would need an image and bind
  configuration; bubblewrap is used for the prototype because it needs neither. No container image was built.
- The sandbox starts from an empty mount namespace and an empty environment (`env -i`): only the entries in
  `allowed_paths.txt` are mounted; `HOME` is a tmpfs (`/tmp/e3home`); new PID/IPC/UTS namespaces; `--die-with-parent`,
  `--new-session`. Network is shared (the agent needs the model API, GitHub and later Globus).

## Files
| File | Content |
|---|---|
| `launch_e3_sandbox.sh` | launcher: `launch_e3_sandbox.sh --system baseline|clio --trial-dir <E3>/<system>/trial_NN [options] -- <command>` (`--help`) |
| `allowed_paths.txt` | everything mounted, with mode and condition |
| `denied_paths.txt` | roots that must never be exposed; the launcher refuses to start if an exposed path is at, under, or above one of them (the account home is added at run time from `$HOME`) |
| `sandbox_probe.sh` | harmless visibility probe to run inside the sandbox (stats and lists only) |
| `sandbox_validation_plan.md` | what has been validated, and what must still be validated before any counted trial |
| `validation_record_login_node.txt` | record of the validation run on 2026-10-10 (login node) |

## What the sandbox exposes
E3 trial-specific paths (trial dir read-write with `agent-inputs/`, `manifest.yaml`, `README.md` read-only; optional
node-local staging dir; optional per-session Claude config dir), the candidate archive (read-only), the private source
collection only under the recorded `posix_readonly_fallback` decision (read-only), the private control-repository
checkout (read-only), the E3 loader with its modulefiles and E3-local runtime copies (read-only; not the environment
README/inventory), the pinned Claude Code executable (one file, mounted read-only at the neutral path
`/opt/e3/bin/claude`), OS paths (`/usr`, `/etc`), CHPC system software (`/uufs/chpc.utah.edu/sys`: Lmod, gcc, openmpi;
contains no Morphorm or Cubit), and, with `--scheduler direct`, the Slurm client tree and the munge socket.

## What it hides (validated)
`Morphorm_ground_truth`, E3 `researcher_only/` and `setup/`, the rest of E3 `automation/`, other trials, E1, E2,
`ThesisExperiments`, `Morphorm_Full_Examples_Tests`, the Morphorm source/docs tree, the original manuals,
`Thesis/researcher_only`, every other Daisy directory and every home directory (including the account home).

## Limitations (all must be resolved or accepted before a counted trial)
1. **Slurm jobs escape the sandbox.** With `--scheduler direct`, munge authentication works from inside (validated with
   a read-only `squeue`). Any `sbatch`/`srun`/`salloc` the agent issues creates a job or step started by Slurm daemons
   outside this namespace, with the account's full filesystem view, so a job script could read ground truth. The frozen
   specification requires the optimisation to run as a Slurm batch job, so `--scheduler none` alone does not fit the
   protocol.
2. **Validated on a login node only.** Counted trials run the agent inside an agent-host allocation on a compute node.
   bubblewrap, user namespaces, Lmod, munge and `$SLURM_TMPDIR` behaviour must be re-validated there.
3. **Not integrated.** `run_baseline_e3_trial.sh` still launches Claude Code directly. Integration (wrap the `claude`
   command and the staging/record steps that run during the session) is future work.
4. **Cubit licence.** Cubit's educational licence activation lives in the account home (`$HOME/.config/Coreform`), which is
   deliberately not mounted, so Cubit is expected to be unlicensed in the sandbox (not executed here).
5. **Same account, same kernel.** The namespace hides paths; it is not a security boundary against kernel exploits, and
   anything the agent starts outside the namespace (limitation 1) runs with full access. Outbound ssh was refused in the
   test (no keys; host-based signing unavailable in the user namespace) but this was checked on a login node only.
6. Network is not restricted (by design, for the model API/GitHub/Globus).
