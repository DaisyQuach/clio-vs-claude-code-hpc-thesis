# CLIO trials for E2_interrupted_recovery_example16 (planned, paired with baseline/)

`trial_01` … `trial_05` are **planned, unexecuted** CLIO packets (status `planned`). They were prepared 2026-10-11 by
`Thesis/automation/clio/prepare_clio_trial.sh --experiment e2-example16 --all-planned` from the same frozen configuration as the
baseline packets (`FROZEN-EX16-v1`). Their `agent_inputs/` are byte-identical to `baseline/trial_NN/agent_inputs/`.

- **Run ids:** `E2-example16-clio-NN`. Paired blocks are the same as the baseline (`E2-NN`).
- **Runner:** `Thesis/automation/clio/run_e2_clio.sh` (see `Thesis/automation/clio/README.md`).
- **Ready to run?** No. The CLIO version and blueprint decisions in `Thesis/automation/clio/clio_trial_config.env` are still placeholders, so counted runs are refused until they are filled in.
- **Replacements:** the same policy as the baseline. Aborted packets are kept and excluded, and a replacement is `trial_NNR` (`--suffix R`).

The previous text of this file is in `README.pre_20261011.md`.
