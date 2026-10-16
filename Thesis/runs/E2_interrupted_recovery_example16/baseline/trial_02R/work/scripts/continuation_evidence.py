"""Continuation evidence (spec section 7): did Stage 2 resume from the iteration-20 `control` design of Stage 1?
Usage: continuation_evidence.py <stage1_run_dir> <stage2_run_dir> <out.json> [probe_dir_label=path ...]"""
import sys, os, re, json, hashlib, datetime
import xml.etree.ElementTree as ET
import numpy as np
from netCDF4 import Dataset

s1, s2, out = sys.argv[1], sys.argv[2], sys.argv[3]
probes = dict(a.split("=", 1) for a in sys.argv[4:])
def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()
def names(ds, var):
    res = []
    for row in ds.variables[var][:]:
        if hasattr(row, "filled"): row = row.filled(b"")
        res.append(b"".join(x if isinstance(x, bytes) else x.encode() for x in row).decode().strip("\x00").strip())
    return res
def diag_rows(p):
    rows = []
    for line in open(p).read().splitlines():
        m = re.match(r"\s*(\d+)\s+(\d+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)\s+([-+0-9.eE]+)", line)
        if m: rows.append({"iter": int(m.group(1)), "F": float(m.group(3)), "normF": float(m.group(4)), "H1": float(m.group(5))})
    return rows
def csv_vals(p):
    r = [l.strip() for l in open(p).read().replace("\r", "\n").splitlines() if l.strip()]
    return [float(x) for x in r[0].split(",")[1:] if x.strip()] if r else []
def field(p, name, step):
    ds = Dataset(p, "r"); nod = names(ds, "name_nod_var"); i = nod.index(name) + 1
    v = np.array(ds.variables[f"vals_nod_var{i}"][step - 1]); nt = int(len(ds.variables["time_whole"][:])); ds.close(); return v, nt

C = {}
def check(name, cond, observed): C[name] = {"pass": bool(cond), "observed": observed}

# restart settings actually used (generated configuration of Stage 2)
eo_xml = open(os.path.join(s2, "engine_operations.xml")).read()
root = ET.fromstring("<root>" + eo_xml.replace('<?xml version="1.0"?>', "") + "</root>")
init = [o for o in root.findall("Operation") if o.findtext("Name") == "Initialize Field"][0]
ff = init.find("FromFieldOnInputMesh")
restart = {"Method": init.findtext("Method"), "file": ff.findtext("Name"), "field": ff.findtext("VariableName"), "Iteration": int(ff.findtext("Iteration"))}
deck = open(os.path.join(s2, "input_deck.i")).read()
deck_kw = {k: re.search(r"^\s*%s\s+(\S+)" % k, deck, re.M).group(1) for k in ["initial_guess_file_name", "initial_guess_field_name", "restart_iteration", "max_iterations"]}
check("stage 2 reads the `control` field (not `topology`)", restart["field"] == "control" and deck_kw["initial_guess_field_name"] == "control", restart)
check("stage 2 reads restart_input.exo = byte-identical copy of the Stage-1 checkpoint", sha(os.path.join(s2, "restart_input.exo")) == sha(os.path.join(s1, "engine_output.exo")), {"restart_input.exo": sha(os.path.join(s2, "restart_input.exo")), "stage1 engine_output.exo": sha(os.path.join(s1, "engine_output.exo"))})

# compliance comparison
d1 = diag_rows(os.path.join(s1, "morphorm_oc_optimizer_diagnostics.txt"))
d2 = diag_rows(os.path.join(s2, "morphorm_oc_optimizer_diagnostics.txt"))
c1 = csv_vals(os.path.join(s1, "opt_criteria_history.csv")); c2 = csv_vals(os.path.join(s2, "opt_criteria_history.csv"))
F1_20 = d1[20]["F"]; F2_0 = d2[0]["F"]
matches = [r["iter"] for r in d1 if r["F"] == F2_0]
check("first Stage-2 compliance (local iter 0) == Stage-1 iteration-20 compliance (diagnostics, 7 significant digits)", F2_0 == F1_20, {"stage1_iter20_F": F1_20, "stage2_iter0_F": F2_0, "stage1_iterations_with_equal_F": matches})
check("Stage-1 iteration matched by the first Stage-2 compliance is 20 only", matches == [20], matches)
rel = abs(c2[0] - c1[-1]) / abs(c1[-1]) if c1 and c2 else None
check("first Stage-2 objective == last Stage-1 objective (full precision, opt_criteria_history.csv, rel diff <= 1e-12)", rel is not None and rel <= 1e-12, {"stage1_last": c1[-1] if c1 else None, "stage2_first": c2[0] if c2 else None, "rel_diff": rel})
check("first Stage-2 Norm(F') and H1 equal Stage-1 iteration-20 values", d2[0]["normF"] == d1[20]["normF"] and d2[0]["H1"] == d1[20]["H1"], {"stage1_iter20": d1[20], "stage2_iter0": d2[0]})

# saved-field comparison: Stage-2 engine output step 1 (local iteration 0) vs checkpoint step used (and step 20 for contrast)
ck = os.path.join(s2, "restart_input.exo")
ck_ctrl_21, nt_ck = field(ck, "control", 21); ck_ctrl_20, _ = field(ck, "control", 20); ck_topo_21, _ = field(ck, "topology", 21)
s2_ctrl_0, nt_s2 = field(os.path.join(s2, "engine_output.exo"), "control", 1); s2_topo_0, _ = field(os.path.join(s2, "engine_output.exo"), "topology", 1)
used_ctrl, _ = field(ck, "control", restart["Iteration"])
dev21 = float(np.max(np.abs(s2_ctrl_0 - ck_ctrl_21))); dev20 = float(np.max(np.abs(s2_ctrl_0 - ck_ctrl_20))); devt = float(np.max(np.abs(s2_topo_0 - ck_topo_21)))
check("checkpoint has 21 saved states; restart <Iteration> points at the last one (time step 21 = optimizer iteration 20)", nt_ck == 21 and restart["Iteration"] == 21, {"checkpoint_time_steps": nt_ck, "Iteration": restart["Iteration"]})
check("Stage-2 initial `control` (engine output step 1) == checkpoint `control` at time step 21 (iteration 20), max|diff| == 0", dev21 == 0.0, {"max_abs_diff_vs_step21": dev21, "max_abs_diff_vs_step20_for_contrast": dev20})
check("Stage-2 initial `topology` == checkpoint `topology` at time step 21 (filter reproduces the same filtered density)", devt <= 1e-10, {"max_abs_diff": devt})
check("the saved state named by <Iteration> is the iteration-20 control field", float(np.max(np.abs(used_ctrl - ck_ctrl_21))) == 0.0, restart["Iteration"])

# probe evidence (short runs used to determine the restart_iteration convention)
probe_info = {}
for label, p in probes.items():
    pr = diag_rows(os.path.join(p, "morphorm_oc_optimizer_diagnostics.txt"))
    pdeck = open(os.path.join(p, "input_deck.i")).read()
    ri = int(re.search(r"^\s*restart_iteration\s+(\d+)", pdeck, re.M).group(1))
    m = [r["iter"] for r in d1 if r["F"] == pr[0]["F"]]
    probe_info[label] = {"run_dir": p, "restart_iteration": ri, "first_F": pr[0]["F"], "matches_stage1_iteration": m, "rows": pr}

record = {"frozen_configuration_id": "FROZEN-EX16-v1", "verified_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
          "stage1_run_dir": s1, "stage2_run_dir": s2,
          "restart_settings_in_deck": deck_kw, "restart_settings_in_generated_config": restart,
          "checkpoint": {"file": ck, "sha256": sha(ck), "time_steps": nt_ck, "time_step_to_iteration": "time step k+1 holds optimizer iteration k (steps 1..21 = iterations 0..20)"},
          "compliance": {"stage1_iter20_diag": F1_20, "stage2_iter0_diag": F2_0, "stage1_last_csv": c1[-1] if c1 else None, "stage2_first_csv": c2[0] if c2 else None,
                          "stage1_history_diag": [r["F"] for r in d1], "stage2_history_diag": [r["F"] for r in d2]},
          "stage2_iterations_completed": d2[-1]["iter"] if d2 else None, "overall_iteration_reached": 20 + d2[-1]["iter"] if d2 else None,
          "field_comparison": {"stage2_step1_control_vs_checkpoint_step21": dev21, "stage2_step1_control_vs_checkpoint_step20": dev20, "stage2_step1_topology_vs_checkpoint_step21": devt},
          "probes": probe_info,
          "checks": C, "all_checks_pass": all(v["pass"] for v in C.values()), "n_pass": sum(v["pass"] for v in C.values()), "n_checks": len(C)}
json.dump(record, open(out, "w"), indent=2)
for k, v in C.items(): print(("PASS" if v["pass"] else "FAIL"), k, "->", v["observed"])
print("ALL PASS" if record["all_checks_pass"] else "SOME CHECKS FAILED", record["n_pass"], "/", record["n_checks"])
sys.exit(0 if record["all_checks_pass"] else 1)
