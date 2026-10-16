"""Verify the XMLGenerator output of a stage against the locked settings of FROZEN-EX16-v1.
Usage: python3 -I verify_generated_config_stage2.py <run_dir> stage2 <restart_iteration>
"""
import sys, os, re, json, math, hashlib, datetime
import xml.etree.ElementTree as ET

run = sys.argv[1]; stage = sys.argv[2]; restart_iter = sys.argv[3]
def read(f): return open(os.path.join(run, f)).read()
def parse_multi(f):
    # generated files are sequences of root elements -> wrap
    return ET.fromstring("<root>" + re.sub(r"<\?xml[^>]*\?>", "", read(f)) + "</root>")
def plist_params(root):
    out = {}
    def walk(node, path):
        for ch in node:
            if ch.tag == "ParameterList":
                walk(ch, path + [ch.get("name")])
            elif ch.tag == "Parameter":
                out["/".join(path + [ch.get("name")])] = ch.get("value")
    walk(root, [root.get("name")])
    return out

res = {"run_dir": run, "stage": stage, "utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "files": {}, "checks": {}}
for f in sorted(os.listdir(run)):
    if f.endswith(".xml") or f == "mpirun.source" or f.endswith(".i"):
        res["files"][f] = hashlib.sha256(open(os.path.join(run, f), "rb").read()).hexdigest()
C = res["checks"]
# --- analyze (physics) deck
a = plist_params(ET.fromstring(read("analyze_2_input_deck.xml")))
res["analyze_2_params"] = a
P = "Problem/Scenarios/"
C["analyze: 3D mechanical, elliptic"] = a[P+"../Spatial Dimension".replace("../","")] == "3" if False else (a["Problem/Spatial Dimension"] == "3" and a[P+"Physics"] == "Mechanical" and a[P+"PDE Constraint"] == "Elliptic")
C["analyze: mesh.exo"] = a["Problem/Input Mesh"] == "mesh.exo"
C["material: E=1.0, nu=0.3 on material_1 assigned to block_1"] = (float(a[P+"Material Models/material_1/Isotropic Linear Elastic/Youngs Modulus"]) == 1.0 and float(a[P+"Material Models/material_1/Isotropic Linear Elastic/Poissons Ratio"]) == 0.3 and a[P+"Spatial Model/Domains/block_1/Element Block"] == "block_1" and a[P+"Spatial Model/Domains/block_1/Material Model"] == "material_1")
C["residual SIMP single-phase, exponent 3.0, min 1e-3, linear"] = (a[P+"Residual/Mechanical Residual/Material Interpolation Model"] == "Single-Phase" and a[P+"Residual/Mechanical Residual/Response"] == "Linear" and a[P+"Residual/Mechanical Residual/Penalty Function/Type"] == "SIMP" and float(a[P+"Residual/Mechanical Residual/Penalty Function/Exponent"]) == 3.0 and float(a[P+"Residual/Mechanical Residual/Penalty Function/Minimum Value"]) == 1e-3)
C["compliance criterion (Internal Elastic Energy) SIMP exp 3.0, ersatz min 1e-3, domain block_1"] = (a[P+"Criteria/My Objective/Scalar Function Type"] == "Internal Elastic Energy" and a[P+"Criteria/My Objective/Penalty Function/Type"] == "SIMP" and float(a[P+"Criteria/My Objective/Penalty Function/Exponent"]) == 3.0 and float(a[P+"Criteria/My Objective/Penalty Function/Minimum Value"]) == 1e-3 and a[P+"Criteria/My Objective/Domains"] == "{block_1}")
C["load: single concentrated load, dof 1 (y), value -1.0, nodeset ns_load"] = (a[P+"Concentrated Loads/Concentrated Load with ID 0/Dof"] == "1" and float(a[P+"Concentrated Loads/Concentrated Load with ID 0/Value"]) == -1.0 and a[P+"Concentrated Loads/Concentrated Load with ID 0/Nodes"] == "ns_load" and len([k for k in a if k.startswith(P+"Concentrated Loads/")]) == 3)
C["no natural BCs (tractions) and no body loads"] = (len([k for k in a if "Natural Boundary Conditions/" in k]) == 0 and len([k for k in a if "Body Load" in k]) == 0)
ebc = {k: v for k, v in a.items() if k.startswith(P+"Essential Boundary Conditions/")}
C["BC: ns_fix fixed value 0 for dispx, dispy, dispz (indices 0,1,2), nothing else"] = (len(ebc) == 12 and all(ebc[P+"Essential Boundary Conditions/Displacement %s with ID %d/%s" % (d, i+1, key)] == val for i, d in enumerate("XYZ") for key, val in [("Type", "Fixed Value"), ("Index", str(i)), ("Sides", "ns_fix"), ("Value", "0.0")]))
C["output: displacement_x, displacement_y, displacement_z"] = a[P+"Output/Plottable"] == "{displacement_x, displacement_y, displacement_z}"
# --- helmholtz deck
h = plist_params(ET.fromstring(read("analyze_helmholtz_input_deck.xml")))
res["helmholtz_params"] = h
ls = float(h[P+"Parameters/Length Scale"]); sls = float(h[P+"Parameters/Surface Length Scale"])
res["expected_length_scale_from_radius_0.15"] = 0.15 / (2.0 * math.sqrt(3.0))
C["helmholtz filter: Length Scale == 0.15/(2*sqrt(3)) = 0.043301 (radius_absolute 0.15)"] = (h[P+"Physics"] == "Helmholtz Filter" and abs(ls - 0.15 / (2 * math.sqrt(3))) < 1e-6)
C["helmholtz filter: Surface Length Scale == 1.0 (boundary_sticking_penalty 1.0)"] = sls == 1.0
C["helmholtz filter: no symmetry plane sidesets"] = not any("Symmetry" in k for k in h)
C["helmholtz filter: mesh.exo, domain block_1"] = h["Problem/Input Mesh"] == "mesh.exo" and h[P+"Spatial Model/Domains/block_1/Element Block"] == "block_1"
# --- engine operations
eo = parse_multi("engine_operations.xml")
ops = {o.findtext("Name"): o for o in eo.findall("Operation")}
pmo = ops["PlatoMainOutput"]
C["engine output: WriteRestart true"] = pmo.findtext("WriteRestart") == "true"
C["engine output: OutputFrequency 1 (every iteration)"] = pmo.findtext("OutputFrequency") == "1"
C["engine output: MaxIterations 40"] = pmo.findtext("MaxIterations") == "40"
C["engine output: writes topology and control nodal fields"] = sorted(i.findtext("ArgumentName") for i in pmo.findall("Input")) == ["control", "topology"] and all(i.findtext("Layout") == "Nodal Field" for i in pmo.findall("Input"))
init = ops["Initialize Field"]
C["initial design: FromFieldOnInputMesh (restart read), not Uniform"] = init.findtext("Method") == "FromFieldOnInputMesh" and init.find("Uniform") is None
C["restart source: file restart_input.exo, field control, saved state (Iteration) = " + restart_iter] = (init.findtext("FromFieldOnInputMesh/Name") == "restart_input.exo" and init.findtext("FromFieldOnInputMesh/VariableName") == "control" and init.findtext("FromFieldOnInputMesh/Iteration") == restart_iter)
C["restart source file is an exact copy of the Stage-1 checkpoint (sha256 58dee776...)"] = hashlib.sha256(open(os.path.join(run, "restart_input.exo"), "rb").read()).hexdigest() == "58dee7768b6c3bd768df5e4db4ec2c012e7eb9706647484920a38b03be5a07e8"
C["update problem operation, frequency 1"] = ops["Update Problem"].findtext("UpdateProblemFrequency") == "1"
C["bounds: density discretization, solid use case"] = ops["Compute Lower Bounds"].findtext("Discretization") == "density" and ops["Compute Upper Bounds"].findtext("Discretization") == "density"
cv = ops["Compute Constraint Value 1"]
C["volume constraint computed by engine (ComputeVolume, SIMP exp 1.0, min 0.0 = plain volume)"] = cv.findtext("Function") == "ComputeVolume" and cv.findtext("SIMP/PenaltyExponent") == "1.0" and cv.findtext("SIMP/MinimumValue") == "0.0"
agg = ops["Aggregate Data"]
C["objective aggregator: single weight 1, no normalization element"] = [w.findtext("Value") for w in agg.findall("Weighting/Weight")] == ["1"] and agg.find("Weighting/Normals") is None and "Normal" not in ET.tostring(agg).decode()
# --- engine input deck
ei = parse_multi("engine_input_deck.xml")
C["engine mesh: mesh.exo, block 1 material 1, output file engine_output (exodus)"] = ei.findtext("mesh/mesh") == "mesh.exo" and ei.findtext("mesh/block/index") == "1" and ei.findtext("output/file") == "engine_output" and ei.findtext("output/format") == "exodus"
# --- interface
it = parse_multi("interface.xml")
perf = [(p.findtext("Name"), p.findtext("Code")) for p in it.findall("Performer")]
C["performers: engine_1 (engine), analyze_2 (analyze), analyze_helmholtz (analyze)"] = perf == [("engine_1", "engine"), ("analyze_2", "analyze"), ("analyze_helmholtz", "analyze")]
opt = it.find("Optimizer")
C["optimizer: OC"] = opt.findtext("Package") == "OC"
C["optimizer: MaxIterations 40"] = opt.findtext("Convergence/MaxIterations") == "40"
C["optimizer: default tolerances (control 1e-4, objective 1e-8, gradient 1e-8)"] = (opt.findtext("Options/OCControlStagnationTolerance") == "1e-4" and opt.findtext("Options/OCObjectiveStagnationTolerance") == "1e-8" and opt.findtext("Options/OCGradientTolerance") == "1e-8")
C["optimizer: ProblemUpdateFrequency 1 with Update Problem stage"] = opt.findtext("Options/ProblemUpdateFrequency") == "1" and opt.findtext("UpdateProblemStage/Name") == "Update Problem"
C["optimizer: constraint normalized target 0.15, reference Design Volume (volume <= 15%)"] = opt.findtext("Constraint/NormalizedTargetValue") == "0.15" and opt.findtext("Constraint/ReferenceValueName") == "Design Volume" and len(it.findall("Optimizer/Constraint")) == 1
C["optimizer: bounds [0,1], Control initialized by 'Initial Guess' stage, filtered name Topology"] = opt.findtext("BoundConstraint/Lower") == "0.0" and opt.findtext("BoundConstraint/Upper") == "1.0" and opt.findtext("OptimizationVariables/InitializationStage") == "Initial Guess" and opt.findtext("OptimizationVariables/FilteredName") == "Topology"
stages = {s.findtext("Name"): s for s in it.findall("Stage")}
def stage_ops(n): return [(o.findtext("Name"), o.findtext("PerformerName")) for o in stages[n].findall("Operation")]
C["objective value stage: Helmholtz filter -> analyze_2 compliance -> engine aggregate"] = stage_ops("Compute Objective Value") == [("Filter Control", "analyze_helmholtz"), ("Compute Objective Value", "analyze_2"), ("Aggregate Data", "engine_1")]
C["objective gradient stage: filter -> analyze_2 gradient -> aggregate -> filter gradient"] = stage_ops("Compute Objective Gradient") == [("Filter Control", "analyze_helmholtz"), ("Compute Objective Gradient", "analyze_2"), ("Aggregate Data", "engine_1"), ("Filter Gradient", "analyze_helmholtz")]
C["constraint value stage evaluated by engine_1"] = ("Compute Constraint Value 1", "engine_1") in stage_ops("Compute Constraint Value 1")
C["output stage: analyze Visualization + engine PlatoMainOutput(topology, control)"] = stage_ops("Output To File") == [("Visualization", "analyze_2"), ("PlatoMainOutput", "engine_1")]
C["initial guess stage uses Initialize Field (engine_1) which reads the restart file"] = stage_ops("Initial Guess") == [("Initialize Field", "engine_1")]
# --- mpirun.source
ms = read("mpirun.source")
C["mpirun: three single-rank performers (-np 1 each), PlatoMain + 2x analyze_MPMD"] = ms.count("-np 1") == 3 and ms.count("PlatoMain engine_input_deck.xml") == 1 and ms.count("analyze_MPMD") == 2 and "analyze_2_input_deck.xml" in ms and "analyze_helmholtz_input_deck.xml" in ms
# --- analyze operations (visualization every iteration)
ao = parse_multi("analyze_2_operations.xml")
C["analyze visualization every iteration (OutputFrequency 1) into analyze_id_2_output"] = ao.find("Operation[Name='Visualization']").findtext("OutputFrequency") == "1" and ao.find("Operation[Name='Visualization']").findtext("VizDirectory") == "analyze_id_2_output"
res["ALL_CHECKS_PASS"] = all(C.values())
print(json.dumps(res, indent=2))
sys.exit(0 if res["ALL_CHECKS_PASS"] else 1)
