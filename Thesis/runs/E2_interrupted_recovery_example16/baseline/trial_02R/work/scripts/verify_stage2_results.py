"""Verify Stage-2 (continuation) results: iteration count, stopping message, engine output saved states, final analyze output.
Usage: verify_stage2_results.py <run_dir> <out.json>"""
import sys, os, re, json, glob, hashlib, datetime
import numpy as np
from netCDF4 import Dataset

run_dir, out = sys.argv[1], sys.argv[2]
N = 40  # locked Stage-2 max_iterations
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

diag_path = os.path.join(run_dir, "morphorm_oc_optimizer_diagnostics.txt")
diag = open(diag_path).read()
rows = []
for line in diag.splitlines():
    m = re.match(r"\s*(\d+)\s+(\d+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)", line)
    if m:
        rows.append({"iter": int(m.group(1)), "fcount": int(m.group(2)), "F": float(m.group(3)), "normF": float(m.group(4)), "H1": float(m.group(5)), "dX": float(m.group(6)), "dF": float(m.group(7))})
iters = [r["iter"] for r in rows]
stop_msgs = [l.strip() for l in diag.splitlines() if l.strip().startswith("******")]
check(f"diagnostics: local iterations 0..{N} present ({N+1} rows)", iters == list(range(N + 1)), iters)
check(f"diagnostics: last local iteration == {N} (overall iteration 20+{N} = {20+N})", bool(iters) and iters[-1] == N, iters[-1] if iters else None)
check("diagnostics: stopping message = maximum number of iterations", any("maximum number of iterations" in m for m in stop_msgs), stop_msgs)
check("diagnostics: objective values finite", all(np.isfinite(r["F"]) for r in rows), [r["F"] for r in rows][-3:])

eo_path = os.path.join(run_dir, "engine_output.exo")
ds = Dataset(eo_path, "r")
times = np.array(ds.variables["time_whole"][:]) if "time_whole" in ds.variables else np.array([])
nod = names(ds, "name_nod_var") if "name_nod_var" in ds.variables else []
n_nodes = int(ds.dimensions["num_nodes"].size); n_elem = int(ds.dimensions["num_elem"].size)
check(f"engine output: {N+1} saved states (time steps, local iterations 0..{N})", len(times) == N + 1, {"num_time_steps": int(len(times)), "first_last_times": [float(times[0]), float(times[-1])] if len(times) else None})
check("engine output: nodal fields include control and topology", "control" in nod and "topology" in nod, nod)
check("engine output: same mesh size as input (30625 nodes, 27648 elements)", n_nodes == 30625 and n_elem == 27648, (n_nodes, n_elem))
field_stats = {}
if "control" in nod and "topology" in nod and len(times):
    ic = nod.index("control") + 1; it = nod.index("topology") + 1
    ctrl = np.array(ds.variables[f"vals_nod_var{ic}"][:]); topo = np.array(ds.variables[f"vals_nod_var{it}"][:])
    for k in [0, len(times) - 1]:
        field_stats[f"step_{k}"] = {"control_min": float(ctrl[k].min()), "control_max": float(ctrl[k].max()), "control_mean": float(ctrl[k].mean()),
                                    "topology_min": float(topo[k].min()), "topology_max": float(topo[k].max()), "topology_mean": float(topo[k].mean())}
    check("engine output: step 0 control is NOT uniform (restart from a non-uniform design)", ctrl[0].max() - ctrl[0].min() > 0.5, field_stats["step_0"])
    check("engine output: all saved control fields finite and within [0,1]", bool(np.all(np.isfinite(ctrl)) and ctrl.min() >= -1e-12 and ctrl.max() <= 1 + 1e-12), (float(ctrl.min()), float(ctrl.max())))
    check("engine output: consecutive saved control states differ (design evolves)", all(np.max(np.abs(ctrl[k+1] - ctrl[k])) > 0 for k in range(len(times) - 1)), [float(np.max(np.abs(ctrl[k+1] - ctrl[k]))) for k in range(len(times) - 1)][:5] + ["..."])
ds.close()

viz_dirs = sorted(glob.glob(os.path.join(run_dir, "analyze_id_2_output*")))
it_files = sorted(glob.glob(os.path.join(viz_dirs[0], "iteration*.exo")), key=lambda p: int(re.search(r"iteration(\d+)", p).group(1))) if viz_dirs else []
it_nums = [int(re.search(r"iteration(\d+)", p).group(1)) for p in it_files]
check("analyze output directory present", bool(viz_dirs), viz_dirs)
check(f"analyze per-iteration files 0..{N}", it_nums == list(range(N + 1)), (it_nums[:3], it_nums[-3:]) if it_nums else None)
final = os.path.join(viz_dirs[0], f"iteration{N}.exo") if viz_dirs else None
fin_info = None
if final and os.path.exists(final):
    d3 = Dataset(final, "r"); fnod = names(d3, "name_nod_var") if "name_nod_var" in d3.variables else []; felem = names(d3, "name_elem_var") if "name_elem_var" in d3.variables else []
    fin_info = {"path": final, "sha256": sha(final), "nodal_vars": fnod, "elem_vars": felem, "num_time_steps": int(len(d3.variables["time_whole"][:])) if "time_whole" in d3.variables else 0}; d3.close()
    low = [v.lower().replace("_", " ") for v in fnod]
    check(f"final analyze output (iteration{N}.exo = overall iteration {20+N}) has dispx dispy dispz (nodal displacement x/y/z)", all(any(v in (f"displacement {a}", f"disp{a}") for v in low) for a in ["x", "y", "z"]), fnod)
else:
    check(f"final analyze output (iteration{N}.exo) exists", False, final)

och = os.path.join(run_dir, "opt_criteria_history.csv")
och_txt = open(och).read() if os.path.exists(och) else ""
och_rows = [l.strip() for l in och_txt.replace("\r", "\n").splitlines() if l.strip()]
och_vals = [float(x) for x in och_rows[0].split(",")[1:] if x.strip()] if och_rows else []
check(f"opt_criteria_history.csv present with {N+1} objective values", len(och_vals) == N + 1, {"n_values": len(och_vals), "label": och_rows[0].split(",")[0] if och_rows else None})
check("opt_criteria_history.csv objective values match diagnostics F(X)", len(och_vals) == len(rows) and all(abs(a - r["F"]) <= 1e-6 * abs(r["F"]) for a, r in zip(och_vals, rows)), [och_vals[0], och_vals[-1]] if och_vals else None)

record = {"frozen_configuration_id": "FROZEN-EX16-v1", "stage": 2, "run_dir": run_dir,
          "verified_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
          "diagnostics_rows": rows, "stopping_messages": stop_msgs,
          "engine_output": {"path": eo_path, "sha256": sha(eo_path), "num_time_steps": int(len(times)), "nodal_vars": nod, "field_stats": field_stats},
          "restart_input_sha256": sha(os.path.join(run_dir, "restart_input.exo")) if os.path.exists(os.path.join(run_dir, "restart_input.exo")) else None,
          "final_analyze_output": fin_info, "opt_criteria_history_values": och_vals,
          "checks": C, "all_checks_pass": all(v["pass"] for v in C.values()), "n_pass": sum(v["pass"] for v in C.values()), "n_checks": len(C)}
json.dump(record, open(out, "w"), indent=2)
for k, v in C.items(): print(("PASS" if v["pass"] else "FAIL"), k, "->", v["observed"])
print("ALL PASS" if record["all_checks_pass"] else "SOME CHECKS FAILED", record["n_pass"], "/", record["n_checks"])
sys.exit(0 if record["all_checks_pass"] else 1)
