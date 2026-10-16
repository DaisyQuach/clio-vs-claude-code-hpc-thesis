#!/usr/bin/env bash
# Harmless visibility probe, run INSIDE the E3 sandbox. Only stats and lists paths; writes nothing; runs no solver/model.
# Usage (inside):  sandbox_probe.sh [--with-loader]
#   --with-loader  also source the E3 environment loader and report which executables resolve (Lmod only; nothing is run)
# Prints one line per check:  <PASS|FAIL|INFO> <check> <detail>; exit 0 only if every PASS/FAIL check passed.
D=/uufs/chpc.utah.edu/common/home/chet/Daisy
E3=$D/Thesis/runs/E3_disparate_storage_example8
rc=0
pass() { echo "PASS $1 $2"; }
fail() { echo "FAIL $1 $2"; rc=1; }
info() { echo "INFO $1 $2"; }
visible()   { if [[ -e "$2" ]]; then pass "$1" "visible: $2"; else fail "$1" "NOT visible: $2"; fi; }
invisible() { if [[ -e "$2" ]]; then fail "$1" "VISIBLE: $2"; else pass "$1" "not visible: $2"; fi; }

[[ "${E3_SANDBOX:-}" == 1 ]] && pass in_sandbox "E3_SANDBOX=1" || fail in_sandbox "not running inside the E3 sandbox"
td=${E3_TRIAL_ROOT:-}
# ---- permitted E3 paths
visible trial_dir "$td"
visible trial_agent_inputs "$td/agent-inputs"
visible trial_work "$td/work"
visible candidate_archive "$E3/chpc_candidate_archive/MANIFEST.sha256"
visible candidate_example_13 "$E3/chpc_candidate_archive/example_13/problem_card.yaml"
visible environment_loader "$E3/automation/environment/load_morphorm_e3.sh"
[[ -n "${E3_STAGING_DIR:-}" ]] && visible staging_dir "$E3_STAGING_DIR"
# ---- write protection of the packet (access(2) only; nothing is written)
[[ -w "$td/agent-inputs" ]] && fail agent_inputs_readonly "agent-inputs is writable" || pass agent_inputs_readonly "agent-inputs not writable"
[[ -w "$td/work" ]] && pass trial_work_writable "work/ writable" || fail trial_work_writable "work/ not writable"
# ---- denied paths
invisible researcher_only "$E3/researcher_only"
invisible e3_setup "$E3/setup"
invisible e3_automation_other "$E3/automation/baseline"
invisible ground_truth "$D/Morphorm_ground_truth"
invisible e1 "$D/Thesis/runs/E1_uninterrupted_example8"
invisible e2 "$D/Thesis/runs/E2_interrupted_recovery_example16"
invisible thesis_experiments "$D/ThesisExperiments"
invisible full_examples_tests "$D/Morphorm_Full_Examples_Tests"
invisible morphorm_source_docs "$D/Morphorm"
invisible morphorm_manuals_originals "$D/morphorm_manuals"
invisible thesis_researcher_only "$D/Thesis/researcher_only"
invisible legacy_agent_inputs "$td/agent_inputs"
for s in baseline clio; do for t in "$E3/$s"/trial_*; do [[ -e "$t" && "$t" != "$td" ]] && fail other_trial_visible "$t"; done; done
pass other_trials "no other trial directory visible"
# ---- directory listings: only bind-mount scaffolding may appear
info listing_daisy "$(ls -A "$D" 2>/dev/null | tr '\n' ' ')"
info listing_thesis_runs "$(ls -A "$D/Thesis/runs" 2>/dev/null | tr '\n' ' ')"
info listing_e3_root "$(ls -A "$E3" 2>/dev/null | tr '\n' ' ')"
n=$(ls -A /uufs/chpc.utah.edu/common/home 2>/dev/null | grep -vx chet | wc -l)
[[ $n -eq 0 ]] && pass home_dirs "no home directory other than the bind-mount scaffold for the E3 tree" || fail home_dirs "$n other entries under /uufs/chpc.utah.edu/common/home"
[[ "$HOME" == /tmp/e3home ]] && pass sandbox_home "HOME=$HOME (tmpfs)" || fail sandbox_home "HOME is not the sandbox tmpfs"
# ---- escape-relevant facts (informational; see README "Limitations")
info pid1 "$(tr '\0' ' ' < /proc/1/cmdline 2>/dev/null | cut -c1-60)"
info process_count "$(ls -d /proc/[0-9]* 2>/dev/null | wc -l) processes visible"
[[ -S /run/munge/munge.socket.2 ]] && info munge_socket "visible (Slurm submission possible; submitted jobs run OUTSIDE the sandbox)" || info munge_socket "not visible"
command -v sbatch >/dev/null 2>&1 && info sbatch "on PATH" || info sbatch "not on PATH"
command -v ssh >/dev/null 2>&1 && info ssh "on PATH (network not unshared)" || info ssh "not on PATH"
if [[ "${1:-}" == --with-loader ]]; then
  # shellcheck disable=SC1091
  if source "$E3/automation/environment/load_morphorm_e3.sh" >/dev/null 2>&1; then
    pass loader "load_morphorm_e3.sh sourced; MORPHORM_RUNTIME=$MORPHORM_RUNTIME"
    for x in XMLGenerator PlatoMain analyze_MPMD mpiexec python3 cubit; do
      p=$(command -v "$x" 2>/dev/null); [[ -n "$p" ]] && info resolve "$x -> $p" || fail resolve "$x not found"; done
    case "$PATH" in *ThesisExperiments*) fail loader_path "PATH references ThesisExperiments";; *) pass loader_path "PATH has no ThesisExperiments entry";; esac
  else fail loader "load_morphorm_e3.sh failed inside the sandbox"; fi
fi
exit $rc
