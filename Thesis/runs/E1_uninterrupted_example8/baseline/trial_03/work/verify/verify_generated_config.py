#!/usr/bin/env python3
"""Verify XMLGenerator output of FROZEN-EX8-v1 against the locked settings. Usage: verify_generated_config.py <run_dir>"""
import sys, os, json, datetime, re, math
import xml.etree.ElementTree as ET

d = sys.argv[1]
res = {"run_dir": os.path.abspath(d), "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "checks": []}
def check(name, got, want, ok=None):
    if ok is None: ok = (got == want)
    res["checks"].append({"check": name, "got": got, "expected": want, "pass": bool(ok)})
def fnum(s): return float(s)

def load_multi_root(path):
    with open(path) as f: txt = f.read()
    txt = re.sub(r'<\?xml[^>]*\?>', '', txt)
    return ET.fromstring("<root>" + txt + "</root>")

# ---- Helmholtz configuration ----
hp = os.path.join(d, "analyze_helmholtz_input_deck.xml")
check("helmholtz_input_deck_exists", os.path.exists(hp), True)
if os.path.exists(hp):
    h = ET.parse(hp).getroot()
    params = {p.get("name"): p.get("value") for p in h.iter("Parameter")}
    check("helmholtz_physics", params.get("Physics"), "Helmholtz Filter")
    ls = params.get("Length Scale")
    # Morphorm converts the absolute radius R to the PDE length scale l0 = R/(2*sqrt(3))
    expect_ls = 0.15/(2*math.sqrt(3))
    check("helmholtz_length_scale_present", ls is not None, True)
    check("helmholtz_length_scale_value (R=0.15 -> R/(2*sqrt3))", ls, round(expect_ls, 6), ls is not None and abs(fnum(ls)-expect_ls) < 1e-5)
    sls = params.get("Surface Length Scale")
    check("helmholtz_surface_length_scale_present", sls is not None, True)
    check("helmholtz_surface_length_scale_value (boundary_sticking_penalty 1.0)", sls, "1.0", sls is not None and abs(fnum(sls)-1.0) < 1e-12)
    sym_keys = {k: v for k, v in params.items() if k and "ymmetry" in k}
    check("helmholtz_symmetry_plane_sideset_present (ss_sym)", sym_keys, "a parameter naming ss_sym", any("ss_sym" in (v or "") for v in sym_keys.values()))
    check("helmholtz_mesh", params.get("Input Mesh"), "mesh.exo")
    check("helmholtz_domain_block", params.get("Element Block"), "block_1")

# ---- analyze (physics) configuration ----
ap = os.path.join(d, "analyze_2_input_deck.xml")
check("analyze_input_deck_exists", os.path.exists(ap), True)
if os.path.exists(ap):
    a = ET.parse(ap).getroot()
    def plist(root, name):
        for pl in root.iter("ParameterList"):
            if pl.get("name") == name: return pl
        return None
    def pval(pl, name):
        if pl is None: return None
        for p in pl.findall("Parameter"):
            if p.get("name") == name: return p.get("value")
        return None
    check("analyze_physics", pval(plist(a, "Scenarios"), "Physics"), "Mechanical")
    check("analyze_dimension", pval(a, "Spatial Dimension"), "3")
    check("analyze_mesh", pval(a, "Input Mesh"), "mesh.exo")
    mm = plist(a, "Isotropic Linear Elastic")
    check("material_youngs_modulus", pval(mm, "Youngs Modulus"), "1.0", mm is not None and abs(fnum(pval(mm, "Youngs Modulus"))-1.0) < 1e-12)
    check("material_poissons_ratio", pval(mm, "Poissons Ratio"), "0.3", mm is not None and abs(fnum(pval(mm, "Poissons Ratio"))-0.3) < 1e-12)
    dom = plist(a, "block_1")
    check("block_1_domain_present", pval(dom, "Element Block"), "block_1")
    check("block_1_uses_material_1", pval(dom, "Material Model"), "material_1")
    obj = plist(a, "My Objective")
    check("objective_criterion_type", pval(obj, "Scalar Function Type"), "Internal Elastic Energy")
    check("objective_domains", pval(obj, "Domains"), "{block_1}")
    pf = plist(obj, "Penalty Function") if obj is not None else None
    check("criterion_simp_type", pval(pf, "Type"), "SIMP")
    check("criterion_simp_exponent", pval(pf, "Exponent"), "3.0", pf is not None and abs(fnum(pval(pf, "Exponent"))-3.0) < 1e-12)
    check("criterion_simp_minimum_value (minimum_ersatz_material_value)", pval(pf, "Minimum Value"), "1e-3", pf is not None and abs(fnum(pval(pf, "Minimum Value"))-1e-3) < 1e-15)
    resid = plist(a, "Mechanical Residual")
    check("residual_interpolation_single_phase", pval(resid, "Material Interpolation Model"), "Single-Phase")
    check("residual_response_linear", pval(resid, "Response"), "Linear")
    rpf = plist(resid, "Penalty Function") if resid is not None else None
    check("residual_simp_type", pval(rpf, "Type"), "SIMP")
    check("residual_simp_exponent", pval(rpf, "Exponent"), "3.0", rpf is not None and abs(fnum(pval(rpf, "Exponent"))-3.0) < 1e-12)
    check("residual_simp_minimum_value", pval(rpf, "Minimum Value"), "1e-3", rpf is not None and abs(fnum(pval(rpf, "Minimum Value"))-1e-3) < 1e-15)
    # loads
    cl = plist(a, "Concentrated Loads")
    loads = [pl for pl in cl.findall("ParameterList")] if cl is not None else []
    check("num_concentrated_loads", len(loads), 1)
    if loads:
        check("load_dof_y (index 1)", pval(loads[0], "Dof"), "1")
        check("load_value", pval(loads[0], "Value"), "-1.0", abs(fnum(pval(loads[0], "Value"))+1.0) < 1e-12)
        check("load_nodeset", pval(loads[0], "Nodes"), "ns_load")
    nbc = plist(a, "Mechanical Natural Boundary Conditions")
    check("no_tractions_or_pressures", len(list(nbc)) if nbc is not None else 0, 0)
    bf = plist(a, "Body Loads")
    check("no_body_loads", bf is None or len(list(bf)) == 0, True)
    # essential BCs
    ebc = plist(a, "Essential Boundary Conditions")
    bcs = []
    for pl in (ebc.findall("ParameterList") if ebc is not None else []):
        bcs.append((pval(pl, "Sides"), int(pval(pl, "Index")), pval(pl, "Type"), float(pval(pl, "Value"))))
    want = {("ns_fix", 0, "Fixed Value", 0.0), ("ns_fix", 1, "Fixed Value", 0.0), ("ns_fix", 2, "Fixed Value", 0.0), ("ss_sym", 2, "Fixed Value", 0.0)}
    check("essential_bcs (ns_fix ux,uy,uz=0; ss_sym uz=0)", sorted(bcs), sorted(want), set(bcs) == want and len(bcs) == 4)
    out = plist(a, "Output")
    check("analyze_output_displacements", pval(out, "Plottable"), "{displacement_x, displacement_y, displacement_z}")

# ---- engine configuration / interface ----
ip = os.path.join(d, "interface.xml")
check("interface_exists", os.path.exists(ip), True)
if os.path.exists(ip):
    r = load_multi_root(ip)
    perf = [(p.findtext("Name"), p.findtext("Code")) for p in r.findall("Performer")]
    check("performers (engine, analyze, helmholtz analyze)", perf, [("engine_1", "engine"), ("analyze_2", "analyze"), ("analyze_helmholtz", "analyze")])
    opt = r.find("Optimizer")
    check("optimizer_package_OC", opt.findtext("Package"), "OC")
    check("max_iterations_50", opt.findtext("Convergence/MaxIterations"), "50")
    check("update_problem_frequency_1", opt.findtext("Options/ProblemUpdateFrequency"), "1")
    check("update_problem_stage_present", opt.findtext("UpdateProblemStage/Name"), "Update Problem")
    check("oc_control_stagnation_tol_default", opt.findtext("Options/OCControlStagnationTolerance"), "1e-4")
    check("oc_objective_stagnation_tol_default", opt.findtext("Options/OCObjectiveStagnationTolerance"), "1e-8")
    check("oc_gradient_tol_default", opt.findtext("Options/OCGradientTolerance"), "1e-8")
    check("constraint_normalized_target_0.15", opt.findtext("Constraint/NormalizedTargetValue"), "0.15")
    check("constraint_reference_design_volume", opt.findtext("Constraint/ReferenceValueName"), "Design Volume")
    check("bounds_0_1", (opt.findtext("BoundConstraint/Lower"), opt.findtext("BoundConstraint/Upper")), ("0.0", "1.0"))
    check("filtered_variable_is_Topology", opt.findtext("OptimizationVariables/FilteredName"), "Topology")
    # constraint evaluated by engine; objective by analyze_2; filter by analyze_helmholtz
    stages = {s.findtext("Name"): s for s in r.findall("Stage")}
    def ops(stage): return [(o.findtext("Name"), o.findtext("PerformerName")) for o in stages[stage].findall("Operation")]
    check("constraint_value_by_engine", ("Compute Constraint Value 1", "engine_1") in ops("Compute Constraint Value 1"), True)
    check("objective_value_by_analyze", ("Compute Objective Value", "analyze_2") in ops("Compute Objective Value"), True)
    check("filter_control_by_helmholtz_in_objective_stage", ("Filter Control", "analyze_helmholtz") in ops("Compute Objective Value"), True)
    check("filter_gradient_by_helmholtz_in_objective_gradient_stage", ("Filter Gradient", "analyze_helmholtz") in ops("Compute Objective Gradient"), True)
    check("output_stage_has_engine_output", ("PlatoMainOutput", "engine_1") in ops("Output To File"), True)
    check("output_stage_has_analyze_visualization", ("Visualization", "analyze_2") in ops("Output To File"), True)
ep = os.path.join(d, "engine_operations.xml")
if os.path.exists(ep):
    e = load_multi_root(ep)
    ops_e = {o.findtext("Name"): o for o in e.findall("Operation")}
    init = ops_e.get("Initialize Field")
    check("initial_density_uniform_0.15", (init.findtext("Method"), init.findtext("Uniform/Value")), ("Uniform", "0.15"))
    check("engine_output_fields_topology_control", sorted(i.findtext("ArgumentName") for i in ops_e["PlatoMainOutput"].findall("Input")), ["control", "topology"])
    check("engine_output_max_iterations_50", ops_e["PlatoMainOutput"].findtext("MaxIterations"), "50")
    agg = ops_e.get("Aggregate Data")
    check("aggregator_weight_1", agg.findtext("Weighting/Weight/Value"), "1")
    check("normalize_in_aggregator_false (no Normals element)", agg.find("Normals") is None and "ormaliz" not in ET.tostring(agg).decode(), True)
    check("volume_constraint_by_ComputeVolume", ops_e["Compute Constraint Value 1"].findtext("Function"), "ComputeVolume")
    check("update_problem_operation_freq_1", ops_e["Update Problem"].findtext("UpdateProblemFrequency"), "1")
mp = os.path.join(d, "mpirun.source")
if os.path.exists(mp):
    txt = open(mp).read()
    check("mpirun_three_single_rank_performers", txt.count("-np 1"), 3)
    check("mpirun_no_decomposition (no -np >1)", re.findall(r"-np (\d+)", txt), ["1", "1", "1"])
res["all_pass"] = all(c["pass"] for c in res["checks"])
print(json.dumps(res, indent=1))
sys.exit(0 if res["all_pass"] else 1)
