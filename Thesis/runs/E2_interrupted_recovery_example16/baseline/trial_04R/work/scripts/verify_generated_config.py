#!/usr/bin/env python3
"""Verify the XMLGenerator output of a stage against the locked settings of FROZEN-EX16-v1.
Usage: verify_generated_config.py <run_dir> <stage: 1|2>
"""
import sys, os, re, json, math, datetime, hashlib
import xml.etree.ElementTree as ET

run = sys.argv[1]; stage = int(sys.argv[2])
def load(name):
    txt = open(os.path.join(run, name)).read()
    # files contain multiple top-level elements; wrap them
    txt = re.sub(r'<\?xml[^>]*\?>', '', txt)
    return ET.fromstring('<root>' + txt + '</root>')
def sha(name):
    return hashlib.sha256(open(os.path.join(run, name), 'rb').read()).hexdigest()

iface = load('interface.xml'); eng_ops = load('engine_operations.xml'); eng_in = load('engine_input_deck.xml')
an_in = load('analyze_2_input_deck.xml'); an_ops = load('analyze_2_operations.xml')
hh_in = load('analyze_helmholtz_input_deck.xml'); hh_ops = load('analyze_helmholtz_operations.xml')
mpirun = open(os.path.join(run, 'mpirun.source')).read()

def plist_param(root, name):
    out = []
    for p in root.iter('Parameter'):
        if p.get('name') == name: out.append(p.get('value'))
    return out
def text(root, path):
    e = root.find(path); return None if e is None else (e.text or '').strip()

checks = {}
# --- filter (Helmholtz) ---
ls = float(plist_param(hh_in, 'Length Scale')[0]); sls = float(plist_param(hh_in, 'Surface Length Scale')[0])
expected_ls = 0.15/(2*math.sqrt(3.0))
checks['helmholtz physics selected'] = plist_param(hh_in, 'Physics') == ['Helmholtz Filter']
checks['helmholtz Length Scale == 0.15/(2*sqrt(3)) = %.6f (radius 0.15)' % expected_ls] = abs(ls - expected_ls) < 1e-5
checks['helmholtz Surface Length Scale == 1.0 (boundary_sticking_penalty 1.0)'] = abs(sls - 1.0) < 1e-12
checks['helmholtz performer present in interface'] = any((p.findtext('Name') or '') == 'analyze_helmholtz' for p in iface.iter('Performer'))
checks['no symmetry plane in helmholtz deck'] = 'Symmetry' not in open(os.path.join(run,'analyze_helmholtz_input_deck.xml')).read()
# --- material ---
checks['Youngs Modulus == 1.0'] = plist_param(an_in, 'Youngs Modulus') == ['1.0']
checks['Poissons Ratio == 0.3'] = plist_param(an_in, 'Poissons Ratio') == ['0.3']
checks['material model isotropic linear elastic'] = any(pl.get('name') == 'Isotropic Linear Elastic' for pl in an_in.iter('ParameterList'))
checks['material assigned to block_1'] = plist_param(an_in, 'Element Block') == ['block_1']
checks['spatial dimension 3'] = plist_param(an_in, 'Spatial Dimension') == ['3']
checks['physics Mechanical'] = plist_param(an_in, 'Physics') == ['Mechanical']
# --- SIMP ---
pfs = [pl for pl in an_in.iter('ParameterList') if pl.get('name') == 'Penalty Function']
checks['two SIMP penalty functions (criterion + residual)'] = len(pfs) == 2
checks['SIMP type on both'] = all(plist_param(pl, 'Type') == ['SIMP'] for pl in pfs)
checks['SIMP exponent 3.0 on both'] = all(float(plist_param(pl, 'Exponent')[0]) == 3.0 for pl in pfs)
checks['SIMP minimum value 1e-3 on both'] = all(float(plist_param(pl, 'Minimum Value')[0]) == 1e-3 for pl in pfs)
checks['single-phase material interpolation on residual'] = plist_param(an_in, 'Material Interpolation Model') == ['Single-Phase']
checks['objective criterion = compliance (Internal Elastic Energy)'] = plist_param(an_in, 'Scalar Function Type') == ['Internal Elastic Energy']
checks['criterion domain = block_1'] = plist_param(an_in, 'Domains') == ['{block_1}']
# --- load ---
cl = [pl for pl in an_in.iter('ParameterList') if pl.get('name') == 'Concentrated Loads']
loads = list(cl[0]) if cl else []
checks['exactly one concentrated load'] = len(loads) == 1
if loads:
    checks['load Dof == 1 (y)'] = plist_param(loads[0], 'Dof') == ['1']
    checks['load Value == -1.0'] = float(plist_param(loads[0], 'Value')[0]) == -1.0
    checks['load Nodes == ns_load'] = plist_param(loads[0], 'Nodes') == ['ns_load']
nbc = [pl for pl in an_in.iter('ParameterList') if pl.get('name') == 'Mechanical Natural Boundary Conditions']
checks['no tractions (natural BC list empty)'] = bool(nbc) and len(list(nbc[0])) == 0
checks['no body loads'] = 'Body Load' not in open(os.path.join(run,'analyze_2_input_deck.xml')).read()
# --- displacement BCs ---
ebc = [pl for pl in an_in.iter('ParameterList') if pl.get('name') == 'Essential Boundary Conditions'][0]
bcs = list(ebc)
checks['three essential BCs'] = len(bcs) == 3
checks['BC indices 0,1,2 (ux,uy,uz)'] = sorted(plist_param(b, 'Index')[0] for b in bcs) == ['0','1','2']
checks['all BCs on ns_fix'] = all(plist_param(b, 'Sides') == ['ns_fix'] for b in bcs)
checks['all BCs value 0.0, Fixed Value'] = all(float(plist_param(b, 'Value')[0]) == 0.0 and plist_param(b, 'Type') == ['Fixed Value'] for b in bcs)
# --- output ---
checks['analyze output dispx dispy dispz'] = plist_param(an_in, 'Plottable') == ['{displacement_x, displacement_y, displacement_z}']
pmo = [op for op in eng_ops.iter('Operation') if (op.findtext('Function') or '') == 'PlatoMainOutput'][0]
args = sorted((i.findtext('ArgumentName') or '') for i in pmo.findall('Input'))
checks['engine output writes control and topology nodal fields'] = args == ['control', 'topology']
checks['engine output WriteRestart true'] = (pmo.findtext('WriteRestart') or '') == 'true'
checks['engine output OutputFrequency 1 (every iteration)'] = (pmo.findtext('OutputFrequency') or '') == '1'
checks['engine output file name engine_output'] = text(eng_in, './/output/file') == 'engine_output'
checks['analyze visualization OutputFrequency 1'] = any((op.findtext('OutputFrequency') or '') == '1' for op in an_ops.iter('Operation') if (op.findtext('Function') or '') == 'Visualization')
# --- optimizer ---
opt = iface.find('Optimizer')
checks['optimizer package OC'] = (opt.findtext('Package') or '') == 'OC'
max_it = int(opt.find('Convergence').findtext('MaxIterations'))
checks['MaxIterations == %d' % (20 if stage == 1 else 40)] = max_it == (20 if stage == 1 else 40)
checks['engine output MaxIterations consistent'] = (pmo.findtext('MaxIterations') or '') == str(20 if stage == 1 else 40)
checks['ProblemUpdateFrequency 1'] = (opt.find('Options').findtext('ProblemUpdateFrequency') or '') == '1'
checks['UpdateProblemStage wired'] = opt.find('UpdateProblemStage') is not None
upd = [op for op in eng_ops.iter('Operation') if (op.findtext('Function') or '') == 'Update Problem']
checks['engine Update Problem operation, frequency 1'] = len(upd) == 1 and (upd[0].findtext('UpdateProblemFrequency') or '') == '1'
checks['OC default tolerances (1e-4, 1e-8, 1e-8)'] = [opt.find('Options').findtext(k) for k in ('OCControlStagnationTolerance','OCObjectiveStagnationTolerance','OCGradientTolerance')] == ['1e-4','1e-8','1e-8']
checks['bounds [0,1] (density)'] = (opt.find('BoundConstraint').findtext('Lower'), opt.find('BoundConstraint').findtext('Upper')) == ('0.0','1.0')
con = opt.findall('Constraint')
checks['exactly one constraint'] = len(con) == 1
checks['constraint NormalizedTargetValue 0.15 relative to Design Volume'] = con[0].findtext('NormalizedTargetValue') == '0.15' and con[0].findtext('ReferenceValueName') == 'Design Volume'
vol_ops = [op for op in eng_ops.iter('Operation') if (op.findtext('Function') or '') == 'ComputeVolume']
checks['volume constraint evaluated by engine (ComputeVolume ops)'] = len(vol_ops) == 2
checks['constraint value stage performed by engine_1'] = any((st.findtext('Name') or '') == 'Compute Constraint Value 1' and any((o.findtext('PerformerName') or '') == 'engine_1' for o in st.findall('Operation') if (o.findtext('Name') or '') == 'Compute Constraint Value 1') for st in iface.iter('Stage'))
checks['objective value computed by analyze_2'] = any((st.findtext('Name') or '') == 'Compute Objective Value' and any((o.findtext('PerformerName') or '') == 'analyze_2' for o in st.findall('Operation') if (o.findtext('Name') or '') == 'Compute Objective Value') for st in iface.iter('Stage'))
agg = [op for op in eng_ops.iter('Operation') if (op.findtext('Function') or '') == 'Aggregator'][0]
checks['aggregator weight 1, single criterion'] = [w.findtext('Value') for w in agg.find('Weighting').findall('Weight')] == ['1']
checks['aggregator has no normalization element (normalize_in_aggregator false)'] = agg.find('Normalize') is None and 'ormaliz' not in ET.tostring(agg).decode()
checks['filtered variable name Topology, control variable Control'] = (opt.find('OptimizationVariables').findtext('ValueName'), opt.find('OptimizationVariables').findtext('FilteredName')) == ('Control','Topology')
# --- initialization / restart ---
init = [op for op in eng_ops.iter('Operation') if (op.findtext('Function') or '') == 'InitializeField'][0]
if stage == 1:
    checks['initial field Uniform 0.15'] = (init.findtext('Method') or '') == 'Uniform' and float(init.find('Uniform').findtext('Value')) == 0.15
    checks['no restart source in stage 1'] = init.find('FromFieldOnInputMesh') is None and 'FileName' not in ET.tostring(init).decode()
else:
    checks['restart initialization present'] = (init.findtext('Method') or '') != 'Uniform'
    checks['restart field name control'] = 'control' in ET.tostring(init).decode()
    checks['restart Iteration setting 21 (Exodus time step 21 = Stage-1 iteration 20; engine indexes 1-based time steps, established empirically in cancelled attempt 1)'] = init.find('FromFieldOnInputMesh').findtext('Iteration') == '21'
    checks['restart source file restart_input.exo'] = init.find('FromFieldOnInputMesh').findtext('Name') == 'restart_input.exo'
# --- services / performers ---
checks['three performers (engine, analyze, helmholtz)'] = len(list(iface.iter('Performer'))) == 3
checks['mpirun: every performer -np 1 (single rank, no decomposition)'] = re.findall(r'-np (\d+)', mpirun) == ['1','1','1']
checks['mpirun uses PlatoMain and analyze_MPMD'] = 'PlatoMain' in mpirun and mpirun.count('analyze_MPMD') == 2
checks['mesh file mesh.exo in all decks'] = plist_param(an_in, 'Input Mesh') == ['mesh.exo'] and plist_param(hh_in, 'Input Mesh') == ['mesh.exo'] and text(eng_in, './/mesh/mesh') == 'mesh.exo'
checks['engine block 1 -> material 1'] = text(eng_in, './/block/index') == '1' and text(eng_in, './/block/material') == '1'

rec = {'run_dir': run, 'stage': stage, 'verified_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
       'values': {'helmholtz_length_scale': ls, 'helmholtz_surface_length_scale': sls, 'max_iterations': max_it,
                  'engine_output_frequency': pmo.findtext('OutputFrequency'), 'write_restart': pmo.findtext('WriteRestart')},
       'sha256': {f: sha(f) for f in ['input_deck.i','interface.xml','engine_input_deck.xml','engine_operations.xml','analyze_2_input_deck.xml','analyze_2_operations.xml','analyze_helmholtz_input_deck.xml','analyze_helmholtz_operations.xml','mpirun.source','mesh.exo']},
       'checks': checks, 'ALL_CHECKS_PASS': all(checks.values())}
print(json.dumps(rec, indent=2))
sys.exit(0 if rec['ALL_CHECKS_PASS'] else 1)
