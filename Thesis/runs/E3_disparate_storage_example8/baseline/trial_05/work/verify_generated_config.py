import sys, re, os, datetime, hashlib
d=sys.argv[1]
def rd(f): return open(os.path.join(d,f)).read()
H=rd('analyze_helmholtz_input_deck.xml'); A=rd('analyze_2_input_deck.xml'); I=rd('interface.xml'); E=rd('engine_operations.xml'); M=rd('mpirun.source'); EI=rd('engine_input_deck.xml')
def has(txt,pat): return re.search(pat,txt,re.S) is not None
chk=[]
def c(name,ok,where): chk.append((name,bool(ok),where))
# Helmholtz filter
c('helmholtz: filter length scale present (0.15 -> 0.043301 = R/(2*sqrt(3)))', has(H,r'name="Length Scale".*?value="0\.043301"'), 'analyze_helmholtz_input_deck.xml')
c('helmholtz: surface (boundary-sticking) length scale 1.0 present', has(H,r'name="Surface Length Scale".*?value="1\.0"'), 'analyze_helmholtz_input_deck.xml')
c('helmholtz: symmetry plane sideset ss_sym present', has(H,r'name="Symmetry Plane Sides".*?value="\{ss_sym\}"'), 'analyze_helmholtz_input_deck.xml')
c('helmholtz: mesh.exo, dimension 3, block_1', has(H,r'"Input Mesh".*?"mesh.exo"') and has(H,r'"Spatial Dimension".*?value="3"') and has(H,r'"Element Block".*?"block_1"'), 'analyze_helmholtz_input_deck.xml')
# analyze
c('analyze: isotropic linear elastic E=1.0 nu=0.3 on material_1', has(A,r'Isotropic Linear Elastic.*?"Youngs Modulus".*?value="1\.0".*?"Poissons Ratio".*?value="0\.3"'), 'analyze_2_input_deck.xml')
c('analyze: block_1 -> material_1 (only domain)', has(A,r'<ParameterList name="block_1">.*?"Material Model".*?"material_1"') and A.count('<Parameter name="Element Block"')==1, 'analyze_2_input_deck.xml')
c('analyze: residual SIMP single-phase exponent 3.0 minimum 1e-3', has(A,r'Mechanical Residual.*?Single-Phase.*?"Type".*?"SIMP".*?"Exponent".*?value="3\.0".*?"Minimum Value".*?value="1e-3"'), 'analyze_2_input_deck.xml')
c('analyze: compliance criterion (Internal Elastic Energy) SIMP exponent 3.0 minimum ersatz 1e-3', has(A,r'My Objective.*?Internal Elastic Energy.*?"SIMP".*?"Exponent".*?value="3\.0".*?"Minimum Value".*?value="1e-3"'), 'analyze_2_input_deck.xml')
c('analyze: concentrated load ns_load, dof 1 (y), value -1.0; exactly one load', has(A,r'Concentrated Load.*?"Dof".*?value="1".*?"Value".*?value="-1\.0".*?"Nodes".*?"ns_load"') and A.count('Concentrated Load with ID')==1, 'analyze_2_input_deck.xml')
c('analyze: no tractions / natural BCs, no body forces', has(A,r'<ParameterList name="Mechanical Natural Boundary Conditions" />') and 'Body Load' not in A, 'analyze_2_input_deck.xml')
for idx,nm in ((0,'X'),(1,'Y'),(2,'Z')):
    c(f'analyze: ns_fix displacement {nm} fixed 0', has(A,rf'"Displacement {nm} with ID \d+">.*?"Fixed Value".*?"Index".*?value="{idx}".*?"Sides".*?"ns_fix".*?"Value".*?value="0"'), 'analyze_2_input_deck.xml')
c('analyze: ss_sym displacement Z fixed 0 (symmetry)', has(A,r'"Displacement Z with ID \d+">.*?"Fixed Value".*?"Index".*?value="2".*?"Sides".*?"ss_sym".*?"Value".*?value="0"'), 'analyze_2_input_deck.xml')
c('analyze: exactly 4 essential BC entries', A.count('"Fixed Value"')==4, 'analyze_2_input_deck.xml')
c('analyze: output displacement_x,y,z', has(A,r'Plottable.*?\{displacement_x, displacement_y, displacement_z\}'), 'analyze_2_input_deck.xml')
c('analyze: mesh.exo, dimension 3', has(A,r'"Input Mesh".*?"mesh.exo"') and has(A,r'"Spatial Dimension".*?value="3"'), 'analyze_2_input_deck.xml')
# interface / optimizer
c('optimizer OC, MaxIterations 50', has(I,r'<Package>OC</Package>') and has(I,r'<MaxIterations>50</MaxIterations>'), 'interface.xml')
c('OC default tolerances (1e-4 control stagnation, 1e-8 objective stagnation, 1e-8 gradient)', has(I,r'<OCControlStagnationTolerance>1e-4<') and has(I,r'<OCObjectiveStagnationTolerance>1e-8<') and has(I,r'<OCGradientTolerance>1e-8<'), 'interface.xml')
c('update problem stage, frequency 1', has(I,r'<ProblemUpdateFrequency>1<') and has(I,r'<UpdateProblemStage>\s*<Name>Update Problem</Name>') and has(E,r'<UpdateProblemFrequency>1</UpdateProblemFrequency>'), 'interface.xml / engine_operations.xml')
c('volume constraint normalized target 0.15 (less_than), evaluated by engine_1', has(I,r'<NormalizedTargetValue>0\.15</NormalizedTargetValue>') and has(I,r'<Name>Compute Constraint Value 1</Name>.*?<PerformerName>engine_1</PerformerName>'), 'interface.xml')
c('objective: single compliance criterion weight 1 aggregated (weighted sum) from analyze_2', has(E,r'<Weighting>\s*<Weight>\s*<Value>1</Value>') and E.count('<Weight>')==1 and has(I,r'<Name>Compute Objective Value</Name>.*?<PerformerName>analyze_2</PerformerName>'), 'interface.xml / engine_operations.xml')
c('normalize_in_aggregator false (no Normalize element in Aggregator)', 'Normalize' not in E, 'engine_operations.xml')
c('density discretization, uniform initial density 0.15', has(E,r'<Method>Uniform</Method>\s*<Uniform>\s*<Value>0\.15</Value>') and has(E,r'<Discretization>density</Discretization>'), 'engine_operations.xml')
c('engine output of topology and control fields', has(I,r'<Name>PlatoMainOutput</Name>.*?<ArgumentName>topology</ArgumentName>.*?<ArgumentName>control</ArgumentName>'), 'interface.xml')
c('engine output file engine_output (exodus), mesh.exo', has(EI,r'<file>engine_output</file>') and has(EI,r'<mesh>mesh.exo</mesh>'), 'engine_input_deck.xml')
c('three performers: engine_1, analyze_2, analyze_helmholtz', all(x in I for x in ('<Name>engine_1</Name>','<Name>analyze_2</Name>','<Name>analyze_helmholtz</Name>')), 'interface.xml')
c('mpirun.source: every performer -np 1 (single rank), no decomposition', M.count('-np 1')==3 and '-np ' not in M.replace('-np 1','') , 'mpirun.source')
c('no restart file written / no initial guess file', has(E,r'<WriteRestart>false</WriteRestart>') and 'initialguess' not in I+E, 'engine_operations.xml')
now=datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
print(f'# Generated-configuration verification (E3-SPC-v1), utc {now}\n# directory: {d}')
for f in sorted(os.listdir(d)):
    if f.endswith('.xml') or f=='mpirun.source' or f=='input_deck.i':
        print(f'# sha256 {hashlib.sha256(open(os.path.join(d,f),"rb").read()).hexdigest()}  {f}')
allok=True
for n,ok,w in chk:
    print(f'[{"PASS" if ok else "FAIL"}] {n}  ({w})'); allok&=ok
print('ALL_CHECKS_PASS' if allok else 'SOME_CHECKS_FAILED'); sys.exit(0 if allok else 1)
