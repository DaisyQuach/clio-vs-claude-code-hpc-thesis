"""Verify Stage-1 results of FROZEN-EX16-v1: iteration count, optimizer stop message, checkpoint saved states.
Usage: python3 -I verify_stage1_results.py <run_dir>
"""
import sys, os, re, json, hashlib, datetime
import numpy as np
import netCDF4

run = sys.argv[1]
res = {"run_dir": run, "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "checks": {}}
C = res["checks"]
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
# --- optimizer diagnostics
diag_path = os.path.join(run, "morphorm_oc_optimizer_diagnostics.txt")
diag = open(diag_path).read()
res["diagnostics_sha256"] = sha(diag_path)
rows = []
for line in diag.splitlines():
    m = re.match(r"^\s*(\d+)\s+(\d+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s*$", line)
    if m:
        rows.append({"iter": int(m.group(1)), "fcount": int(m.group(2)), "F": float(m.group(3)), "normF": float(m.group(4)), "H1": float(m.group(5)), "dX": float(m.group(6)), "dF": float(m.group(7))})
res["diagnostic_rows"] = rows
res["num_diagnostic_rows"] = len(rows)
res["last_iteration"] = rows[-1]["iter"] if rows else None
res["stop_message"] = [l.strip() for l in diag.splitlines() if "******" in l]
C["diagnostics: iterations 0..20 present (21 rows)"] = [r["iter"] for r in rows] == list(range(21))
C["diagnostics: stopped at the iteration cap (max iterations message)"] = any("maximum number of iterations" in m for m in res["stop_message"])
C["diagnostics: finite objective values"] = all(np.isfinite(r["F"]) and r["F"] > 0 for r in rows)
res["compliance_iter20"] = rows[20]["F"] if len(rows) > 20 else None
res["compliance_iter0"] = rows[0]["F"] if rows else None
# --- engine output (checkpoint)
eo_path = os.path.join(run, "engine_output.exo")
res["engine_output_sha256"] = sha(eo_path)
ds = netCDF4.Dataset(eo_path, "r")
def names(var):
    return ["".join(c.decode() if isinstance(c, bytes) else c for c in row.tobytes().split(b"\x00")[0:1][0].decode()) for row in ds.variables[var][:]] if False else [row.tobytes().split(b"\x00")[0].decode().strip() for row in ds.variables[var][:]]
nvars = names("name_nod_var") if "name_nod_var" in ds.variables else []
times = ds.variables["time_whole"][:].tolist() if "time_whole" in ds.variables else []
res["engine_output"] = {"num_nodes": int(ds.dimensions["num_nodes"].size), "num_elem": int(ds.dimensions["num_elem"].size), "nodal_vars": nvars, "num_time_steps": len(times), "times": times}
C["checkpoint: 21 saved states (time steps)"] = len(times) == 21
C["checkpoint: nodal fields include control and topology"] = "control" in nvars and "topology" in nvars
C["checkpoint: mesh size 30625 nodes / 27648 elements"] = res["engine_output"]["num_nodes"] == 30625 and res["engine_output"]["num_elem"] == 27648
stats = []
if "control" in nvars and "topology" in nvars:
    ic = nvars.index("control") + 1; it = nvars.index("topology") + 1
    for k in range(len(times)):
        c = ds.variables["vals_nod_var%d" % ic][k, :]; t = ds.variables["vals_nod_var%d" % it][k, :]
        stats.append({"step": k + 1, "time": times[k], "control_min": float(c.min()), "control_max": float(c.max()), "control_mean": float(c.mean()), "topology_min": float(t.min()), "topology_max": float(t.max()), "topology_mean": float(t.mean())})
res["engine_output"]["field_stats"] = stats
if stats:
    C["checkpoint: state 1 is the uniform initial density 0.15 (control)"] = abs(stats[0]["control_min"] - 0.15) < 1e-12 and abs(stats[0]["control_max"] - 0.15) < 1e-12
    C["checkpoint: states are distinct (design evolves) and within [0,1]"] = all(0.0 - 1e-12 <= s["control_min"] and s["control_max"] <= 1.0 + 1e-12 for s in stats) and len({round(s["control_mean"], 12) for s in stats}) > 1
    C["checkpoint: control field for last state differs from step 20 (states not duplicated)"] = len(stats) < 2 or (stats[-1]["control_mean"] != stats[-2]["control_mean"])
ds.close()
# --- restart file
rs_path = os.path.join(run, "engine_restart.exo")
res["engine_restart_exists"] = os.path.exists(rs_path)
if res["engine_restart_exists"]:
    res["engine_restart_sha256"] = sha(rs_path)
    d2 = netCDF4.Dataset(rs_path, "r")
    res["engine_restart"] = {"nodal_vars": [row.tobytes().split(b"\x00")[0].decode().strip() for row in d2.variables["name_nod_var"][:]] if "name_nod_var" in d2.variables else [], "num_time_steps": int(d2.dimensions["time_step"].size) if "time_step" in d2.dimensions else 0}
    d2.close()
# --- analyze outputs
viz = os.path.join(run, "analyze_id_2_output_scenario_id_1")
res["analyze_output_files"] = sorted(os.listdir(viz)) if os.path.isdir(viz) else []
fin = os.path.join(viz, "iteration20.exo")
res["final_analyze_output_exists"] = os.path.exists(fin)
C["final analyze output iteration20.exo exists"] = res["final_analyze_output_exists"]
if res["final_analyze_output_exists"]:
    res["final_analyze_output_sha256"] = sha(fin)
    d3 = netCDF4.Dataset(fin, "r")
    res["final_analyze_output"] = {"nodal_vars": [row.tobytes().split(b"\x00")[0].decode().strip() for row in d3.variables["name_nod_var"][:]] if "name_nod_var" in d3.variables else [], "num_time_steps": int(d3.dimensions["time_step"].size) if "time_step" in d3.dimensions else 0}
    d3.close()
    C["final analyze output has displacement fields"] = any("disp" in v.lower() for v in res["final_analyze_output"]["nodal_vars"])
# --- criteria history
ch = os.path.join(run, "opt_criteria_history.csv")
if os.path.exists(ch):
    res["opt_criteria_history_head"] = open(ch).read().splitlines()[:3]
    res["opt_criteria_history_lines"] = len(open(ch).read().splitlines())
res["ALL_CHECKS_PASS"] = all(C.values())
print(json.dumps(res, indent=2))
sys.exit(0 if res["ALL_CHECKS_PASS"] else 1)
