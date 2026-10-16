#!/usr/bin/env python3
"""Researcher-only scientific scorer for one completed baseline trial.

Compares the trial's artifacts with the applicable reference package using the
predeclared acceptance specification (JSON).  Records `accepted`, `rejected` or
`needs_review` with the reason and every measured value, separately from any
telemetry.  Never writes into the trial packet.

Usage: score_trial.py --trial-dir D --spec acceptance_spec.json --out-dir O [--figures-dir F]
Run with the approved runtime's python3 (numpy, netCDF4).
"""
import argparse, csv, glob, json, os, re, subprocess, sys, time
import numpy as np
from netCDF4 import Dataset

ap = argparse.ArgumentParser()
ap.add_argument("--trial-dir", required=True)
ap.add_argument("--spec", required=True)
ap.add_argument("--out-dir", required=True)
ap.add_argument("--figures-dir")
a = ap.parse_args()
T = os.path.abspath(a.trial_dir)
S = json.load(open(a.spec))
tools = os.path.dirname(os.path.abspath(__file__))
rid = re.search(r"^run_id:\s*(\S+)", open(os.path.join(T, "manifest.yaml")).read(), re.M).group(1)
reasons, measured, checks = [], {}, {}
decision_floor = None  # 'needs_review' caps the decision; 'rejected' forces it


def cap(level, why):
    global decision_floor
    reasons.append(f"[{level}] {why}")
    order = {None: 0, "needs_review": 1, "rejected": 2}
    if order[level] > order[decision_floor]:
        decision_floor = level


# ---------------------------------------------------------------- helpers
def names(ds, var):
    return [b"".join(r.compressed()).decode().strip() for r in ds.variables[var][:]] if var in ds.variables else []


def nodal(path, name, step=-1):
    with Dataset(path) as ds:
        nm = names(ds, "name_nod_var")
        return np.asarray(ds.variables[f"vals_nod_var{nm.index(name) + 1}"][step, :], float)


def allsteps(path, name):
    with Dataset(path) as ds:
        nm = names(ds, "name_nod_var")
        return np.asarray(ds.variables[f"vals_nod_var{nm.index(name) + 1}"][:], float), np.asarray(ds.variables["time_whole"][:], float)


def coords(path):
    with Dataset(path) as ds:
        return np.stack([np.asarray(ds.variables[c][:]) for c in ("coordx", "coordy", "coordz")], 1)


def mesh_report(path):
    with Dataset(path) as ds:
        x = coords(path)
        rep = {"num_nodes": len(ds.dimensions["num_nodes"]), "num_elem": len(ds.dimensions["num_elem"]),
               "block_names": names(ds, "eb_names"), "element_type": ds.variables["connect1"].getncattr("elem_type"),
               "bbox": [float(x[:, i].min()) for i in range(3)] + [float(x[:, i].max()) for i in range(3)], "nodesets": {}, "sidesets": {}}
        for i, n in enumerate(names(ds, "ns_names"), 1):
            rep["nodesets"][n] = int(len(ds.dimensions[f"num_nod_ns{i}"]))
        for i, n in enumerate(names(ds, "ss_names"), 1):
            rep["sidesets"][n] = int(len(ds.dimensions[f"num_side_ss{i}"]))
    return rep


def diag_rows(path):
    rows = []
    for line in open(path):
        p = line.split()
        if p and p[0].isdigit():
            rows.append((int(p[0]), float(p[2]), float(p[4])))
    stop = any("Optimization stopping" in l for l in open(path))
    return rows, stop


def find_one(rel_candidates, glob_patterns, label):
    """Locked deliverable path first; otherwise search the packet (ambiguity -> needs_review)."""
    for rel in rel_candidates:
        p = os.path.join(T, rel)
        if os.path.isfile(p) and os.path.getsize(p) > 0:
            return p, "locked_path"
    hits = sorted({h for pat in glob_patterns for h in glob.glob(os.path.join(T, pat), recursive=True) if os.path.getsize(h) > 0}, key=os.path.getmtime)
    if not hits:
        cap("rejected", f"{label}: not found at its locked path nor anywhere in the packet")
        return None, "missing"
    cap("needs_review", f"{label}: not at its locked path; using newest of {len(hits)} candidate(s): {os.path.relpath(hits[-1], T)}")
    return hits[-1], "searched"


def field_compare(trial_exo, ref_exo, field="Topology"):
    """Compare a final nodal field after matching nodes by coordinates (robust to node numbering)."""
    xt, xr = coords(trial_exo), coords(ref_exo)
    if xt.shape != xr.shape:
        return {"comparable": False, "reason": f"node count {xt.shape[0]} vs reference {xr.shape[0]}"}
    it = np.lexsort((np.round(xt[:, 2], 8), np.round(xt[:, 1], 8), np.round(xt[:, 0], 8)))
    ir = np.lexsort((np.round(xr[:, 2], 8), np.round(xr[:, 1], 8), np.round(xr[:, 0], 8)))
    if np.abs(xt[it] - xr[ir]).max() > 1e-8:
        return {"comparable": False, "reason": "node coordinates differ after sorting (different mesh)"}
    ft, fr = nodal(trial_exo, field)[it], nodal(ref_exo, field)[ir]
    return {"comparable": True, "max_abs_diff": float(np.abs(ft - fr).max()), "mean_abs_diff": float(np.abs(ft - fr).mean()),
            "node_order_identical": bool((it == np.arange(len(it))).all() and (ir == np.arange(len(ir))).all())}


def history_compare(rows, ref_csv):
    ref = {int(r["iteration"]): (float(r["compliance_F"]), float(r["volume_constraint_H1"])) for r in csv.DictReader(open(ref_csv))}
    common = [i for i, _, _ in rows if i in ref]
    if not common:
        return {"comparable": False}
    rel = [abs(F - ref[i][0]) / abs(ref[i][0]) for i, F, _ in rows if i in ref]
    last = rows[-1]
    return {"comparable": True, "iterations_compared": len(common), "max_rel_diff_compliance": float(max(rel)),
            "final_rel_diff_compliance": float(abs(last[1] - ref[max(ref)][0]) / abs(ref[max(ref)][0])) if last[0] == max(ref) else None,
            "trial_final_compliance": last[1], "reference_final_compliance": ref[max(ref)][0], "trial_final_H1": last[2]}


def run_checker(rundir, args):
    p = subprocess.run([sys.executable, "-I", os.path.join(tools, "check_generated_config.py"), rundir] + args + ["--out", os.path.join(a.out_dir, f"generated_config_check_{os.path.basename(rundir.rstrip('/'))}.json")],
                       capture_output=True, text=True)
    fails = [l for l in p.stdout.splitlines() if l.startswith("FAIL")]
    return p.returncode == 0, fails, p.stdout.splitlines()[-1] if p.stdout else p.stderr[-300:]


def input_mesh_name(rundir):
    """Mesh file name the generated configuration refers to (the agent's own name for its mesh)."""
    try:
        m = re.search(r'name="Input Mesh"[^>]*value="([^"]+)"', open(os.path.join(rundir, "analyze_2_input_deck.xml")).read())
        return m.group(1) if m else None
    except FileNotFoundError:
        return None


def helmholtz_symmetry_present(rundir):
    try:
        return "Symmetry Plane Sides" in open(os.path.join(rundir, "analyze_helmholtz_input_deck.xml")).read()
    except FileNotFoundError:
        return None


tol = S["tolerances"]
os.makedirs(a.out_dir, exist_ok=True)
pv = os.path.join(T, "logs", "packet_verification.json")
if os.path.isfile(pv):
    v = json.load(open(pv))
    measured["packet_verification"] = v.get("result")
    if v.get("result") == "failed":
        cap("rejected", "packet verification failed (deliverables/hashes/boundary/session checks); see logs/packet_verification.json")
    elif v.get("result") == "ambiguous":
        cap("needs_review", "packet verification ambiguous")
else:
    cap("needs_review", "no packet verification record (run verify_trial_packet.sh --completed first)")

# ================================================================ mesh
mesh_path, how = find_one(["outputs/mesh.exo"], ["**/*.exo"], "mesh")
if mesh_path:
    rep = mesh_report(mesh_path)
    m = S["mesh"]
    exp_nodes = (m["NX"] + 1) * (m["NY"] + 1) * (m["NZ"] + 1)
    mesh_checks = {"num_elem": rep["num_elem"] == m["NX"] * m["NY"] * m["NZ"], "num_nodes": rep["num_nodes"] == exp_nodes,
                   "block_1": rep["block_names"] == ["block_1"], "HEX8": rep["element_type"].upper().startswith("HEX8"),
                   "bbox": all(abs(x - y) < 1e-6 for x, y in zip(rep["bbox"], [0, 0, 0, m["LX"], m["LY"], m["LZ"]])),
                   "ns_fix": rep["nodesets"].get("ns_fix") == (m["NY"] + 1) * (m["NZ"] + 1), "ns_load": rep["nodesets"].get("ns_load") == m["NZ"] + 1}
    for s in m.get("sidesets", []):
        mesh_checks[f"sideset_{s}"] = rep["sidesets"].get(s) == m["NX"] * m["NY"]
    measured["mesh"] = {"path": os.path.relpath(mesh_path, T), "report": rep, "checks": mesh_checks}
    bad = [k for k, v in mesh_checks.items() if not v]
    if bad:
        cap("rejected", f"mesh does not match the frozen discretization: {bad}")

workflow = S["workflow"]
# ================================================================ EX8 (single run)
if workflow == "frozen_example8":
    diag, _ = find_one(["outputs/morphorm_oc_optimizer_diagnostics.txt"], ["**/morphorm_oc_optimizer_diagnostics.txt"], "optimizer diagnostics")
    final, _ = find_one(["outputs/final_analyze_output.exo"], ["**/analyze_id_*_output_scenario_id_*/iteration50.exo"], "final analyze output")
    cfg_dir = os.path.join(T, "outputs", "generated_config")
    if not os.path.isfile(os.path.join(cfg_dir, "analyze_helmholtz_input_deck.xml")):
        hits = glob.glob(os.path.join(T, "**", "analyze_helmholtz_input_deck.xml"), recursive=True)
        if hits:
            cfg_dir = os.path.dirname(sorted(hits, key=os.path.getmtime)[-1]); cap("needs_review", f"generated config not at locked path; using {os.path.relpath(cfg_dir, T)}")
        else:
            cfg_dir = None; cap("rejected", "no generated Helmholtz configuration found")
    sym = helmholtz_symmetry_present(cfg_dir) if cfg_dir else None
    measured["generated_config"] = {"dir": os.path.relpath(cfg_dir, T) if cfg_dir else None, "symmetry_plane_sides_present": sym}
    if cfg_dir:
        mname = input_mesh_name(cfg_dir) or "mesh.exo"
        measured["generated_config"]["input_mesh_name"] = mname
        ok, fails, summary = run_checker(cfg_dir, S["generated_config_args"].split() + ["--mesh", mname] + (["--symmetry-sides", "ss_sym"] if sym else ["--no-symmetry-sides"]))
        measured["generated_config"].update({"all_other_checks_pass": ok, "fails": fails, "summary": summary})
        if fails:
            cap("rejected", f"generated configuration deviates from the frozen formulation: {fails}")
    if diag:
        rows, stop = diag_rows(diag)
        measured["iterations"] = {"first": rows[0][0] if rows else None, "last": rows[-1][0] if rows else None, "count": len(rows), "stop_message_present": stop}
        if not rows or rows[-1][0] != S["iterations"]:
            cap("rejected", f"optimizer did not reach iteration {S['iterations']} (last logged: {rows[-1][0] if rows else None})")
        # which reference variant does the trial reproduce?
        comp = {}
        for name, ref in S["references"].items():
            comp[name] = history_compare(rows, ref["history_csv"])
            if final and os.path.isfile(ref["final_exo"]):
                comp[name]["final_topology"] = field_compare(final, ref["final_exo"])
        measured["reference_comparison"] = comp
        best = min(comp, key=lambda n: comp[n].get("final_rel_diff_compliance") if comp[n].get("final_rel_diff_compliance") is not None else 9e99)
        measured["matched_variant"] = best
        d = comp[best].get("final_rel_diff_compliance")
        measured["matched_final_rel_diff"] = d
        if d is None or d > tol["final_compliance_rel_review"]:
            cap("rejected", f"final compliance matches no reference variant within {tol['final_compliance_rel_review']:g} (closest: {best}, rel diff {d})")
        elif d > tol["final_compliance_rel_accept"]:
            cap("needs_review", f"final compliance within review tolerance of {best} but outside accept tolerance (rel diff {d:.3e})")
        ft = comp[best].get("final_topology", {})
        if ft.get("comparable"):
            if ft["max_abs_diff"] > tol["density_max_abs_review"]:
                cap("rejected", f"final density field differs from {best} by max {ft['max_abs_diff']:.3e}")
            elif ft["max_abs_diff"] > tol["density_max_abs_accept"]:
                cap("needs_review", f"final density field within review tolerance of {best} (max {ft['max_abs_diff']:.3e})")
        else:
            cap("needs_review", f"final density field not comparable node-by-node: {ft.get('reason')}")
        policy = S["reference_policy"]
        measured["reference_policy"] = policy
        if policy == "undecided":
            cap("needs_review", "acceptance_spec reference_policy is undecided (researcher must choose the accepted Example 8 variant)")
        elif best != policy:
            cap("rejected", f"trial reproduces the '{best}' variant, but the accepted reference is '{policy}'")
        if sym is False and policy == "symmetry_honored_variant":
            cap("rejected", "filter symmetry plane absent from the generated Helmholtz configuration (specification requires it)")
    if a.figures_dir and final:
        ref = S["references"].get(measured.get("matched_variant") or next(iter(S["references"])))
        png = os.path.join(a.figures_dir, f"{rid}_final_iteration50_vs_{measured.get('matched_variant','reference')}.png")
        subprocess.run([os.path.join(tools, "render_figures.sh"), final, png, f"{rid}: final topology (density >= 0.5) vs reference", "--mirror-z=0.5", f"--compare={ref['final_exo']}", f"--compare-title=reference: {measured.get('matched_variant')}"], capture_output=True)
        measured["figure"] = png if os.path.isfile(png) else None

# ================================================================ EX16 (two stages)
elif workflow == "frozen_example16":
    d1, _ = find_one(["outputs/stage1/morphorm_oc_optimizer_diagnostics.txt"], ["**/stage1*/**/morphorm_oc_optimizer_diagnostics.txt", "**/stage_1*/**/morphorm_oc_optimizer_diagnostics.txt"], "stage-1 diagnostics")
    d2, _ = find_one(["outputs/stage2/morphorm_oc_optimizer_diagnostics.txt"], ["**/stage2*/**/morphorm_oc_optimizer_diagnostics.txt", "**/stage_2*/**/morphorm_oc_optimizer_diagnostics.txt", "**/restart*/**/morphorm_oc_optimizer_diagnostics.txt"], "stage-2 diagnostics")
    ck, _ = find_one(["outputs/stage1/engine_output.exo"], ["**/stage1*/**/engine_output.exo"], "stage-1 engine output (checkpoint)")
    e2, _ = find_one(["outputs/stage2/engine_output.exo"], ["**/stage2*/**/engine_output.exo", "**/restart*/**/engine_output.exo"], "stage-2 engine output")
    f2, _ = find_one(["outputs/stage2/final_analyze_output.exo"], ["**/stage2*/**/iteration40.exo", "**/restart*/**/iteration40.exo"], "stage-2 final analyze output")
    for stage, sub in (("stage1", "outputs/stage1/generated_config"), ("stage2", "outputs/stage2/generated_config")):
        cd = os.path.join(T, sub)
        if os.path.isfile(os.path.join(cd, "interface.xml")):
            args = S["generated_config_args"][stage].split() + ["--mesh", input_mesh_name(cd) or "mesh.exo"]
            if stage == "stage2":
                # read the restart state the agent actually configured
                try:
                    eo = open(os.path.join(cd, "engine_operations.xml")).read()
                    it = re.search(r"<Iteration>(\d+)</Iteration>", eo); fn = re.search(r"<Name>([^<]+)</Name>\s*<VariableName>([^<]+)</VariableName>", eo)
                    measured.setdefault("stage2_restart_config", {}).update({"Iteration": int(it.group(1)) if it else None, "file": fn.group(1) if fn else None, "field": fn.group(2) if fn else None})
                    args += ["--restart-file", fn.group(1) if fn else "initialguess.exo", "--restart-field", "control", "--restart-iteration", it.group(1) if it else "0"]
                except FileNotFoundError:
                    pass
            ok, fails, summary = run_checker(cd, args)
            measured[f"generated_config_{stage}"] = {"all_checks_pass": ok, "fails": fails, "summary": summary}
            real_fails = [f for f in fails if "restart file ==" not in f]
            if real_fails:
                cap("rejected", f"{stage} generated configuration deviates from the frozen formulation: {real_fails}")
        else:
            cap("needs_review", f"{stage} generated configuration not at its locked path")
    if d1:
        r1, s1 = diag_rows(d1)
        measured["stage1"] = {"last_iteration": r1[-1][0] if r1 else None, "count": len(r1), "stop": s1, "final_compliance": r1[-1][1] if r1 else None,
                              "history_vs_reference": history_compare(r1, S["references"]["stage1"]["history_csv"])}
        if not r1 or r1[-1][0] != S["stage1_iterations"]:
            cap("rejected", f"Stage 1 did not reach iteration {S['stage1_iterations']}")
        h = measured["stage1"]["history_vs_reference"]
        if h.get("comparable") and h["max_rel_diff_compliance"] > tol["final_compliance_rel_review"]:
            cap("rejected", f"Stage-1 compliance history differs from the reference (max rel diff {h['max_rel_diff_compliance']:.3e})")
        elif h.get("comparable") and h["max_rel_diff_compliance"] > tol["final_compliance_rel_accept"]:
            cap("needs_review", f"Stage-1 history within review tolerance only (max rel diff {h['max_rel_diff_compliance']:.3e})")
    if ck:
        with Dataset(ck) as ds:
            nsteps, flds = len(ds.dimensions["time_step"]), names(ds, "name_nod_var")
        measured["checkpoint"] = {"path": os.path.relpath(ck, T), "steps": nsteps, "fields": flds}
        if nsteps != S["stage1_iterations"] + 1 or not {"control", "topology"} <= set(flds):
            cap("rejected", f"checkpoint does not hold {S['stage1_iterations'] + 1} states with control and topology (has {nsteps}, {flds})")
    if d1 and d2 and ck and e2:
        r2, s2 = diag_rows(d2)
        r1, _ = diag_rows(d1)
        allc, _ = allsteps(ck, "control")
        c2, _ = allsteps(e2, "control")
        match = [float(np.abs(allc[k] - c2[0]).max()) for k in range(allc.shape[0])]
        km = int(np.argmin(match))
        F1 = {i: F for i, F, _ in r1}
        ev = {"stage2_first_compliance": r2[0][1], "stage1_compliance_at_matched_iteration": F1.get(km), "matched_stage1_iteration": km,
              "match_max_abs_diff": match[km], "compliance_abs_diff_at_match": abs(r2[0][1] - F1.get(km, np.nan)),
              "stage2_last_local_iteration": r2[-1][0], "stage2_count": len(r2), "stop": s2, "stage2_final_compliance": r2[-1][1],
              "overall_final_iteration_equivalent": km + r2[-1][0]}
        measured["continuation"] = ev
        if r2[-1][0] != S["stage2_iterations"]:
            cap("rejected", f"Stage 2 did not reach local iteration {S['stage2_iterations']}")
        if match[km] > 1e-12:
            cap("rejected", "Stage-2 initial control field matches no saved Stage-1 state (not a restart from the checkpoint)")
        variant = {S["resume_iteration"]: "manual_semantics_iteration_20", S["resume_iteration"] - 1: "shipped_listing_iteration_19"}.get(km, "other")
        measured["matched_variant"] = variant
        ref = S["references"].get(variant)
        if ref:
            hc = history_compare(r2, ref["history_csv"])
            measured["stage2_history_vs_reference"] = hc
            if f2 and os.path.isfile(ref["final_exo"]):
                measured["stage2_final_topology_vs_reference"] = field_compare(f2, ref["final_exo"])
            d = hc.get("final_rel_diff_compliance")
            if d is None or d > tol["final_compliance_rel_review"]:
                cap("rejected", f"Stage-2 final compliance differs from the {variant} reference (rel diff {d})")
            elif d > tol["final_compliance_rel_accept"]:
                cap("needs_review", f"Stage-2 final compliance within review tolerance only (rel diff {d:.3e})")
            ft = measured.get("stage2_final_topology_vs_reference", {})
            if ft.get("comparable") and ft["max_abs_diff"] > tol["density_max_abs_review"]:
                cap("rejected", f"Stage-2 final density differs from reference by max {ft['max_abs_diff']:.3e}")
            elif ft.get("comparable") and ft["max_abs_diff"] > tol["density_max_abs_accept"]:
                cap("needs_review", f"Stage-2 final density within review tolerance (max {ft['max_abs_diff']:.3e})")
        else:
            cap("rejected", f"Stage 2 resumed from Stage-1 iteration {km}, which matches no reference variant")
        policy = S["reference_policy"]
        measured["reference_policy"] = policy
        if policy == "undecided":
            cap("needs_review", "acceptance_spec reference_policy is undecided (researcher must choose the accepted restart semantics)")
        elif variant != policy:
            cap("rejected", f"Stage 2 resumed per '{variant}', but the accepted policy is '{policy}'")
        if a.figures_dir and f2 and ref:
            png = os.path.join(a.figures_dir, f"{rid}_final_iteration60_vs_{variant}.png")
            subprocess.run([os.path.join(tools, "render_figures.sh"), f2, png, f"{rid}: final topology (overall iteration 60, density >= 0.5) vs reference", f"--compare={ref['final_exo']}", f"--compare-title=reference: {variant}"], capture_output=True)
            measured["figure"] = png if os.path.isfile(png) else None
else:
    cap("rejected", f"unknown workflow in spec: {workflow}")

decision = decision_floor or "accepted"
if decision == "accepted":
    reasons.append("[accepted] all predeclared checks passed within accept tolerances against the accepted reference")
out = {"run_id": rid, "spec_id": S["spec_id"], "workflow": workflow, "scored_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "decision": decision, "reasons": reasons, "tolerances": tol, "reference_policy": S["reference_policy"], "measured": measured}
json.dump(out, open(os.path.join(a.out_dir, "score.json"), "w"), indent=2)
with open(os.path.join(a.out_dir, "score.md"), "w") as fh:
    fh.write(f"# Score: {rid}\n\n**Decision: {decision}** (spec {S['spec_id']}, policy `{S['reference_policy']}`, scored {out['scored_utc']})\n\n## Reasons\n")
    fh.write("".join(f"- {r}\n" for r in reasons))
    fh.write("\n## Measured values\n```json\n" + json.dumps(measured, indent=2, default=str) + "\n```\n")
print(f"{rid}: {decision}")
for r in reasons:
    print("  " + r)
