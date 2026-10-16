#!/usr/bin/env python3
"""Verify the XMLGenerator output of the EX8 run against the locked settings.
Usage: python3 -I verify_generated_config.py <run_dir> <out.txt>"""
import sys, os, re, math, datetime
import xml.etree.ElementTree as ET
run, out = sys.argv[1], sys.argv[2]
checks = []
def chk(name, got, exp):
    checks.append((name, got, exp, got == exp))
def plist(path):
    return ET.parse(os.path.join(run, path)).getroot()
def params(root):
    """flatten Teuchos ParameterList: list of (listpath, name, value)"""
    out = []
    def walk(node, path):
        for ch in node:
            if ch.tag == "ParameterList":
                walk(ch, path + "/" + ch.get("name"))
            elif ch.tag == "Parameter":
                out.append((path, ch.get("name"), ch.get("value")))
    walk(root, root.get("name", ""))
    return out
def get(ps, pathsuffix, name):
    for p, n, v in ps:
        if p.endswith(pathsuffix) and n == name:
            return v
    return None
def fl(v):
    try: return float(v)
    except: return None

# ---------------- Helmholtz filter configuration ----------------
hp = params(plist("analyze_helmholtz_input_deck.xml"))
chk("helmholtz: Physics", get(hp, "Scenarios", "Physics"), "Helmholtz Filter")
ls = fl(get(hp, "Parameters", "Length Scale"))
chk("helmholtz: Length Scale present", ls is not None, True)
chk("helmholtz: Length Scale == 0.15/(2*sqrt(3)) (radius 0.15)", ls is not None and abs(ls - 0.15/(2*math.sqrt(3))) < 1e-5, True)
sls = fl(get(hp, "Parameters", "Surface Length Scale"))
chk("helmholtz: Surface Length Scale present", sls is not None, True)
chk("helmholtz: Surface Length Scale == 1.0 (sticking penalty 1.0)", sls, 1.0)
sym = get(hp, "Parameters", "Symmetry Plane Sides")
chk("helmholtz: Symmetry Plane Sides present", sym is not None, True)
chk("helmholtz: Symmetry Plane Sides contains ss_sym", sym is not None and "ss_sym" in re.findall(r"[\w]+", sym), True)
chk("helmholtz: Input Mesh", get(hp, "Problem", "Input Mesh"), "mesh.exo")
chk("helmholtz: domain block_1", get(hp, "Domains/block_1", "Element Block"), "block_1")

# ---------------- analyze (mechanical) configuration ----------------
ap = params(plist("analyze_2_input_deck.xml"))
chk("analyze: Spatial Dimension", get(ap, "Problem", "Spatial Dimension"), "3")
chk("analyze: Input Mesh", get(ap, "Problem", "Input Mesh"), "mesh.exo")
chk("analyze: Physics Mechanical", get(ap, "Scenarios", "Physics"), "Mechanical")
chk("analyze: domain block_1", get(ap, "Domains/block_1", "Element Block"), "block_1")
chk("analyze: Youngs Modulus 1.0", fl(get(ap, "Isotropic Linear Elastic", "Youngs Modulus")), 1.0)
chk("analyze: Poissons Ratio 0.3", fl(get(ap, "Isotropic Linear Elastic", "Poissons Ratio")), 0.3)
chk("analyze: residual interpolation Single-Phase", get(ap, "Mechanical Residual", "Material Interpolation Model"), "Single-Phase")
chk("analyze: residual SIMP type", get(ap, "Mechanical Residual/Penalty Function", "Type"), "SIMP")
chk("analyze: residual SIMP exponent 3.0", fl(get(ap, "Mechanical Residual/Penalty Function", "Exponent")), 3.0)
chk("analyze: residual SIMP minimum 1e-3", fl(get(ap, "Mechanical Residual/Penalty Function", "Minimum Value")), 1e-3)
chk("analyze: objective criterion type", get(ap, "Criteria/My Objective", "Scalar Function Type"), "Internal Elastic Energy")
chk("analyze: criterion SIMP exponent 3.0", fl(get(ap, "My Objective/Penalty Function", "Exponent")), 3.0)
chk("analyze: criterion minimum ersatz 1e-3", fl(get(ap, "My Objective/Penalty Function", "Minimum Value")), 1e-3)
# load
loads = [(p, n, v) for p, n, v in ap if "/Concentrated Loads/" in p]
load_lists = sorted(set(p for p, n, v in loads))
chk("analyze: exactly one concentrated load", len(load_lists), 1)
if load_lists:
    L = load_lists[0]
    chk("analyze: load Dof 1 (y)", get(ap, L, "Dof"), "1")
    chk("analyze: load Value -1.0", fl(get(ap, L, "Value")), -1.0)
    chk("analyze: load Nodes ns_load", get(ap, L, "Nodes"), "ns_load")
nbc = [p for p, n, v in ap if "/Mechanical Natural Boundary Conditions/" in p]
chk("analyze: no natural BCs (tractions)", len(nbc), 0)
# essential BCs
ebc = {}
for p, n, v in ap:
    if "/Essential Boundary Conditions/" in p:
        ebc.setdefault(p.split("/")[-1], {})[n] = v
ebc_set = sorted((d.get("Sides"), d.get("Index"), d.get("Type"), fl(d.get("Value"))) for d in ebc.values())
chk("analyze: essential BC set", ebc_set, sorted([("ns_fix","0","Fixed Value",0.0),("ns_fix","1","Fixed Value",0.0),("ns_fix","2","Fixed Value",0.0),("ss_sym","2","Fixed Value",0.0)]))
plot = get(ap, "Output", "Plottable") or ""
chk("analyze: output dispx dispy dispz", sorted(re.findall(r"[\w]+", plot)), sorted(["displacement_x","displacement_y","displacement_z"]))

# ---------------- interface.xml (optimizer) ----------------
itxt = open(os.path.join(run, "interface.xml")).read()
iroot = ET.fromstring("<root>" + itxt.split("?>",1)[1] + "</root>")
performers = [(p.findtext("Name"), p.findtext("Code")) for p in iroot.findall("Performer")]
chk("interface: performers", performers, [("engine_1","engine"),("analyze_2","analyze"),("analyze_helmholtz","analyze")])
opt = iroot.find("Optimizer")
chk("interface: optimizer package OC", opt.findtext("Package"), "OC")
chk("interface: MaxIterations 50", opt.findtext("Convergence/MaxIterations"), "50")
chk("interface: OC control stagnation tol default 1e-4", opt.findtext("Options/OCControlStagnationTolerance"), "1e-4")
chk("interface: OC objective stagnation tol default 1e-8", opt.findtext("Options/OCObjectiveStagnationTolerance"), "1e-8")
chk("interface: OC gradient tol default 1e-8", opt.findtext("Options/OCGradientTolerance"), "1e-8")
chk("interface: ProblemUpdateFrequency 1", opt.findtext("Options/ProblemUpdateFrequency"), "1")
chk("interface: UpdateProblemStage defined", opt.findtext("UpdateProblemStage/Name"), "Update Problem")
chk("interface: constraint NormalizedTargetValue 0.15", opt.findtext("Constraint/NormalizedTargetValue"), "0.15")
chk("interface: constraint reference Design Volume", opt.findtext("Constraint/ReferenceValueName"), "Design Volume")
chk("interface: filtered variable name Topology", opt.findtext("OptimizationVariables/FilteredName"), "Topology")
stages = {s.findtext("Name"): s for s in iroot.findall("Stage")}
cv = stages.get("Compute Constraint Value 1")
chk("interface: constraint value computed by engine_1", cv is not None and any(o.findtext("Name")=="Compute Constraint Value 1" and o.findtext("PerformerName")=="engine_1" for o in cv.findall("Operation")), True)
ov = stages.get("Compute Objective Value")
chk("interface: objective value computed by analyze_2", ov is not None and any(o.findtext("Name")=="Compute Objective Value" and o.findtext("PerformerName")=="analyze_2" for o in ov.findall("Operation")), True)
chk("interface: objective stage applies Helmholtz filter", ov is not None and any(o.findtext("Name")=="Filter Control" and o.findtext("PerformerName")=="analyze_helmholtz" for o in ov.findall("Operation")), True)
out_stage = stages.get("Output To File")
pm = [o for o in out_stage.findall("Operation") if o.findtext("Name")=="PlatoMainOutput"] if out_stage is not None else []
pm_in = sorted(i.findtext("ArgumentName") for i in pm[0].findall("Input")) if pm else []
chk("interface: engine output fields control+topology", pm_in, ["control","topology"])
agg = iroot.find("Optimizer")
# aggregator normalization: check engine_operations Aggregator has no Normalize element set true
etxt = open(os.path.join(run, "engine_operations.xml")).read()
eroot = ET.fromstring("<root>" + etxt.split("?>",1)[1] + "</root>")
ops = {o.findtext("Name"): o for o in eroot.findall("Operation")}
chk("engine ops: Initialize Field Uniform", ops["Initialize Field"].findtext("Method"), "Uniform")
chk("engine ops: initial density 0.15", fl(ops["Initialize Field"].findtext("Uniform/Value")), 0.15)
chk("engine ops: Update Problem frequency 1", ops["Update Problem"].findtext("UpdateProblemFrequency"), "1")
chk("engine ops: PlatoMainOutput MaxIterations 50", ops["PlatoMainOutput"].findtext("MaxIterations"), "50")
chk("engine ops: discretization density (bounds)", ops["Compute Lower Bounds"].findtext("Discretization"), "density")
aggop = ops["Aggregate Data"]
chk("engine ops: aggregator weight 1", [w.findtext("Value") for w in aggop.findall("Weighting/Weight")], ["1"])
chk("engine ops: aggregator normalization not enabled", any(e.tag.lower().startswith("normal") and (e.text or "").strip().lower()=="true" for e in aggop.iter()), False)
# mpirun.source
m = open(os.path.join(run, "mpirun.source")).read()
chk("mpirun: three single-rank performers", re.findall(r"-np\s+(\d+)", m), ["1","1","1"])
chk("mpirun: PlatoMain + 2x analyze_MPMD", (m.count("PlatoMain "), m.count("analyze_MPMD ")), (1, 2))
chk("mpirun: no decomposition (no decomp/epu step)", ("decomp" in m.lower()), False)
# engine input deck
eid = open(os.path.join(run, "engine_input_deck.xml")).read()
chk("engine deck: mesh mesh.exo", "<mesh>mesh.exo</mesh>" in eid, True)
chk("engine deck: output engine_output", "<file>engine_output</file>" in eid, True)

allok = all(c[3] for c in checks)
lines = ["EX8 generated-configuration verification record (FROZEN-EX8-v1)",
         f"utc_timestamp: {datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
         f"run_dir: {run}", ""]
lines.append(f"{'check':62s} {'got':>44s} {'expected':>44s} result")
for n, g, e, ok in checks:
    lines.append(f"{n:62s} {str(g)[:44]:>44s} {str(e)[:44]:>44s} {'PASS' if ok else 'FAIL'}")
lines += ["", f"OVERALL: {'PASS' if allok else 'FAIL'} ({sum(c[3] for c in checks)}/{len(checks)} checks passed)"]
open(out, "w").write("\n".join(lines) + "\n")
print("\n".join(lines))
sys.exit(0 if allok else 1)
