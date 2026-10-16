# E3 automation — where it is

The scripts in this folder are the E1/E2 baseline automation. **E3 has its own automation, kept in the E3 run folder:**
`Thesis/runs/E3_disparate_storage_example8/automation/` (README there). It cannot move here before CLIO without changing E3's frozen configuration;
see `Thesis/researcher_only/docs/E3/README.md` for the reasons.

| E3 task | Script (under `Thesis/runs/E3_disparate_storage_example8/`) |
|---|---|
| prepare / run / verify one baseline trial | `automation/baseline/{prepare_baseline_trial,run_baseline_e3_trial,verify_baseline_trial}.sh` |
| boundary audit | `automation/audit_boundary.sh` (+ `automation/lib/`) |
| approved software interface (agent-usable) | `automation/environment/load_morphorm_e3.sh` |
| counted-trial Slurm jobs, freeze, postprocessing | `setup/baseline_execution/{jobs,freeze,postprocess,postprocess_r1}/` |
| CLIO runner (not yet run) | `automation/clio/` |
| scoring | E1 scorer `researcher_only/ground_truth/tools/score_trial.py` (as used for E3; see `researcher_only/docs/E3/E3_BASELINE_EXECUTION_REPORT.md`) |
