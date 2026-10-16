#!/usr/bin/env python3
"""Verify XMLGenerator output of the run directory against the locked settings of E3-SPC-v1. Writes a JSON record."""
import sys, json, re, math, datetime, os
import xml.etree.ElementTree as ET
rd = sys.argv[1]; out = sys.argv[2]
def P(path): return os.path.join(rd, path)
def plist(path):
    root = ET.parse(P(path)).getroot(); d = {}
    def walk(node, prefix):
        for c in node:
            if c.tag == "Parameter": d[prefix + c.get("name")] = c.get("value")
            elif c.tag == "ParameterList": walk(c, prefix + c.get("name") + "/")
    walk(root, ""); return d
def multi_root(path):  # files with several top-level elements
    return ET.fromstring("<root>" + open(P(path)).read().split("?>", 1)[-1] + "</root>")
h = plist("analyze_helmholtz_input_deck.xml"); a = plist("analyze_2_input_deck.xml")
iface = multi_root("interface.xml"); eops = multi_root("engine_operations.xml"); aops = multi_root("analyze_2_operations.xml")
mp = open(P("mpirun.source")).read()
S = "Scenarios/"
checks = {}
# Helmholtz filter
expected_ls = 0.15 / (2.0 * math.sqrt(3.0))
checks["helmholtz_physics"] = h.get(S+"Physics") == "Helmholtz Filter"
checks["helmholtz_length_scale_present"] = S+"Parameters/Length Scale" in h
checks["helmholtz_length_scale_equals_0.15_over_2sqrt3"] = abs(float(h.get(S+"Parameters/Length Scale", "nan")) - expected_ls) < 1e-5
checks["helmholtz_surface_length_scale_present"] = S+"Parameters/Surface Length Scale" in h
checks["helmholtz_surface_length_scale_1.0"] = float(h.get(S+"Parameters/Surface Length Scale", "nan")) == 1.0
checks["helmholtz_symmetry_plane_sides_present"] = S+"Parameters/Symmetry Plane Sides" in h
checks["helmholtz_symmetry_plane_is_ss_sym"] = h.get(S+"Parameters/Symmetry Plane Sides", "").replace(" ", "") == "{ss_sym}"
checks["helmholtz_mesh"] = h.get("Input Mesh") == "mesh.exo" and h.get("Spatial Dimension") == "3"
checks["helmholtz_domain_block_1"] = h.get(S+"Spatial Model/Domains/block_1/Element Block") == "block_1"
# analyze (mechanical)
checks["analyze_physics_mechanical_linear"] = a.get(S+"Physics") == "Mechanical" and a.get(S+"Residual/Mechanical Residual/Response") == "Linear"
checks["analyze_mesh"] = a.get("Input Mesh") == "mesh.exo" and a.get("Spatial Dimension") == "3"
checks["material_E_1.0"] = float(a.get(S+"Material Models/material_1/Isotropic Linear Elastic/Youngs Modulus", "nan")) == 1.0
checks["material_nu_0.3"] = float(a.get(S+"Material Models/material_1/Isotropic Linear Elastic/Poissons Ratio", "nan")) == 0.3
checks["material_assigned_to_block_1"] = a.get(S+"Spatial Model/Domains/block_1/Element Block") == "block_1" and a.get(S+"Spatial Model/Domains/block_1/Material Model") == "material_1"
for who, base in (("residual", S+"Residual/Mechanical Residual/Penalty Function/"), ("objective_criterion", S+"Criteria/My Objective/Penalty Function/")):
    checks[f"simp_{who}_type_SIMP"] = a.get(base+"Type") == "SIMP"
    checks[f"simp_{who}_exponent_3.0"] = float(a.get(base+"Exponent", "nan")) == 3.0
    checks[f"simp_{who}_minimum_1e-3"] = float(a.get(base+"Minimum Value", "nan")) == 1e-3
checks["single_phase_interpolation"] = a.get(S+"Residual/Mechanical Residual/Material Interpolation Model") == "Single-Phase"
checks["objective_internal_elastic_energy_on_block_1"] = a.get(S+"Criteria/My Objective/Scalar Function Type") == "Internal Elastic Energy" and a.get(S+"Criteria/My Objective/Domains","").replace(" ","") == "{block_1}"
loads = {k: v for k, v in a.items() if k.startswith(S+"Concentrated Loads/")}
load_ids = sorted({k.split("/")[2] for k in loads})
checks["exactly_one_concentrated_load"] = len(load_ids) == 1
if load_ids:
    L = S+"Concentrated Loads/"+load_ids[0]+"/"
    checks["load_on_ns_load"] = a.get(L+"Nodes") == "ns_load"
    checks["load_dof_y"] = a.get(L+"Dof") == "1"
    checks["load_value_-1.0"] = float(a.get(L+"Value", "nan")) == -1.0
checks["no_natural_boundary_conditions"] = not any(k.startswith(S+"Mechanical Natural Boundary Conditions/") for k in a)
checks["no_body_loads"] = not any("Body Load" in k for k in a)
ebc = {}
for k, v in a.items():
    if k.startswith(S+"Essential Boundary Conditions/"):
        name = k.split("/")[2]; ebc.setdefault(name, {})[k.split("/")[3]] = v
fixed = [(b["Sides"], b["Index"], b["Value"], b["Type"]) for b in ebc.values()]
checks["ebc_count_4"] = len(fixed) == 4
checks["ebc_ns_fix_x"] = ("ns_fix", "0", "0", "Fixed Value") in fixed
checks["ebc_ns_fix_y"] = ("ns_fix", "1", "0", "Fixed Value") in fixed
checks["ebc_ns_fix_z"] = ("ns_fix", "2", "0", "Fixed Value") in fixed
checks["ebc_ss_sym_z_only"] = ("ss_sym", "2", "0", "Fixed Value") in fixed and not any(s == "ss_sym" and i != "2" for s, i, _, _ in fixed)
checks["analyze_output_dispx_dispy_dispz"] = a.get(S+"Output/Plottable", "").replace(" ", "") == "{displacement_x,displacement_y,displacement_z}"
# interface / optimizer
opt = iface.find("Optimizer")
checks["optimizer_OC"] = opt.findtext("Package") == "OC"
checks["max_iterations_50"] = opt.findtext("Convergence/MaxIterations") == "50"
checks["oc_default_tolerances"] = (opt.findtext("Options/OCControlStagnationTolerance"), opt.findtext("Options/OCObjectiveStagnationTolerance"), opt.findtext("Options/OCGradientTolerance")) == ("1e-4", "1e-8", "1e-8")
checks["update_problem_frequency_1"] = opt.findtext("Options/ProblemUpdateFrequency") == "1" and opt.find("UpdateProblemStage") is not None
checks["constraint_normalized_target_0.15_vs_design_volume"] = opt.findtext("Constraint/NormalizedTargetValue") == "0.15" and opt.findtext("Constraint/ReferenceValueName") == "Design Volume"
checks["bounds_0_1"] = (opt.findtext("BoundConstraint/Lower"), opt.findtext("BoundConstraint/Upper")) == ("0.0", "1.0")
perf = {p.findtext("Name"): p.findtext("Code") for p in iface.findall("Performer")}
checks["performers_engine_analyze_helmholtz"] = perf == {"engine_1": "engine", "analyze_2": "analyze", "analyze_helmholtz": "analyze"}
stages = {s.findtext("Name"): s for s in iface.findall("Stage")}
cv = stages.get("Compute Constraint Value 1"); checks["volume_constraint_evaluated_by_engine"] = cv is not None and any(o.findtext("Name") == "Compute Constraint Value 1" and o.findtext("PerformerName") == "engine_1" for o in cv.findall("Operation"))
ov = stages.get("Compute Objective Value"); checks["compliance_objective_evaluated_by_analyze"] = ov is not None and any(o.findtext("Name") == "Compute Objective Value" and o.findtext("PerformerName") == "analyze_2" for o in ov.findall("Operation"))
checks["filter_applied_to_control_before_objective"] = ov is not None and any(o.findtext("Name") == "Filter Control" and o.findtext("PerformerName") == "analyze_helmholtz" for o in ov.findall("Operation"))
of = stages.get("Output To File"); checks["engine_outputs_topology_and_control"] = of is not None and any(o.findtext("Name") == "PlatoMainOutput" and {i.findtext("ArgumentName") for i in o.findall("Input")} == {"topology", "control"} for o in of.findall("Operation"))
# engine operations
agg = [o for o in eops.findall("Operation") if o.findtext("Function") == "Aggregator"][0]
checks["weighted_sum_single_weight_1"] = [w.findtext("Value") for w in agg.findall("Weighting/Weight")] == ["1"]
checks["aggregator_no_normalization_element"] = agg.find("Normalize") is None and agg.find("Normalization") is None  # normalize_in_aggregator false
init = [o for o in eops.findall("Operation") if o.findtext("Function") == "InitializeField"][0]
checks["initial_density_uniform_0.15"] = init.findtext("Method") == "Uniform" and float(init.findtext("Uniform/Value")) == 0.15
lb = [o for o in eops.findall("Operation") if o.findtext("Function") == "SetLowerBounds"][0]
checks["discretization_density"] = lb.findtext("Discretization") == "density"
checks["engine_output_max_iterations_50_no_restart"] = any(o.findtext("Function") == "PlatoMainOutput" and o.findtext("MaxIterations") == "50" and o.findtext("WriteRestart") == "false" for o in eops.findall("Operation"))
checks["update_problem_operation_frequency_1"] = any(o.findtext("Function") == "Update Problem" and o.findtext("UpdateProblemFrequency") == "1" for o in eops.findall("Operation"))
checks["analyze_visualization_every_iteration"] = any(o.findtext("Function") == "Visualization" and o.findtext("OutputFrequency") == "1" for o in aops.findall("Operation"))
# mpirun: single rank per performer, no decomposition
nps = re.findall(r"-np\s+(\d+)", mp)
checks["three_performers_one_rank_each"] = nps == ["1", "1", "1"]
checks["no_decomposition_tool_in_launch"] = "decomp" not in mp.lower()
checks["engine_is_PlatoMain_with_engine_input_deck"] = "PlatoMain engine_input_deck.xml" in mp
rec = {"utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "run_directory": os.path.abspath(rd),
       "files": sorted(f for f in os.listdir(rd) if f.endswith(".xml") or f == "mpirun.source"),
       "helmholtz_parameters": {k.split("/")[-1]: v for k, v in h.items() if "/Parameters/" in k},
       "essential_boundary_conditions": ebc, "concentrated_loads": {k.replace(S+"Concentrated Loads/", ""): v for k, v in loads.items()},
       "checks": checks, "result": "PASS" if all(checks.values()) else "FAIL"}
json.dump(rec, open(out, "w"), indent=2); print(json.dumps(rec, indent=2)); sys.exit(0 if rec["result"] == "PASS" else 1)
