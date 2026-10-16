# E3 — disparate-storage deployment (planned, not implemented)

E3 will re-run the frozen Example 8 workflow (`FROZEN-EX8-v1`, byte-identical to E1's agent inputs) with the independent variable being
the storage deployment: trial workspace, approved runtime, scheduler scratch and outputs placed on disparate storage tiers/locations
(to be frozen in a future `compute_resources.md` addendum). The scientific formulation, deliverables, prompts and scoring are unchanged,
so E1's Example 8 reference applies (`researcher_only/ground_truth/example_8`), provided the agent-inputs hash still equals `FROZEN-EX8-v1`.

This build provides only: documentation (this file, `runs/E3_disparate_storage_example8/README.md`), the frozen specification (shared),
and five `status: planned` packets with an `E3_PLANNED_NOT_EXECUTABLE.md` note. There is no E3 launcher; `run_all_planned_baselines.sh`
refuses `--experiment e3-example8`. A future version adds the storage-distribution variable and its automation without changing the
frozen Example 8 problem.
