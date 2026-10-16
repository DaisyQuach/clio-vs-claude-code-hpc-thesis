"""Verify the XMLGenerator output of the accepted run against the locked FROZEN-EX8-v1 settings."""
import sys, os, re, json, math, datetime, hashlib
import xml.etree.ElementTree as ET
run = sys.argv[1]
def rd(f): return open(os.path.join(run,f)).read()
def params(xml_text):
    """flatten Teuchos ParameterList to {path: value}"""
    root = ET.fromstring(xml_text); out={}
    def walk(node, path):
        for ch in node:
            if ch.tag=='ParameterList': walk(ch, path+'/'+ch.get('name'))
            elif ch.tag=='Parameter': out[path+'/'+ch.get('name')] = ch.get('value')
    walk(root, root.get('name')); return out
hz = params(rd('analyze_helmholtz_input_deck.xml'))
an = params(rd('analyze_2_input_deck.xml'))
iface = rd('interface.xml'); eng_ops = rd('engine_operations.xml'); eng_in = rd('engine_input_deck.xml'); mpi = rd('mpirun.source'); an_ops = rd('analyze_2_operations.xml')
R = 0.15; expected_ls = R/(2*math.sqrt(3))
checks = {}
# --- Helmholtz filter (generated) ---
ls = float(hz.get('Problem/Scenarios/Parameters/Length Scale','nan'))
checks['helmholtz: physics = Helmholtz Filter'] = hz.get('Problem/Scenarios/Physics')=='Helmholtz Filter'
checks['helmholtz: Length Scale present and == 0.15/(2*sqrt(3)) = %.6f'%expected_ls] = abs(ls-expected_ls)<1e-6
checks['helmholtz: Surface Length Scale (boundary sticking) present and == 1.0'] = float(hz.get('Problem/Scenarios/Parameters/Surface Length Scale','nan'))==1.0
checks['helmholtz: Symmetry Plane Sides present and == {ss_sym}'] = hz.get('Problem/Scenarios/Parameters/Symmetry Plane Sides','').replace(' ','')=='{ss_sym}'
checks['helmholtz: mesh = mesh.exo, dim 3, domain block_1'] = hz.get('Problem/Input Mesh')=='mesh.exo' and hz.get('Problem/Spatial Dimension')=='3' and hz.get('Problem/Scenarios/Spatial Model/Domains/block_1/Element Block')=='block_1'
# --- analyze (mechanical) ---
checks['analyze: physics Mechanical, Elliptic, dim 3, mesh.exo'] = an.get('Problem/Scenarios/Physics')=='Mechanical' and an.get('Problem/Scenarios/PDE Constraint')=='Elliptic' and an.get('Problem/Spatial Dimension')=='3' and an.get('Problem/Input Mesh')=='mesh.exo'
checks['analyze: material_1 isotropic linear elastic E=1.0 nu=0.3 on block_1'] = float(an.get('Problem/Scenarios/Material Models/material_1/Isotropic Linear Elastic/Youngs Modulus','nan'))==1.0 and float(an.get('Problem/Scenarios/Material Models/material_1/Isotropic Linear Elastic/Poissons Ratio','nan'))==0.3 and an.get('Problem/Scenarios/Spatial Model/Domains/block_1/Material Model')=='material_1' and an.get('Problem/Scenarios/Spatial Model/Domains/block_1/Element Block')=='block_1'
checks['analyze: residual SIMP single-phase, exponent 3.0, min 1e-3'] = an.get('Problem/Scenarios/Residual/Mechanical Residual/Material Interpolation Model')=='Single-Phase' and an.get('Problem/Scenarios/Residual/Mechanical Residual/Penalty Function/Type')=='SIMP' and float(an.get('Problem/Scenarios/Residual/Mechanical Residual/Penalty Function/Exponent','nan'))==3.0 and float(an.get('Problem/Scenarios/Residual/Mechanical Residual/Penalty Function/Minimum Value','nan'))==1e-3
checks['analyze: compliance criterion (Internal Elastic Energy) SIMP exponent 3.0, min ersatz 1e-3, domain block_1'] = an.get('Problem/Scenarios/Criteria/My Objective/Scalar Function Type')=='Internal Elastic Energy' and an.get('Problem/Scenarios/Criteria/My Objective/Penalty Function/Type')=='SIMP' and float(an.get('Problem/Scenarios/Criteria/My Objective/Penalty Function/Exponent','nan'))==3.0 and float(an.get('Problem/Scenarios/Criteria/My Objective/Penalty Function/Minimum Value','nan'))==1e-3 and an.get('Problem/Scenarios/Criteria/My Objective/Domains','').replace(' ','')=='{block_1}'
cl = {k:v for k,v in an.items() if '/Concentrated Loads/' in k}
checks['analyze: exactly one concentrated load: ns_load, Dof 1 (y), value -1.0'] = len({k.split('/')[-2] for k in cl})==1 and an.get('Problem/Scenarios/Concentrated Loads/Concentrated Load with ID 0/Dof')=='1' and float(an.get('Problem/Scenarios/Concentrated Loads/Concentrated Load with ID 0/Value','nan'))==-1.0 and an.get('Problem/Scenarios/Concentrated Loads/Concentrated Load with ID 0/Nodes')=='ns_load'
checks['analyze: no natural (traction) boundary conditions'] = not any('/Mechanical Natural Boundary Conditions/' in k for k in an)
ebc = {}
for k,v in an.items():
    m = re.match(r'Problem/Scenarios/Essential Boundary Conditions/([^/]+)/(.+)', k)
    if m: ebc.setdefault(m.group(1),{})[m.group(2)] = v
bcset = {(d['Sides'], d['Index'], d['Type'], float(d['Value'])) for d in ebc.values()}
checks['analyze: essential BCs == {ns_fix x,y,z = 0} U {ss_sym z = 0}, all Fixed Value'] = bcset == {('ns_fix','0','Fixed Value',0.0),('ns_fix','1','Fixed Value',0.0),('ns_fix','2','Fixed Value',0.0),('ss_sym','2','Fixed Value',0.0)} and len(ebc)==4
checks['analyze: output plottable displacement_x,y,z'] = an.get('Problem/Scenarios/Output/Plottable','').replace(' ','')=='{displacement_x,displacement_y,displacement_z}'
checks['analyze ops: visualization every iteration into analyze_id_2_output'] = '<OutputFrequency>1</OutputFrequency>' in an_ops and '<VizDirectory>analyze_id_2_output</VizDirectory>' in an_ops
# --- interface / optimizer ---
checks['interface: optimizer package OC'] = '<Package>OC</Package>' in iface
checks['interface: MaxIterations 50'] = '<MaxIterations>50</MaxIterations>' in iface
checks['interface: OC default tolerances (1e-4 control, 1e-8 objective, 1e-8 gradient)'] = all(s in iface for s in ['<OCControlStagnationTolerance>1e-4<','<OCObjectiveStagnationTolerance>1e-8<','<OCGradientTolerance>1e-8<'])
checks['interface: volume constraint NormalizedTargetValue 0.15 relative to Design Volume'] = '<NormalizedTargetValue>0.15</NormalizedTargetValue>' in iface and '<ReferenceValueName>Design Volume</ReferenceValueName>' in iface
checks['interface: exactly one constraint'] = iface.count('<Constraint>')==1
checks['interface: constraint value computed by engine_1 (ComputeVolume)'] = re.search(r'<Name>Compute Constraint Value 1</Name>\s*<PerformerName>engine_1</PerformerName>', iface) is not None and '<Function>ComputeVolume</Function>' in eng_ops
checks['interface: objective value computed by analyze_2'] = re.search(r'<Name>Compute Objective Value</Name>\s*<PerformerName>analyze_2</PerformerName>', iface) is not None
checks['interface: update problem stage present, ProblemUpdateFrequency 1'] = '<UpdateProblemStage>' in iface and '<ProblemUpdateFrequency>1</ProblemUpdateFrequency>' in iface and '<UpdateProblemFrequency>1</UpdateProblemFrequency>' in eng_ops
checks['interface: performers engine_1, analyze_2, analyze_helmholtz (3 performers)'] = iface.count('<Performer>')==3 and all(f'<Name>{n}</Name>' in iface for n in ['engine_1','analyze_2','analyze_helmholtz'])
checks['interface: Helmholtz filter applied to Control in every value/gradient stage'] = iface.count('<Name>Filter Control</Name>')==4 and iface.count('<Name>Filter Gradient</Name>')==2
checks['interface: engine output stage writes topology and control'] = re.search(r'<Name>PlatoMainOutput</Name>.*?<ArgumentName>topology</ArgumentName>.*?<ArgumentName>control</ArgumentName>', iface, re.S) is not None
checks['interface: bounds 0..1'] = '<Upper>1.0</Upper>' in iface and '<Lower>0.0</Lower>' in iface
# --- engine ---
checks['engine ops: uniform initial density 0.15'] = re.search(r'<Method>Uniform</Method>\s*<Uniform>\s*<Value>0.15</Value>', eng_ops) is not None
checks['engine ops: density discretization'] = '<Discretization>density</Discretization>' in eng_ops
checks['engine ops: aggregator weight 1, no normalization'] = re.search(r'<Weight>\s*<Value>1</Value>', eng_ops) is not None and 'Normaliz' not in eng_ops
checks['engine ops: output max iterations 50'] = '<MaxIterations>50</MaxIterations>' in eng_ops
checks['engine input: mesh.exo, block 1, engine_output exodus'] = '<mesh>mesh.exo</mesh>' in eng_in and '<file>engine_output</file>' in eng_in
# --- mpirun.source ---
checks['mpirun: three performers, -np 1 each (single rank; no decomposition)'] = mpi.count('-np 1')==3 and '-np 2' not in mpi and 'decomp' not in mpi.lower()
checks['mpirun: PlatoMain + analyze_MPMD x2 with the generated files'] = 'PlatoMain engine_input_deck.xml' in mpi and 'analyze_MPMD --input-config=analyze_2_input_deck.xml' in mpi and 'analyze_MPMD --input-config=analyze_helmholtz_input_deck.xml' in mpi
files = sorted(f for f in os.listdir(run) if f.endswith('.xml') or f=='mpirun.source' or f=='input_deck.i' or f=='mesh.exo')
rec = {'run_dir': run, 'utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
       'files_sha256': {f: hashlib.sha256(open(os.path.join(run,f),'rb').read()).hexdigest() for f in files},
       'helmholtz_generated_parameters': {k.split('/')[-1]: v for k,v in hz.items() if '/Parameters/' in k},
       'checks': checks, 'ALL_CHECKS_PASS': all(checks.values())}
print(json.dumps(rec, indent=2)); sys.exit(0 if rec['ALL_CHECKS_PASS'] else 1)
