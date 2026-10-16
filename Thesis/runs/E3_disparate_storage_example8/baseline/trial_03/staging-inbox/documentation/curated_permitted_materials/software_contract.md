# Approved Software Contract

Use only the approved software interface below, in agent-host shells and in every Slurm script:

```bash
source /uufs/chpc.utah.edu/common/home/chet/Daisy/Thesis/runs/E3_disparate_storage_example8/automation/environment/load_morphorm_e3.sh
```

It loads the approved, read-only Morphorm runtime (`morphorm/approved-runtime`, with CHPC `gcc/11.2.0` and `openmpi/5.0.3`)
and the approved Coreform Cubit module (`cubit-edu/2026.8`). After sourcing, the following commands are on `PATH`:

| Command | Purpose |
|---|---|
| `cubit -batch -nographics -nojournal -input <journal.jou>` | batch meshing (Cubit journal → Exodus II) |
| `XMLGenerator <deck.i>` | translate a Morphorm input deck into the runtime configuration files (`interface.xml`, `*_input_deck.xml`, `*_operations.xml`, `mpirun.source`) |
| `bash mpirun.source` | launch the Morphorm performers described by the generated `mpirun.source` |
| `PlatoMain`, `analyze_MPMD`, `mpiexec` | runtime executables used by `mpirun.source` |
| `python3` | the runtime's Python 3.13 (numpy, netCDF4 available) for verification scripts |

Notes:
- `cubit -version` prints the version and then aborts with exit 134 (known vendor behavior); normal batch runs exit 0.
- Deck syntax reference: `manuals/Morphorm_User_Manual.pdf` (private source collection); theory: `manuals/Morphorm_Theory_Manual.pdf` (private source collection).

Rules:
1. Do not search for, source, or use any other Morphorm, Cubit, or Python installation (including developer or Spack environments).
2. Do not access software documentation, examples, tests, meshes, input decks, or completed outputs outside the collections in the E3 storage catalog;
   the manuals in the private source collection are the only permitted software documentation.
3. If an approved executable is unavailable or fails, preserve the current state and report the blocking condition in `work/run_summary.md`.
