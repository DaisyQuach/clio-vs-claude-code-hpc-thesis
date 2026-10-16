#!/usr/bin/env bash
# Mesh-generation job body for a reference case.  Called from an sbatch wrapper.
# Required env: REF JOU NX NY NZ LX LY LZ ; optional: SIDESETS (space-separated)
set -uo pipefail
TE=/uufs/chpc.utah.edu/common/home/chet/Daisy/ThesisExperiments/common
echo "job=${SLURM_JOB_ID:-none} name=${SLURM_JOB_NAME:-none} node=$(hostname -s) start_utc=$(date -u +%FT%TZ)"
type module >/dev/null 2>&1 || source /etc/profile.d/modules.sh
module purge >/dev/null 2>&1
module use "$TE/modulefiles/Core"
module load cubit-edu/2026.8 morphorm/approved-runtime || { echo "FATAL: module load failed"; exit 2; }
mkdir -p "$REF/mesh" "$REF/logs" "$REF/jobs" "$REF/environment"
scontrol show job "${SLURM_JOB_ID:-0}" > "$REF/jobs/scontrol_${SLURM_JOB_NAME:-mesh}_${SLURM_JOB_ID:-0}.txt" 2>&1 || true
"$REF/tools/env_capture.sh" "$REF/environment/environment_${SLURM_JOB_NAME:-mesh}_${SLURM_JOB_ID:-0}.txt"
cd "$REF/mesh" || exit 3
cp -p "$REF/inputs/$JOU" .
echo "journal_sha256=$(sha256sum "$JOU" | cut -c1-64)"
echo "mesh_start_utc=$(date -u +%FT%TZ)" > timestamps.txt
cubit -batch -nographics -nojournal -input "$JOU" > cubit_mesh_generation.log 2>&1
crc=$?; echo "cubit_exit_code=$crc" | tee -a timestamps.txt
echo "mesh_end_utc=$(date -u +%FT%TZ)" >> timestamps.txt
exo="${JOU%.jou}.exo"
[[ -s "$exo" ]] || { echo "FATAL: $exo not produced"; exit 4; }
python3 -I "$REF/tools/validate_mesh.py" "$exo" "$NX" "$NY" "$NZ" "$LX" "$LY" "$LZ" ${SIDESETS:-} > mesh_validation.json 2> mesh_validation.stderr
vrc=$?; echo "mesh_validation_exit_code=$vrc" | tee -a timestamps.txt
grep -E '"all_checks_pass"' mesh_validation.json
sha256sum "$exo" "$JOU" > mesh_sha256.txt; cat mesh_sha256.txt
echo "end_utc=$(date -u +%FT%TZ)"
[[ $crc -eq 0 && $vrc -eq 0 ]] || exit 1
exit 0
