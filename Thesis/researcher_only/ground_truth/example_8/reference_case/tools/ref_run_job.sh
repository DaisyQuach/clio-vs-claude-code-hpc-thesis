#!/usr/bin/env bash
# Reference-run job body: preflight translation + generated-config check, then the
# manual's own execution command (python runmorphorm.py <deck>), then post-checks.
# Required env: REF DECK RUN MESH EXPECT_ITERS CHECK_ARGS PREFIX
# Optional env: CKPT (absolute path of a stage-1 engine_output.exo to copy to
#               initialguess.exo), STAGE1_DIR, INTENDED_RESUME (int),
#               EXPECT_RESUME_MATCH (true|false; default true when CKPT is set)
set -uo pipefail
TE=/uufs/chpc.utah.edu/common/home/chet/Daisy/ThesisExperiments/common
echo "job=${SLURM_JOB_ID:-none} name=${SLURM_JOB_NAME:-none} node=$(hostname -s) start_utc=$(date -u +%FT%TZ)"
echo "partition=${SLURM_JOB_PARTITION:-} account=${SLURM_JOB_ACCOUNT:-} qos=${SLURM_JOB_QOS:-} cpus=${SLURM_CPUS_PER_TASK:-} mem_mb=${SLURM_MEM_PER_NODE:-}"
type module >/dev/null 2>&1 || source /etc/profile.d/modules.sh
module purge >/dev/null 2>&1
module use "$TE/modulefiles/Core"
module load morphorm/approved-runtime || { echo "FATAL: module load failed"; exit 2; }
export PYTHONDONTWRITEBYTECODE=1
mkdir -p "$REF/$RUN" "$REF/preflight_$RUN" "$REF/results" "$REF/logs" "$REF/jobs" "$REF/environment"
scontrol show job "${SLURM_JOB_ID:-0}" > "$REF/jobs/scontrol_${SLURM_JOB_NAME:-run}_${SLURM_JOB_ID:-0}.txt" 2>&1 || true
"$REF/tools/env_capture.sh" "$REF/environment/environment_${SLURM_JOB_NAME:-run}_${SLURM_JOB_ID:-0}.txt"
GEN="interface.xml engine_input_deck.xml engine_operations.xml analyze_2_input_deck.xml analyze_2_operations.xml analyze_helmholtz_input_deck.xml analyze_helmholtz_operations.xml mpirun.source"

# ---- 1. preflight translation and generated-configuration check -------------
cd "$REF/preflight_$RUN" || exit 3
cp -p "$REF/inputs/$DECK" .; cp -p "$REF/mesh/$MESH" .
[[ -n "${CKPT:-}" ]] && cp -p "$CKPT" initialguess.exo
XMLGenerator "$DECK" > xmlgenerator.log 2>&1
xrc=$?; echo "preflight XMLGenerator exit=$xrc"; [[ $xrc -eq 0 ]] || { echo "FATAL: XMLGenerator failed"; exit 6; }
# shellcheck disable=SC2086
python3 -I "$REF/tools/check_generated_config.py" . --mesh "$MESH" $CHECK_ARGS --out preflight_check.json > preflight_check.txt 2>&1
prc=$?; tail -1 preflight_check.txt; grep '^FAIL' preflight_check.txt || true
[[ $prc -eq 0 ]] || { echo "FATAL: generated configuration does not match the frozen formulation"; exit 7; }
sha256sum $GEN > generated_config_sha256.txt
rm -f "$MESH" initialguess.exo   # keep the preflight directory small; hashes are in generated_config_sha256.txt

# ---- 2. execution with the manual's command ----------------------------------
cd "$REF/$RUN" || exit 3
cp -p "$REF/inputs/$DECK" "$REF/inputs/runmorphorm.py" .; cp -p "$REF/mesh/$MESH" .
if [[ -n "${CKPT:-}" ]]; then cp -p "$CKPT" initialguess.exo; fi
sha256sum "$DECK" runmorphorm.py "$MESH" ${CKPT:+initialguess.exo} > inputs_sha256.txt; cat inputs_sha256.txt
grep " $MESH\$" "$REF/mesh/mesh_sha256.txt" | sha256sum -c - || { echo "FATAL: mesh hash mismatch"; exit 4; }
if [[ -n "${CKPT:-}" ]]; then echo "checkpoint_source=$CKPT sha256=$(sha256sum "$CKPT" | cut -c1-64)" | tee checkpoint_source.txt; fi
echo "morphorm_command=python3 runmorphorm.py $DECK" > timestamps.txt
echo "morphorm_start_utc=$(date -u +%FT%TZ)" | tee -a timestamps.txt
/usr/bin/time -v -o time_v.txt python3 runmorphorm.py "$DECK" > runmorphorm.stdout 2> runmorphorm.stderr
rc=$?
echo "morphorm_end_utc=$(date -u +%FT%TZ) runmorphorm_exit_code=$rc" | tee -a timestamps.txt
echo "$rc" > runmorphorm_exit_code.txt
tail -3 morphorm_oc_optimizer_diagnostics.txt 2>/dev/null

# ---- 3. post-run checks -------------------------------------------------------
same=1
for f in $GEN; do if cmp -s "$f" "$REF/preflight_$RUN/$f"; then echo "identical to preflight: $f"; else echo "DIFFERS from preflight: $f"; same=0; fi; done | tee generated_config_matches_preflight.txt
[[ $same -eq 1 ]] || echo "WARNING: run-time translation differs from the validated preflight"
python3 -I "$REF/tools/summarize_run.py" . "$REF/results/$PREFIX" --expect-iterations "$EXPECT_ITERS" > "$REF/results/${PREFIX}_summarize.stdout" 2> "$REF/results/${PREFIX}_summarize.stderr"
src=$?; echo "summarize exit=$src"; grep -E '"(final_compliance|last_iteration|stop_message|reached_expected_iterations)"' "$REF/results/${PREFIX}_summary.json"
rrc=0
if [[ -n "${CKPT:-}" ]]; then
  python3 -I "$REF/tools/restart_evidence.py" "$STAGE1_DIR" . "$DECK" "$REF/results/${PREFIX}_restart_evidence.json" "${INTENDED_RESUME:-20}" > "$REF/results/${PREFIX}_restart_evidence.stdout" 2> "$REF/results/${PREFIX}_restart_evidence.stderr"
  rrc=$?; echo "restart_evidence exit=$rrc (0 = resumed from the intended iteration)"
  grep -E '"(restart_resumes_from_stage1_iteration|resumed_from_intended_iteration|restart_first_compliance|restart_final_compliance)"' "$REF/results/${PREFIX}_restart_evidence.json"
  if [[ "${EXPECT_RESUME_MATCH:-true}" == "false" ]]; then echo "note: this variant is expected NOT to resume from the intended iteration"; rrc=0; fi
fi
find . -type f ! -name outputs_sha256.txt -print0 | sort -z | xargs -0 sha256sum > outputs_sha256.txt
echo "end_utc=$(date -u +%FT%TZ)" | tee -a timestamps.txt
[[ $rc -eq 0 && $same -eq 1 && $src -eq 0 && $rrc -eq 0 ]] || exit 1
exit 0
