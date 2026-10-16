# E3 environment loader (`automation/environment/`)

`load_morphorm_e3.sh` is the E3 approved software interface. It replaces, for E3 only, the thesis loader that depended on
the obsolete `ThesisExperiments` tree. Everything it needs lives in this directory or in CHPC system software:

```bash
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/automation/environment/load_morphorm_e3.sh
```

| Path | Content |
|---|---|
| `load_morphorm_e3.sh` | the loader (checksum in `load_morphorm_e3.sha256`) |
| `modulefiles/Core/morphorm/approved-runtime.lua` | E3 modulefile for the approved Morphorm runtime |
| `modulefiles/Core/cubit-edu/2026.8.lua` | E3 modulefile for the approved Coreform Cubit |
| `runtime/morphorm/` | byte-identical copy of the approved Morphorm runtime (read-only) |
| `runtime/coreform_cubit/` | byte-identical copy of the approved Coreform Cubit 2026.8 bundle and launchers (read-only) |
| `runtime_manifests/coreform_cubit.sha256` | per-file hashes of the Cubit copy |
| `environment_inventory.txt` | versions, hashes, verification results |
| `.copy_started_utc`, `.copy_finished_utc` | copy timestamps |

## Source loader inspected (read only, not modified)
- `Thesis/common/scripts/load_approved_software.sh` (sha256 `38848816…43c0`) — sets the default
  `THESIS_CUBIT_MODULE=cubit-edu/2026.8`, falls back to `/etc/profile.d/modules.sh` when `module` is undefined, and
  sources the obsolete-tree loader.
- The obsolete-tree loader `ThesisExperiments/common/scripts/load_approved_software.sh` (sha256 `d459b935…ab37`) and the
  two modulefiles it uses (`morphorm/approved-runtime.lua`, `cubit-edu/2026.8.lua`), the runtime's `env.sh`, its
  `provenance/` records and the Cubit `PROVENANCE.md` and `cubit` launcher. The runtime and the Cubit bundle were then
  copied (read-only on the source side) into `runtime/`. Nothing in the obsolete tree was changed.

## Behaviour retained
- Same interface contract: source it; it changes no shell options and returns non-zero on failure.
- Same default `THESIS_CUBIT_MODULE=cubit-edu/2026.8` (applied when unset or empty, `:=` as in the original).
- Same module names and order: `module use <Core>`; `module load morphorm/approved-runtime` (which `depends_on`
  CHPC `gcc/11.2.0` and `openmpi/5.0.3` and runs `source_sh` on the runtime's `env.sh`); then `module load cubit-edu/2026.8`
  and a `command -v cubit` check.
- Same runtime identity: the Morphorm runtime is byte-identical (its `SHA256SUMS` hash equals the frozen-configuration
  value `fa0d97b9…e4d2`) and so is the Cubit bundle; the modulefiles differ from the originals only in root paths and
  help/comment text. Same commands on `PATH` (`XMLGenerator`, `PlatoMain`, `analyze_MPMD`, `mpiexec`, `python3`, `cubit`).

## Deliberate differences
1. Root paths point to `runtime/` here instead of the obsolete tree.
2. Guards: the loader fails unless `MORPHORM_RUNTIME` is exactly the E3 runtime and `CUBIT_ROOT` is inside the E3
   Cubit copy, so a same-named module from another module path cannot be loaded silently.
3. Lmod initialisation: when `module` is not CHPC Lmod, the loader sources CHPC's Lmod initialiser
   (`/uufs/chpc.utah.edu/sys/etc/profile.d/module.sh`) instead of the original fallback `/etc/profile.d/modules.sh`.
   The original fallback starts the OS Tcl "Environment Modules", which cannot read the Lua modulefiles. Observed with
   that same fallback in an empty environment: "Unable to locate a modulefile for 'morphorm/approved-runtime'" (the
   original loader itself was not executed). This matters for the E3 sandbox, which starts from an empty environment.
4. Module identity records change: modulefile hashes are new (see `environment_inventory.txt`); the runtime hashes are not.

## Behaviour that could not be reproduced safely
- **Cubit licensing inside the sandbox.** The educational license is activated in the researcher's own Coreform user
  configuration under the account home directory (`$HOME/.config/Coreform`). The loader never referenced it and still
  does not. On the host Cubit finds it as before. Inside the E3 sandbox the account home is deliberately not mounted, so
  Cubit is expected to be unlicensed there. Exposing that directory (or copying a license credential) is a researcher
  decision and is not done here; see `setup/GROUND_TRUTH_ISOLATION_ACTION_REQUIRED.md`.
- Nothing was run: no Morphorm executable, no Cubit, no Slurm job. Verification consisted of `bash -n`, Lmod loading,
  `command -v`, `ldd` and hash comparisons. Execution on a compute node remains part of compute-node qualification.

## Verification performed (2026-10-10 UTC)
`bash -n` PASS; Morphorm `sha256sum -c provenance/SHA256SUMS` 2064/2064 PASS; Cubit 30,819/30,819 file hashes identical;
loading succeeds in an empty environment, a login environment and the E3 sandbox; resolved executables are all under
`runtime/` (plus CHPC `mpiexec`); 0 `ThesisExperiments` entries in `PATH`, `LD_LIBRARY_PATH`, `MODULEPATH`, the loader,
the modulefiles, `env.sh`, the launchers or the runtime binaries; `ldd` inside the sandbox: 0 missing libraries.
