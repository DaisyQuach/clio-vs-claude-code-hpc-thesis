# E3 CLIO automation

| Script | Status |
|---|---|
| `run_clio_e3_trial_v2.sh --trial-dir <E3>/clio/trial_NN (--dry-run \| --execute-counted)` | **Current (2026-10-11).** Runs inside the trial's own allocation and performs every E3 check: allocation, `$TMPDIR`, control repository at the pin, Globus, sources, freshness. It prepares the same packet as the baseline (`../baseline/prepare_baseline_trial.sh --system clio`) and launches a fresh CLIO deployment and session through `Thesis/automation/clio/launch_clio_session.sh`, sending the byte-identical frozen prompt. It writes the E3 records (`logs/session/{session_record,export,messages,tool_inputs}.json[l]`, staging snapshot, provenance, boundary audit, metrics) and verifies with `../baseline/verify_baseline_trial.sh --system clio`. Model usage, including cache writes, goes to `logs/session/clio/usage_summary.json` |
| `collect_clio_metrics.sh` | Used unchanged by v2 |
| `run_clio_e3_trial.sh`, `start_e3_clio_server.sh` | 2026-10-09 versions, kept unchanged as the record. Never run. Superseded because they did not set `CLIO_BIN_DIR` (the service is unhealthy without it, a known pilot pitfall), did not attach a blueprint, and posted the prompt without `confirmation_policy` (it falls back to `ask`, which stops a bypass trial at its first tool call). They also lacked the runtime tuning, the usage telemetry and the CLI pin |

A dry run was performed 2026-10-11 on the login node: all E3 checks passed, nothing was written in the trial, and the
placeholders were reported.
