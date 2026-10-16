#!/usr/bin/env python3
"""Verify the XMLGenerator output of frozen workflow EX8 against every locked setting.
Usage: python3 -I verify_generated_config.py <run_dir>
Exit 0 only if every check passes."""
import sys, os, json, re, datetime, math
import xml.etree.ElementTree as ET

run = sys.argv[1]
checks = []
def check(name, actual, expected):
    ok = (actual == expected)
    checks.append({"check": name, "expected": expected, "actual": actual, "pass": bool(ok), })
    return ok
def near(a, b, tol=1e-6):
    return abs(float(a) - float(b)) <= tol

def plist_params(root):
    """Return dict path -> value for all <Parameter> in a Teuchos ParameterList xml."""
    out = {}
    def walk(node, path):
        for ch in node:
            if ch.tag == 'ParameterList':
                walk(ch, path + [ch.get('name')])
            elif ch.tag == 'Parameter':
                out['/'.join(path + [ch.get('name')])] = (ch.get('type'), ch.get('value'))
    walk(root, [root.get('name')])
    return out

# ---------------- Helmholtz filter configuration ----------------
hf = os.path.join(run, 'analyze_helmholtz_input_deck.xml')
check("helmholtz_input_deck_exists", os.path.exists(hf), True)
hp = plist_params(ET.parse(hf).getroot())
check("helmholtz_physics", hp.get('Problem/Scenarios/Physics', (None, None))[1], 'Helmholtz Filter')
check("helmholtz_mesh", hp.get('Problem/Input Mesh', (None, None))[1], 'mesh.exo')
check("helmholtz_dimension", hp.get('Problem/Spatial Dimension', (None, None))[1], '3')
ls = hp.get('Problem/Scenarios/Parameters/Length Scale', (None, None))[1]
check("helmholtz_length_scale_present", ls is not None, True)
# radius 0.15 -> length scale = R / (2*sqrt(3)) = 0.0433013 (written with 6 decimals by the generator)
check("helmholtz_length_scale_equals_0.15/(2*sqrt(3))", bool(ls is not None and near(ls, 0.15 / (2 * math.sqrt(3)), 1e-6)), True)
checks.append({"check": "helmholtz_length_scale_value(info)", "expected": 0.15 / (2 * math.sqrt(3)), "actual": ls, "pass": True})
sls = hp.get('Problem/Scenarios/Parameters/Surface Length Scale', (None, None))[1]
check("helmholtz_surface_length_scale_present", sls is not None, True)
check("helmholtz_surface_length_scale_(boundary_sticking_penalty)=1.0", bool(sls is not None and near(sls, 1.0)), True)
sym = hp.get('Problem/Scenarios/Parameters/Symmetry Plane Sides', (None, None))[1]
check("helmholtz_symmetry_plane_sides_present", sym is not None, True)
check("helmholtz_symmetry_plane_sides", sym, '{ss_sym}')
check("helmholtz_domain_block", hp.get('Problem/Scenarios/Spatial Model/Domains/block_1/Element Block', (None, None))[1], 'block_1')

# ---------------- Analyze (mechanical) configuration ----------------
af = os.path.join(run, 'analyze_2_input_deck.xml')
check("analyze_input_deck_exists", os.path.exists(af), True)
aroot = ET.parse(af).getroot()
ap = plist_params(aroot)
check("analyze_physics", ap.get('Problem/Scenarios/Physics', (None, None))[1], 'Mechanical')
check("analyze_pde", ap.get('Problem/Scenarios/PDE Constraint', (None, None))[1], 'Elliptic')
check("analyze_dimension", ap.get('Problem/Spatial Dimension', (None, None))[1], '3')
check("analyze_mesh", ap.get('Problem/Input Mesh', (None, None))[1], 'mesh.exo')
# material
E = ap.get('Problem/Scenarios/Material Models/material_1/Isotropic Linear Elastic/Youngs Modulus', (None, None))[1]
nu = ap.get('Problem/Scenarios/Material Models/material_1/Isotropic Linear Elastic/Poissons Ratio', (None, None))[1]
check("material_isotropic_linear_elastic_E=1.0", bool(E is not None and near(E, 1.0)), True)
check("material_nu=0.3", bool(nu is not None and near(nu, 0.3)), True)
check("material_assigned_to_block_1", ap.get('Problem/Scenarios/Spatial Model/Domains/block_1/Material Model', (None, None))[1], 'material_1')
check("single_domain_block_1", [k.split('/')[4] for k in ap if k.startswith('Problem/Scenarios/Spatial Model/Domains/') and k.endswith('/Element Block')], ['block_1'])
# SIMP in residual
check("residual_interpolation_single_phase", ap.get('Problem/Scenarios/Residual/Mechanical Residual/Material Interpolation Model', (None, None))[1], 'Single-Phase')
check("residual_response_linear", ap.get('Problem/Scenarios/Residual/Mechanical Residual/Response', (None, None))[1], 'Linear')
check("residual_penalty_type_SIMP", ap.get('Problem/Scenarios/Residual/Mechanical Residual/Penalty Function/Type', (None, None))[1], 'SIMP')
pe = ap.get('Problem/Scenarios/Residual/Mechanical Residual/Penalty Function/Exponent', (None, None))[1]
mv = ap.get('Problem/Scenarios/Residual/Mechanical Residual/Penalty Function/Minimum Value', (None, None))[1]
check("residual_SIMP_exponent=3.0", bool(pe is not None and near(pe, 3.0)), True)
check("residual_SIMP_minimum_value=1e-3", bool(mv is not None and near(mv, 1e-3, 1e-12)), True)
# compliance criterion
crit = sorted(set(k.split('/')[3] for k in ap if k.startswith('Problem/Scenarios/Criteria/') and k.count('/') == 4 and k.endswith('/Type')))
check("single_analyze_criterion", len(crit), 1)
cname = crit[0] if crit else None
check("criterion_scalar_function", ap.get(f'Problem/Scenarios/Criteria/{cname}/Type', (None, None))[1], 'Scalar Function')
check("criterion_type_compliance(Internal Elastic Energy)", ap.get(f'Problem/Scenarios/Criteria/{cname}/Scalar Function Type', (None, None))[1], 'Internal Elastic Energy')
check("criterion_domains_block_1", ap.get(f'Problem/Scenarios/Criteria/{cname}/Domains', (None, None))[1], '{block_1}')
check("criterion_penalty_SIMP", ap.get(f'Problem/Scenarios/Criteria/{cname}/Penalty Function/Type', (None, None))[1], 'SIMP')
cpe = ap.get(f'Problem/Scenarios/Criteria/{cname}/Penalty Function/Exponent', (None, None))[1]
cmv = ap.get(f'Problem/Scenarios/Criteria/{cname}/Penalty Function/Minimum Value', (None, None))[1]
check("criterion_SIMP_exponent=3.0", bool(cpe is not None and near(cpe, 3.0)), True)
check("criterion_minimum_ersatz_material_value=1e-3", bool(cmv is not None and near(cmv, 1e-3, 1e-12)), True)
# loads
loads = sorted(set(k.split('/')[3] for k in ap if k.startswith('Problem/Scenarios/Concentrated Loads/')))
check("exactly_one_concentrated_load", len(loads), 1)
if loads:
    L = loads[0]
    check("load_nodeset_ns_load", ap.get(f'Problem/Scenarios/Concentrated Loads/{L}/Nodes', (None, None))[1], 'ns_load')
    check("load_dof_y(index 1)", ap.get(f'Problem/Scenarios/Concentrated Loads/{L}/Dof', (None, None))[1], '1')
    lv = ap.get(f'Problem/Scenarios/Concentrated Loads/{L}/Value', (None, None))[1]
    check("load_value_-1.0_per_node", bool(lv is not None and near(lv, -1.0)), True)
nbc = [k for k in ap if k.startswith('Problem/Scenarios/Mechanical Natural Boundary Conditions/')]
check("no_tractions_or_pressures", len(nbc), 0)
# essential BCs
ebc_names = sorted(set(k.split('/')[3] for k in ap if k.startswith('Problem/Scenarios/Essential Boundary Conditions/')))
ebcs = []
for n in ebc_names:
    g = lambda key: ap.get(f'Problem/Scenarios/Essential Boundary Conditions/{n}/{key}', (None, None))[1]
    ebcs.append((g('Sides'), g('Index'), g('Type'), g('Value')))
ebcs_sorted = sorted(ebcs)
check("essential_bcs_(sides,index,type,value)", ebcs_sorted, sorted([
    ('ns_fix', '0', 'Fixed Value', '0.0'), ('ns_fix', '1', 'Fixed Value', '0.0'), ('ns_fix', '2', 'Fixed Value', '0.0'),
    ('ss_sym', '2', 'Fixed Value', '0.0')]))
check("ns_fix_ux_uy_uz_fixed", sorted(i for s, i, t, v in ebcs if s == 'ns_fix'), ['0', '1', '2'])
check("ss_sym_uz_fixed_only", [i for s, i, t, v in ebcs if s == 'ss_sym'], ['2'])
# output
check("analyze_output_displacements", ap.get('Problem/Scenarios/Output/Plottable', (None, None))[1], '{displacement_x, displacement_y, displacement_z}')
# linear solver (informational)
checks.append({"check": "linear_solver_package(info)", "expected": None, "actual": ap.get('Problem/Scenarios/Linear Solver/Solver Options/Solver Package', (None, None))[1], "pass": True})

# ---------------- Interface / optimizer ----------------
itf = os.path.join(run, 'interface.xml')
check("interface_exists", os.path.exists(itf), True)
itxt = open(itf).read()
iroot = ET.fromstring('<root>' + itxt.split('?>', 1)[1] + '</root>')
performers = [(p.findtext('Name'), p.findtext('Code'), p.findtext('PerformerID')) for p in iroot.findall('Performer')]
check("performers_engine_analyze_helmholtz", performers, [('engine_1', 'engine', '0'), ('analyze_2', 'analyze', '1'), ('analyze_helmholtz', 'analyze', '2')])
opt = iroot.find('Optimizer')
check("optimizer_package_OC", opt.findtext('Package'), 'OC')
check("optimizer_max_iterations_50", opt.findtext('Convergence/MaxIterations'), '50')
check("optimizer_update_problem_frequency_1", opt.findtext('Options/ProblemUpdateFrequency'), '1')
check("optimizer_update_problem_stage_present", opt.findtext('UpdateProblemStage/Name'), 'Update Problem')
checks.append({"check": "oc_default_tolerances(info)", "expected": None, "actual": {c.tag: c.text for c in opt.find('Options')}, "pass": True})
check("constraint_normalized_target_0.15", opt.findtext('Constraint/NormalizedTargetValue'), '0.15')
check("constraint_reference_design_volume", opt.findtext('Constraint/ReferenceValueName'), 'Design Volume')
check("single_constraint", len(opt.findall('Constraint')), 1)
check("bounds_0_1", (opt.findtext('BoundConstraint/Lower'), opt.findtext('BoundConstraint/Upper')), ('0.0', '1.0'))
check("filtered_variable_name_Topology", opt.findtext('OptimizationVariables/FilteredName'), 'Topology')
# constraint stage evaluated by engine, objective stage by analyze
stages = {s.findtext('Name'): s for s in iroot.findall('Stage')}
cv = stages.get('Compute Constraint Value 1')
check("constraint_value_computed_by_engine", [o.findtext('PerformerName') for o in cv.findall('Operation') if o.findtext('Name') == 'Compute Constraint Value 1'] if cv is not None else None, ['engine_1'])
ov = stages.get('Compute Objective Value')
check("objective_value_computed_by_analyze", [o.findtext('PerformerName') for o in ov.findall('Operation') if o.findtext('Name') == 'Compute Objective Value'] if ov is not None else None, ['analyze_2'])
check("objective_filtered_by_helmholtz_performer", [o.findtext('PerformerName') for o in ov.findall('Operation') if o.findtext('Name') == 'Filter Control'] if ov is not None else None, ['analyze_helmholtz'])
out_stage = stages.get('Output To File')
check("engine_output_control_and_topology", sorted(i.findtext('ArgumentName') for o in out_stage.findall('Operation') if o.findtext('Name') == 'PlatoMainOutput' for i in o.findall('Input')) if out_stage is not None else None, ['control', 'topology'])

# ---------------- Engine operations ----------------
ef = os.path.join(run, 'engine_operations.xml')
etxt = open(ef).read()
eroot = ET.fromstring('<root>' + etxt.split('?>', 1)[1] + '</root>')
ops = {o.findtext('Name'): o for o in eroot.findall('Operation')}
check("engine_initialize_uniform", ops['Initialize Field'].findtext('Method'), 'Uniform')
check("engine_initial_density_0.15", ops['Initialize Field'].findtext('Uniform/Value'), '0.15')
check("engine_update_problem_frequency_1", ops['Update Problem'].findtext('UpdateProblemFrequency'), '1')
check("engine_output_max_iterations_50", ops['PlatoMainOutput'].findtext('MaxIterations'), '50')
check("engine_discretization_density", ops['Compute Lower Bounds'].findtext('Discretization'), 'density')
check("aggregator_single_weight_1", [w.findtext('Value') for w in ops['Aggregate Data'].findall('Weighting/Weight')], ['1'])
check("aggregator_no_normalization_element", ops['Aggregate Data'].find('Normalize') is None, True)
check("engine_volume_constraint_linear(SIMP exponent 1, min 0)", (ops['Compute Constraint Value 1'].findtext('SIMP/PenaltyExponent'), ops['Compute Constraint Value 1'].findtext('SIMP/MinimumValue')), ('1.0', '0.0'))
checks.append({"check": "engine_PlatoMainOutput_OutputFrequency(info)", "expected": None, "actual": ops['PlatoMainOutput'].findtext('OutputFrequency'), "pass": True})

# ---------------- Engine input deck / mpirun.source ----------------
eng_in = open(os.path.join(run, 'engine_input_deck.xml')).read()
check("engine_mesh_file", re.search(r'<mesh>(mesh\.exo)</mesh>', eng_in) is not None, True)
check("engine_output_file_engine_output", '<file>engine_output</file>' in eng_in, True)
mp = open(os.path.join(run, 'mpirun.source')).read()
nps = re.findall(r'-np\s+(\d+)', mp)
check("mpirun_single_rank_per_performer", nps, ['1', '1', '1'])
check("mpirun_executables", (('PlatoMain engine_input_deck.xml' in mp), mp.count('analyze_MPMD')), (True, 2))
check("mpirun_no_decomposition", ('decomp' in mp.lower()), False)
check("analyze_viz_output_frequency_1", re.search(r'<OutputFrequency>(\d+)</OutputFrequency>', open(os.path.join(run, 'analyze_2_operations.xml')).read()).group(1), '1')

all_pass = all(c["pass"] for c in checks)
print(json.dumps({"trial_id": "E1-example8-baseline-02", "frozen_configuration_id": "FROZEN-EX8-v1", "run_dir": os.path.abspath(run),
                  "verification_utc": datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                  "checks": checks, "all_checks_pass": all_pass}, indent=2, default=str))
sys.exit(0 if all_pass else 1)
