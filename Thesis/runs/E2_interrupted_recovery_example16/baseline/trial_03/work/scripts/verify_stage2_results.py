"""Verify Stage-2 (continuation) results and produce the continuation evidence of spec section 7.
usage: python3 -I verify_stage2_results.py <stage2_rundir> <stage1_rundir> <restart_iteration_used>
Checks: iteration cap 40 reached (41 diagnostics rows, local iterations 0..40), stopping message, engine output has 41 saved
states with control+topology, final analyze output iteration40.exo present, AND the continuation evidence:
  * Stage-2 first evaluated compliance (local iteration 0) == Stage-1 compliance at iteration 20 (diagnostics, 7 significant digits;
    and opt_criteria_history.csv values, relative 1e-9),
  * Stage-2 saved control state 0 == Stage-1 saved control state 20 (last time step of the checkpoint), nodewise,
  * which Stage-1 iteration the first Stage-2 compliance actually matches (must be 20)."""
import sys, os, re, json, hashlib, datetime
import numpy as np
from netCDF4 import Dataset
d2, d1, rit = sys.argv[1], sys.argv[2], int(sys.argv[3])
res = []
def chk(label, ok, got, want):
    res.append({"check": label, "pass": bool(ok), "got": got, "expected": want})
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def names(ds, var):
    out = []
    for row in ds.variables[var][:]:
        out.append("".join(c.decode() if isinstance(c, bytes) else str(c) for c in row.compressed()).strip())
    return out
def diag(path):
    txt = open(path).read()
    rows = [l.split() for l in txt.splitlines() if re.match(r'^\s*\d+\s+\d+\s', l)]
    hist = {int(r[0]): {"F-count": int(r[1]), "F(X)": float(r[2]), "Norm(F')": float(r[3]), "H1(X)": float(r[4]), "abs(dX)": float(r[5]), "abs(dF)": float(r[6]), "F(X)_text": r[2]} for r in rows}
    stop = [l.strip() for l in txt.splitlines() if l.strip().startswith("******")]
    return hist, stop
def csvvals(path):
    if not os.path.exists(path): return []
    lines = open(path).read().strip().splitlines()
    return [float(x) for x in lines[0].split(",")[1:] if x.strip()] if lines else []
def fields(path):
    ds = Dataset(path)
    nv = names(ds, "name_nod_var") if "name_nod_var" in ds.variables else []
    n = int(ds.dimensions["time_step"].size)
    out = {"time_steps": n, "nodal_fields": nv, "num_nodes": int(ds.dimensions["num_nodes"].size), "num_elem": int(ds.dimensions["num_elem"].size), "times": [float(t) for t in ds.variables["time_whole"][:]]}
    arr = {}
    for f in ("control", "topology"):
        if f in nv: arr[f] = np.asarray(ds.variables[f"vals_nod_var{nv.index(f)+1}"][:], dtype=float)
    ds.close(); return out, arr
# ---- Stage-2 diagnostics
h2, stop2 = diag(os.path.join(d2, "morphorm_oc_optimizer_diagnostics.txt"))
h1, stop1 = diag(os.path.join(d1, "morphorm_oc_optimizer_diagnostics.txt"))
chk("stage 2 diagnostics rows = local iterations 0..40 (41 rows)", sorted(h2) == list(range(41)), sorted(h2), list(range(41)))
chk("stage 2 stopping message = max iterations", len(stop2) == 1 and "maximum number of iterations" in stop2[0], stop2, "****** Optimization stopping due to exceeding maximum number of iterations. ******")
chk("stage 2 last local iteration = 40 (overall 60)", max(h2) == 40 if h2 else False, max(h2) if h2 else None, 40)
chk("stage 2 objective values finite and positive", all(np.isfinite(v["F(X)"]) and v["F(X)"] > 0 for v in h2.values()), [v["F(X)"] for v in sorted(h2) and [h2[k] for k in sorted(h2)]][-3:], "finite > 0")
# ---- continuation evidence (compliance)
f2_first = h2[0]["F(X)"] if 0 in h2 else None
f1_last = h1[20]["F(X)"] if 20 in h1 else None
chk("CONTINUATION: stage 2 first compliance (local it. 0) == stage 1 compliance at iteration 20 (diagnostics text)", h2.get(0, {}).get("F(X)_text") == h1.get(20, {}).get("F(X)_text"), h2.get(0, {}).get("F(X)_text"), h1.get(20, {}).get("F(X)_text"))
matches = [k for k, v in h1.items() if v["F(X)_text"] == h2.get(0, {}).get("F(X)_text")]
chk("CONTINUATION: the stage-1 iteration whose compliance equals stage 2's first compliance is exactly 20", matches == [20], matches, [20])
c1 = csvvals(os.path.join(d1, "opt_criteria_history.csv")); c2 = csvvals(os.path.join(d2, "opt_criteria_history.csv"))
chk("CONTINUATION: opt_criteria_history.csv stage2[0] == stage1[20] (rel 1e-9)", len(c1) >= 21 and len(c2) >= 1 and abs(c2[0] - c1[20]) <= 1e-9 * abs(c1[20]), {"stage2_first": c2[0] if c2 else None, "stage1_iter20": c1[20] if len(c1) >= 21 else None}, "equal to 1e-9 relative")
chk("stage 2 opt_criteria_history.csv holds 41 objective values", len(c2) == 41, len(c2), 41)
chk("stage 2 csv values match diagnostics F(X) (rel 1e-6)", len(c2) == 41 and all(abs(c2[i] - h2[i]["F(X)"]) <= 1e-6 * abs(h2[i]["F(X)"]) for i in range(41)), c2[-1:] if c2 else None, h2[40]["F(X)"] if 40 in h2 else None)
# ---- Stage-2 engine output and saved fields
eo2 = os.path.join(d2, "engine_output.exo"); ri = os.path.join(d2, "restart_input.exo"); eo1 = os.path.join(d1, "engine_output.exo")
m2, a2 = fields(eo2); m1, a1 = fields(ri)
chk("stage 2 engine_output.exo time steps = 41 (local iterations 0..40)", m2["time_steps"] == 41, m2["time_steps"], 41)
chk("stage 2 engine_output.exo nodal fields include control and topology", "control" in m2["nodal_fields"] and "topology" in m2["nodal_fields"], m2["nodal_fields"], ["control", "topology"])
chk("stage 2 engine_output.exo node/element counts", m2["num_nodes"] == 30625 and m2["num_elem"] == 27648, [m2["num_nodes"], m2["num_elem"]], [30625, 27648])
chk("restart_input.exo is byte-identical to the Stage-1 checkpoint", sha(ri) == sha(eo1), sha(ri), sha(eo1))
chk("restart_input.exo has 21 saved states (iterations 0..20)", m1["time_steps"] == 21, m1["time_steps"], 21)
fs = {}
if "control" in a2 and "control" in a1:
    d_all = [float(np.abs(a2["control"][0] - a1["control"][s]).max()) for s in range(m1["time_steps"])]
    best = int(np.argmin(d_all))
    chk("CONTINUATION: stage 2 saved control state 0 == stage 1 saved control state of iteration 20 (time step 21), nodewise (max abs diff <= 1e-12)", d_all[20] <= 1e-12, d_all[20], "<= 1e-12")
    chk("CONTINUATION: the checkpoint state closest to stage 2's initial control is iteration 20 (and it is an exact match)", best == 20 and d_all[20] == 0.0, {"closest_stage1_iteration": best, "max_abs_diff": d_all[best]}, {"closest_stage1_iteration": 20, "max_abs_diff": 0.0})
    fs["max_abs_diff_stage2_control0_vs_stage1_control_state_k"] = {str(k): v for k, v in enumerate(d_all)}
    if "topology" in a2 and "topology" in a1:
        fs["max_abs_diff_stage2_topology0_vs_stage1_topology20"] = float(np.abs(a2["topology"][0] - a1["topology"][20]).max())
    chk("stage 2 saved control states all finite and in [0,1]", bool(np.all(np.isfinite(a2["control"])) and a2["control"].min() >= -1e-12 and a2["control"].max() <= 1 + 1e-12), [float(a2["control"].min()), float(a2["control"].max())], "[0,1]")
    chk("stage 2 design evolves (consecutive saved control states differ)", all(np.abs(a2["control"][s] - a2["control"][s-1]).max() > 0 for s in range(1, m2["time_steps"])), m2["time_steps"] - 1, "all consecutive pairs differ")
    fs["stage2_final_control_stats"] = {"min": float(a2["control"][-1].min()), "max": float(a2["control"][-1].max()), "mean": float(a2["control"][-1].mean())}
    if "topology" in a2: fs["stage2_final_topology_mean"] = float(a2["topology"][-1].mean())
# ---- analyze outputs
adir = os.path.join(d2, "analyze_id_2_output_scenario_id_1")
afiles = sorted(os.listdir(adir)) if os.path.isdir(adir) else []
it_exo = sorted(int(m.group(1)) for f in afiles for m in [re.match(r'iteration(\d+)\.exo$', f)] if m)
chk("stage 2 analyze per-iteration exodus files iteration0..40", it_exo == list(range(41)), it_exo[:3] + ["..."] + it_exo[-3:] if it_exo else [], list(range(41)))
fin = os.path.join(adir, "iteration40.exo")
if os.path.exists(fin):
    da = Dataset(fin); nv = names(da, "name_nod_var") if "name_nod_var" in da.variables else []
    chk("stage 2 final analyze output (iteration40.exo) has displacement fields", any("displacement" in v or "disp" in v for v in nv), nv, "displacement_x/y/z present"); da.close()
out = {"stage2_directory": d2, "stage1_directory": d1, "verified_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
       "continuation_evidence": {
           "checkpoint_used": {"path_read_by_stage2": "restart_input.exo (run directory work/stage2; deliverable outputs/stage2/restart_input.exo)", "copy_of": "outputs/stage1/engine_output.exo", "sha256": sha(ri)},
           "field_used": "control", "restart_iteration_keyword_value": rit, "generated_config_Iteration_tag": rit,
           "saved_state_used": "Stage-1 iteration 20 (checkpoint Exodus time step 21 of 21, the last saved state)",
           "stage1_compliance_iteration_20": {"diagnostics": h1.get(20, {}).get("F(X)_text"), "opt_criteria_history_csv": c1[20] if len(c1) >= 21 else None},
           "stage2_first_evaluated_compliance_local_iteration_0": {"diagnostics": h2.get(0, {}).get("F(X)_text"), "opt_criteria_history_csv": c2[0] if c2 else None},
           "stage1_iterations_whose_compliance_equals_stage2_first": matches,
           "stage1_compliance_history_for_reference": {str(k): h1[k]["F(X)_text"] for k in sorted(h1)},
           "field_comparison": fs},
       "stage2_engine_output": {"path": eo2, "sha256": sha(eo2), "time_steps": m2["time_steps"], "nodal_fields": m2["nodal_fields"]},
       "stage2_final_analyze_output": {"path": fin, "sha256": sha(fin) if os.path.exists(fin) else None},
       "stage2_diagnostics_sha256": sha(os.path.join(d2, "morphorm_oc_optimizer_diagnostics.txt")),
       "stage2_stopping_message": stop2, "stage2_diagnostics_history": {str(k): {kk: vv for kk, vv in h2[k].items() if kk != "F(X)_text"} for k in sorted(h2)},
       "checks": res, "ALL_CHECKS_PASS": all(r["pass"] for r in res)}
print(json.dumps(out, indent=2)); sys.exit(0 if out["ALL_CHECKS_PASS"] else 1)
