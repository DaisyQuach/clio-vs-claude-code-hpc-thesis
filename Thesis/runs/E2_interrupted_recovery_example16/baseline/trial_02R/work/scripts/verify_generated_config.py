"""Verify the XMLGenerator output of a stage against the locked settings of FROZEN-EX16-v1.
Usage: verify_generated_config.py <run_dir> <stage: 1|2> <out.json> [expected_restart_iteration (stage 2)]"""
import sys, os, json, math, re, datetime, hashlib
import xml.etree.ElementTree as ET

run_dir, stage, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
def load_multi_root(path):
    txt = open(path).read()
    txt = re.sub(r'<\?xml[^>]*\?>', '', txt)
    return ET.fromstring("<root>" + txt + "</root>")
def plist_params(node):
    """flatten Teuchos ParameterList into dict path->value"""
    d = {}
    def rec(n, prefix):
        for c in n:
            if c.tag == "ParameterList":
                rec(c, prefix + "/" + c.get("name"))
            elif c.tag == "Parameter":
                d[prefix + "/" + c.get("name")] = c.get("value")
    rec(node, "")
    return d

C = {}  # check name -> (pass, observed)
def check(name, cond, observed):
    C[name] = {"pass": bool(cond), "observed": observed}

# ---- analyze_helmholtz_input_deck.xml : filter ----
hp = plist_params(load_multi_root(os.path.join(run_dir, "analyze_helmholtz_input_deck.xml")).find("ParameterList"))
ls = float(hp.get("/Scenarios/Parameters/Length Scale", "nan"))
sls = float(hp.get("/Scenarios/Parameters/Surface Length Scale", "nan"))
expected_ls = 0.15 / (2.0 * math.sqrt(3.0))
check("helmholtz: Physics = Helmholtz Filter", hp.get("/Scenarios/Physics") == "Helmholtz Filter", hp.get("/Scenarios/Physics"))
check("helmholtz: Length Scale = 0.15/(2*sqrt(3)) = 0.043301 (radius_absolute 0.15)", abs(ls - expected_ls) < 1e-5, ls)
check("helmholtz: Surface Length Scale = 1.0 (boundary_sticking_penalty 1.0)", abs(sls - 1.0) < 1e-12, sls)
check("helmholtz: no symmetry plane sidesets", not any("Symmetry" in k for k in hp), [k for k in hp if "Symmetry" in k])
check("helmholtz: Input Mesh = mesh.exo", hp.get("/Scenarios/../Input Mesh", hp.get("/Input Mesh")) == "mesh.exo", hp.get("/Input Mesh"))
check("helmholtz: Spatial Dimension = 3", hp.get("/Spatial Dimension") == "3", hp.get("/Spatial Dimension"))
check("helmholtz: domain block_1", hp.get("/Scenarios/Spatial Model/Domains/block_1/Element Block") == "block_1", hp.get("/Scenarios/Spatial Model/Domains/block_1/Element Block"))

# ---- analyze_2_input_deck.xml : physics, material, SIMP, load, BCs, output ----
ap = plist_params(load_multi_root(os.path.join(run_dir, "analyze_2_input_deck.xml")).find("ParameterList"))
check("analyze: Physics = Mechanical", ap.get("/Scenarios/Physics") == "Mechanical", ap.get("/Scenarios/Physics"))
check("analyze: Spatial Dimension = 3", ap.get("/Spatial Dimension") == "3", ap.get("/Spatial Dimension"))
check("analyze: Input Mesh = mesh.exo", ap.get("/Input Mesh") == "mesh.exo", ap.get("/Input Mesh"))
check("analyze: domain block_1 -> material_1", ap.get("/Scenarios/Spatial Model/Domains/block_1/Material Model") == "material_1", ap.get("/Scenarios/Spatial Model/Domains/block_1/Material Model"))
E = float(ap.get("/Scenarios/Material Models/material_1/Isotropic Linear Elastic/Youngs Modulus", "nan"))
nu = float(ap.get("/Scenarios/Material Models/material_1/Isotropic Linear Elastic/Poissons Ratio", "nan"))
check("material: isotropic linear elastic E = 1.0", E == 1.0, E)
check("material: nu = 0.3", nu == 0.3, nu)
obj = "/Scenarios/Criteria/My Objective"
check("objective criterion: compliance (Internal Elastic Energy)", ap.get(obj + "/Scalar Function Type") == "Internal Elastic Energy", ap.get(obj + "/Scalar Function Type"))
check("objective criterion: SIMP", ap.get(obj + "/Penalty Function/Type") == "SIMP", ap.get(obj + "/Penalty Function/Type"))
check("objective criterion: exponent 3.0", float(ap.get(obj + "/Penalty Function/Exponent", "nan")) == 3.0, ap.get(obj + "/Penalty Function/Exponent"))
check("objective criterion: minimum ersatz value 1e-3", float(ap.get(obj + "/Penalty Function/Minimum Value", "nan")) == 1e-3, ap.get(obj + "/Penalty Function/Minimum Value"))
check("objective criterion: domain block_1", ap.get(obj + "/Domains") == "{block_1}", ap.get(obj + "/Domains"))
res = "/Scenarios/Residual/Mechanical Residual"
check("residual: single-phase interpolation", ap.get(res + "/Material Interpolation Model") == "Single-Phase", ap.get(res + "/Material Interpolation Model"))
check("residual: linear response", ap.get(res + "/Response") == "Linear", ap.get(res + "/Response"))
check("residual: SIMP exponent 3.0", float(ap.get(res + "/Penalty Function/Exponent", "nan")) == 3.0, ap.get(res + "/Penalty Function/Exponent"))
check("residual: SIMP minimum value 1e-3", float(ap.get(res + "/Penalty Function/Minimum Value", "nan")) == 1e-3, ap.get(res + "/Penalty Function/Minimum Value"))
loads = [k for k in ap if k.startswith("/Scenarios/Concentrated Loads/")]
load_lists = sorted(set(k.rsplit("/", 1)[0] for k in loads))
check("load: exactly one concentrated load", len(load_lists) == 1, load_lists)
if load_lists:
    L = load_lists[0]
    check("load: direction y (Dof 1)", ap.get(L + "/Dof") == "1", ap.get(L + "/Dof"))
    check("load: value -1.0 per node", float(ap.get(L + "/Value", "nan")) == -1.0, ap.get(L + "/Value"))
    check("load: nodeset ns_load", ap.get(L + "/Nodes") == "ns_load", ap.get(L + "/Nodes"))
nbc = [k for k in ap if k.startswith("/Scenarios/Mechanical Natural Boundary Conditions/")]
check("load: no tractions / natural BCs", len(nbc) == 0, nbc)
bcs = sorted(set(k.rsplit("/", 1)[0] for k in ap if k.startswith("/Scenarios/Essential Boundary Conditions/")))
check("BC: exactly three essential BCs", len(bcs) == 3, bcs)
idx = sorted(ap.get(b + "/Index") for b in bcs)
check("BC: indices 0,1,2 (u_x,u_y,u_z)", idx == ["0", "1", "2"], idx)
check("BC: all on ns_fix", all(ap.get(b + "/Sides") == "ns_fix" for b in bcs), [ap.get(b + "/Sides") for b in bcs])
check("BC: all Fixed Value 0.0", all(ap.get(b + "/Type") == "Fixed Value" and float(ap.get(b + "/Value")) == 0.0 for b in bcs), [(ap.get(b + "/Type"), ap.get(b + "/Value")) for b in bcs])
check("output: dispx dispy dispz plottable", ap.get("/Scenarios/Output/Plottable") == "{displacement_x, displacement_y, displacement_z}", ap.get("/Scenarios/Output/Plottable"))

# ---- engine_operations.xml ----
eo = load_multi_root(os.path.join(run_dir, "engine_operations.xml"))
ops = {o.findtext("Name"): o for o in eo.findall("Operation")}
pmo = ops.get("PlatoMainOutput")
check("engine output: WriteRestart true", pmo is not None and pmo.findtext("WriteRestart") == "true", pmo.findtext("WriteRestart") if pmo is not None else None)
check("engine output: OutputFrequency 1 (every iteration saved)", pmo is not None and pmo.findtext("OutputFrequency") == "1", pmo.findtext("OutputFrequency") if pmo is not None else None)
check("engine output: MaxIterations 20" if stage == 1 else "engine output: MaxIterations 40", pmo is not None and pmo.findtext("MaxIterations") == ("20" if stage == 1 else "40"), pmo.findtext("MaxIterations") if pmo is not None else None)
pmo_in = sorted(i.findtext("ArgumentName") for i in pmo.findall("Input")) if pmo is not None else []
check("engine output: control and topology nodal fields written", pmo_in == ["control", "topology"], pmo_in)
init = ops.get("Initialize Field")
if stage == 1:
    check("initial design: uniform 0.15", init is not None and init.findtext("Method") == "Uniform" and float(init.findtext("Uniform/Value")) == 0.15, (init.findtext("Method"), init.findtext("Uniform/Value")) if init is not None else None)
    check("stage 1 is not a restart (no FromFile initial guess)", init is not None and init.findtext("Method") == "Uniform" and init.find("FromFile") is None and init.find("FileName") is None, [c.tag for c in init] if init is not None else None)
else:
    # ---- Stage 2 (continuation) restart checks; expected <Iteration> value given as optional argv[4] ----
    exp_iter = sys.argv[4] if len(sys.argv) > 4 else None
    check("stage 2: initial design read from a field on an input mesh (FromFieldOnInputMesh)", init is not None and init.findtext("Method") == "FromFieldOnInputMesh", init.findtext("Method") if init is not None else None)
    ff = init.find("FromFieldOnInputMesh") if init is not None else None
    check("stage 2: restart source file restart_input.exo", ff is not None and ff.findtext("Name") == "restart_input.exo", ff.findtext("Name") if ff is not None else None)
    check("stage 2: restart field `control` (raw design variable, not `topology`)", ff is not None and ff.findtext("VariableName") == "control", ff.findtext("VariableName") if ff is not None else None)
    check("stage 2: restart saved state <Iteration> = %s" % exp_iter if exp_iter else "stage 2: restart saved state <Iteration> present", ff is not None and ff.findtext("Iteration") is not None and (exp_iter is None or ff.findtext("Iteration") == exp_iter), ff.findtext("Iteration") if ff is not None else None)
    check("stage 2: PlatoMainOutput RestartFieldName control", pmo is not None and pmo.findtext("RestartFieldName") == "control", pmo.findtext("RestartFieldName") if pmo is not None else None)
    rp = os.path.join(run_dir, "restart_input.exo")
    ck = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "outputs", "stage1", "engine_output.exo")
    h_rp = hashlib.sha256(open(rp, "rb").read()).hexdigest() if os.path.exists(rp) else None
    h_ck = hashlib.sha256(open(ck, "rb").read()).hexdigest() if os.path.exists(ck) else None
    check("stage 2: restart_input.exo in run dir is byte-identical to the Stage-1 checkpoint outputs/stage1/engine_output.exo", h_rp is not None and h_rp == h_ck, {"restart_input.exo": h_rp, "checkpoint": h_ck})
up = ops.get("Update Problem")
check("update problem operation present, frequency 1", up is not None and up.findtext("UpdateProblemFrequency") == "1", up.findtext("UpdateProblemFrequency") if up is not None else None)
cv = ops.get("Compute Constraint Value 1")
check("constraint: volume computed by engine (ComputeVolume)", cv is not None and cv.findtext("Function") == "ComputeVolume", cv.findtext("Function") if cv is not None else None)
agg = ops.get("Aggregate Data")
w = [x.findtext("Value") for x in agg.findall("Weighting/Weight")] if agg is not None else []
check("objective: weighted sum, single criterion, weight 1", w == ["1"], w)
check("objective: normalize_in_aggregator false (no Normals in aggregator)", agg is not None and agg.find("Normals") is None and agg.find("Aggregate/Normals") is None, "Normals present" if agg is not None and (agg.find("Normals") is not None) else "no Normals")

# ---- interface.xml ----
ix = load_multi_root(os.path.join(run_dir, "interface.xml"))
opt = ix.find("Optimizer")
check("optimizer: OC", opt.findtext("Package") == "OC", opt.findtext("Package"))
check("optimizer: MaxIterations 20" if stage == 1 else "optimizer: MaxIterations 40", opt.findtext("Convergence/MaxIterations") == ("20" if stage == 1 else "40"), opt.findtext("Convergence/MaxIterations"))
check("optimizer: default OC tolerances (1e-4, 1e-8, 1e-8)", (opt.findtext("Options/OCControlStagnationTolerance"), opt.findtext("Options/OCObjectiveStagnationTolerance"), opt.findtext("Options/OCGradientTolerance")) == ("1e-4", "1e-8", "1e-8"), (opt.findtext("Options/OCControlStagnationTolerance"), opt.findtext("Options/OCObjectiveStagnationTolerance"), opt.findtext("Options/OCGradientTolerance")))
check("optimizer: ProblemUpdateFrequency 1", opt.findtext("Options/ProblemUpdateFrequency") == "1", opt.findtext("Options/ProblemUpdateFrequency"))
cons = opt.findall("Constraint")
check("constraint: exactly one", len(cons) == 1, len(cons))
check("constraint: NormalizedTargetValue 0.15 relative to Design Volume", cons and cons[0].findtext("NormalizedTargetValue") == "0.15" and cons[0].findtext("ReferenceValueName") == "Design Volume", (cons[0].findtext("NormalizedTargetValue"), cons[0].findtext("ReferenceValueName")) if cons else None)
check("design variables: bounds [0,1]", opt.findtext("BoundConstraint/Lower") == "0.0" and opt.findtext("BoundConstraint/Upper") == "1.0", (opt.findtext("BoundConstraint/Lower"), opt.findtext("BoundConstraint/Upper")))
perf = [(p.findtext("Name"), p.findtext("Code")) for p in ix.findall("Performer")]
check("performers: engine_1 (engine), analyze_2 (analyze), analyze_helmholtz (analyze)", perf == [("engine_1", "engine"), ("analyze_2", "analyze"), ("analyze_helmholtz", "analyze")], perf)
check("optimizer: filtered design name Topology, control name Control", opt.findtext("OptimizationVariables/ValueName") == "Control" and opt.findtext("OptimizationVariables/FilteredName") == "Topology", (opt.findtext("OptimizationVariables/ValueName"), opt.findtext("OptimizationVariables/FilteredName")))
stages = [s.findtext("Name") for s in ix.findall("Stage")]
check("stages: objective value/gradient via analyze_2 and Helmholtz filter", "Compute Objective Value" in stages and "Compute Objective Gradient" in stages, stages)

# ---- engine_input_deck.xml ----
ei = load_multi_root(os.path.join(run_dir, "engine_input_deck.xml"))
check("engine: mesh mesh.exo, exodus", ei.findtext("mesh/mesh") == "mesh.exo" and ei.findtext("mesh/format") == "exodus", (ei.findtext("mesh/mesh"), ei.findtext("mesh/format")))
check("engine: output file engine_output (exodus)", ei.findtext("output/file") == "engine_output" and ei.findtext("output/format") == "exodus", (ei.findtext("output/file"), ei.findtext("output/format")))

# ---- mpirun.source ----
ms = open(os.path.join(run_dir, "mpirun.source")).read()
nps = re.findall(r"-np\s+(\d+)", ms)
check("mpirun.source: three single-rank performers (-np 1 each)", nps == ["1", "1", "1"], nps)
check("mpirun.source: PlatoMain + analyze_MPMD x2", ms.count("PlatoMain") == 1 and ms.count("analyze_MPMD") == 2, (ms.count("PlatoMain"), ms.count("analyze_MPMD")))

files = sorted(f for f in os.listdir(run_dir) if f.endswith(".xml") or f == "mpirun.source" or f == "input_deck.i")
record = {
    "frozen_configuration_id": "FROZEN-EX16-v1", "stage": stage, "run_dir": run_dir,
    "verified_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    "files_sha256": {f: hashlib.sha256(open(os.path.join(run_dir, f), "rb").read()).hexdigest() for f in files},
    "checks": C, "all_checks_pass": all(v["pass"] for v in C.values()),
    "n_checks": len(C), "n_pass": sum(v["pass"] for v in C.values()),
}
json.dump(record, open(out, "w"), indent=2)
for k, v in C.items():
    print(("PASS" if v["pass"] else "FAIL"), k, "->", v["observed"])
print("ALL PASS" if record["all_checks_pass"] else "SOME CHECKS FAILED", record["n_pass"], "/", record["n_checks"])
sys.exit(0 if record["all_checks_pass"] else 1)
