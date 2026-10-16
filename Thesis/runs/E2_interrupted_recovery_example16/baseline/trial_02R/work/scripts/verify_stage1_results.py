"""Verify Stage-1 results: iteration count, stopping message, checkpoint saved states, final analyze output.
Usage: verify_stage1_results.py <run_dir> <out.json>"""
import sys, os, re, json, glob, hashlib, datetime
import numpy as np
from netCDF4 import Dataset

run_dir, out = sys.argv[1], sys.argv[2]
C = {}
def check(name, cond, observed):
    C[name] = {"pass": bool(cond), "observed": observed}
def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()
def names(ds, var):
    res = []
    for row in ds.variables[var][:]:
        if hasattr(row, "filled"): row = row.filled(b"")
        res.append(b"".join(x if isinstance(x, bytes) else x.encode() for x in row).decode().strip("\x00").strip())
    return res

# ---- optimizer diagnostics ----
diag_path = os.path.join(run_dir, "morphorm_oc_optimizer_diagnostics.txt")
diag = open(diag_path).read()
rows = []
for line in diag.splitlines():
    m = re.match(r"\s*(\d+)\s+(\d+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)", line)
    if m:
        rows.append({"iter": int(m.group(1)), "fcount": int(m.group(2)), "F": float(m.group(3)), "normF": float(m.group(4)), "H1": float(m.group(5)), "dX": float(m.group(6)), "dF": float(m.group(7))})
iters = [r["iter"] for r in rows]
stop_msgs = [l.strip() for l in diag.splitlines() if l.strip().startswith("******")]
check("diagnostics: iterations 0..20 present (21 rows)", iters == list(range(21)), iters)
check("diagnostics: last iteration == 20", bool(iters) and iters[-1] == 20, iters[-1] if iters else None)
check("diagnostics: stopping message = maximum number of iterations", any("maximum number of iterations" in m for m in stop_msgs), stop_msgs)
check("diagnostics: objective values finite", all(np.isfinite(r["F"]) for r in rows), [r["F"] for r in rows][-3:])

# ---- engine_output.exo (checkpoint) ----
eo_path = os.path.join(run_dir, "engine_output.exo")
ds = Dataset(eo_path, "r")
times = np.array(ds.variables["time_whole"][:]) if "time_whole" in ds.variables else np.array([])
nod = names(ds, "name_nod_var") if "name_nod_var" in ds.variables else []
n_nodes = int(ds.dimensions["num_nodes"].size); n_elem = int(ds.dimensions["num_elem"].size)
check("checkpoint: engine_output.exo exists", True, eo_path)
check("checkpoint: 21 saved states (time steps)", len(times) == 21, {"num_time_steps": int(len(times)), "times": [float(t) for t in times]})
check("checkpoint: nodal fields include control and topology", "control" in nod and "topology" in nod, nod)
check("checkpoint: same mesh size as input (30625 nodes, 27648 elements)", n_nodes == 30625 and n_elem == 27648, (n_nodes, n_elem))
field_stats = {}
if "control" in nod and "topology" in nod and len(times):
    ic = nod.index("control") + 1; it = nod.index("topology") + 1
    ctrl = np.array(ds.variables[f"vals_nod_var{ic}"][:]); topo = np.array(ds.variables[f"vals_nod_var{it}"][:])
    for k in [0, len(times) - 1]:
        field_stats[f"step_{k}"] = {"control_min": float(ctrl[k].min()), "control_max": float(ctrl[k].max()), "control_mean": float(ctrl[k].mean()),
                                    "topology_min": float(topo[k].min()), "topology_max": float(topo[k].max()), "topology_mean": float(topo[k].mean())}
    check("checkpoint: step 0 control is uniform 0.15 (initial design)", abs(ctrl[0].min() - 0.15) < 1e-12 and abs(ctrl[0].max() - 0.15) < 1e-12, field_stats["step_0"])
    check("checkpoint: all saved control fields finite and within [0,1]", bool(np.all(np.isfinite(ctrl)) and ctrl.min() >= -1e-12 and ctrl.max() <= 1 + 1e-12), (float(ctrl.min()), float(ctrl.max())))
    check("checkpoint: consecutive saved control states differ (design evolves)", all(np.max(np.abs(ctrl[k+1] - ctrl[k])) > 0 for k in range(len(times) - 1)), [float(np.max(np.abs(ctrl[k+1] - ctrl[k]))) for k in range(len(times) - 1)])
glob_names = names(ds, "name_glo_var") if "name_glo_var" in ds.variables else []
ds.close()

# ---- engine_restart.exo (also written when write_restart_file true) ----
er_path = os.path.join(run_dir, "engine_restart.exo")
er_info = None
if os.path.exists(er_path):
    d2 = Dataset(er_path, "r"); er_info = {"num_time_steps": int(len(d2.variables["time_whole"][:])) if "time_whole" in d2.variables else 0, "nodal_vars": names(d2, "name_nod_var") if "name_nod_var" in d2.variables else []}; d2.close()
# informational only: the locked checkpoint is engine_output.exo (spec section 7); engine_restart.exo is described in the manual but not required
INFO = {"engine_restart.exo present (manual-described, not a locked requirement)": {"observed": os.path.exists(er_path), "info": er_info}}

# ---- final analyze output ----
viz_dirs = sorted(glob.glob(os.path.join(run_dir, "analyze_id_2_output*")))
it_files = sorted(glob.glob(os.path.join(viz_dirs[0], "iteration*.exo")), key=lambda p: int(re.search(r"iteration(\d+)", p).group(1))) if viz_dirs else []
it_nums = [int(re.search(r"iteration(\d+)", p).group(1)) for p in it_files]
check("analyze output directory present", bool(viz_dirs), viz_dirs)
check("analyze per-iteration files 0..20", it_nums == list(range(21)), it_nums)
final = os.path.join(viz_dirs[0], "iteration20.exo") if viz_dirs else None
fin_info = None
if final and os.path.exists(final):
    d3 = Dataset(final, "r"); fnod = names(d3, "name_nod_var") if "name_nod_var" in d3.variables else []; felem = names(d3, "name_elem_var") if "name_elem_var" in d3.variables else []
    fin_info = {"path": final, "nodal_vars": fnod, "elem_vars": felem, "num_time_steps": int(len(d3.variables["time_whole"][:])) if "time_whole" in d3.variables else 0}; d3.close()
    low = [v.lower().replace("_", " ") for v in fnod]
    check("final analyze output (iteration20.exo) has dispx dispy dispz (nodal displacement x/y/z)", all(any(v in (f"displacement {a}", f"disp{a}") for v in low) for a in ["x", "y", "z"]), fnod)
else:
    check("final analyze output (iteration20.exo) exists", False, final)

# ---- opt_criteria_history.csv ----
och = os.path.join(run_dir, "opt_criteria_history.csv")
och_txt = open(och).read() if os.path.exists(och) else ""
och_rows = [l.strip() for l in och_txt.replace("\r", "\n").splitlines() if l.strip()]
och_vals = [float(x) for x in och_rows[0].split(",")[1:] if x.strip()] if och_rows else []
check("opt_criteria_history.csv present with 21 objective values (iterations 0..20)", len(och_vals) == 21, {"n_values": len(och_vals), "label": och_rows[0].split(",")[0] if och_rows else None})
check("opt_criteria_history.csv objective values match diagnostics F(X)", len(och_vals) == len(rows) and all(abs(a - r["F"]) <= 1e-6 * abs(r["F"]) for a, r in zip(och_vals, rows)), [och_vals[0], och_vals[-1]] if och_vals else None)

record = {"frozen_configuration_id": "FROZEN-EX16-v1", "stage": 1, "run_dir": run_dir,
          "verified_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
          "diagnostics_rows": rows, "stopping_messages": stop_msgs,
          "checkpoint": {"path": eo_path, "sha256": sha(eo_path), "num_time_steps": int(len(times)), "nodal_vars": nod, "global_vars": glob_names, "field_stats": field_stats},
          "informational": INFO, "final_analyze_output": fin_info, "opt_criteria_history_values": och_vals,
          "checks": C, "all_checks_pass": all(v["pass"] for v in C.values()), "n_pass": sum(v["pass"] for v in C.values()), "n_checks": len(C)}
json.dump(record, open(out, "w"), indent=2)
for k, v in C.items(): print(("PASS" if v["pass"] else "FAIL"), k, "->", v["observed"])
print("ALL PASS" if record["all_checks_pass"] else "SOME CHECKS FAILED", record["n_pass"], "/", record["n_checks"])
sys.exit(0 if record["all_checks_pass"] else 1)
