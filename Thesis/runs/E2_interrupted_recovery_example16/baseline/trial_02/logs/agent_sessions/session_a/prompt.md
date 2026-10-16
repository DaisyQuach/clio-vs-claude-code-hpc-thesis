You are running headless, with no human available, inside a prepared trial workspace. Your working directory is the trial root. The trial identifier is given in the environment variable THESIS_TRIAL_ID; record it in your run summary.

Read every file in agent_inputs/ first: formal_configuration.md, scientific_problem_specification.md, compute_resources.md, software_contract.md, workspace_rules.md, provenance_requirements.md and acceptance_visibility_boundary.md. The manuals in agent_inputs/manuals/ are the only permitted documentation.

Task for this session: construct and validate the frozen two-stage workflow locked in agent_inputs/scientific_problem_specification.md, and run it only up to the end of Stage 1. Generate the mesh with the approved Cubit, write the Stage-1 input deck, translate it, verify the mesh and the generated runtime configuration against every locked setting, submit the Stage-1 job through Slurm with the frozen resources and the approved software interface, wait for it to finish, and verify it reached the required iteration count and preserved the checkpoint with all saved states. Place every Stage-1 deliverable at its locked path under outputs/ with a SHA-256 manifest, and record all commands, decisions, retries, job IDs, the checkpoint location and artifact paths in work/run_summary.md, stating clearly that Stage 1 is complete and Stage 2 has not been started.

Stop after Stage 1. Do not create, translate, submit or run a Stage-2 or continuation deck, job script or job in this session.

Do not seek or use external reference meshes, decks, completed runs, numerical outputs or scoring criteria. Do not modify anything outside this trial root. If something blocks you, preserve the state, record the blocking condition in work/run_summary.md and stop.
