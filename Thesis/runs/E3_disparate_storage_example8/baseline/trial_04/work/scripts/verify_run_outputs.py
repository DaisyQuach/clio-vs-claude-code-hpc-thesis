#!/usr/bin/env python3
"""Verify the accepted run's outputs: iteration count, final analyze output fields, engine output history."""
import sys, json, re, datetime, os
import numpy as np
from netCDF4 import Dataset
rd = sys.argv[1]; out = sys.argv[2]
def names(ds, var): return [b"".join(np.asarray(r).astype("S1")).decode().strip("\x00 ") for r in ds.variables[var][:]] if var in ds.variables else []
diag = open(os.path.join(rd, "morphorm_oc_optimizer_diagnostics.txt")).read()
rows = [l.split() for l in diag.splitlines() if re.match(r"^\s*\d+\s+\d+\s", l)]
iters = [int(r[0]) for r in rows]
stop = [l.strip(" *") for l in diag.splitlines() if "stopping" in l.lower()]
final = os.path.join(rd, "analyze_id_2_output_scenario_id_1", "iteration50.exo")
fa = Dataset(final); nodal = names(fa, "name_nod_var"); elem = names(fa, "name_elem_var")
fa_steps = fa.dimensions["time_step"].size; fa_nodes = fa.dimensions["num_nodes"].size; fa_elems = fa.dimensions["num_elem"].size
dens = None
for i, n in enumerate(nodal):
    if n.lower() in ("topology", "density", "control"): dens = (n, float(fa.variables[f"vals_nod_var{i+1}"][-1].min()), float(fa.variables[f"vals_nod_var{i+1}"][-1].max()), float(fa.variables[f"vals_nod_var{i+1}"][-1].mean()))
eo = Dataset(os.path.join(rd, "engine_output.exo")); eo_nodal = names(eo, "name_nod_var"); eo_steps = eo.dimensions["time_step"].size
eo_times = [float(t) for t in eo.variables["time_whole"][:]] if "time_whole" in eo.variables else []
ctrl_i = [i for i, n in enumerate(eo_nodal) if n.lower() == "control"]; topo_i = [i for i, n in enumerate(eo_nodal) if n.lower() == "topology"]
eo_last = {}
for lab, idx in (("control", ctrl_i), ("topology", topo_i)):
    if idx: v = eo.variables[f"vals_nod_var{idx[0]+1}"][-1]; eo_last[lab] = {"min": float(v.min()), "max": float(v.max()), "mean": float(v.mean())}
crit = open(os.path.join(rd, "opt_criteria_history.csv")).read().strip().splitlines()
checks = {
  "diagnostics_last_iteration_50": max(iters) == 50, "diagnostics_rows_0_to_50": iters == list(range(51)),
  "stopped_at_max_iterations": any("maximum number of iterations" in s for s in stop),
  "iteration50_exo_exists": os.path.isfile(final), "final_output_has_displacements": all(any(n.lower().replace(" ", "").replace("_", "") in (f"disp{c}", f"displacement{c}") for n in nodal) for c in "xyz"),
  "final_output_has_density_field": dens is not None, "final_output_mesh_matches": (fa_nodes, fa_elems) == (15925, 13824),
  "engine_output_has_control_and_topology": bool(ctrl_i and topo_i), "engine_output_mesh_matches": (eo.dimensions["num_nodes"].size, eo.dimensions["num_elem"].size) == (15925, 13824),
  "engine_output_has_history": eo_steps >= 2, "criteria_history_51_values": len([v for v in crit[-1].split(",")[1:] if v.strip()]) == 51,
}
rec = {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "run_directory": os.path.abspath(rd),
       "iterations_reached": max(iters), "function_evaluations": int(rows[-1][1]), "first_row": rows[0], "last_row": rows[-1], "stopping_message": stop,
       "final_analyze_output": {"file": final, "time_steps": fa_steps, "nodal_variables": nodal, "element_variables": elem, "density_field_last_step(name,min,max,mean)": dens},
       "engine_output": {"time_steps": eo_steps, "times": eo_times, "nodal_variables": eo_nodal, "last_step": eo_last},
       "opt_criteria_history_header": crit[0], "opt_criteria_history_last": crit[-1], "opt_criteria_history_values": len([v for v in crit[-1].split(",")[1:] if v.strip()]),
       "checks": checks, "result": "PASS" if all(checks.values()) else "FAIL"}
json.dump(rec, open(out, "w"), indent=2); print(json.dumps(rec, indent=2)); sys.exit(0 if rec["result"] == "PASS" else 1)
