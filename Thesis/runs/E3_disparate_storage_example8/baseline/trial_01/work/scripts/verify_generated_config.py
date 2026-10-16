#!/usr/bin/env python3
"""E3-SPC-v1 generated-configuration verification (XMLGenerator output) against the locked settings of sections 4-6."""
import sys, json, re, math, datetime, os
import xml.etree.ElementTree as ET
d = sys.argv[1]
def read(f): return open(os.path.join(d, f)).read()
def plist(f): return ET.fromstring(read(f))
def params(root):
    out = {}
    def walk(node, prefix):
        for c in node:
            if c.tag == "ParameterList":
                walk(c, prefix + "/" + c.get("name"))
            elif c.tag == "Parameter":
                out[prefix + "/" + c.get("name")] = c.get("value")
    walk(root, root.get("name"))
    return out
H = params(plist("analyze_helmholtz_input_deck.xml"))
A = params(plist("analyze_2_input_deck.xml"))
I = read("interface.xml"); E = read("engine_operations.xml"); M = read("mpirun.source"); EI = read("engine_input_deck.xml"); AO = read("analyze_2_operations.xml")
def f(v): return float(v)
exp_ls = 0.15 / (2.0*math.sqrt(3.0))
ebc = {k: v for k, v in A.items() if "/Essential Boundary Conditions/" in k}
bc_sets = {}
for k, v in ebc.items():
    name = k.split("/Essential Boundary Conditions/")[1].split("/")[0]
    bc_sets.setdefault(name, {})[k.rsplit("/",1)[1]] = v
bc_tuples = sorted((b["Sides"], b["Index"], b["Type"], b["Value"]) for b in bc_sets.values())
checks = {
 # section 6 filter (generated Helmholtz configuration)
 "helmholtz: filter length scale present and = 0.15/(2*sqrt(3)) = %.6f" % exp_ls: "Problem/Scenarios/Parameters/Length Scale" in H and abs(f(H["Problem/Scenarios/Parameters/Length Scale"]) - exp_ls) < 1e-5,
 "helmholtz: surface (boundary-sticking) length scale present and = 1.0": "Problem/Scenarios/Parameters/Surface Length Scale" in H and f(H["Problem/Scenarios/Parameters/Surface Length Scale"]) == 1.0,
 "helmholtz: symmetry-plane sideset ss_sym declared": H.get("Problem/Scenarios/Parameters/Symmetry Plane Sides", "").replace(" ", "") == "{ss_sym}",
 "helmholtz: physics = Helmholtz Filter, mesh = mesh.exo, 3-D": H.get("Problem/Scenarios/Physics") == "Helmholtz Filter" and H.get("Problem/Input Mesh") == "mesh.exo" and H.get("Problem/Spatial Dimension") == "3",
 # section 4 material (generated analyze configuration)
 "analyze: isotropic linear elastic E=1.0 nu=0.3 for material of block_1": A.get("Problem/Scenarios/Material Models/material_1/Isotropic Linear Elastic/Youngs Modulus") == "1.0" and A.get("Problem/Scenarios/Material Models/material_1/Isotropic Linear Elastic/Poissons Ratio") == "0.3" and A.get("Problem/Scenarios/Spatial Model/Domains/block_1/Material Model") == "material_1" and A.get("Problem/Scenarios/Spatial Model/Domains/block_1/Element Block") == "block_1",
 # section 6 SIMP
 "analyze: residual SIMP exponent 3.0, minimum 1e-3": A.get("Problem/Scenarios/Residual/Mechanical Residual/Penalty Function/Type") == "SIMP" and f(A["Problem/Scenarios/Residual/Mechanical Residual/Penalty Function/Exponent"]) == 3.0 and f(A["Problem/Scenarios/Residual/Mechanical Residual/Penalty Function/Minimum Value"]) == 1e-3,
 "analyze: compliance criterion SIMP exponent 3.0, minimum ersatz 1e-3": A.get("Problem/Scenarios/Criteria/My Objective/Scalar Function Type") == "Internal Elastic Energy" and A.get("Problem/Scenarios/Criteria/My Objective/Penalty Function/Type") == "SIMP" and f(A["Problem/Scenarios/Criteria/My Objective/Penalty Function/Exponent"]) == 3.0 and f(A["Problem/Scenarios/Criteria/My Objective/Penalty Function/Minimum Value"]) == 1e-3,
 "analyze: single-phase material interpolation, linear response": A.get("Problem/Scenarios/Residual/Mechanical Residual/Material Interpolation Model") == "Single-Phase" and A.get("Problem/Scenarios/Residual/Mechanical Residual/Response") == "Linear",
 # section 5 load and BCs
 "analyze: exactly one concentrated load, dof y (1), value -1.0, nodes ns_load; no tractions": sorted(k for k in A if "/Concentrated Loads/" in k) == ["Problem/Scenarios/Concentrated Loads/Concentrated Load with ID 0/Dof","Problem/Scenarios/Concentrated Loads/Concentrated Load with ID 0/Nodes","Problem/Scenarios/Concentrated Loads/Concentrated Load with ID 0/Value"] and A["Problem/Scenarios/Concentrated Loads/Concentrated Load with ID 0/Dof"] == "1" and f(A["Problem/Scenarios/Concentrated Loads/Concentrated Load with ID 0/Value"]) == -1.0 and A["Problem/Scenarios/Concentrated Loads/Concentrated Load with ID 0/Nodes"] == "ns_load" and not any("/Mechanical Natural Boundary Conditions/" in k for k in A),
 "analyze: ns_fix fixed in dispx, dispy, dispz (three displacement conditions, value 0)": [t for t in bc_tuples if t[0]=="ns_fix"] == [("ns_fix","0","Fixed Value","0"),("ns_fix","1","Fixed Value","0"),("ns_fix","2","Fixed Value","0")],
 "analyze: ss_sym fixed in dispz only (value 0)": [t for t in bc_tuples if t[0]=="ss_sym"] == [("ss_sym","2","Fixed Value","0")],
 "analyze: no other essential boundary conditions": len(bc_tuples) == 4,
 "analyze: output dispx dispy dispz": A.get("Problem/Scenarios/Output/Plottable","").replace(" ","") == "{displacement_x,displacement_y,displacement_z}",
 "analyze: physics Mechanical, mesh mesh.exo, 3-D": A.get("Problem/Scenarios/Physics") == "Mechanical" and A.get("Problem/Input Mesh") == "mesh.exo" and A.get("Problem/Spatial Dimension") == "3",
 # section 6 optimization (interface.xml / engine_operations.xml)
 "interface: optimizer OC": "<Package>OC</Package>" in I,
 "interface: max iterations 50": "<MaxIterations>50</MaxIterations>" in I and "<MaxIterations>50</MaxIterations>" in E,
 "interface: OC runtime-default tolerances present (control 1e-4, objective 1e-8, gradient 1e-8)": all(s in I for s in ["<OCControlStagnationTolerance>1e-4<","<OCObjectiveStagnationTolerance>1e-8<","<OCGradientTolerance>1e-8<"]),
 "interface: volume constraint normalized target 0.15 referenced to Design Volume": "<NormalizedTargetValue>0.15</NormalizedTargetValue>" in I and "<ReferenceValueName>Design Volume</ReferenceValueName>" in I,
 "engine: volume constraint evaluated by engine_1 (ComputeVolume)": "Compute Constraint Value 1" in E and re.search(r"<Name>Compute Constraint Value 1</Name>\s*<PerformerName>engine_1</PerformerName>", I) is not None,
 "interface: compliance objective evaluated by analyze_2": re.search(r"<Name>Compute Objective Value</Name>\s*<PerformerName>analyze_2</PerformerName>", I) is not None,
 "engine: weighted-sum aggregator with single weight 1": re.search(r"<Weighting>\s*<Weight>\s*<Value>1</Value>\s*</Weight>\s*</Weighting>", E) is not None and E.count("<Weight>") == 1,
 "engine: normalize_in_aggregator false (no Normals block, no initial criterion value)": "<Normals>" not in E and "Initial Criterion Value" not in I,
 "engine: uniform initial density 0.15, density discretization": re.search(r"<Method>Uniform</Method>\s*<Uniform>\s*<Value>0.15</Value>", E) is not None and "<Discretization>density</Discretization>" in E,
 "engine: update problem frequency 1 and Update Problem stage": "<UpdateProblemFrequency>1</UpdateProblemFrequency>" in E and "<ProblemUpdateFrequency>1</ProblemUpdateFrequency>" in I and "<UpdateProblemStage>" in I,
 "engine: output of control and topology fields": re.search(r"<Function>PlatoMainOutput</Function>.*?<ArgumentName>topology</ArgumentName>.*?<ArgumentName>control</ArgumentName>", E, re.S) is not None,
 "engine: block 1 material 1, mesh mesh.exo, engine_output": "<mesh>mesh.exo</mesh>" in EI and "<file>engine_output</file>" in EI,
 "services: engine, analyze and helmholtz performers, one rank each (mpirun.source -np 1 x3)": M.count("-np 1") == 3 and "PlatoMain engine_input_deck.xml" in M and "analyze_MPMD --input-config=analyze_2_input_deck.xml" in M and "analyze_MPMD --input-config=analyze_helmholtz_input_deck.xml" in M,
 "analyze: visualization output every iteration to analyze_id_2_output": "<OutputFrequency>1</OutputFrequency>" in AO and "<VizDirectory>analyze_id_2_output</VizDirectory>" in AO,
}
rec = dict(utc=datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), directory=os.path.abspath(d), spec="E3-SPC-v1 sections 4-6 (generated-configuration requirement)",
           helmholtz_parameters={k:v for k,v in H.items() if "/Parameters/" in k}, essential_boundary_conditions=bc_sets,
           concentrated_loads={k:v for k,v in A.items() if "/Concentrated Loads/" in k}, material={k:v for k,v in A.items() if "/Material Models/" in k},
           penalty={k:v for k,v in A.items() if "/Penalty Function/" in k}, checks=checks)
rec["result"] = "PASS" if all(checks.values()) else "FAIL"
print(json.dumps(rec, indent=2)); sys.exit(0 if rec["result"] == "PASS" else 1)
