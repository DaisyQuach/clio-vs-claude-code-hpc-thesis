"""Verify the accepted optimization run reached 50 iterations and produced the required fields."""
import sys, os, re, json, datetime, hashlib, numpy as np, netCDF4
run = sys.argv[1]
def names(ds,var):
    out=[]
    for row in ds.variables[var][:]:
        if np.ma.is_masked(row): row=row.filled(b'')
        out.append(b''.join(x for x in row.tolist() if x not in (b'',b'\x00')).decode())
    return out
diag = open(os.path.join(run,'morphorm_oc_optimizer_diagnostics.txt')).read()
rows = [l.split() for l in diag.splitlines() if re.match(r'^\s*\d+\s+\d+\s', l)]
iters = [int(r[0]) for r in rows]
stop = [l.strip() for l in diag.splitlines() if 'Optimization stopping' in l]
rec = {'run_dir': run, 'utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
rec['diagnostics_rows'] = len(rows); rec['first_iter'] = iters[0]; rec['last_iter'] = iters[-1]
rec['stopping_message'] = stop[0] if stop else None
rec['final_objective_F'] = float(rows[-1][2]); rec['final_constraint_H1'] = float(rows[-1][4])
mesh = netCDF4.Dataset(os.path.join(run,'mesh.exo'))
x=mesh.variables['coordx'][:]; y=mesh.variables['coordy'][:]; z=mesh.variables['coordz'][:]
ns = {}
nsn = names(mesh,'ns_names')
for i,n in enumerate(nsn): ns[n] = mesh.variables[f'node_ns{i+1}'][:]-1
f50 = os.path.join(run,'analyze_id_2_output_scenario_id_1','iteration50.exo')
ds = netCDF4.Dataset(f50)
nv = names(ds,'name_nod_var'); ev = names(ds,'name_elem_var') if 'name_elem_var' in ds.variables else []
t = ds.variables['time_whole'][:]
fld = {n: ds.variables[f'vals_nod_var{i+1}'][-1,:] for i,n in enumerate(nv)}
rec['final_analyze_file'] = f50; rec['final_analyze_nodal_vars'] = nv; rec['final_analyze_elem_vars'] = ev; rec['final_analyze_time'] = float(t[-1])
dz = fld['displacement Z']; dx = fld['displacement X']; dy = fld['displacement Y']
sym = np.abs(z-0.5)<1e-9
rec['max_abs_dispZ_on_symmetry_plane'] = float(np.abs(dz[sym]).max())
rec['max_abs_disp_on_ns_fix'] = float(max(np.abs(dx[ns['ns_fix']]).max(), np.abs(dy[ns['ns_fix']]).max(), np.abs(dz[ns['ns_fix']]).max()))
rec['max_abs_dispZ_overall'] = float(np.abs(dz).max())
rec['min_dispY_overall'] = float(dy.min()); rec['dispY_at_ns_load_mean'] = float(dy[ns['ns_load']].mean())
# element-volume-weighted volume fraction of the filtered topology (uniform hexes -> nodal average per element)
c = mesh.variables['connect1'][:]-1
topo = fld['Topology']; vf = float(np.mean(topo[c].mean(axis=1)))
rec['volume_fraction_from_topology_iter50'] = vf
eng = netCDF4.Dataset(os.path.join(run,'engine_output.exo'))
rec['engine_output_time_steps'] = int(len(eng.variables['time_whole'][:])); rec['engine_output_nodal_vars'] = names(eng,'name_nod_var')
checks = {
 'diagnostics: iterations 0..50 present (51 rows), last iteration == 50': iters == list(range(51)),
 'diagnostics: stop reason is maximum number of iterations (no early convergence)': stop and 'maximum number of iterations' in stop[0],
 'final analyze output = iteration50.exo exists with Topology + displacement X/Y/Z': set(['Topology','displacement X','displacement Y','displacement Z']).issubset(nv),
 'final analyze output time step == 50': float(t[-1])==50.0,
 'symmetry BC honoured: |u_z| on z=0.5 nodes == 0': rec['max_abs_dispZ_on_symmetry_plane'] < 1e-12,
 'fixed BC honoured: |u| on ns_fix == 0': rec['max_abs_disp_on_ns_fix'] < 1e-12,
 'load direction consistent: u_y at ns_load negative': rec['dispY_at_ns_load_mean'] < 0,
 'volume constraint active/feasible: |H1| < 1e-6 and volume fraction ~ 0.15 (within 2%)': abs(rec['final_constraint_H1'])<1e-6 and abs(vf-0.15)<0.003,
 'engine_output.exo has control and topology, >= 50 time steps': set(['control','topology'])==set(rec['engine_output_nodal_vars']) and rec['engine_output_time_steps']>=50,
}
rec['checks']=checks; rec['ALL_CHECKS_PASS']=all(bool(v) for v in checks.values())
print(json.dumps(rec, indent=2)); sys.exit(0 if rec['ALL_CHECKS_PASS'] else 1)
