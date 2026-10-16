# Preliminary thesis figures — controlled E1/E2 baseline (built 2026-10-10 UTC)

Researcher-only. Regenerate with:
```bash
cd analysis && python3 -I build_dataset.py && python3 make_figures.py   # miniconda python3 (matplotlib 3.11); renders/ via ParaView 6.0.1
```

## Trials in the analysis
| Experiment | Counted (all `accepted`) | Excluded (provider usage limit, non-agent cause) |
|---|---|---|
| E1 (Example 8) | 01, 02, 03, 04R2*, 05 | 04, 04R |
| E2 (Example 16) | 01, 02R, 03, 04R, 05 | 02, 04 |

\* 04R2 counted by researcher decision: the limit ended the process after its final successful tool call (`RESEARCHER_DECISIONS.md`).

## Figures (`figures/`, PNG 300 dpi + PDF)
| File | Shows | Table view |
|---|---|---|
| `fig1_E1_compliance_vs_reference` | compliance history of all 5 E1 trials over the rebuilt reference; every trial coincides (final difference 0.0) | `data/compliance_histories.csv` |
| `fig2_E2_compliance_vs_reference` | same for E2 across the Session A → Session B interruption at iteration 20 | `data/compliance_histories.csv` |
| `fig3_time_breakdown_by_session` | stacked agent wall time by activity per session; thin lane = Slurm queue + Morphorm run (overlaps "Slurm submit & wait") | `data/time_breakdown_by_session.csv`, `data/time_share_summary.csv` |
| `fig4_gantt_representative_trials` | activity timeline, E1 trial 01 and E2 trial 03 (both sessions and the interruption) | `data/gantt_segments.csv` |
| `fig5_telemetry_descriptive` | wall time, turns, output tokens, reported cost per counted trial (descriptive only) | `data/trials.csv` |
| `fig6_E1_topology_grid`, `fig6_E2_topology_grid` | final topology (density ≥ 0.5), reference and each counted trial | `renders/` |

## Headline numbers (means over counted trials)
| Session | Mean wall time | Model reasoning & writing | Slurm submit & wait | All other tool activity |
|---|---|---|---|---|
| E1 single session | 22.0 min | 52.9 % | 43.1 % | 4.0 % |
| E2 Session A (Stage 1) | 28.7 min | 37.1 % | 59.7 % | 3.2 % |
| E2 Session B (recovery) | 39.6 min | 22.7 % | 75.8 % | 1.5 % |

Scientific outcome: 10/10 counted trials reproduce their reference exactly (final compliance and node-wise final density differences 0.0);
every E2 Session B resumed from the iteration-20 design with zero compliance discontinuity.

## Method and caveats (state these with the figures)
- Time attribution uses transcript timestamps: each tool call spans `tool_use` → `tool_result`; overlapping calls are assigned once by a fixed
  priority; uncovered time is model reasoning & writing. Cross-check: attributed model time matches the API-reported model time per session
  (e.g. E1-01: 727.3 s vs 726.6 s).
- Activity categories come from keyword rules on the shell commands (`analysis/build_dataset.py: RULES`). They are heuristic: a command that
  writes a summary mentioning `cubit` can register as a sub-second meshing tick (visible near session ends in fig4).
- "Slurm submit & wait" is agent time spent submitting and polling; the Morphorm run itself is the parallel grey lane and is not additive.
- `sacct` times (America/Denver) are converted to UTC. E2 Session B includes some short probe/translation jobs, so its Slurm lane exceeds one Stage-2 run.
- Token, cost and tool-call figures are descriptive audit metadata, not performance measures (`EXPERIMENTAL_DESIGN.md`); n = 5 per experiment.
- Colors: validated 8-slot categorical palette (adjacent-pair CVD ΔE ≥ 9.1); three slots are below 3:1 contrast on white, so every figure has a
  legend and a CSV table view.
