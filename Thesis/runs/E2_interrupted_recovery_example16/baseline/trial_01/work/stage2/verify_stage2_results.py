#!/usr/bin/env python3
"""Verify Stage-2 (continuation) results and produce the continuation evidence of specification section 7.
Usage: verify_stage2_results.py <stage2_run_dir> <stage1_checkpoint.exo> <stage1_diagnostics.txt> <restart_iteration_used> [attempt1_diag]
Writes JSON to stdout. Exit 0 only if every check passes.
"""
import sys, os, re, json, hashlib
import numpy as np, netCDF4

run, ck, s1diag, rit = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
att1 = sys.argv[5] if len(sys.argv) > 5 else None
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def names(ds, var):
    return ["".join(x.decode() for x in row.compressed() if x != b"") if hasattr(row, "compressed") else row.tobytes().split(b"\x00")[0].decode() for row in ds.variables[var][:]]
def parse_diag(path):
    txt = open(path).read()
    rows = [l.split() for l in txt.splitlines() if re.match(r"^\s*\d+\s+\d+\s", l)]
    stop = [l.strip() for l in txt.splitlines() if l.strip().startswith("******")]
    return rows, stop, [l for l in txt.splitlines() if re.match(r"^\s*\d+\s+\d+\s", l)]
def nodal_field(path, field):
    ds = netCDF4.Dataset(path); nodal = names(ds, "name_nod_var"); i = nodal.index(field) + 1
    arr = np.array(ds.variables[f"vals_nod_var{i}"][:]); t = ds.variables["time_whole"][:].tolist(); n = ds.dimensions["num_nodes"].size; e = ds.dimensions["num_elem"].size
    ds.close(); return arr, t, nodal, n, e

rec = {"stage2_run_dir": run, "stage1_checkpoint": ck, "restart_iteration_used": rit}
# ---- diagnostics of both stages
r1, stop1, raw1 = parse_diag(s1diag); r2, stop2, raw2 = parse_diag(os.path.join(run, "morphorm_oc_optimizer_diagnostics.txt"))
it1 = [int(r[0]) for r in r1]; it2 = [int(r[0]) for r in r2]
F1 = {int(r[0]): r[2] for r in r1}; F2 = {int(r[0]): r[2] for r in r2}
rec["stage1_diagnostics"] = {"file": s1diag, "sha256": sha(s1diag), "iterations": [it1[0], it1[-1]], "num_rows": len(r1), "stopping_message": stop1,
                             "row_iteration_19": [l for l in raw1 if l.split()[0] == "19"], "row_iteration_20": [l for l in raw1 if l.split()[0] == "20"]}
rec["stage2_diagnostics"] = {"file": os.path.join(run, "morphorm_oc_optimizer_diagnostics.txt"), "sha256": sha(rec["stage1_diagnostics"]["file"]) and sha(os.path.join(run, "morphorm_oc_optimizer_diagnostics.txt")),
                             "iterations": [it2[0], it2[-1]], "num_rows": len(r2), "stopping_message": stop2,
                             "row_iteration_0": [l for l in raw2 if l.split()[0] == "0"], "row_iteration_40": [l for l in raw2 if l.split()[0] == "40"],
                             "compliance_history_local_iter": {k: float(v) for k, v in F2.items()},
                             "compliance_history_overall_iter": {k + 20: float(v) for k, v in F2.items()}}
first2 = r2[0]; last1 = [r for r in r1 if int(r[0]) == 20][0]
match_iter = [k for k, v in F1.items() if v == first2[2]]
rec["continuation_evidence"] = {
    "checkpoint_file": ck, "checkpoint_sha256": sha(ck),
    "restart_copy_read_by_stage2": os.path.join(run, "restart_input.exo"), "restart_copy_sha256": sha(os.path.join(run, "restart_input.exo")),
    "field_read": "control", "restart_iteration_keyword_value": rit,
    "saved_state_semantics": "restart_iteration is the 1-based Exodus time-step index of the checkpoint; time step 21 holds the iteration-20 (end of Stage 1) design",
    "stage1_iteration_20_compliance": last1[2], "stage1_iteration_20_norm_gradient": last1[3], "stage1_iteration_20_constraint": last1[4],
    "stage2_first_evaluated_compliance": first2[2], "stage2_first_norm_gradient": first2[3], "stage2_first_constraint": first2[4],
    "stage1_iterations_whose_compliance_equals_stage2_first": match_iter,
}
if att1 and os.path.exists(att1):
    ra, _, rawa = parse_diag(att1)
    rec["continuation_evidence"]["rejected_attempt1_restart_iteration_20"] = {"diagnostics_snapshot": att1, "first_row": rawa[:1], "first_compliance": ra[0][2] if ra else None,
        "stage1_iterations_whose_compliance_equals_it": [k for k, v in F1.items() if ra and v == ra[0][2]]}
# ---- saved fields: Stage-2 engine_output step 1 (its iteration-0 = initial design) vs checkpoint step 21 (Stage-1 iteration 20)
c1, t1, nod1, n1, e1 = nodal_field(ck, "control"); c2, t2, nod2, n2, e2 = nodal_field(os.path.join(run, "engine_output.exo"), "control")
tp1, _, _, _, _ = nodal_field(ck, "topology"); tp2, _, _, _, _ = nodal_field(os.path.join(run, "engine_output.exo"), "topology")
d_ctrl = {f"stage1_step{k+1}_iter{k}": float(np.abs(c2[0] - c1[k]).max()) for k in range(c1.shape[0])}
best = min(d_ctrl, key=d_ctrl.get)
rec["saved_fields"] = {
    "checkpoint_time_steps": c1.shape[0], "checkpoint_time_values_first_last": [t1[0], t1[-1]], "checkpoint_nodal_fields": nod1,
    "stage2_engine_output_time_steps": c2.shape[0], "stage2_time_values_first_last": [t2[0], t2[-1]], "stage2_nodal_fields": nod2,
    "stage2_nodes_elems": [n2, e2],
    "max_abs_diff_stage2_step1_control_vs_checkpoint_step21_control_(iteration20)": float(np.abs(c2[0] - c1[20]).max()),
    "max_abs_diff_stage2_step1_control_vs_checkpoint_step20_control_(iteration19)": float(np.abs(c2[0] - c1[19]).max()),
    "max_abs_diff_stage2_step1_topology_vs_checkpoint_step21_topology": float(np.abs(tp2[0] - tp1[20]).max()),
    "closest_checkpoint_step_to_stage2_step1_control": best, "max_abs_diff_per_checkpoint_step": d_ctrl,
    "stage2_final_step_control_stats": {"min": float(c2[-1].min()), "max": float(c2[-1].max()), "mean": float(c2[-1].mean())},
    "stage2_final_step_topology_stats": {"min": float(tp2[-1].min()), "max": float(tp2[-1].max()), "mean": float(tp2[-1].mean())},
}
# ---- analyze outputs
ad = os.path.join(run, "analyze_id_2_output_scenario_id_1"); files = sorted(os.listdir(ad)) if os.path.isdir(ad) else []
rec["analyze_output_dir"] = {"dir": ad, "num_files": len(files), "exo_files": sorted([f for f in files if f.endswith(".exo")], key=lambda s: int(re.findall(r"\d+", s)[0]))}
fin = os.path.join(ad, "iteration40.exo"); finrec = None
if os.path.exists(fin):
    d3 = netCDF4.Dataset(fin); finrec = {"file": fin, "sha256": sha(fin), "num_time_steps": d3.dimensions["time_step"].size, "nodal_fields": names(d3, "name_nod_var"), "num_nodes": d3.dimensions["num_nodes"].size}; d3.close()
rec["final_analyze_output"] = finrec
och = os.path.join(run, "opt_criteria_history.csv"); rec["opt_criteria_history"] = open(och).read().strip().splitlines() if os.path.exists(och) else None
checks = {
  "stage2 diagnostics: local iterations 0..40 present (41 rows)": it2 == list(range(41)),
  "stage2 diagnostics: last local iteration == 40 == max_iterations (overall iteration 60)": it2[-1] == 40,
  "stage2 diagnostics: stopped at iteration cap (max iterations message)": any("maximum number of iterations" in s for s in stop2),
  "continuation: Stage-2 first evaluated compliance == Stage-1 iteration-20 compliance (printed values identical)": first2[2] == last1[2],
  "continuation: Stage-2 first compliance matches no other Stage-1 iteration": match_iter == [20],
  "continuation: Stage-2 first gradient norm and constraint value == Stage-1 iteration-20 values": first2[3] == last1[3] and first2[4] == last1[4],
  "continuation: restart copy read by Stage 2 is byte-identical to the checkpoint": rec["continuation_evidence"]["restart_copy_sha256"] == rec["continuation_evidence"]["checkpoint_sha256"],
  "continuation: checkpoint unchanged (sha256 58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8)": rec["continuation_evidence"]["checkpoint_sha256"] == "58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8",
  "saved fields: Stage-2 step-1 control field == checkpoint step-21 (iteration-20) control field (max abs diff 0)": rec["saved_fields"]["max_abs_diff_stage2_step1_control_vs_checkpoint_step21_control_(iteration20)"] == 0.0,
  "saved fields: Stage-2 step-1 control differs from checkpoint step-20 (iteration-19) control": rec["saved_fields"]["max_abs_diff_stage2_step1_control_vs_checkpoint_step20_control_(iteration19)"] > 0.0,
  "saved fields: Stage-2 engine_output has 41 time steps with control and topology": c2.shape[0] == 41 and "control" in nod2 and "topology" in nod2,
  "saved fields: Stage-2 engine_output node/element counts match mesh": n2 == 30625 and e2 == 27648,
  "saved fields: all Stage-2 control values finite and within [0,1]": bool(np.isfinite(c2).all() and c2.min() >= -1e-12 and c2.max() <= 1 + 1e-12),
  "final analyze output iteration40.exo exists with displacement fields": finrec is not None and all(any(f.lower().replace(" ", "_") == p for f in finrec["nodal_fields"]) for p in ("displacement_x", "displacement_y", "displacement_z")),
  "analyze outputs iteration0..40 present": [f"iteration{i}.exo" for i in range(41)] == rec["analyze_output_dir"]["exo_files"],
}
checks = {k: bool(v) for k, v in checks.items()}
rec["checks"] = checks; rec["ALL_CHECKS_PASS"] = all(checks.values())
print(json.dumps(rec, indent=2))
sys.exit(0 if rec["ALL_CHECKS_PASS"] else 1)
