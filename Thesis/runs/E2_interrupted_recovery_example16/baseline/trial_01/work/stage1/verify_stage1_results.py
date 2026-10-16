#!/usr/bin/env python3
"""Verify Stage-1 results: iteration count, stopping message, checkpoint saved states, final analyze output.
Usage: verify_stage1_results.py <run_dir>
"""
import sys, os, re, json, hashlib
import numpy as np, netCDF4

run = sys.argv[1]
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def names(ds, var):
    return ["".join(x.decode() for x in row.compressed() if x != b"") if hasattr(row, "compressed") else row.tobytes().split(b"\x00")[0].decode() for row in ds.variables[var][:]]

rec = {"run_dir": run}
# optimizer diagnostics
diag = open(os.path.join(run, "morphorm_oc_optimizer_diagnostics.txt")).read()
rows = [l.split() for l in diag.splitlines() if re.match(r"^\s*\d+\s+\d+\s", l)]
iters = [int(r[0]) for r in rows]
stop = [l.strip() for l in diag.splitlines() if l.strip().startswith("******")]
rec["diagnostics"] = {"first_iteration": iters[0], "last_iteration": iters[-1], "num_rows": len(rows),
                      "stopping_message": stop, "iteration_20_row": [r for r in rows if int(r[0]) == 20],
                      "compliance_history": {int(r[0]): float(r[2]) for r in rows},
                      "constraint_history": {int(r[0]): float(r[4]) for r in rows}}
# opt criteria history
och = os.path.join(run, "opt_criteria_history.csv")
rec["opt_criteria_history"] = open(och).read().strip().splitlines() if os.path.exists(och) else None
# engine output (checkpoint)
eo = os.path.join(run, "engine_output.exo")
ds = netCDF4.Dataset(eo)
nsteps = ds.dimensions["time_step"].size
nodal = names(ds, "name_nod_var")
times = ds.variables["time_whole"][:].tolist()
ctrl_i = nodal.index("control") + 1; topo_i = nodal.index("topology") + 1
ctrl = ds.variables[f"vals_nod_var{ctrl_i}"][:]; topo = ds.variables[f"vals_nod_var{topo_i}"][:]
rec["engine_output"] = {"file": eo, "sha256": sha(eo), "num_time_steps": nsteps, "time_values": times,
                        "nodal_fields": nodal, "num_nodes": ds.dimensions["num_nodes"].size, "num_elem": ds.dimensions["num_elem"].size,
                        "control_step_stats": [{"step": i + 1, "min": float(ctrl[i].min()), "max": float(ctrl[i].max()), "mean": float(ctrl[i].mean())} for i in range(nsteps)],
                        "topology_step_stats": [{"step": i + 1, "min": float(topo[i].min()), "max": float(topo[i].max()), "mean": float(topo[i].mean())} for i in range(nsteps)]}
ds.close()
# restart file (if written)
er = os.path.join(run, "engine_restart.exo")
if os.path.exists(er):
    d2 = netCDF4.Dataset(er); rec["engine_restart"] = {"file": er, "sha256": sha(er), "num_time_steps": d2.dimensions["time_step"].size, "nodal_fields": names(d2, "name_nod_var")}; d2.close()
# analyze per-iteration output
ad = os.path.join(run, "analyze_id_2_output_scenario_id_1")
files = sorted(os.listdir(ad)) if os.path.isdir(ad) else []
rec["analyze_output_dir"] = {"dir": ad, "num_files": len(files), "first": files[:3], "last": files[-3:]}
fin = os.path.join(ad, "iteration20.exo")
if os.path.exists(fin):
    d3 = netCDF4.Dataset(fin); rec["final_analyze_output"] = {"file": fin, "sha256": sha(fin), "num_time_steps": d3.dimensions["time_step"].size, "nodal_fields": names(d3, "name_nod_var"), "num_nodes": d3.dimensions["num_nodes"].size}; d3.close()
checks = {
  "diagnostics: iterations 0..20 present (21 rows)": iters == list(range(21)),
  "diagnostics: last iteration == 20 == max_iterations": iters[-1] == 20,
  "diagnostics: stopped at iteration cap (max iterations message)": any("maximum number of iterations" in s for s in stop),
  "checkpoint: engine_output.exo has 21 time steps": nsteps == 21,
  "checkpoint: control and topology nodal fields present": "control" in nodal and "topology" in nodal,
  "checkpoint: node/element counts match mesh": rec["engine_output"]["num_nodes"] == 30625 and rec["engine_output"]["num_elem"] == 27648,
  "checkpoint: step 1 control is uniform 0.15 (initial design)": abs(ctrl[0].min() - 0.15) < 1e-12 and abs(ctrl[0].max() - 0.15) < 1e-12,
  "checkpoint: all steps finite, within [0,1]": bool(np.isfinite(ctrl).all() and np.isfinite(topo).all() and ctrl.min() >= -1e-12 and ctrl.max() <= 1 + 1e-12),
  "final analyze output iteration20.exo exists with displacement fields": "final_analyze_output" in rec and all(any(f.lower().replace(" ", "_") == p for f in rec["final_analyze_output"]["nodal_fields"]) for p in ("displacement_x", "displacement_y", "displacement_z")),
}
checks = {k: bool(v) for k, v in checks.items()}
rec["checks"] = checks; rec["ALL_CHECKS_PASS"] = all(checks.values())
print(json.dumps(rec, indent=2))
sys.exit(0 if rec["ALL_CHECKS_PASS"] else 1)
