"""Verify the XMLGenerator output of the run directory against the locked E3-SPC-v1 settings (§4-§6).
Usage: python3 -I verify_generated_config.py <run_dir> <out.txt>"""
import sys, os, re, json, datetime
import xml.etree.ElementTree as ET
run, out = sys.argv[1], sys.argv[2]
res = {}; ok = True
def chk(key, got, exp):
    global ok
    good = (got == exp); ok &= bool(good); res[key] = {"expected": exp, "actual": got, "pass": bool(good)}
def plist(path):
    return ET.parse(os.path.join(run, path)).getroot()
def params(node):  # name -> value for direct Parameter children
    return {p.get('name'): p.get('value') for p in node.findall('Parameter')}
def sub(node, name):
    for pl in node.iter('ParameterList'):
        if pl.get('name') == name: return pl
    return None
# ---- Helmholtz configuration ----
h = plist('analyze_helmholtz_input_deck.xml')
hp = params(sub(h, 'Parameters'))
chk("helmholtz.physics", params(sub(h,'Scenarios')).get('Physics'), "Helmholtz Filter")
chk("helmholtz.length_scale_present", 'Length Scale' in hp, True)
chk("helmholtz.length_scale_value_(0.15/(2*sqrt(3)))", round(float(hp.get('Length Scale','nan')),6), round(0.15/(2*3**0.5),6))
chk("helmholtz.surface_length_scale_present", 'Surface Length Scale' in hp, True)
chk("helmholtz.surface_length_scale_value_(boundary_sticking_penalty)", float(hp.get('Surface Length Scale','nan')), 1.0)
chk("helmholtz.symmetry_plane_sides_present", 'Symmetry Plane Sides' in hp, True)
chk("helmholtz.symmetry_plane_sides_value", hp.get('Symmetry Plane Sides'), "{ss_sym}")
chk("helmholtz.input_mesh", params(h).get('Input Mesh'), "mesh.exo")
chk("helmholtz.block", params(sub(h,'block_1')).get('Element Block'), "block_1")
# ---- analyze (mechanical) configuration ----
a = plist('analyze_2_input_deck.xml')
chk("analyze.spatial_dimension", params(a).get('Spatial Dimension'), "3")
chk("analyze.input_mesh", params(a).get('Input Mesh'), "mesh.exo")
chk("analyze.physics", params(sub(a,'Scenarios')).get('Physics'), "Mechanical")
mat = params(sub(sub(a,'material_1'),'Isotropic Linear Elastic'))
chk("analyze.material.youngs_modulus", float(mat.get('Youngs Modulus','nan')), 1.0)
chk("analyze.material.poissons_ratio", float(mat.get('Poissons Ratio','nan')), 0.3)
chk("analyze.block_1_material", params(sub(a,'block_1')).get('Material Model'), "material_1")
chk("analyze.domains_count", len(list(sub(a,'Domains'))), 1)
obj = sub(a,'My Objective'); op = params(obj); pen = params(sub(obj,'Penalty Function'))
chk("analyze.objective.type", op.get('Scalar Function Type'), "Internal Elastic Energy")
chk("analyze.objective.simp.type", pen.get('Type'), "SIMP")
chk("analyze.objective.simp.exponent", float(pen.get('Exponent','nan')), 3.0)
chk("analyze.objective.simp.minimum_value_(minimum_ersatz_material_value)", float(pen.get('Minimum Value','nan')), 1e-3)
rp = params(sub(sub(a,'Mechanical Residual'),'Penalty Function')); rr = params(sub(a,'Mechanical Residual'))
chk("analyze.residual.material_interpolation", rr.get('Material Interpolation Model'), "Single-Phase")
chk("analyze.residual.simp.type", rp.get('Type'), "SIMP")
chk("analyze.residual.simp.exponent", float(rp.get('Exponent','nan')), 3.0)
chk("analyze.residual.simp.minimum_value", float(rp.get('Minimum Value','nan')), 1e-3)
loads = [params(l) for l in sub(a,'Concentrated Loads').findall('ParameterList')]
chk("analyze.concentrated_loads_count", len(loads), 1)
chk("analyze.load.nodes", loads[0].get('Nodes'), "ns_load")
chk("analyze.load.dof_(1=y)", loads[0].get('Dof'), "1")
chk("analyze.load.value", float(loads[0].get('Value','nan')), -1.0)
chk("analyze.natural_bcs_(tractions)_count", len(list(sub(a,'Mechanical Natural Boundary Conditions'))), 0)
ebc = [(l.get('name'), params(l)) for l in sub(a,'Essential Boundary Conditions').findall('ParameterList')]
ebcset = sorted((p['Sides'], p['Index'], p['Type'], float(p['Value'])) for n,p in ebc)
chk("analyze.essential_bcs", ebcset, sorted([("ns_fix","0","Fixed Value",0.0),("ns_fix","1","Fixed Value",0.0),("ns_fix","2","Fixed Value",0.0),("ss_sym","2","Fixed Value",0.0)]))
chk("analyze.essential_bc_ns_fix_all_three_dofs", sorted(p['Index'] for n,p in ebc if p['Sides']=='ns_fix'), ["0","1","2"])
chk("analyze.essential_bc_ss_sym_dispz_only", [p['Index'] for n,p in ebc if p['Sides']=='ss_sym'], ["2"])
chk("analyze.output_plottable", params(sub(a,'Output')).get('Plottable'), "{displacement_x, displacement_y, displacement_z}")
# ---- interface.xml (optimizer) ----
txt = open(os.path.join(run,'interface.xml')).read()
iface = ET.fromstring("<root>"+txt.split('?>',1)[1]+"</root>")
opt = iface.find('Optimizer')
chk("interface.optimizer.package", opt.findtext('Package'), "OC")
chk("interface.optimizer.max_iterations", opt.findtext('Convergence/MaxIterations'), "50")
chk("interface.optimizer.problem_update_frequency", opt.findtext('Options/ProblemUpdateFrequency'), "1")
chk("interface.optimizer.update_problem_stage", opt.findtext('UpdateProblemStage/Name'), "Update Problem")
chk("interface.constraint.normalized_target", opt.findtext('Constraint/NormalizedTargetValue'), "0.15")
chk("interface.constraint.reference", opt.findtext('Constraint/ReferenceValueName'), "Design Volume")
chk("interface.performers", [(p.findtext('Name'),p.findtext('Code')) for p in iface.findall('Performer')], [("engine_1","engine"),("analyze_2","analyze"),("analyze_helmholtz","analyze")])
stages = {s.findtext('Name'): s for s in iface.findall('Stage')}
chk("interface.objective_value_stage_performer", [o.findtext('PerformerName') for o in stages['Compute Objective Value'].findall('Operation') if o.findtext('Name')=='Compute Objective Value'], ["analyze_2"])
chk("interface.constraint_value_stage_performer", [o.findtext('PerformerName') for o in stages['Compute Constraint Value 1'].findall('Operation') if o.findtext('Name')=='Compute Constraint Value 1'], ["engine_1"])
chk("interface.filter_applied_in_objective_stage", any(o.findtext('PerformerName')=='analyze_helmholtz' for o in stages['Compute Objective Value'].findall('Operation')), True)
outops = stages['Output To File'].findall('Operation')
chk("interface.engine_output_fields", sorted(i.findtext('ArgumentName') for o in outops if o.findtext('Name')=='PlatoMainOutput' for i in o.findall('Input')), ["control","topology"])
chk("interface.output_stage_has_analyze_visualization", any(o.findtext('Name')=='Visualization' and o.findtext('PerformerName')=='analyze_2' for o in outops), True)
# ---- engine_operations.xml ----
etxt = open(os.path.join(run,'engine_operations.xml')).read()
eops = ET.fromstring("<root>"+etxt.split('?>',1)[1]+"</root>")
ops = {o.findtext('Name'): o for o in eops.findall('Operation')}
chk("engine.initial_density_uniform", ops['Initialize Field'].findtext('Method'), "Uniform")
chk("engine.initial_density_value", float(ops['Initialize Field'].findtext('Uniform/Value')), 0.15)
chk("engine.discretization", ops['Compute Lower Bounds'].findtext('Discretization'), "density")
chk("engine.update_problem_frequency", ops['Update Problem'].findtext('UpdateProblemFrequency'), "1")
chk("engine.volume_constraint_operation_present", 'Compute Constraint Value 1' in ops and ops['Compute Constraint Value 1'].findtext('Function')=='ComputeVolume', True)
agg = ops['Aggregate Data']
chk("engine.aggregator_weights", [w.findtext('Value') for w in agg.findall('Weighting/Weight')], ["1"])
chk("engine.aggregator_normalize_absent_(normalize_in_aggregator false)", agg.find('Weighting/Normals') is None and 'Normal' not in etxt, True)
chk("engine.output_fields", sorted(i.findtext('ArgumentName') for i in ops['PlatoMainOutput'].findall('Input')), ["control","topology"])
chk("engine.output_max_iterations", ops['PlatoMainOutput'].findtext('MaxIterations'), "50")
# ---- engine_input_deck.xml ----
eid = ET.fromstring("<root>"+open(os.path.join(run,'engine_input_deck.xml')).read().split('?>',1)[1]+"</root>")
chk("engine_input.mesh", eid.findtext('mesh/mesh'), "mesh.exo")
chk("engine_input.blocks", [b.findtext('index') for b in eid.findall('mesh/block')], ["1"])
chk("engine_input.output_file", eid.findtext('output/file'), "engine_output")
# ---- mpirun.source ----
m = open(os.path.join(run,'mpirun.source')).read()
nps = re.findall(r'-np\s+(\d+)', m)
chk("mpirun.ranks_per_performer", nps, ["1","1","1"])
chk("mpirun.executables", re.findall(r'\b(PlatoMain|analyze_MPMD)\b', m), ["PlatoMain","analyze_MPMD","analyze_MPMD"])
chk("mpirun.configs", re.findall(r'--input-config=(\S+)', m), ["analyze_2_input_deck.xml","analyze_helmholtz_input_deck.xml"])
chk("mpirun.no_decomposition_(no decomp call)", 'decomp' in m.lower(), False)
# ---- deck vs generated consistency ----
deck = open(os.path.join(run,'input_deck.i')).read()
chk("deck.max_iterations", re.search(r'max_iterations\s+(\d+)', deck).group(1), "50")
chk("deck.sym_bc_location_type_sideset", bool(re.search(r'location_type sideset\s+location_name ss_sym\s+degree_of_freedom dispz\s+value 0', deck)), True)
res["_summary"] = {"run_dir": os.path.abspath(run), "utc": datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'), "all_pass": bool(ok), "checks": len(res)}
with open(out,'w') as f:
    f.write("# Generated-configuration verification record (E3-SPC-v1 §4-§6, generated-configuration requirement) -- work/scripts/verify_generated_config.py\n")
    f.write(json.dumps(res, indent=2)+"\n")
for k,v in res.items():
    if k!="_summary" and not v["pass"]: print("FAIL", k, v)
print("ALL_PASS" if ok else "FAIL", len(res)-1, "checks"); sys.exit(0 if ok else 1)
