"""Verify XMLGenerator output in a run directory against the locked E3-SPC-v1 settings (sections 4-6)."""
import sys, re, json, datetime, os
import xml.etree.ElementTree as ET
run = sys.argv[1]
res = {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "run_dir": run, "checks": {}}
def check(name, ok, got, expected):
    res["checks"][name] = {"pass": bool(ok), "got": got, "expected": expected}
def params(path):
    """Flatten Teuchos ParameterList XML into {'List/Sub/Name': value}."""
    out = {}
    def walk(node, prefix):
        for ch in node:
            if ch.tag == "ParameterList":
                walk(ch, prefix + ch.get("name") + "/")
            elif ch.tag == "Parameter":
                out[prefix + ch.get("name")] = ch.get("value")
    walk(ET.parse(path).getroot(), "")
    return out
def multiroot(path):
    txt = open(path).read()
    txt = re.sub(r"<\?xml[^>]*\?>", "", txt)
    return ET.fromstring("<root>" + txt + "</root>")

# --- Helmholtz filter configuration ---
h = params(os.path.join(run, "analyze_helmholtz_input_deck.xml"))
check("helmholtz_physics", h.get("Scenarios/Physics") == "Helmholtz Filter", h.get("Scenarios/Physics"), "Helmholtz Filter")
ls = h.get("Scenarios/Parameters/Length Scale")
check("helmholtz_length_scale_present", ls is not None and float(ls) > 0, ls, "present (filter radius 0.15 translated by XMLGenerator: 0.15/(2*sqrt(3)) = 0.043301)")
check("helmholtz_length_scale_value", ls is not None and abs(float(ls) - 0.15 / (2 * 3 ** 0.5)) < 1e-5, ls, 0.15 / (2 * 3 ** 0.5))
sls = h.get("Scenarios/Parameters/Surface Length Scale")
check("helmholtz_surface_length_scale", sls is not None and abs(float(sls) - 1.0) < 1e-12, sls, "1.0 (boundary_sticking_penalty 1.0)")
sym = h.get("Scenarios/Parameters/Symmetry Plane Sides")
check("helmholtz_symmetry_plane_sides", sym is not None and re.sub(r"[{}\s]", "", sym).split(",") == ["ss_sym"], sym, "{ss_sym}")
check("helmholtz_mesh", h.get("Input Mesh") == "mesh.exo", h.get("Input Mesh"), "mesh.exo")
check("helmholtz_block", h.get("Scenarios/Spatial Model/Domains/block_1/Element Block") == "block_1", h.get("Scenarios/Spatial Model/Domains/block_1/Element Block"), "block_1")

# --- analyze (mechanical) configuration ---
a = params(os.path.join(run, "analyze_2_input_deck.xml"))
check("analyze_physics", a.get("Scenarios/Physics") == "Mechanical" and a.get("Scenarios/PDE Constraint") == "Elliptic", [a.get("Scenarios/Physics"), a.get("Scenarios/PDE Constraint")], ["Mechanical", "Elliptic"])
check("analyze_dimension", a.get("Spatial Dimension") == "3", a.get("Spatial Dimension"), "3")
check("analyze_mesh", a.get("Input Mesh") == "mesh.exo", a.get("Input Mesh"), "mesh.exo")
E = a.get("Scenarios/Material Models/material_1/Isotropic Linear Elastic/Youngs Modulus"); nu = a.get("Scenarios/Material Models/material_1/Isotropic Linear Elastic/Poissons Ratio")
check("material_E", E is not None and float(E) == 1.0, E, "1.0"); check("material_nu", nu is not None and float(nu) == 0.3, nu, "0.3")
check("material_assigned_block_1", a.get("Scenarios/Spatial Model/Domains/block_1/Material Model") == "material_1" and a.get("Scenarios/Spatial Model/Domains/block_1/Element Block") == "block_1", a.get("Scenarios/Spatial Model/Domains/block_1/Material Model"), "material_1 on block_1")
for where in ("Residual/Mechanical Residual", "Criteria/My Objective"):
    p = "Scenarios/" + where + "/Penalty Function/"
    check("simp_" + where.split("/")[0].lower(), a.get(p + "Type") == "SIMP" and float(a.get(p + "Exponent")) == 3.0 and float(a.get(p + "Minimum Value")) == 1e-3,
          [a.get(p + "Type"), a.get(p + "Exponent"), a.get(p + "Minimum Value")], ["SIMP", "3.0", "1e-3"])
check("residual_single_phase", a.get("Scenarios/Residual/Mechanical Residual/Material Interpolation Model") == "Single-Phase", a.get("Scenarios/Residual/Mechanical Residual/Material Interpolation Model"), "Single-Phase")
check("objective_compliance", a.get("Scenarios/Criteria/My Objective/Scalar Function Type") == "Internal Elastic Energy" and a.get("Scenarios/Criteria/My Objective/Domains") == "{block_1}", [a.get("Scenarios/Criteria/My Objective/Scalar Function Type"), a.get("Scenarios/Criteria/My Objective/Domains")], ["Internal Elastic Energy", "{block_1}"])
loads = {k: v for k, v in a.items() if k.startswith("Scenarios/Concentrated Loads/")}
check("load_single_concentrated", len({k.split("/")[2] for k in loads}) == 1, sorted({k.split("/")[2] for k in loads}), "exactly one concentrated load")
lk = "Scenarios/Concentrated Loads/Concentrated Load with ID 0/"
check("load_dof_y_value_-1_on_ns_load", a.get(lk + "Dof") == "1" and float(a.get(lk + "Value")) == -1.0 and a.get(lk + "Nodes") == "ns_load", [a.get(lk + "Dof"), a.get(lk + "Value"), a.get(lk + "Nodes")], ["1 (y)", "-1.0", "ns_load"])
nbc = [k for k in a if k.startswith("Scenarios/Mechanical Natural Boundary Conditions/")]
check("no_tractions", len(nbc) == 0, nbc, "no natural boundary conditions")
ebc = {}
for k, v in a.items():
    m = re.match(r"Scenarios/Essential Boundary Conditions/([^/]+)/(.+)", k)
    if m: ebc.setdefault(m.group(1), {})[m.group(2)] = v
sets = sorted((d.get("Sides"), d.get("Index"), d.get("Type"), d.get("Value")) for d in ebc.values())
exp_sets = sorted([("ns_fix", "0", "Fixed Value", "0"), ("ns_fix", "1", "Fixed Value", "0"), ("ns_fix", "2", "Fixed Value", "0"), ("ss_sym", "2", "Fixed Value", "0")])
check("essential_bcs", sets == exp_sets, sets, exp_sets)
check("output_displacements", a.get("Scenarios/Output/Plottable") == "{displacement_x, displacement_y, displacement_z}", a.get("Scenarios/Output/Plottable"), "{displacement_x, displacement_y, displacement_z}")

# --- interface.xml: optimizer ---
i = multiroot(os.path.join(run, "interface.xml"))
opt = i.find("Optimizer")
check("optimizer_oc", opt.findtext("Package") == "OC", opt.findtext("Package"), "OC")
check("max_iterations_50", opt.findtext("Convergence/MaxIterations") == "50", opt.findtext("Convergence/MaxIterations"), "50")
check("update_problem_stage", opt.findtext("UpdateProblemStage/Name") == "Update Problem" and opt.findtext("Options/ProblemUpdateFrequency") == "1", [opt.findtext("UpdateProblemStage/Name"), opt.findtext("Options/ProblemUpdateFrequency")], ["Update Problem", "1"])
check("oc_default_tolerances", [opt.findtext("Options/OCControlStagnationTolerance"), opt.findtext("Options/OCObjectiveStagnationTolerance"), opt.findtext("Options/OCGradientTolerance")] == ["1e-4", "1e-8", "1e-8"], [opt.findtext("Options/OCControlStagnationTolerance"), opt.findtext("Options/OCObjectiveStagnationTolerance"), opt.findtext("Options/OCGradientTolerance")], ["1e-4", "1e-8", "1e-8"])
check("constraint_target_0.15", opt.findtext("Constraint/NormalizedTargetValue") == "0.15" and opt.findtext("Constraint/ReferenceValueName") == "Design Volume", [opt.findtext("Constraint/NormalizedTargetValue"), opt.findtext("Constraint/ReferenceValueName")], ["0.15", "Design Volume"])
perf = [(p.findtext("Name"), p.findtext("Code")) for p in i.findall("Performer")]
check("performers", perf == [("engine_1", "engine"), ("analyze_2", "analyze"), ("analyze_helmholtz", "analyze")], perf, "engine_1/engine, analyze_2/analyze, analyze_helmholtz/analyze")
out_stage = [s for s in i.findall("Stage") if s.findtext("Name") == "Output To File"][0]
pm = [o for o in out_stage.findall("Operation") if o.findtext("Name") == "PlatoMainOutput"][0]
args = sorted(x.findtext("ArgumentName") for x in pm.findall("Input"))
check("engine_output_control_topology", args == ["control", "topology"], args, ["control", "topology"])
cv = [s for s in i.findall("Stage") if s.findtext("Name") == "Compute Constraint Value 1"][0]
check("constraint_evaluated_by_engine", any(o.findtext("PerformerName") == "engine_1" and o.findtext("Name") == "Compute Constraint Value 1" for o in cv.findall("Operation")), True, "engine_1 computes constraint value")
ov = [s for s in i.findall("Stage") if s.findtext("Name") == "Compute Objective Value"][0]
check("objective_evaluated_by_analyze", any(o.findtext("PerformerName") == "analyze_2" and o.findtext("Name") == "Compute Objective Value" for o in ov.findall("Operation")), True, "analyze_2 computes objective value")

# --- engine_operations.xml ---
e = multiroot(os.path.join(run, "engine_operations.xml"))
ops = {o.findtext("Name"): o for o in e.findall("Operation")}
check("initial_density_0.15", ops["Initialize Field"].findtext("Method") == "Uniform" and ops["Initialize Field"].findtext("Uniform/Value") == "0.15", [ops["Initialize Field"].findtext("Method"), ops["Initialize Field"].findtext("Uniform/Value")], ["Uniform", "0.15"])
check("discretization_density", ops["Compute Lower Bounds"].findtext("Discretization") == "density", ops["Compute Lower Bounds"].findtext("Discretization"), "density")
check("update_problem_frequency_1", ops["Update Problem"].findtext("UpdateProblemFrequency") == "1", ops["Update Problem"].findtext("UpdateProblemFrequency"), "1")
agg = ops["Aggregate Data"]
w = [x.findtext("Value") for x in agg.findall("Weighting/Weight")]
check("weighted_sum_weight_1", w == ["1"] and agg.find("Normalize") is None and agg.findtext("Weighting/Normalize") is None, {"weights": w, "normalize_elements": [x.tag for x in agg.iter() if "ormal" in x.tag]}, "single weight 1, no normalization")
check("engine_output_max_iterations", ops["PlatoMainOutput"].findtext("MaxIterations") == "50", ops["PlatoMainOutput"].findtext("MaxIterations"), "50")
res["notes"] = ["engine PlatoMainOutput OutputFrequency = " + str(ops["PlatoMainOutput"].findtext("OutputFrequency")) + " (runtime default isosurface_output_frequency; not a locked value; iteration 50 is a multiple of it)",
                "analyze Visualization OutputFrequency = " + str(multiroot(os.path.join(run, "analyze_2_operations.xml")).findall("Operation")[0].findtext("OutputFrequency"))]
# --- mpirun.source: single-rank performers, no decomposition ---
ms = open(os.path.join(run, "mpirun.source")).read()
nps = re.findall(r"-np\s+(\d+)", ms)
check("single_rank_performers", nps == ["1", "1", "1"], nps, ["1", "1", "1"])
check("no_decomp", "decomp" not in ms, "decomp" in ms, "no decomp command")
res["all_pass"] = all(v["pass"] for v in res["checks"].values())
print(json.dumps(res, indent=2))
sys.exit(0 if res["all_pass"] else 1)
