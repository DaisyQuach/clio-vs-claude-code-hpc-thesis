#!/usr/bin/env python3
"""Check the final analyze output and engine output of the accepted run (fields, time steps, element/node counts)."""
import sys, json, datetime, netCDF4, numpy as np
run = sys.argv[1]
def names(ds, var):
    if var not in ds.variables: return []
    v = ds.variables[var]; v.set_auto_mask(False)
    return [bytes(r).decode("ascii","ignore").strip("\x00 ") for r in v[:]]
rec = {"utc": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")}
a = netCDF4.Dataset(f"{run}/analyze_id_2_output_scenario_id_1/iteration50.exo")
rec["final_analyze_output"] = dict(file="analyze_id_2_output_scenario_id_1/iteration50.exo", num_nodes=a.dimensions["num_nodes"].size, num_elem=a.dimensions["num_elem"].size,
    nodal_vars=names(a,"name_nod_var"), elem_vars=names(a,"name_elem_var"), time_steps=int(a.dimensions["time_step"].size) if "time_step" in a.dimensions else 0,
    time_values=[float(t) for t in a.variables["time_whole"][:]] if "time_whole" in a.variables else [])
e = netCDF4.Dataset(f"{run}/engine_output.exo")
rec["engine_output"] = dict(file="engine_output.exo", num_nodes=e.dimensions["num_nodes"].size, num_elem=e.dimensions["num_elem"].size,
    nodal_vars=names(e,"name_nod_var"), time_steps=int(e.dimensions["time_step"].size), time_values=[float(t) for t in e.variables["time_whole"][:]])
nv = rec["engine_output"]["nodal_vars"]
if "control" in nv and "topology" in nv:
    c = e.variables["vals_nod_var%d" % (nv.index("control")+1)][-1,:]; t = e.variables["vals_nod_var%d" % (nv.index("topology")+1)][-1,:]
    rec["engine_output"]["last_step_control_range"] = [float(c.min()), float(c.max())]; rec["engine_output"]["last_step_topology_range"] = [float(t.min()), float(t.max())]
    rec["engine_output"]["last_step_mean_control"] = float(c.mean())
hist = open(f"{run}/opt_criteria_history.csv").read().strip().splitlines()
rec["opt_criteria_history_rows"] = len(hist)-1; rec["opt_criteria_history_last"] = hist[-1]; rec["opt_criteria_history_header"] = hist[0]
diag = open(f"{run}/morphorm_oc_optimizer_diagnostics.txt").read()
last = [l for l in diag.splitlines() if l.strip() and l.split()[0].isdigit()][-1]
rec["diagnostics_last_iteration"] = int(last.split()[0]); rec["stop_message"] = [l.strip() for l in diag.splitlines() if "******" in l]
checks = {
  "optimizer reached iteration 50": rec["diagnostics_last_iteration"] == 50,
  "stop message = max iterations (not convergence)": any("maximum number of iterations" in m for m in rec["stop_message"]),
  "final analyze output is iteration50.exo with displacement x, y, z fields": all(any(v.lower().replace(" ","").replace("_","") in (f"displacement{c}", f"disp{c}") for v in rec["final_analyze_output"]["nodal_vars"]) for c in "xyz") and rec["final_analyze_output"]["time_values"] == [50.0],
  "final analyze output has a density/topology field": any(("topolog" in v.lower() or "densit" in v.lower() or "control" in v.lower()) for v in rec["final_analyze_output"]["nodal_vars"] + rec["final_analyze_output"]["elem_vars"]),
  "final analyze output on the accepted mesh (13824 elements, 15925 nodes)": rec["final_analyze_output"]["num_elem"] == 13824 and rec["final_analyze_output"]["num_nodes"] == 15925,
  "engine output has control and topology fields": "control" in nv and "topology" in nv,
  "engine output on the accepted mesh": rec["engine_output"]["num_elem"] == 13824 and rec["engine_output"]["num_nodes"] == 15925,
}
rec["checks"] = checks; rec["result"] = "PASS" if all(checks.values()) else "FAIL"
print(json.dumps(rec, indent=2)); sys.exit(0 if rec["result"]=="PASS" else 1)
