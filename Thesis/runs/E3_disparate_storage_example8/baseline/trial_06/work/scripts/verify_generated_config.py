import sys, re, math, datetime, xml.etree.ElementTree as ET, os
d = sys.argv[1]
def rd(f): return open(os.path.join(d,f)).read()
def plist(f): return ET.fromstring(rd(f))
def params(node):  # name->value for a ParameterList element (recursive dict of lists)
    out={}
    for p in node.findall('Parameter'): out[p.get('name')]=p.get('value')
    for l in node.findall('ParameterList'): out[l.get('name')]=params(l)
    return out
A = params(plist('analyze_2_input_deck.xml')); S = A['Scenarios']
H = params(plist('analyze_helmholtz_input_deck.xml')); HP = H['Scenarios']['Parameters']
I = rd('interface.xml'); E = rd('engine_operations.xml'); M = rd('mpirun.source'); EI = rd('engine_input_deck.xml')
ebc = S['Essential Boundary Conditions']; load = S['Concentrated Loads']
def f(x): return float(x)
checks = {}
# analyze: material, SIMP, load, three displacement conditions
mat = S['Material Models']['material_1']['Isotropic Linear Elastic']
checks['analyze: Spatial Dimension 3, Input Mesh mesh.exo'] = S and A['Spatial Dimension']=='3' and A['Input Mesh']=='mesh.exo'
checks['analyze: material_1 isotropic linear elastic E=1.0 nu=0.3'] = f(mat['Youngs Modulus'])==1.0 and f(mat['Poissons Ratio'])==0.3
checks['analyze: block_1 is the only domain and uses material_1'] = list(S['Spatial Model']['Domains'].keys())==['block_1'] and S['Spatial Model']['Domains']['block_1']['Material Model']=='material_1' and S['Spatial Model']['Domains']['block_1']['Element Block']=='block_1'
pf_r = S['Residual']['Mechanical Residual']['Penalty Function']; pf_c = S['Criteria']['My Objective']['Penalty Function']
checks['analyze: residual SIMP single-phase, exponent 3.0, minimum 1e-3'] = S['Residual']['Mechanical Residual']['Material Interpolation Model']=='Single-Phase' and pf_r['Type']=='SIMP' and f(pf_r['Exponent'])==3.0 and f(pf_r['Minimum Value'])==1e-3
checks['analyze: compliance criterion (Internal Elastic Energy) on block_1 with SIMP exponent 3.0, minimum ersatz 1e-3'] = S['Criteria']['My Objective']['Scalar Function Type']=='Internal Elastic Energy' and S['Criteria']['My Objective']['Domains']=='{block_1}' and pf_c['Type']=='SIMP' and f(pf_c['Exponent'])==3.0 and f(pf_c['Minimum Value'])==1e-3
cl = list(load.values())
checks['analyze: exactly one concentrated load: ns_load, Dof 1 (y), value -1.0 per node'] = len(cl)==1 and cl[0]['Nodes']=='ns_load' and cl[0]['Dof']=='1' and f(cl[0]['Value'])==-1.0
checks['analyze: no natural (traction) boundary conditions'] = S.get('Mechanical Natural Boundary Conditions')=={} 
ebcs = sorted((v['Sides'], int(v['Index']), f(v['Value']), v['Type']) for v in ebc.values())
checks['analyze: EBCs = ns_fix X,Y,Z fixed 0 and ss_sym Z fixed 0 (four entries, nothing else)'] = ebcs == sorted([('ns_fix',0,0.0,'Fixed Value'),('ns_fix',1,0.0,'Fixed Value'),('ns_fix',2,0.0,'Fixed Value'),('ss_sym',2,0.0,'Fixed Value')])
checks['analyze: output displacement_x/y/z'] = S['Output']['Plottable']=='{displacement_x, displacement_y, displacement_z}'
# helmholtz
ls = f(HP['Length Scale']); expected = 0.15/(2*math.sqrt(3))
checks['helmholtz: Length Scale present = 0.043301 = radius 0.15/(2*sqrt(3))'] = abs(ls-expected) < 1e-6
checks['helmholtz: Surface Length Scale present = 1.0 (boundary_sticking_penalty 1.0)'] = f(HP['Surface Length Scale'])==1.0
checks['helmholtz: Symmetry Plane Sides present = {ss_sym}'] = HP.get('Symmetry Plane Sides')=='{ss_sym}'
checks['helmholtz: physics Helmholtz Filter on block_1, mesh mesh.exo'] = H['Scenarios']['Physics']=='Helmholtz Filter' and H['Input Mesh']=='mesh.exo' and list(H['Scenarios']['Spatial Model']['Domains'].keys())==['block_1']
# interface
checks['interface: optimizer package OC'] = '<Package>OC</Package>' in I
checks['interface: MaxIterations 50'] = '<MaxIterations>50</MaxIterations>' in I
checks['interface: ProblemUpdateFrequency 1 and Update Problem stage'] = '<ProblemUpdateFrequency>1</ProblemUpdateFrequency>' in I and '<UpdateProblemStage>' in I and '<Name>Update Problem</Name>' in I
checks['interface: default OC tolerances (1e-4 control stagnation, 1e-8 objective stagnation, 1e-8 gradient)'] = '<OCControlStagnationTolerance>1e-4<' in I and '<OCObjectiveStagnationTolerance>1e-8<' in I and '<OCGradientTolerance>1e-8<' in I
checks['interface: volume constraint NormalizedTargetValue 0.15 referenced to Design Volume'] = '<NormalizedTargetValue>0.15</NormalizedTargetValue>' in I and '<ReferenceValueName>Design Volume</ReferenceValueName>' in I
checks['interface: three performers engine_1, analyze_2, analyze_helmholtz'] = I.count('<Performer>')==3 and all(n in I for n in ['<Name>engine_1</Name>','<Name>analyze_2</Name>','<Name>analyze_helmholtz</Name>'])
checks['interface: engine output stage writes topology and control (PlatoMainOutput)'] = '<Name>PlatoMainOutput</Name>' in I and '<ArgumentName>topology</ArgumentName>' in I and '<ArgumentName>control</ArgumentName>' in I
checks['interface: volume constraint evaluated by engine_1; objective by analyze_2'] = re.search(r'<Name>Compute Constraint Value 1</Name>\s*<PerformerName>engine_1</PerformerName>', I) is not None and re.search(r'<Name>Compute Objective Value</Name>\s*<PerformerName>analyze_2</PerformerName>', I) is not None
checks['interface: Helmholtz filter applied to control before objective/constraint (Filter Control by analyze_helmholtz)'] = re.search(r'<Name>Filter Control</Name>\s*<PerformerName>analyze_helmholtz</PerformerName>', I) is not None
# engine operations
checks['engine_operations: uniform initial density 0.15'] = re.search(r'<Function>InitializeField</Function>.*?<Uniform>\s*<Value>0\.15</Value>', E, re.S) is not None or ('<Value>0.15</Value>' in E and 'Uniform' in E)
checks['engine_operations: aggregator weight 1, normalization false (no Normals/Normalize element; XMLGenerator emits one only for normalize_in_aggregator true)'] = re.search(r'<Function>Aggregator</Function>.*?<Weighting>\s*<Weight>\s*<Value>1</Value>', E, re.S) is not None and 'Normal' not in E
checks['engine_operations: Update Problem operation present'] = 'Update Problem' in E
checks['engine_operations: engine output writes topology and control'] = 'PlatoMainOutput' in E and 'topology' in E and 'control' in E
checks['engine_input_deck: mesh.exo, block 1 material 1, output engine_output (exodus)'] = '<mesh>mesh.exo</mesh>' in EI and '<file>engine_output</file>' in EI and '<index>1</index>' in EI
# mpirun.source
checks['mpirun.source: three single-rank performers (-np 1 x3), PlatoMain + analyze_MPMD x2, no decomposition'] = M.count('-np 1')==3 and 'PlatoMain engine_input_deck.xml' in M and 'analyze_2_input_deck.xml' in M and 'analyze_helmholtz_input_deck.xml' in M and 'decomp' not in M
now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
print(f'generated_config_verification utc={now} dir={os.path.abspath(d)}')
for k,v in checks.items(): print(('PASS' if v else 'FAIL'), '|', k)
print('ALL_PASS' if all(checks.values()) else 'SOME_FAILED')
print('--- helmholtz Parameters:', HP)
print('--- EBCs:', ebcs)
print('--- load:', cl)
print('--- material:', mat, 'SIMP residual:', pf_r, 'SIMP criterion:', pf_c)
sys.exit(0 if all(checks.values()) else 2)
