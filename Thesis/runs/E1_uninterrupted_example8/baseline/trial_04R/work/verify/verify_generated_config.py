#!/usr/bin/env python3
"""Verify the XMLGenerator output of FROZEN-EX8-v1 against every locked runtime setting."""
import sys, json, re, math, datetime, os
import xml.etree.ElementTree as ET
run = sys.argv[1]
def rd(f): return open(os.path.join(run, f)).read()
def multi_root(f):  # Plato files have multiple root elements
    return ET.fromstring("<root>" + re.sub(r'<\?xml[^>]*\?>', '', rd(f)) + "</root>")
def plist_params(root):
    """Return list of (path, name, value) from a Teuchos ParameterList tree."""
    out = []
    def walk(node, path):
        for ch in node:
            if ch.tag == 'ParameterList': walk(ch, path + '/' + ch.get('name'))
            elif ch.tag == 'Parameter': out.append((path, ch.get('name'), ch.get('value')))
    walk(root, root.get('name', '')); return out

hz = plist_params(ET.fromstring(rd('analyze_helmholtz_input_deck.xml')))
an = plist_params(ET.fromstring(rd('analyze_2_input_deck.xml')))
itf = multi_root('interface.xml'); eng = multi_root('engine_operations.xml'); anop = multi_root('analyze_2_operations.xml')
mpir = rd('mpirun.source'); deck = rd('input_deck.i')
def get(params, name, path_sub=''):
    return [v for p, n, v in params if n == name and path_sub in p]
def f(x): return float(x)
C = {}
# ---- Helmholtz generated configuration (spec section 6, generated-configuration requirement)
ls = get(hz, 'Length Scale'); sls = get(hz, 'Surface Length Scale'); sym = get(hz, 'Symmetry Plane Sides')
C['helmholtz: Physics == Helmholtz Filter'] = get(hz, 'Physics') == ['Helmholtz Filter']
C['helmholtz: filter Length Scale present'] = len(ls) == 1
C['helmholtz: Length Scale == 0.15/(2*sqrt(3)) = 0.043301 (absolute radius 0.15)'] = len(ls)==1 and abs(f(ls[0]) - 0.15/(2*math.sqrt(3))) < 1e-5
C['helmholtz: Surface Length Scale (boundary sticking) present == 1.0'] = sls == ['1.0'] or (len(sls)==1 and f(sls[0])==1.0)
C['helmholtz: Symmetry Plane Sides present == {ss_sym}'] = len(sym)==1 and sym[0].replace(' ','') == '{ss_sym}'
C['helmholtz: domain block_1, mesh mesh.exo'] = get(hz,'Element Block')==['block_1'] and get(hz,'Input Mesh')==['mesh.exo']
# ---- analyze generated configuration
C['analyze: Physics Mechanical, 3-D, mesh.exo'] = get(an,'Physics')==['Mechanical'] and get(an,'Spatial Dimension')==['3'] and get(an,'Input Mesh')==['mesh.exo']
C['analyze: material isotropic linear elastic E=1.0 nu=0.3 (material_1)'] = get(an,'Youngs Modulus','Isotropic Linear Elastic')==['1.0'] and get(an,'Poissons Ratio','Isotropic Linear Elastic')==['0.3']
C['analyze: block_1 -> material_1'] = get(an,'Element Block','Domains/block_1')==['block_1'] and get(an,'Material Model','Domains/block_1')==['material_1']
C['analyze: residual SIMP exponent 3.0, minimum 1e-3, Single-Phase'] = get(an,'Type','Residual')==['SIMP'] and [f(v) for v in get(an,'Exponent','Residual')]==[3.0] and [f(v) for v in get(an,'Minimum Value','Residual')]==[1e-3] and get(an,'Material Interpolation Model')==['Single-Phase']
C['analyze: compliance criterion (Internal Elastic Energy) SIMP exponent 3.0, minimum ersatz 1e-3'] = get(an,'Scalar Function Type')==['Internal Elastic Energy'] and get(an,'Type','Criteria/My Objective/Penalty Function')==['SIMP'] and [f(v) for v in get(an,'Exponent','Criteria')]==[3.0] and [f(v) for v in get(an,'Minimum Value','Criteria')]==[1e-3]
cl = [(p,n,v) for p,n,v in an if 'Concentrated Loads' in p]
C['analyze: exactly one concentrated load: ns_load, Dof 1 (y), value -1.0'] = len({p for p,_,_ in cl})==1 and get(an,'Nodes','Concentrated Loads')==['ns_load'] and get(an,'Dof','Concentrated Loads')==['1'] and [f(v) for v in get(an,'Value','Concentrated Loads')]==[-1.0]
C['analyze: no tractions / natural BCs'] = not [p for p,_,_ in an if 'Natural Boundary Conditions' in p]
ebc = {}
for p,n,v in an:
    if 'Essential Boundary Conditions/' in p:
        ebc.setdefault(p.split('Essential Boundary Conditions/')[1], {})[n] = v
ebc_set = {(d['Sides'], d['Index'], d['Type'], f(d['Value'])) for d in ebc.values()}
C['analyze: essential BCs = ns_fix x,y,z fixed 0 and ss_sym z fixed 0 (4 entries)'] = ebc_set == {('ns_fix','0','Fixed Value',0.0),('ns_fix','1','Fixed Value',0.0),('ns_fix','2','Fixed Value',0.0),('ss_sym','2','Fixed Value',0.0)} and len(ebc)==4
C['analyze: output displacement_x/y/z'] = get(an,'Plottable') and set(get(an,'Plottable')[0].strip('{}').replace(' ','').split(',')) == {'displacement_x','displacement_y','displacement_z'}
# ---- interface.xml (engine / optimizer)
opt = itf.find('Optimizer')
C['interface: Optimizer Package OC'] = opt.findtext('Package') == 'OC'
C['interface: MaxIterations 50'] = opt.findtext('Convergence/MaxIterations') == '50'
C['interface: OC default tolerances (1e-4 control, 1e-8 objective, 1e-8 gradient)'] = (opt.findtext('Options/OCControlStagnationTolerance'),opt.findtext('Options/OCObjectiveStagnationTolerance'),opt.findtext('Options/OCGradientTolerance'))==('1e-4','1e-8','1e-8')
C['interface: ProblemUpdateFrequency 1 and Update Problem stage wired'] = opt.findtext('Options/ProblemUpdateFrequency')=='1' and opt.findtext('UpdateProblemStage/Name')=='Update Problem' and any(s.findtext('Name')=='Update Problem' for s in itf.findall('Stage'))
C['interface: single constraint, NormalizedTargetValue 0.15 referenced to Design Volume'] = len(opt.findall('Constraint'))==1 and opt.findtext('Constraint/NormalizedTargetValue')=='0.15' and opt.findtext('Constraint/ReferenceValueName')=='Design Volume'
C['interface: constraint value computed by engine_1 (ComputeVolume)'] = any(s.findtext('Name')=='Compute Constraint Value 1' and any(o.findtext('Name')=='Compute Constraint Value 1' and o.findtext('PerformerName')=='engine_1' for o in s.findall('Operation')) for s in itf.findall('Stage'))
C['interface: objective value computed by analyze_2, aggregated in engine'] = any(s.findtext('Name')=='Compute Objective Value' and any(o.findtext('Name')=='Compute Objective Value' and o.findtext('PerformerName')=='analyze_2' for o in s.findall('Operation')) for s in itf.findall('Stage'))
C['interface: filter applied by analyze_helmholtz performer (Filter Control / Filter Gradient)'] = any(o.findtext('PerformerName')=='analyze_helmholtz' and o.findtext('Name')=='Filter Control' for s in itf.findall('Stage') for o in s.findall('Operation')) and any(o.findtext('PerformerName')=='analyze_helmholtz' and o.findtext('Name')=='Filter Gradient' for s in itf.findall('Stage') for o in s.findall('Operation'))
C['interface: three performers engine_1, analyze_2, analyze_helmholtz'] = [p.findtext('Name') for p in itf.findall('Performer')]==['engine_1','analyze_2','analyze_helmholtz']
C['interface: engine output stage writes topology and control'] = any(s.findtext('Name')=='Output To File' and {i.findtext('ArgumentName') for o in s.findall('Operation') if o.findtext('Name')=='PlatoMainOutput' for i in o.findall('Input')}=={'topology','control'} for s in itf.findall('Stage'))
C['interface: bound constraint [0,1]'] = (opt.findtext('BoundConstraint/Lower'),opt.findtext('BoundConstraint/Upper'))==('0.0','1.0')
# ---- engine_operations.xml
init = [o for o in eng.findall('Operation') if o.findtext('Function')=='InitializeField'][0]
C['engine ops: uniform initial density 0.15'] = init.findtext('Method')=='Uniform' and f(init.findtext('Uniform/Value'))==0.15
C['engine ops: discretization density'] = all(o.findtext('Discretization')=='density' for o in eng.findall('Operation') if o.findtext('Function') in ('SetLowerBounds','SetUpperBounds'))
agg = [o for o in eng.findall('Operation') if o.findtext('Function')=='Aggregator'][0]
C['engine ops: aggregator single weight 1, no normalization element (normalize_in_aggregator false)'] = [w.findtext('Value') for w in agg.findall('Weighting/Weight')]==['1'] and agg.find('Weighting/Normals') is None and 'Normali' not in ET.tostring(agg).decode()
C['engine ops: Update Problem frequency 1'] = any(o.findtext('Function')=='Update Problem' and o.findtext('UpdateProblemFrequency')=='1' for o in eng.findall('Operation'))
C['engine ops: PlatoMainOutput MaxIterations 50 with topology+control inputs'] = any(o.findtext('Function')=='PlatoMainOutput' and o.findtext('MaxIterations')=='50' and {i.findtext('ArgumentName') for i in o.findall('Input')}=={'topology','control'} for o in eng.findall('Operation'))
C['engine ops: volume criterion with linear (exponent 1) SIMP'] = all(o.findtext('SIMP/PenaltyExponent')=='1.0' for o in eng.findall('Operation') if o.findtext('Function')=='ComputeVolume')
# ---- analyze operations / mpirun
C['analyze ops: Visualization every iteration (OutputFrequency 1)'] = any(o.findtext('Function')=='Visualization' and o.findtext('OutputFrequency')=='1' for o in anop.findall('Operation'))
C['mpirun.source: every performer -np 1 (single-rank, no decomposition)'] = re.findall(r'-np\s+(\d+)', mpir)==['1','1','1']
C['mpirun.source: PlatoMain + analyze_MPMD(analyze_2) + analyze_MPMD(helmholtz)'] = 'PlatoMain engine_input_deck.xml' in mpir and 'analyze_2_input_deck.xml' in mpir and 'analyze_helmholtz_input_deck.xml' in mpir
C['mesh in run dir identical to verified mesh (sha256)'] = __import__('hashlib').sha256(open(os.path.join(run,'mesh.exo'),'rb').read()).hexdigest() == __import__('hashlib').sha256(open(sys.argv[2],'rb').read()).hexdigest()
rec = {'run_dir': run, 'verified_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
       'helmholtz_parameters': {n: v for p,n,v in hz if 'Parameters' in p},
       'analyze_essential_bcs': ebc, 'analyze_concentrated_loads': {n: v for p,n,v in cl},
       'checks': {k: bool(v) for k,v in C.items()}, 'ALL_CHECKS_PASS': all(C.values())}
print(json.dumps(rec, indent=2)); sys.exit(0 if rec['ALL_CHECKS_PASS'] else 1)
