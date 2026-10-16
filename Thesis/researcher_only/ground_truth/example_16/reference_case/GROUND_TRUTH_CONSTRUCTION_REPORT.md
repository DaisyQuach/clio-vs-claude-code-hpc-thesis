# Example 16 — Ground-Truth Construction Report

Built 2026-10-09 (UTC) under `Thesis/researcher_only/ground_truth/example_16/reference_case/`. Companion documents: `../SOURCE_AUDIT.md`,
`ACCEPTANCE_SPEC.md`, `REFERENCE_VALIDATION.md`.

## 1. What "rebuilt from scratch" meant here
1. Canonical inputs copied unmodified (hash-pinned in `../SOURCE_AUDIT.md`): `topology_mech_ex16.jou`, `topology_mech_ex16.i`,
   `topology_mech_ex16_restart.i`, `runmorphorm.py`. One derived input: `topology_mech_ex16_restart_corrected_21.i` (one line,
   `restart_iteration 20 → 21`, researcher-authorized 2026-10-06; `inputs/README.md`).
2. Mesh regenerated with Coreform Cubit 2026.8 (`cubit-edu/2026.8`) from the unmodified journal in job **16154331** (11 s):
   `cubit -batch -nographics -nojournal -input topology_mech_ex16.jou`. Validation 7/7: 27,648 HEX8, 30,625 nodes, bbox [0,2]×[0,1]×[0,1], `block_1`,
   `ns_fix` 625, `ns_load` 25.
3. Stage 1 (job **16154332**): canonical deck translated (`preflight_stage1/`, 33/33 checks incl. `WriteRestart true`, `MaxIterations 20`) and executed
   with the manual's command `python3 runmorphorm.py topology_mech_ex16.i`; `engine_output.exo` (21 states, `control` + `topology`) is the checkpoint.
4. Two restarts from that single checkpoint, each copying it to `initialguess.exo` exactly as the manual's `cp engine_output.exo initialguess.exo`
   (byte identity recorded in `*/inputs_sha256.txt` and `results/*_restart_evidence.json`):
   - **`restart_corrected_21`** (job **16154333**): `restart_iteration 21` → reads the iteration-20 design (manual semantics). Preflight 36/36.
   - **`restart_shipped_20`** (job **16154334**): unmodified shipped deck, `restart_iteration 20` → reads the iteration-19 design. Preflight 36/36.
5. Run-time translations byte-identical to the preflight translations (8/8 files, all three runs); diagnostics parsed into `results/`; everything hashed.

## 2. Jobs (frozen contract: `--account=hochhalter-np --partition=hochhalter-np --nodes=1 --ntasks=1 --cpus-per-task=8 --mem=32G --time=02:00:00`)

| Job | Script | Purpose | State / exit | Elapsed | Node | MaxRSS |
|---|---|---|---|---|---|---|
| 16154331 | `ex16_01_mesh.sbatch` | mesh generation + validation | COMPLETED 0:0 | 00:00:11 | notch351 | 0.28 GB |
| 16154332 | `ex16_02_stage1.sbatch` (afterok 16154331) | Stage 1, canonical deck, 20 iterations | COMPLETED 0:0 | 00:18:30 | notch272 | 2.2 GB |
| 16154333 | `ex16_03_restart_corrected_21.sbatch` (afterok 16154332) | restart from the iteration-20 design, 40 iterations | COMPLETED 0:0 | 00:21:02 | notch351 | 2.4 GB |
| 16154334 | `ex16_04_restart_shipped_20.sbatch` (afterok 16154332) | shipped restart deck, 40 iterations | COMPLETED 0:0 | 00:20:52 | notch351 | 2.4 GB |

Records: `jobs/submissions.log`, `jobs/job_ids.txt`, `jobs/scontrol_*.txt`, `jobs/sacct_accounting.psv`, `logs/` (all `.err` empty), `*/timestamps.txt`
(`runmorphorm_exit_code=0`), `*/time_v.txt`, `environment/`.

## 3. Results

| Quantity | Stage 1 | Restart from iteration 20 (`restart_iteration 21`) | Shipped restart (`restart_iteration 20`) |
|---|---|---|---|
| Iterations logged | 0–20 (21), stop at cap | 0–40 (41), stop at cap | 0–40 (41), stop at cap |
| First compliance | 4.893235e6 (cold start) | **2.360040e5** = Stage-1 iteration 20 (diff 0) | 2.388394e5 = Stage-1 iteration **19** (+1.20 % vs iteration 20) |
| Saved state matched by the initial `control` field | — | state 21 = iteration 20, max abs diff 0.0 | state 20 = iteration 19, max abs diff 0.0 |
| Overall iteration reached | 20 | **60** | 59 (one iteration repeated) |
| Final compliance | 2.360040e5 | **2.135584e5** | 2.136843e5 |
| Volume fraction / H1 | 0.150000 / 3.96e-13 | 0.150000 / −7.55e-14 | 0.150000 / −5.68e-14 |
| Max displacement magnitude | 2.5420e4 | 2.3300e4 | 2.3314e4 |
| Cross-chain | — | corrected step *k* `control` == shipped step *k*+1 (max abs diff 0.0, k = 0..39): the two runs are the same trajectory offset by one iteration | |
| Final `Topology` difference between the two restarts | — | max abs diff 0.0164 | |
| Figures | `figures/Example_16_stage1_final_iteration20.png` | `figures/Example_16_restart_corrected_21_final_iteration60.png`, `figures/Example_16_corrected_vs_shipped_iteration60.png`, `figures/Example_16_compliance_history.png` | |

## 4. Deviations, decisions, retries
- **No retries, no failures**; every job completed on first submission.
- Only one derived input (the one-line corrected restart deck), documented and justified by the manual's own statement of the restart semantics
  (`../SOURCE_AUDIT.md` §5). Both restart results are kept; the accepted semantics is a researcher decision (`acceptance_spec.json: reference_policy`).
- `OMP_NUM_THREADS` unset (manual's plain invocation); dedicated `sbatch` jobs, no job steps; `runmorphorm.py` exit code not used as the success criterion.
