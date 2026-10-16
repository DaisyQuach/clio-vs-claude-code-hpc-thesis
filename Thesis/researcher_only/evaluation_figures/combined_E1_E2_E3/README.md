# Combined baseline results — E1 / E2 / E3 (built 2026-10-10 UTC)

Researcher-only. Counted trials only (5 per experiment): E1 01, 02, 03, 04R2, 05; E2 01, 02R, 03, 04R, 05; E3 01, 02R, 03, 04, 05
(E3 attempt 02, audit_failed, excluded). Sources (read only, not modified): `../thesis_prelim/data/` (E1/E2) and `../E3_baseline_prelim/data/` (E3);
same time-attribution method for all three. Regenerate: `cd analysis && python3 -I build_combined.py && python3 make_combined_figures.py`
(miniconda python3; E3 renders via `ground_truth/tools/render_topology_pv.py`, ParaView 6.0.1, same as E1/E2 renders).

| Figure (`figures/`, PNG 300 dpi + PDF) | Shows | Table |
|---|---|---|
| `figC1_time_breakdown_without_slurm_E1_E2_E3` | per-session activity time with **Slurm submit & wait removed**; right: `without Slurm + Slurm = session` minutes | `data/time_breakdown_by_session.csv` |
| `figC2_mean_share_without_slurm_E1_E2_E3` | mean composition of the non-Slurm time per experiment/session | `data/summary_by_experiment_session.csv` |
| `figC3_compliance_histories_E1_E2_E3` | compliance history of every counted trial vs its reference | `data/compliance_histories.csv` |
| `figC4_telemetry_E1_E2_E3` | wall time, model API time, turns, output tokens, cost (descriptive only) | `data/trial_telemetry.csv` |
| `figC5_topology_grid_E1_E2_E3` | final topology, reference + 5 counted trials per experiment | `renders/` |

## Headline (means, minutes)
| | Session | Without Slurm | Slurm submit & wait | Morphorm run | Model share of non-Slurm time |
|---|---|---|---|---|---|
| E1 | 22.0 | 12.5 | 9.5 | 9.8 | 93 % |
| E2 · A | 28.7 | 11.6 | 17.1 | 16.7 | 92 % |
| E2 · B | 39.6 | 9.6 | 30.0 | 31.3 | 94 % |
| E3 | 30.9 | 13.4 | 17.6 | 17.2 | 87 % (reading inputs 7 %) |

- Excluding Slurm, the agent spends a similar 10–13 min per session in all three experiments, almost all of it model reasoning & writing.
  The differences in total session time come mainly from the Morphorm job the agent waits for.
- E3's non-Slurm time is about 1 min longer than E1's, mostly "reading inputs & manuals" (discovery across the distributed collections).
  Globus staging commands have no category of their own here: the unchanged E1 rules assign them to existing categories. E3's separate
  Globus/staging time (about 66 s per session) is in `../E3_baseline_prelim/data/trials.csv`.
- "Slurm submit & wait" can differ slightly from the Morphorm run time: the agent may submit before the job starts or poll after it ends.
- Scientific outcome: every counted trial in all three experiments matches its reference (final compliance and density differences 0.0).
- E1 and E3 have the same physical problem and reference; E2 is Example 16. Cross-experiment telemetry is descriptive (n = 5 each).
