# Example 8 — Ground-Truth Construction Report

Built 2026-10-09 (UTC) under `Thesis/researcher_only/ground_truth/example_8/reference_case/`. Companion documents: `../SOURCE_AUDIT.md`,
`ACCEPTANCE_SPEC.md`, `REFERENCE_VALIDATION.md`.

## 1. What "rebuilt from scratch" meant here
1. Canonical inputs copied unmodified (hash-pinned in `../SOURCE_AUDIT.md`): `topology_mech_ex8.jou`, `topology_mech_ex8.i`, `runmorphorm.py`.
2. Mesh regenerated with the approved Coreform Cubit 2026.8 (`cubit-edu/2026.8`) from the unmodified journal, in Slurm job **16154328**
   (`jobs/ex8_01_mesh.sbatch`, 11 s, notch351): `cubit -batch -nographics -nojournal -input topology_mech_ex8.jou`. Validation 8/8
   (`mesh/mesh_validation.json`): 13,824 HEX8, 15,925 nodes, bbox [0,2]×[0,1]×[0,0.5], `block_1`, `ns_fix` 325, `ns_load` 13, `ss_sym` 1,152 faces.
3. Each deck translated first (`preflight_*/`, `XMLGenerator`), the generated configuration checked field by field against the frozen
   formulation (`tools/check_generated_config.py`, 34/34 in the applicable mode), then executed with the manual's own command
   `python3 runmorphorm.py <deck>` under the approved runtime (`morphorm/approved-runtime`, gcc/11.2.0, openmpi/5.0.3; hashes in `environment/`).
4. After execution the run-time translation was byte-compared with the preflight translation (8/8 identical in both runs), the diagnostics
   parsed (`results/*_summary.json`), and every output hashed (`*/outputs_sha256.txt`, `SHA256SUMS.txt`).

## 2. Jobs (frozen contract: `--account=hochhalter-np --partition=hochhalter-np --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=32G --time=02:00:00`)

| Job | Script | Purpose | State / exit | Elapsed | Node | MaxRSS |
|---|---|---|---|---|---|---|
| 16154328 | `ex8_01_mesh.sbatch` | mesh generation + validation | COMPLETED 0:0 | 00:00:11 | notch351 | 0.29 GB |
| 16154329 | `ex8_02_run_canonical.sbatch` (afterok 16154328) | canonical shipped deck | COMPLETED 0:0 | 00:09:54 | notch351 | 1.50 GB |
| 16154330 | `ex8_03_run_symmetry_honored_variant.sbatch` (afterok 16154328) | symmetry-honored variant | COMPLETED 0:0 | 00:09:52 | notch351 | 1.55 GB |

Submission records: `jobs/submissions.log`, `jobs/job_ids.txt`; scheduler snapshots `jobs/scontrol_*.txt`; accounting `jobs/sacct_accounting.psv`;
Slurm stdout/stderr `logs/` (all `.err` files empty); `runmorphorm_exit_code=0` in both `*/timestamps.txt`; `/usr/bin/time -v` in `*/time_v.txt`.

## 3. Results

| Quantity | Canonical shipped deck (as executed) | Symmetry-honored variant |
|---|---|---|
| Iterations | 0–50 (51 evaluations), stop: "exceeding maximum number of iterations" | same |
| Initial compliance F₀ | 2.837864e6 | 2.654786e6 |
| **Final compliance F₅₀** | **1.468985e5** | **1.044701e5** |
| Final volume fraction (volume-weighted mean filtered density) | 0.150000 (H1 = 7.46e-14) | 0.150000 (H1 = −1.63e-13) |
| Max displacement magnitude | 2.8635e4 | 2.2969e4 |
| Generated Helmholtz deck | Length Scale 0.043301, Surface Length Scale 1.0, **no** Symmetry Plane Sides | Length Scale 0.043301, Surface Length Scale 1.0, **Symmetry Plane Sides {ss_sym}** |
| Mean density on the cut plane z = 0.5 | 0.0137 (material avoids the cut) | 0.506 (material concentrates on the cut, as the manual describes) |
| Figures | `figures/Example_08_canonical_shipped_deck_final_iteration50.png` | `figures/Example_08_symmetry_honored_variant_final_iteration50.png`; comparison `figures/Example_08_variant_vs_canonical_iteration50.png` |

## 4. Deviations, decisions, retries
- **No retries and no failures.** Every job completed on the first submission.
- The only derived input is `inputs/topology_mech_ex8_symmetry_honored_variant.i` (documented in `inputs/README.md`; study-level filter keywords
  instead of a filter block). It exists because the canonical deck's filter symmetry keyword is silently dropped by the frozen software
  (`../SOURCE_AUDIT.md` §5). Both results are kept; the accepted variant is a researcher decision (`acceptance_spec.json: reference_policy`).
- `OMP_NUM_THREADS` was left unset, matching the manual's plain `python runmorphorm.py` invocation (recorded in `environment/`).
- Job steps were not used; every execution is a dedicated `sbatch` job with the frozen contract. The mesh job used the same contract (oversized for 11 s, by design).
- `runmorphorm.py` returns 0 regardless of solver outcome; success was judged from the diagnostics (51 iterations, stop message), empty stderr,
  final Exodus files and the summaries, not from the driver's exit code.
