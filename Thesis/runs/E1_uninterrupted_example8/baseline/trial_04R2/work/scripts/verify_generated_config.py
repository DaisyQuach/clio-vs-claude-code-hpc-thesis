#!/usr/bin/env python3
"""Verify the XMLGenerator output of FROZEN-EX8-v1 against every locked setting (read-only)."""
import sys, os, math, re, json, datetime
import xml.etree.ElementTree as ET

d = sys.argv[1]
checks = []
def chk(name, ok, got, want, where):
    checks.append({"check": name, "pass": bool(ok), "got": got, "expected": want, "where": where})

def plist(path):
    return ET.parse(path).getroot()
def find_pl(node, name):
    for c in node.iter("ParameterList"):
        if c.get("name") == name: return c
    return None
def pval(node, name):
    for c in node.iter("Parameter"):
        if c.get("name") == name: return c.get("value")
    return None
def pvals_in(pl, name):
    return [c.get("value") for c in pl.findall("Parameter") if c.get("name") == name]

# ---------- Helmholtz configuration ----------
hf = os.path.join(d, "analyze_helmholtz_input_deck.xml")
h = plist(hf)
chk("helmholtz_physics", pval(h, "Physics") == "Helmholtz Filter", pval(h, "Physics"), "Helmholtz Filter", hf)
chk("helmholtz_mesh", pval(h, "Input Mesh") == "mesh.exo", pval(h, "Input Mesh"), "mesh.exo", hf)
par = find_pl(h, "Parameters")
ls = float(pval(par, "Length Scale")) if par is not None and pval(par, "Length Scale") else None
want_ls = 0.15 / (2.0 * math.sqrt(3.0))   # radius 0.15 -> Helmholtz length scale R/(2*sqrt(3))
chk("helmholtz_length_scale_present_and_equals_0.15/(2sqrt3)", ls is not None and abs(ls - want_ls) < 1e-5, ls, round(want_ls, 6), hf)
sls = pval(par, "Surface Length Scale") if par is not None else None
chk("helmholtz_surface_length_scale_present_=1.0", sls is not None and abs(float(sls) - 1.0) < 1e-12, sls, "1.0", hf)
sym = pval(par, "Symmetry Plane Sides") if par is not None else None
chk("helmholtz_symmetry_plane_sideset_present_=ss_sym", sym is not None and re.sub(r"[{}\s]", "", sym).split(",") == ["ss_sym"], sym, "{ss_sym}", hf)
hdom = find_pl(h, "Domains")
chk("helmholtz_domain_block_1_only", hdom is not None and [c.get("name") for c in hdom.findall("ParameterList")] == ["block_1"], [c.get("name") for c in hdom.findall("ParameterList")] if hdom is not None else None, ["block_1"], hf)

# ---------- analyze (mechanical) configuration ----------
af = os.path.join(d, "analyze_2_input_deck.xml")
a = plist(af)
chk("analyze_physics_mechanical", pval(a, "Physics") == "Mechanical", pval(a, "Physics"), "Mechanical", af)
chk("analyze_spatial_dimension_3", pval(a, "Spatial Dimension") == "3", pval(a, "Spatial Dimension"), "3", af)
chk("analyze_mesh", pval(a, "Input Mesh") == "mesh.exo", pval(a, "Input Mesh"), "mesh.exo", af)
mm = find_pl(a, "Material Models")
mats = [c.get("name") for c in mm.findall("ParameterList")] if mm is not None else []
chk("analyze_single_material", len(mats) == 1, mats, 1, af)
ile = find_pl(a, "Isotropic Linear Elastic")
chk("analyze_material_isotropic_linear_elastic", ile is not None, ile is not None, True, af)
chk("analyze_youngs_modulus_1.0", ile is not None and abs(float(pval(ile, "Youngs Modulus")) - 1.0) < 1e-12, pval(ile, "Youngs Modulus") if ile is not None else None, "1.0", af)
chk("analyze_poissons_ratio_0.3", ile is not None and abs(float(pval(ile, "Poissons Ratio")) - 0.3) < 1e-12, pval(ile, "Poissons Ratio") if ile is not None else None, "0.3", af)
dom = find_pl(a, "Domains")
dnames = [c.get("name") for c in dom.findall("ParameterList")] if dom is not None else []
chk("analyze_domain_block_1_only", dnames == ["block_1"] and pval(dom, "Element Block") == "block_1", dnames, ["block_1"], af)
# criterion: compliance (internal elastic energy) with SIMP 3.0 / 1e-3
crit = find_pl(a, "Criteria")
cnames = [c.get("name") for c in crit.findall("ParameterList")] if crit is not None else []
chk("analyze_single_objective_criterion", len(cnames) == 1, cnames, 1, af)
obj = crit.findall("ParameterList")[0] if cnames else None
chk("analyze_criterion_type_compliance(Internal Elastic Energy)", obj is not None and pval(obj, "Scalar Function Type") == "Internal Elastic Energy", pval(obj, "Scalar Function Type") if obj is not None else None, "Internal Elastic Energy", af)
cp = find_pl(obj, "Penalty Function") if obj is not None else None
chk("analyze_criterion_SIMP", cp is not None and pval(cp, "Type") == "SIMP", pval(cp, "Type") if cp is not None else None, "SIMP", af)
chk("analyze_criterion_SIMP_exponent_3.0", cp is not None and abs(float(pval(cp, "Exponent")) - 3.0) < 1e-12, pval(cp, "Exponent") if cp is not None else None, "3.0", af)
chk("analyze_criterion_minimum_ersatz_1e-3", cp is not None and abs(float(pval(cp, "Minimum Value")) - 1e-3) < 1e-15, pval(cp, "Minimum Value") if cp is not None else None, "1e-3", af)
res = find_pl(a, "Mechanical Residual")
chk("analyze_residual_single_phase", res is not None and pval(res, "Material Interpolation Model") == "Single-Phase", pval(res, "Material Interpolation Model") if res is not None else None, "Single-Phase", af)
chk("analyze_residual_linear", res is not None and pval(res, "Response") == "Linear", pval(res, "Response") if res is not None else None, "Linear", af)
rp = find_pl(res, "Penalty Function") if res is not None else None
chk("analyze_residual_SIMP", rp is not None and pval(rp, "Type") == "SIMP", pval(rp, "Type") if rp is not None else None, "SIMP", af)
chk("analyze_residual_SIMP_exponent_3.0", rp is not None and abs(float(pval(rp, "Exponent")) - 3.0) < 1e-12, pval(rp, "Exponent") if rp is not None else None, "3.0", af)
chk("analyze_residual_SIMP_minimum_1e-3", rp is not None and abs(float(pval(rp, "Minimum Value")) - 1e-3) < 1e-15, pval(rp, "Minimum Value") if rp is not None else None, "1e-3", af)
# load
cl = find_pl(a, "Concentrated Loads")
loads = cl.findall("ParameterList") if cl is not None else []
chk("analyze_one_concentrated_load", len(loads) == 1, len(loads), 1, af)
if loads:
    L = loads[0]
    chk("analyze_load_dof_y(index1)", pval(L, "Dof") == "1", pval(L, "Dof"), "1", af)
    chk("analyze_load_value_-1.0", abs(float(pval(L, "Value")) + 1.0) < 1e-12, pval(L, "Value"), "-1.0", af)
    chk("analyze_load_nodeset_ns_load", pval(L, "Nodes") == "ns_load", pval(L, "Nodes"), "ns_load", af)
nbc = find_pl(a, "Mechanical Natural Boundary Conditions")
chk("analyze_no_tractions", nbc is None or len(list(nbc)) == 0, len(list(nbc)) if nbc is not None else 0, 0, af)
chk("analyze_no_body_loads", find_pl(a, "Body Loads") is None, find_pl(a, "Body Loads") is not None, False, af)
# essential BCs
ebc = find_pl(a, "Essential Boundary Conditions")
got = sorted((pval(b, "Sides"), pval(b, "Index"), pval(b, "Type"), pval(b, "Value")) for b in ebc.findall("ParameterList")) if ebc is not None else []
want = sorted([("ns_fix", "0", "Fixed Value", "0.0"), ("ns_fix", "1", "Fixed Value", "0.0"), ("ns_fix", "2", "Fixed Value", "0.0"), ("ss_sym", "2", "Fixed Value", "0.0")])
chk("analyze_essential_bcs_ns_fix_xyz_and_ss_sym_z", got == want, got, want, af)
# output
out = find_pl(a, "Output")
plot = pval(out, "Plottable") if out is not None else None
chk("analyze_output_displacements_xyz", plot is not None and re.sub(r"[{}\s]", "", plot).split(",") == ["displacement_x", "displacement_y", "displacement_z"], plot, "{displacement_x, displacement_y, displacement_z}", af)

# ---------- interface.xml (optimizer) ----------
inf = os.path.join(d, "interface.xml")
itxt = open(inf).read()
iroot = ET.fromstring("<root>" + itxt.split("?>", 1)[1] + "</root>")
perf = [(p.findtext("Name"), p.findtext("Code")) for p in iroot.findall("Performer")]
chk("interface_performers_engine+analyze+helmholtz", perf == [("engine_1", "engine"), ("analyze_2", "analyze"), ("analyze_helmholtz", "analyze")], perf, [("engine_1", "engine"), ("analyze_2", "analyze"), ("analyze_helmholtz", "analyze")], inf)
opt = iroot.find("Optimizer")
chk("interface_optimizer_OC", opt.findtext("Package") == "OC", opt.findtext("Package"), "OC", inf)
chk("interface_max_iterations_50", opt.findtext("Convergence/MaxIterations") == "50", opt.findtext("Convergence/MaxIterations"), "50", inf)
chk("interface_update_problem_frequency_1", opt.findtext("Options/ProblemUpdateFrequency") == "1", opt.findtext("Options/ProblemUpdateFrequency"), "1", inf)
chk("interface_update_problem_stage_present", opt.findtext("UpdateProblemStage/Name") == "Update Problem", opt.findtext("UpdateProblemStage/Name"), "Update Problem", inf)
tols = {k: opt.findtext("Options/" + k) for k in ("OCControlStagnationTolerance", "OCObjectiveStagnationTolerance", "OCGradientTolerance")}
chk("interface_OC_default_tolerances", tols == {"OCControlStagnationTolerance": "1e-4", "OCObjectiveStagnationTolerance": "1e-8", "OCGradientTolerance": "1e-8"}, tols, {"OCControlStagnationTolerance": "1e-4", "OCObjectiveStagnationTolerance": "1e-8", "OCGradientTolerance": "1e-8"}, inf)
cons = opt.findall("Constraint")
chk("interface_single_constraint", len(cons) == 1, len(cons), 1, inf)
chk("interface_constraint_relative_target_0.15", cons and cons[0].findtext("NormalizedTargetValue") == "0.15", cons[0].findtext("NormalizedTargetValue") if cons else None, "0.15", inf)
chk("interface_constraint_reference_design_volume", cons and cons[0].findtext("ReferenceValueName") == "Design Volume", cons[0].findtext("ReferenceValueName") if cons else None, "Design Volume", inf)
chk("interface_bounds_0_1", opt.findtext("BoundConstraint/Lower") == "0.0" and opt.findtext("BoundConstraint/Upper") == "1.0", [opt.findtext("BoundConstraint/Lower"), opt.findtext("BoundConstraint/Upper")], ["0.0", "1.0"], inf)
chk("interface_filtered_variable_Topology", opt.findtext("OptimizationVariables/FilteredName") == "Topology", opt.findtext("OptimizationVariables/FilteredName"), "Topology", inf)
# constraint evaluated by the engine, objective by analyze, filter by helmholtz service
def stage_ops(name):
    for s in iroot.findall("Stage"):
        if s.findtext("Name") == name:
            return [(o.findtext("Name"), o.findtext("PerformerName")) for o in s.findall("Operation")]
    return None
chk("interface_constraint_value_by_engine", ("Compute Constraint Value 1", "engine_1") in (stage_ops("Compute Constraint Value 1") or []), stage_ops("Compute Constraint Value 1"), "engine_1 computes constraint", inf)
chk("interface_objective_value_by_analyze", ("Compute Objective Value", "analyze_2") in (stage_ops("Compute Objective Value") or []), stage_ops("Compute Objective Value"), "analyze_2 computes objective", inf)
chk("interface_filter_by_helmholtz_service", ("Filter Control", "analyze_helmholtz") in (stage_ops("Compute Objective Value") or []) and ("Filter Gradient", "analyze_helmholtz") in (stage_ops("Compute Objective Gradient") or []), [stage_ops("Compute Objective Value"), stage_ops("Compute Objective Gradient")], "analyze_helmholtz filters control and gradient", inf)
chk("interface_output_stage_present", opt.findtext("Output/OutputStage") == "Output To File", opt.findtext("Output/OutputStage"), "Output To File", inf)

# ---------- engine_operations.xml ----------
ef = os.path.join(d, "engine_operations.xml")
eroot = ET.fromstring("<root>" + open(ef).read().split("?>", 1)[1] + "</root>")
ops = {o.findtext("Name"): o for o in eroot.findall("Operation")}
ini = ops.get("Initialize Field")
chk("engine_initial_density_uniform_0.15", ini is not None and ini.findtext("Method") == "Uniform" and abs(float(ini.findtext("Uniform/Value")) - 0.15) < 1e-12, [ini.findtext("Method"), ini.findtext("Uniform/Value")] if ini is not None else None, ["Uniform", "0.15"], ef)
up = ops.get("Update Problem")
chk("engine_update_problem_frequency_1", up is not None and up.findtext("UpdateProblemFrequency") == "1", up.findtext("UpdateProblemFrequency") if up is not None else None, "1", ef)
po = ops.get("PlatoMainOutput")
pin = sorted(i.findtext("ArgumentName") for i in po.findall("Input")) if po is not None else []
chk("engine_output_control_and_topology", pin == ["control", "topology"], pin, ["control", "topology"], ef)
chk("engine_output_max_iterations_50", po is not None and po.findtext("MaxIterations") == "50", po.findtext("MaxIterations") if po is not None else None, "50", ef)
agg = ops.get("Aggregate Data")
wts = [w.findtext("Value") for w in agg.findall("Weighting/Weight")] if agg is not None else []
chk("engine_aggregator_single_weight_1", wts == ["1"], wts, ["1"], ef)
chk("engine_aggregator_no_normalization(normalize_in_aggregator=false)", agg is not None and agg.find("Normals") is None and "ormaliz" not in ET.tostring(agg).decode(), "no normalization element", "no normalization element", ef)
lb = ops.get("Compute Lower Bounds")
chk("engine_discretization_density", lb is not None and lb.findtext("Discretization") == "density", lb.findtext("Discretization") if lb is not None else None, "density", ef)
cv = ops.get("Compute Constraint Value 1")
chk("engine_constraint_is_volume", cv is not None and cv.findtext("Function") == "ComputeVolume", cv.findtext("Function") if cv is not None else None, "ComputeVolume", ef)

# ---------- engine_input_deck.xml ----------
gf = os.path.join(d, "engine_input_deck.xml")
groot = ET.fromstring("<root>" + open(gf).read().split("?>", 1)[1] + "</root>")
chk("engine_mesh_file", groot.findtext("mesh/mesh") == "mesh.exo", groot.findtext("mesh/mesh"), "mesh.exo", gf)
chk("engine_single_block", len(groot.findall("mesh/block")) == 1 and groot.findtext("mesh/block/index") == "1", [len(groot.findall("mesh/block")), groot.findtext("mesh/block/index")], [1, "1"], gf)
chk("engine_output_file_engine_output", groot.findtext("output/file") == "engine_output", groot.findtext("output/file"), "engine_output", gf)

# ---------- mpirun.source ----------
mf = os.path.join(d, "mpirun.source")
mtxt = open(mf).read()
nps = re.findall(r"-np\s+(\d+)", mtxt)
chk("mpirun_three_single_rank_performers", nps == ["1", "1", "1"], nps, ["1", "1", "1"], mf)
chk("mpirun_executables", "PlatoMain engine_input_deck.xml" in mtxt and "analyze_MPMD --input-config=analyze_2_input_deck.xml" in mtxt and "analyze_MPMD --input-config=analyze_helmholtz_input_deck.xml" in mtxt, "PlatoMain + 2x analyze_MPMD", "PlatoMain + 2x analyze_MPMD", mf)
chk("mpirun_no_mesh_decomposition", "decomp" not in mtxt.lower() and "mesh.exo." not in mtxt, "no decomposition", "no decomposition", mf)

rec = {"directory": d, "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "checks": checks, "all_pass": all(c["pass"] for c in checks), "n_checks": len(checks)}
print(json.dumps(rec, indent=2))
sys.exit(0 if rec["all_pass"] else 1)
