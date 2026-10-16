"""Verify the XMLGenerator output of a stage against the locked FROZEN-EX16-v1 settings."""
import sys, re, math, json, datetime, hashlib, os
stage = sys.argv[1]  # 1 or 2
d = sys.argv[2]
def rd(f): return open(os.path.join(d, f)).read()
hz, an, eo, ei, itf, mp = rd("analyze_helmholtz_input_deck.xml"), rd("analyze_2_input_deck.xml"), rd("engine_operations.xml"), rd("engine_input_deck.xml"), rd("interface.xml"), rd("mpirun.source")
res = []
def chk(label, ok, got, want, where):
    res.append({"setting": label, "pass": bool(ok), "found": got, "locked": want, "file": where})
def param(txt, name):
    m = re.search(r'<Parameter name="%s" type="\w+(?:\(\w+\))?" value="([^"]*)"' % re.escape(name), txt); return m.group(1) if m else None
def tag(txt, t):
    m = re.search(r'<%s>([^<]*)</%s>' % (t, t), txt); return m.group(1) if m else None
# filter
ls = float(param(hz, "Length Scale")); sls = float(param(hz, "Surface Length Scale"))
chk("helmholtz length scale = 0.15/(2*sqrt(3)) (radius_absolute 0.15)", abs(ls - 0.15/(2*math.sqrt(3))) < 1e-6, ls, 0.15/(2*math.sqrt(3)), "analyze_helmholtz_input_deck.xml")
chk("helmholtz surface length scale (boundary_sticking_penalty 1.0)", abs(sls - 1.0) < 1e-12, sls, 1.0, "analyze_helmholtz_input_deck.xml")
chk("helmholtz physics", param(hz, "Physics") == "Helmholtz Filter", param(hz, "Physics"), "Helmholtz Filter", "analyze_helmholtz_input_deck.xml")
chk("no symmetry plane in helmholtz deck", "Symmetry" not in hz, "Symmetry" in hz, False, "analyze_helmholtz_input_deck.xml")
chk("helmholtz mesh", param(hz, "Input Mesh") == "mesh.exo", param(hz, "Input Mesh"), "mesh.exo", "analyze_helmholtz_input_deck.xml")
# analyze physics
chk("physics mechanical", param(an, "Physics") == "Mechanical", param(an, "Physics"), "Mechanical", "analyze_2_input_deck.xml")
chk("spatial dimension 3", param(an, "Spatial Dimension") == "3", param(an, "Spatial Dimension"), "3", "analyze_2_input_deck.xml")
chk("mesh file", param(an, "Input Mesh") == "mesh.exo", param(an, "Input Mesh"), "mesh.exo", "analyze_2_input_deck.xml")
chk("youngs modulus 1.0", float(param(an, "Youngs Modulus")) == 1.0, param(an, "Youngs Modulus"), "1.0", "analyze_2_input_deck.xml")
chk("poissons ratio 0.3", float(param(an, "Poissons Ratio")) == 0.3, param(an, "Poissons Ratio"), "0.3", "analyze_2_input_deck.xml")
chk("material model isotropic linear elastic", "Isotropic Linear Elastic" in an, "Isotropic Linear Elastic" in an, True, "analyze_2_input_deck.xml")
chk("single element block block_1 -> material_1", an.count('<Parameter name="Element Block"') == 1 and param(an, "Element Block") == "block_1" and param(an, "Material Model") == "material_1", [param(an, "Element Block"), param(an, "Material Model")], ["block_1", "material_1"], "analyze_2_input_deck.xml")
crit = re.search(r'<ParameterList name="My Objective">(.*?)</ParameterList>\s*</ParameterList>', an, re.S).group(1)
chk("objective criterion = compliance (Internal Elastic Energy)", param(crit, "Scalar Function Type") == "Internal Elastic Energy", param(crit, "Scalar Function Type"), "Internal Elastic Energy", "analyze_2_input_deck.xml")
chk("criterion SIMP exponent 3.0", float(param(crit, "Exponent")) == 3.0, param(crit, "Exponent"), "3.0", "analyze_2_input_deck.xml")
chk("criterion minimum_ersatz_material_value 1e-3", float(param(crit, "Minimum Value")) == 1e-3, param(crit, "Minimum Value"), "1e-3", "analyze_2_input_deck.xml")
resid = re.search(r'<ParameterList name="Mechanical Residual">(.*?)</ParameterList>\s*</ParameterList>', an, re.S).group(1)
chk("residual material interpolation single-phase SIMP", param(resid, "Material Interpolation Model") == "Single-Phase" and param(resid, "Type") == "SIMP", [param(resid, "Material Interpolation Model"), param(resid, "Type")], ["Single-Phase", "SIMP"], "analyze_2_input_deck.xml")
chk("residual SIMP exponent 3.0", float(param(resid, "Exponent")) == 3.0, param(resid, "Exponent"), "3.0", "analyze_2_input_deck.xml")
chk("residual SIMP minimum value 1e-3", float(param(resid, "Minimum Value")) == 1e-3, param(resid, "Minimum Value"), "1e-3", "analyze_2_input_deck.xml")
chk("residual response linear", param(resid, "Response") == "Linear", param(resid, "Response"), "Linear", "analyze_2_input_deck.xml")
loads = re.search(r'<ParameterList name="Concentrated Loads">(.*?)</ParameterList>\s*</ParameterList>', an, re.S).group(1)
chk("exactly one concentrated load", loads.count("<ParameterList name=") == 1, loads.count("<ParameterList name="), 1, "analyze_2_input_deck.xml")
chk("load dof = y (index 1)", param(loads, "Dof") == "1", param(loads, "Dof"), "1", "analyze_2_input_deck.xml")
chk("load value -1.0 per node", float(param(loads, "Value")) == -1.0, param(loads, "Value"), "-1.0", "analyze_2_input_deck.xml")
chk("load nodeset ns_load", param(loads, "Nodes") == "ns_load", param(loads, "Nodes"), "ns_load", "analyze_2_input_deck.xml")
chk("no natural (traction/pressure) BCs", re.search(r'<ParameterList name="Mechanical Natural Boundary Conditions"\s*/>', an) is not None, "empty list" if re.search(r'Natural Boundary Conditions"\s*/>', an) else "non-empty", "empty", "analyze_2_input_deck.xml")
chk("no body loads", "Body Load" not in an, "Body Load" in an, False, "analyze_2_input_deck.xml")
ebc = re.search(r'<ParameterList name="Essential Boundary Conditions">(.*?)</ParameterList>\s*<ParameterList name="Output">', an, re.S).group(1)
idx = re.findall(r'<Parameter name="Index" type="int" value="(\d)"', ebc); sides = re.findall(r'<Parameter name="Sides" type="string" value="([^"]*)"', ebc); vals = re.findall(r'<Parameter name="Value" type="double" value="([^"]*)"', ebc); types = re.findall(r'<Parameter name="Type" type="string" value="([^"]*)"', ebc)
chk("fixed support ux=uy=uz=0 on ns_fix (Fixed Value)", sorted(idx) == ["0","1","2"] and set(sides) == {"ns_fix"} and all(float(v) == 0.0 for v in vals) and set(types) == {"Fixed Value"} and len(idx) == 3, {"indices": idx, "sides": sides, "values": vals, "types": types}, {"indices": ["0","1","2"], "sides": ["ns_fix"]*3, "values": ["0.0"]*3}, "analyze_2_input_deck.xml")
chk("analyze output dispx dispy dispz", param(an, "Plottable") == "{displacement_x, displacement_y, displacement_z}", param(an, "Plottable"), "{displacement_x, displacement_y, displacement_z}", "analyze_2_input_deck.xml")
# engine
chk("engine mesh", tag(ei, "mesh") == "mesh.exo", tag(ei, "mesh"), "mesh.exo", "engine_input_deck.xml")
chk("engine output file engine_output", tag(ei, "file") == "engine_output", tag(ei, "file"), "engine_output", "engine_input_deck.xml")
pmo = re.search(r'<Function>PlatoMainOutput</Function>(.*?)</Operation>', eo, re.S).group(1)
chk("restart-file writing enabled (WriteRestart)", tag(pmo, "WriteRestart") == "true", tag(pmo, "WriteRestart"), "true", "engine_operations.xml")
chk("engine output every iteration (OutputFrequency 1)", tag(pmo, "OutputFrequency") == "1", tag(pmo, "OutputFrequency"), "1", "engine_operations.xml")
chk("engine output MaxIterations", tag(pmo, "MaxIterations") == ("20" if stage == "1" else "40"), tag(pmo, "MaxIterations"), "20" if stage == "1" else "40", "engine_operations.xml")
chk("engine output fields topology + control", "<ArgumentName>topology</ArgumentName>" in pmo and "<ArgumentName>control</ArgumentName>" in pmo, ["topology" in pmo, "control" in pmo], [True, True], "engine_operations.xml")
if stage == "1":
    ini = re.search(r'<Function>InitializeField</Function>(.*?)</Operation>', eo, re.S).group(1)
    chk("initial density uniform 0.15", tag(ini, "Method") == "Uniform" and float(tag(ini, "Value")) == 0.15, [tag(ini, "Method"), tag(ini, "Value")], ["Uniform", "0.15"], "engine_operations.xml")
    chk("stage 1 is a fresh run (no restart read)", "FromFieldOnInputMesh" not in ini and "FileName" not in ini, "no restart source", "no restart source", "engine_operations.xml")
chk("update problem frequency 1 (engine operation)", tag(re.search(r'<Function>Update Problem</Function>(.*?)</Operation>', eo, re.S).group(1), "UpdateProblemFrequency") == "1", tag(eo, "UpdateProblemFrequency"), "1", "engine_operations.xml")
chk("volume constraint computed by engine (ComputeVolume)", "<Function>ComputeVolume</Function>" in eo, "<Function>ComputeVolume</Function>" in eo, True, "engine_operations.xml")
agg = re.search(r'<Function>Aggregator</Function>(.*?)</Operation>', eo, re.S).group(1)
chk("aggregator weight 1, no normalization (normalize_in_aggregator false)", tag(agg, "Value") == "1" and "Normal" not in agg and agg.count("<Weight>") == 1, {"weight": tag(agg, "Value"), "normalization_present": "Normal" in agg}, {"weight": "1", "normalization_present": False}, "engine_operations.xml")
# interface
chk("optimizer OC", tag(itf, "Package") == "OC", tag(itf, "Package"), "OC", "interface.xml")
chk("max_iterations", tag(itf, "MaxIterations") == ("20" if stage == "1" else "40"), tag(itf, "MaxIterations"), "20" if stage == "1" else "40", "interface.xml")
chk("OC default tolerances (1e-4, 1e-8, 1e-8)", tag(itf, "OCControlStagnationTolerance") == "1e-4" and tag(itf, "OCObjectiveStagnationTolerance") == "1e-8" and tag(itf, "OCGradientTolerance") == "1e-8", [tag(itf, "OCControlStagnationTolerance"), tag(itf, "OCObjectiveStagnationTolerance"), tag(itf, "OCGradientTolerance")], ["1e-4", "1e-8", "1e-8"], "interface.xml")
chk("problem update frequency 1 (optimizer)", tag(itf, "ProblemUpdateFrequency") == "1", tag(itf, "ProblemUpdateFrequency"), "1", "interface.xml")
chk("update problem stage wired", "<UpdateProblemStage>" in itf and "<Name>Update Problem</Name>" in itf, "<UpdateProblemStage>" in itf, True, "interface.xml")
chk("volume constraint relative target 0.15 of design volume", tag(itf, "NormalizedTargetValue") == "0.15" and tag(itf, "ReferenceValueName") == "Design Volume", [tag(itf, "NormalizedTargetValue"), tag(itf, "ReferenceValueName")], ["0.15", "Design Volume"], "interface.xml")
chk("exactly one constraint", itf.count("<Constraint>") == 1, itf.count("<Constraint>"), 1, "interface.xml")
chk("density bounds [0,1]", tag(itf, "Lower") == "0.0" and tag(itf, "Upper") == "1.0", [tag(itf, "Lower"), tag(itf, "Upper")], ["0.0", "1.0"], "interface.xml")
chk("filtered variable Topology (helmholtz applied in stages)", tag(itf, "FilteredName") == "Topology" and itf.count("<Name>Filter Control</Name>") >= 4, [tag(itf, "FilteredName"), itf.count("<Name>Filter Control</Name>")], ["Topology", ">=4"], "interface.xml")
perf = re.findall(r'<Performer>\s*<Name>([^<]*)</Name>\s*<Code>([^<]*)</Code>', itf)
chk("performers: engine_1(engine), analyze_2(analyze), analyze_helmholtz(analyze)", perf == [("engine_1","engine"),("analyze_2","analyze"),("analyze_helmholtz","analyze")], perf, [["engine_1","engine"],["analyze_2","analyze"],["analyze_helmholtz","analyze"]], "interface.xml")
chk("objective value computed by analyze_2, aggregated by engine", "<Name>Compute Objective Value</Name>\n    <PerformerName>analyze_2</PerformerName>" in itf, True, True, "interface.xml")
chk("constraint value computed by engine_1", "<Name>Compute Constraint Value 1</Name>\n    <PerformerName>engine_1</PerformerName>" in itf, True, True, "interface.xml")
# mpirun.source
nps = re.findall(r'-np (\d+)', mp)
chk("single-rank performers (-np 1 each)", nps == ["1","1","1"], nps, ["1","1","1"], "mpirun.source")
chk("no mesh decomposition (decomp not invoked)", "decomp" not in mp.lower(), "decomp" in mp.lower(), False, "mpirun.source")
chk("executables PlatoMain + analyze_MPMD x2", mp.count("PlatoMain") == 1 and mp.count("analyze_MPMD") == 2, [mp.count("PlatoMain"), mp.count("analyze_MPMD")], [1, 2], "mpirun.source")
allpass = all(r["pass"] for r in res)
files = sorted(f for f in os.listdir(d) if f.endswith(".xml") or f == "mpirun.source")
out = {"stage": int(stage), "directory": d, "verified_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
       "generated_files_sha256": {f: hashlib.sha256(open(os.path.join(d, f), "rb").read()).hexdigest() for f in files},
       "checks": res, "ALL_CHECKS_PASS": allpass}
print(json.dumps(out, indent=2)); sys.exit(0 if allpass else 1)
