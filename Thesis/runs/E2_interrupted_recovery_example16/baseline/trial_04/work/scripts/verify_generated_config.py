"""Verify the XMLGenerator output of a FROZEN-EX16-v1 stage against the locked settings.
Usage: python3 -I verify_generated_config.py <run_dir> stage1
Every check is recorded; exit 1 if any check fails."""
import sys, os, re, json, math, datetime, hashlib
import xml.etree.ElementTree as ET

run = sys.argv[1]; stage = sys.argv[2]
def load_fragment(name):
    txt = open(os.path.join(run, name)).read()
    txt = re.sub(r"<\?xml[^>]*\?>", "", txt)
    return ET.fromstring("<root>" + txt + "</root>")
def plist(root, path_names):
    """descend ParameterList by name sequence"""
    node = root
    for nm in path_names:
        nxt = None
        for ch in node.iter("ParameterList"):
            if ch.get("name") == nm and ch is not node: nxt = ch; break
        if nxt is None: return None
        node = nxt
    return node
def param(pl, name):
    if pl is None: return None
    for p in pl.findall("Parameter"):
        if p.get("name") == name: return p.get("value")
    return None
def text(node, tag):
    e = node.find(tag); return None if e is None else (e.text or "").strip()

C = {}  # check name -> (pass, observed)
def chk(name, cond, observed): C[name] = {"pass": bool(cond), "observed": observed}

# ---------- analyze (physics) deck
a = load_fragment("analyze_2_input_deck.xml")
prob = a.find("ParameterList")
chk("analyze: Spatial Dimension == 3", param(prob,"Spatial Dimension")=="3", param(prob,"Spatial Dimension"))
chk("analyze: Input Mesh == mesh.exo", param(prob,"Input Mesh")=="mesh.exo", param(prob,"Input Mesh"))
sc = plist(prob,["Scenarios"])
chk("analyze: Physics == Mechanical", param(sc,"Physics")=="Mechanical", param(sc,"Physics"))
chk("analyze: PDE Constraint == Elliptic (linear static)", param(sc,"PDE Constraint")=="Elliptic", param(sc,"PDE Constraint"))
obj = plist(sc,["Criteria","My Objective"])
chk("analyze: objective criterion = Internal Elastic Energy (mechanical compliance)", param(obj,"Scalar Function Type")=="Internal Elastic Energy", param(obj,"Scalar Function Type"))
chk("analyze: objective domains == {block_1}", param(obj,"Domains")=="{block_1}", param(obj,"Domains"))
pf = plist(obj,["Penalty Function"])
chk("analyze: compliance penalty SIMP", param(pf,"Type")=="SIMP", param(pf,"Type"))
chk("analyze: compliance SIMP exponent == 3.0", float(param(pf,"Exponent"))==3.0, param(pf,"Exponent"))
chk("analyze: compliance minimum_ersatz_material_value == 1e-3", float(param(pf,"Minimum Value"))==1e-3, param(pf,"Minimum Value"))
res = plist(sc,["Residual","Mechanical Residual"])
chk("analyze: residual material interpolation Single-Phase", param(res,"Material Interpolation Model")=="Single-Phase", param(res,"Material Interpolation Model"))
chk("analyze: residual response Linear", param(res,"Response")=="Linear", param(res,"Response"))
rpf = plist(res,["Penalty Function"])
chk("analyze: residual SIMP exponent == 3.0", param(rpf,"Type")=="SIMP" and float(param(rpf,"Exponent"))==3.0, (param(rpf,"Type"),param(rpf,"Exponent")))
chk("analyze: residual SIMP minimum value == 1e-3", float(param(rpf,"Minimum Value"))==1e-3, param(rpf,"Minimum Value"))
dom = plist(sc,["Spatial Model","Domains"])
domains = [d.get("name") for d in dom.findall("ParameterList")]
chk("analyze: exactly one domain block_1 -> material_1", domains==["block_1"] and param(plist(dom,["block_1"]),"Element Block")=="block_1" and param(plist(dom,["block_1"]),"Material Model")=="material_1", domains)
mat = plist(sc,["Material Models","material_1","Isotropic Linear Elastic"])
chk("analyze: material isotropic linear elastic", mat is not None, "Isotropic Linear Elastic" if mat is not None else None)
chk("analyze: Youngs Modulus == 1.0", mat is not None and float(param(mat,"Youngs Modulus"))==1.0, param(mat,"Youngs Modulus"))
chk("analyze: Poissons Ratio == 0.3", mat is not None and float(param(mat,"Poissons Ratio"))==0.3, param(mat,"Poissons Ratio"))
cl = plist(sc,["Concentrated Loads"])
loads = cl.findall("ParameterList") if cl is not None else []
chk("analyze: exactly one concentrated load", len(loads)==1, len(loads))
if loads:
    L = loads[0]
    chk("analyze: load Dof == 1 (y direction)", param(L,"Dof")=="1", param(L,"Dof"))
    chk("analyze: load Value == -1.0 per node", float(param(L,"Value"))==-1.0, param(L,"Value"))
    chk("analyze: load Nodes == ns_load", param(L,"Nodes")=="ns_load", param(L,"Nodes"))
nbc = plist(sc,["Mechanical Natural Boundary Conditions"])
chk("analyze: no tractions/natural BCs", nbc is not None and len(nbc.findall("ParameterList"))==0, len(nbc.findall("ParameterList")) if nbc is not None else "absent")
chk("analyze: no body loads", plist(sc,["Body Loads"]) is None, "Body Loads list absent" if plist(sc,["Body Loads"]) is None else "present")
ebc = plist(sc,["Essential Boundary Conditions"])
bcs = ebc.findall("ParameterList") if ebc is not None else []
bcidx = sorted(int(param(b,"Index")) for b in bcs)
chk("analyze: exactly three fixed-value BCs (dispx,dispy,dispz)", len(bcs)==3 and bcidx==[0,1,2] and all(param(b,"Type")=="Fixed Value" for b in bcs), [(param(b,"Type"),param(b,"Index")) for b in bcs])
chk("analyze: all BCs on ns_fix with value 0.0", all(param(b,"Sides")=="ns_fix" and float(param(b,"Value"))==0.0 for b in bcs), [(param(b,"Sides"),param(b,"Value")) for b in bcs])
out = plist(sc,["Output"])
chk("analyze: output displacement_x,y,z", param(out,"Plottable")=="{displacement_x, displacement_y, displacement_z}", param(out,"Plottable"))

# ---------- helmholtz deck
h = load_fragment("analyze_helmholtz_input_deck.xml")
hp = h.find("ParameterList"); hs = plist(hp,["Scenarios"]); hpar = plist(hs,["Parameters"])
chk("helmholtz: Physics == Helmholtz Filter", param(hs,"Physics")=="Helmholtz Filter", param(hs,"Physics"))
ls_val = float(param(hpar,"Length Scale")); expect = 0.15/(2*math.sqrt(3))
chk("helmholtz: Length Scale == 0.15/(2*sqrt(3)) = 0.043301 (radius_absolute 0.15)", abs(ls_val-expect)<1e-6, ls_val)
chk("helmholtz: Surface Length Scale == 1.0 (boundary_sticking_penalty 1.0)", float(param(hpar,"Surface Length Scale"))==1.0, param(hpar,"Surface Length Scale"))
chk("helmholtz: no symmetry plane parameter", all("ymmetry" not in (p.get("name") or "") for p in hpar.findall("Parameter")), [p.get("name") for p in hpar.findall("Parameter")])
chk("helmholtz: Input Mesh == mesh.exo", param(hp,"Input Mesh")=="mesh.exo", param(hp,"Input Mesh"))
chk("helmholtz: domain block_1", [d.get("name") for d in plist(hs,["Spatial Model","Domains"]).findall("ParameterList")]==["block_1"], [d.get("name") for d in plist(hs,["Spatial Model","Domains"]).findall("ParameterList")])

# ---------- engine operations
e = load_fragment("engine_operations.xml")
ops = {o.findtext("Name"): o for o in e.findall("Operation")}
po = ops.get("PlatoMainOutput")
chk("engine: PlatoMainOutput WriteRestart == true", po is not None and text(po,"WriteRestart")=="true", text(po,"WriteRestart") if po is not None else None)
chk("engine: PlatoMainOutput OutputFrequency == 1 (every iteration saved)", po is not None and text(po,"OutputFrequency")=="1", text(po,"OutputFrequency") if po is not None else None)
chk("engine: PlatoMainOutput MaxIterations == 20", po is not None and text(po,"MaxIterations")=="20", text(po,"MaxIterations") if po is not None else None)
po_in = sorted(i.findtext("ArgumentName") for i in po.findall("Input")) if po is not None else []
chk("engine: output fields control and topology (nodal)", po_in==["control","topology"], po_in)
ini = ops.get("Initialize Field")
chk("engine: InitializeField Method Uniform", ini is not None and text(ini,"Method")=="Uniform", text(ini,"Method") if ini is not None else None)
chk("engine: initial density value == 0.15", ini is not None and float(ini.find("Uniform").findtext("Value"))==0.15, ini.find("Uniform").findtext("Value") if ini is not None else None)
chk("engine: no restart InitializeField from file (fresh Stage-1 start)", ini is not None and ini.find("FromFieldOnInputMesh") is None and ini.find("FileName") is None and "FileName" not in ET.tostring(ini).decode(), ET.tostring(ini).decode().count("FileName"))
up = ops.get("Update Problem")
chk("engine: Update Problem operation, frequency 1", up is not None and text(up,"UpdateProblemFrequency")=="1", text(up,"UpdateProblemFrequency") if up is not None else None)
cv = ops.get("Compute Constraint Value 1")
chk("engine: volume constraint computed by engine ComputeVolume", cv is not None and cv.findtext("Function")=="ComputeVolume", cv.findtext("Function") if cv is not None else None)
ag = ops.get("Aggregate Data")
w = [x.findtext("Value") for x in ag.find("Weighting").findall("Weight")] if ag is not None else []
chk("engine: aggregator single weight == 1", w==["1"], w)
chk("engine: normalize_in_aggregator false (no Normalize=true in aggregator)", ag is not None and "<Normalize>true" not in ET.tostring(ag).decode().replace(" ",""), "Normalize" in ET.tostring(ag).decode())
chk("engine: SetLowerBounds/SetUpperBounds density", all(ops.get(n) is not None and text(ops[n],"Discretization")=="density" for n in ("Compute Lower Bounds","Compute Upper Bounds")), [text(ops[n],"Discretization") for n in ("Compute Lower Bounds","Compute Upper Bounds") if n in ops])

# ---------- engine input deck
ei = load_fragment("engine_input_deck.xml")
chk("engine_input: mesh == mesh.exo", ei.find("mesh").findtext("mesh").strip()=="mesh.exo", ei.find("mesh").findtext("mesh"))
chk("engine_input: output file engine_output (exodus)", ei.find("output").findtext("file").strip()=="engine_output" and ei.find("output").findtext("format").strip()=="exodus", (ei.find("output").findtext("file"),ei.find("output").findtext("format")))
blk = ei.find("mesh").findall("block")
chk("engine_input: single block index 1, material 1", len(blk)==1 and blk[0].findtext("index").strip()=="1" and blk[0].findtext("material").strip()=="1", [(b.findtext("index"),b.findtext("material")) for b in blk])

# ---------- interface
it = load_fragment("interface.xml")
perf = [(p.findtext("Name"),p.findtext("Code")) for p in it.findall("Performer")]
chk("interface: performers engine_1(engine), analyze_2(analyze), analyze_helmholtz(analyze)", perf==[("engine_1","engine"),("analyze_2","analyze"),("analyze_helmholtz","analyze")], perf)
opt = it.find("Optimizer")
chk("interface: Optimizer Package == OC", opt.findtext("Package")=="OC", opt.findtext("Package"))
chk("interface: Optimizer MaxIterations == 20", opt.find("Convergence").findtext("MaxIterations")=="20", opt.find("Convergence").findtext("MaxIterations"))
oo = opt.find("Options")
tol = {t: oo.findtext(t) for t in ("OCControlStagnationTolerance","OCObjectiveStagnationTolerance","OCGradientTolerance","ProblemUpdateFrequency")}
chk("interface: OC tolerances are runtime defaults (1e-4, 1e-8, 1e-8)", tol["OCControlStagnationTolerance"]=="1e-4" and tol["OCObjectiveStagnationTolerance"]=="1e-8" and tol["OCGradientTolerance"]=="1e-8", tol)
chk("interface: ProblemUpdateFrequency == 1", tol["ProblemUpdateFrequency"]=="1", tol["ProblemUpdateFrequency"])
con = opt.find("Constraint")
chk("interface: constraint NormalizedTargetValue == 0.15", con.findtext("NormalizedTargetValue")=="0.15", con.findtext("NormalizedTargetValue"))
chk("interface: constraint reference == Design Volume (fraction of design-domain volume)", con.findtext("ReferenceValueName")=="Design Volume", con.findtext("ReferenceValueName"))
chk("interface: exactly one constraint", len(opt.findall("Constraint"))==1, len(opt.findall("Constraint")))
stages = {s.findtext("Name"): s for s in it.findall("Stage")}
cvs = stages.get("Compute Constraint Value 1")
cv_perf = [o.findtext("PerformerName") for o in cvs.findall("Operation") if o.findtext("Name")=="Compute Constraint Value 1"] if cvs is not None else []
chk("interface: constraint value computed by engine_1", cv_perf==["engine_1"], cv_perf)
ovs = stages.get("Compute Objective Value")
ov_perf = [o.findtext("PerformerName") for o in ovs.findall("Operation") if o.findtext("Name")=="Compute Objective Value"] if ovs is not None else []
chk("interface: objective (compliance) value computed by analyze_2", ov_perf==["analyze_2"], ov_perf)
filt = [o.findtext("PerformerName") for o in ovs.findall("Operation") if o.findtext("Name")=="Filter Control"] if ovs is not None else []
chk("interface: Helmholtz filter applied to control before objective evaluation", filt==["analyze_helmholtz"], filt)
ofs = stages.get("Output To File")
chk("interface: Output To File stage includes PlatoMainOutput (engine) and Visualization (analyze_2)", ofs is not None and sorted(o.findtext("Name") for o in ofs.findall("Operation"))==["PlatoMainOutput","Visualization"], [o.findtext("Name") for o in ofs.findall("Operation")] if ofs is not None else None)
chk("interface: Update Problem stage registered", opt.find("UpdateProblemStage") is not None and opt.find("UpdateProblemStage").findtext("Name")=="Update Problem", opt.find("UpdateProblemStage").findtext("Name") if opt.find("UpdateProblemStage") is not None else None)
bc = opt.find("BoundConstraint")
chk("interface: density bounds [0,1]", bc.findtext("Lower")=="0.0" and bc.findtext("Upper")=="1.0", (bc.findtext("Lower"),bc.findtext("Upper")))
ig = opt.find("OptimizationVariables")
chk("interface: initialization stage == Initial Guess (uniform field, no restart source)", ig.findtext("InitializationStage")=="Initial Guess", ig.findtext("InitializationStage"))

# ---------- mpirun.source
ms = open(os.path.join(run,"mpirun.source")).read()
chk("mpirun: three single-rank performers (-np 1 x3)", ms.count("-np 1")==3 and ms.count("-np ")==3, ms.count("-np 1"))
chk("mpirun: PlatoMain + 2x analyze_MPMD", ms.count("PlatoMain")==1 and ms.count("analyze_MPMD")==2, (ms.count("PlatoMain"),ms.count("analyze_MPMD")))
chk("mpirun: no mesh decomposition (no decomp/epu)", "decomp" not in ms and "epu" not in ms, "ok")

sha = {f: hashlib.sha256(open(os.path.join(run,f),"rb").read()).hexdigest() for f in sorted(os.listdir(run)) if f.endswith(".xml") or f in ("mpirun.source","input_deck.i","mesh.exo")}
rec = {"frozen_configuration_id":"FROZEN-EX16-v1","stage":stage,"run_dir":os.path.abspath(run),
       "verified_utc":datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
       "checks":C,"n_checks":len(C),"n_pass":sum(1 for v in C.values() if v["pass"]),"all_checks_pass":all(v["pass"] for v in C.values()),
       "sha256":sha}
print(json.dumps(rec,indent=2))
sys.exit(0 if rec["all_checks_pass"] else 1)
