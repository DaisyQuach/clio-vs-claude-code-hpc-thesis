#!/usr/bin/env python3
"""Verify the XMLGenerator output of a FROZEN-EX16-v1 stage against the locked settings.
Usage: verify_generated_config.py <run_dir> <stage: 1|2>
"""
import sys, os, re, json, math, hashlib
import xml.etree.ElementTree as ET

run = sys.argv[1]; stage = int(sys.argv[2])
def read(f): return open(os.path.join(run, f)).read()
def parse_fragments(f):
    # engine/analyze operations and interface files are sequences of top-level elements -> wrap them
    return ET.fromstring("<root>" + re.sub(r"<\?xml[^>]*\?>", "", read(f)) + "</root>")
def plist(f): return ET.fromstring(re.sub(r"<\?xml[^>]*\?>", "", read(f)))
def param(root, name):
    for p in root.iter("Parameter"):
        if p.get("name") == name: return p.get("value")
    return None
def params(root, name): return [p.get("value") for p in root.iter("Parameter") if p.get("name") == name]

iface = parse_fragments("interface.xml")
eng_ops = parse_fragments("engine_operations.xml")
an = plist("analyze_2_input_deck.xml")
helm = plist("analyze_helmholtz_input_deck.xml")
an_ops = parse_fragments("analyze_2_operations.xml")
mpis = read("mpirun.source")

R = 0.15; expect_len = R / (2 * math.sqrt(3))
checks = {}
# filter
L = float(param(helm, "Length Scale")); Ls = float(param(helm, "Surface Length Scale"))
checks["helmholtz: Physics == Helmholtz Filter"] = param(helm, "Physics") == "Helmholtz Filter"
checks[f"helmholtz: Length Scale {L} == R/(2*sqrt(3)) for R=0.15 ({expect_len:.6f})"] = abs(L - expect_len) < 1e-5
checks[f"helmholtz: Surface Length Scale {Ls} == boundary_sticking_penalty 1.0"] = abs(Ls - 1.0) < 1e-12
checks["helmholtz: no symmetry plane sidesets"] = "Symmetry" not in read("analyze_helmholtz_input_deck.xml")
checks["helmholtz: mesh == mesh.exo"] = param(helm, "Input Mesh") == "mesh.exo"
# material
checks["analyze: Youngs Modulus == 1.0"] = float(param(an, "Youngs Modulus")) == 1.0
checks["analyze: Poissons Ratio == 0.3"] = float(param(an, "Poissons Ratio")) == 0.3
checks["analyze: material model Isotropic Linear Elastic"] = any(pl.get("name") == "Isotropic Linear Elastic" for pl in an.iter("ParameterList"))
checks["analyze: block_1 is the only domain"] = [pl.get("name") for pl in [x for x in an.iter("ParameterList") if x.get("name") == "Domains"][0]] == ["block_1"]
# SIMP (residual and criterion)
pf = [pl for pl in an.iter("ParameterList") if pl.get("name") == "Penalty Function"]
checks["analyze: two SIMP penalty functions (criterion + residual)"] = len(pf) == 2
checks["analyze: SIMP Type == SIMP in both"] = all(param(p, "Type") == "SIMP" for p in pf)
checks["analyze: SIMP Exponent == 3.0 in both"] = all(float(param(p, "Exponent")) == 3.0 for p in pf)
checks["analyze: SIMP Minimum Value == 1e-3 in both (incl. compliance minimum_ersatz_material_value)"] = all(float(param(p, "Minimum Value")) == 1e-3 for p in pf)
checks["analyze: Material Interpolation Model == Single-Phase"] = param(an, "Material Interpolation Model") == "Single-Phase"
checks["analyze: objective criterion == Internal Elastic Energy (mechanical compliance), Physics Mechanical, Linear"] = param(an, "Scalar Function Type") == "Internal Elastic Energy" and param(an, "Physics") == "Mechanical" and param(an, "Response") == "Linear"
checks["analyze: Spatial Dimension == 3"] = param(an, "Spatial Dimension") == "3"
checks["analyze: mesh == mesh.exo"] = param(an, "Input Mesh") == "mesh.exo"
# load
cl = [pl for pl in an.iter("ParameterList") if pl.get("name") == "Concentrated Loads"][0]
loads = list(cl)
checks["load: exactly one concentrated load"] = len(loads) == 1
checks["load: Dof == 1 (y), Value == -1.0, Nodes == ns_load"] = param(loads[0], "Dof") == "1" and float(param(loads[0], "Value")) == -1.0 and param(loads[0], "Nodes") == "ns_load"
nbc = [pl for pl in an.iter("ParameterList") if pl.get("name") == "Mechanical Natural Boundary Conditions"][0]
checks["load: no tractions/natural BCs"] = len(list(nbc)) == 0
# displacement BCs
ebc = [pl for pl in an.iter("ParameterList") if pl.get("name") == "Essential Boundary Conditions"][0]
bcs = list(ebc)
checks["bc: three fixed-value BCs on ns_fix, indices 0,1,2, value 0"] = (len(bcs) == 3 and sorted(param(b, "Index") for b in bcs) == ["0", "1", "2"]
    and all(param(b, "Sides") == "ns_fix" and param(b, "Type") == "Fixed Value" and float(param(b, "Value")) == 0.0 for b in bcs))
# output
checks["output: analyze Plottable == displacement_x/y/z"] = param(an, "Plottable") == "{displacement_x, displacement_y, displacement_z}"
checks["output: analyze Visualization OutputFrequency == 1"] = an_ops.find("Operation/OutputFrequency").text == "1"
# optimizer
opt = iface.find("Optimizer")
checks["optimizer: Package == OC"] = opt.find("Package").text == "OC"
checks["optimizer: MaxIterations == %d" % (20 if stage == 1 else 40)] = opt.find("Convergence/MaxIterations").text == ("20" if stage == 1 else "40")
checks["optimizer: default tolerances (1e-4 control, 1e-8 objective, 1e-8 gradient)"] = (opt.find("Options/OCControlStagnationTolerance").text == "1e-4" and opt.find("Options/OCObjectiveStagnationTolerance").text == "1e-8" and opt.find("Options/OCGradientTolerance").text == "1e-8")
checks["optimizer: ProblemUpdateFrequency == 1 and Update Problem stage present"] = opt.find("Options/ProblemUpdateFrequency").text == "1" and opt.find("UpdateProblemStage/Name").text == "Update Problem"
checks["optimizer: volume constraint NormalizedTargetValue == 0.15 referenced to Design Volume"] = opt.find("Constraint/NormalizedTargetValue").text == "0.15" and opt.find("Constraint/ReferenceValueName").text == "Design Volume"
checks["optimizer: bounds 0..1 (density)"] = opt.find("BoundConstraint/Lower").text == "0.0" and opt.find("BoundConstraint/Upper").text == "1.0"
checks["optimizer: one constraint, one objective"] = len(opt.findall("Constraint")) == 1 and len(opt.findall("Objective")) == 1
# engine operations
pmo = [o for o in eng_ops.findall("Operation") if o.findtext("Function") == "PlatoMainOutput"][0]
checks["engine: PlatoMainOutput WriteRestart == true"] = pmo.findtext("WriteRestart") == "true"
checks["engine: PlatoMainOutput OutputFrequency == 1 (every iteration)"] = pmo.findtext("OutputFrequency") == "1"
checks["engine: PlatoMainOutput MaxIterations == %d" % (20 if stage == 1 else 40)] = pmo.findtext("MaxIterations") == ("20" if stage == 1 else "40")
checks["engine: PlatoMainOutput writes nodal fields topology and control"] = sorted(i.findtext("ArgumentName") for i in pmo.findall("Input")) == ["control", "topology"]
init = [o for o in eng_ops.findall("Operation") if o.findtext("Function") == "InitializeField"][0]
if stage == 1:
    checks["engine: InitializeField Method Uniform, Value 0.15"] = init.findtext("Method") == "Uniform" and init.findtext("Uniform/Value") == "0.15"
    checks["engine: restart_iteration not set (fresh start)"] = "restart" not in read("xmlgenerator.log").lower() or 'default value of "0" for parameter "restart_iteration"' in read("xmlgenerator.log")
upd = [o for o in eng_ops.findall("Operation") if o.findtext("Function") == "Update Problem"]
checks["engine: Update Problem operation with UpdateProblemFrequency 1"] = len(upd) == 1 and upd[0].findtext("UpdateProblemFrequency") == "1"
agg = [o for o in eng_ops.findall("Operation") if o.findtext("Function") == "Aggregator"][0]
checks["engine: aggregator weight 1, single value, no Normals (normalize_in_aggregator false)"] = [w.findtext("Value") for w in agg.findall("Weighting/Weight")] == ["1"] and agg.find("Normals") is None
vol = [o for o in eng_ops.findall("Operation") if o.findtext("Function") == "ComputeVolume"]
checks["engine: volume constraint computed by engine (ComputeVolume ops present)"] = len(vol) == 2
checks["engine: engine output file name == engine_output"] = "<file>engine_output</file>" in read("engine_input_deck.xml")
checks["engine: mesh == mesh.exo"] = "<mesh>mesh.exo</mesh>" in read("engine_input_deck.xml")
# performers / services
perf = [(p.findtext("Name"), p.findtext("Code")) for p in iface.findall("Performer")]
checks["interface: performers engine_1(engine), analyze_2(analyze), analyze_helmholtz(analyze)"] = perf == [("engine_1", "engine"), ("analyze_2", "analyze"), ("analyze_helmholtz", "analyze")]
checks["mpirun: every performer launched with -np 1 (single rank, no decomposition)"] = re.findall(r"-np (\d+)", mpis) == ["1", "1", "1"]
checks["mpirun: executables PlatoMain + analyze_MPMD x2"] = mpis.count("PlatoMain engine_input_deck.xml") == 1 and mpis.count("analyze_MPMD --input-config=") == 2
checks["interface: objective value stage uses analyze_2 and aggregator; constraint stage uses engine_1"] = ("<PerformerName>analyze_2</PerformerName>" in read("interface.xml") and "Compute Constraint Value 1" in read("interface.xml"))
checks["console: Verbose false (default)"] = iface.find("Console/Verbose").text == "false"

rec = {"run_dir": run, "stage": stage,
       "files_sha256": {f: hashlib.sha256(open(os.path.join(run, f), "rb").read()).hexdigest() for f in sorted(os.listdir(run)) if os.path.isfile(os.path.join(run, f))},
       "checks": checks, "ALL_CHECKS_PASS": all(checks.values())}
print(json.dumps(rec, indent=2))
sys.exit(0 if rec["ALL_CHECKS_PASS"] else 1)
