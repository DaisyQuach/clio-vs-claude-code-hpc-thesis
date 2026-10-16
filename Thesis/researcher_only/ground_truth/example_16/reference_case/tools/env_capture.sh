#!/usr/bin/env bash
# Capture the software/module environment and the approved-runtime identity hashes.
# Usage: env_capture.sh <output_file>
out=${1:?output file}
TE=/uufs/chpc.utah.edu/common/home/chet/Daisy/ThesisExperiments/common
{
  echo "captured_utc=$(date -u +%FT%TZ)"
  echo "host=$(hostname -s)"
  echo "slurm_job_id=${SLURM_JOB_ID:-none} slurm_job_name=${SLURM_JOB_NAME:-none} partition=${SLURM_JOB_PARTITION:-} account=${SLURM_JOB_ACCOUNT:-} qos=${SLURM_JOB_QOS:-} cpus_per_task=${SLURM_CPUS_PER_TASK:-} mem_per_node_mb=${SLURM_MEM_PER_NODE:-} nodelist=${SLURM_JOB_NODELIST:-}"
  echo "[modules]"; module -t list 2>&1
  echo "[executables]"
  for e in python3 XMLGenerator PlatoMain analyze analyze_MPMD mpiexec cubit epu; do echo "$e=$(command -v $e 2>/dev/null || echo none)"; done
  echo "mpiexec_version=$(mpiexec --version 2>&1 | head -1)"
  echo "python3_version=$(python3 --version 2>&1)"
  echo "MORPHORM_RUNTIME=${MORPHORM_RUNTIME:-}"
  echo "morphorm_modulefile_sha256=$(sha256sum < $TE/modulefiles/Core/morphorm/approved-runtime.lua | cut -c1-64)"
  echo "cubit_modulefile_sha256=$(sha256sum < $TE/modulefiles/Core/cubit-edu/2026.8.lua | cut -c1-64)"
  echo "runtime_env_sh_sha256=$(sha256sum < $TE/approved_runtime/morphorm/env.sh | cut -c1-64)"
  echo "runtime_inventory_SHA256SUMS_sha256=$(sha256sum < $TE/approved_runtime/morphorm/provenance/SHA256SUMS | cut -c1-64)"
  echo "load_approved_software_sha256=$(sha256sum < $TE/scripts/load_approved_software.sh | cut -c1-64)"
  echo "OMP_NUM_THREADS=${OMP_NUM_THREADS:-unset}"
  echo "[uname]"; uname -a
  echo "[cpu]"; grep -m1 "model name" /proc/cpuinfo
} > "$out" 2>&1
sha256sum "$out" > "$out.sha256"
