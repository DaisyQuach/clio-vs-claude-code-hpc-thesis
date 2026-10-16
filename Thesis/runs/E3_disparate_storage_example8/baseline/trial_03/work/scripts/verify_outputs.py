"""Verify the Morphorm run outputs of E3-SPC-v1: iteration count, final analyze output fields, engine output fields,
and that the locked boundary conditions are realized in the final displacement field. Usage: python3 -I verify_outputs.py <run_dir> <out.txt>"""
import sys, os, json, re, datetime
import numpy as np, netCDF4
run, out = sys.argv[1], sys.argv[2]; res = {}; ok = True
def chk(k, got, exp):
    global ok
    good = (got == exp); ok &= bool(good); res[k] = {"expected": exp, "actual": got, "pass": bool(good)}
def names(d, var):
    v = d.variables[var]; v.set_auto_mask(False)
    return [b''.join(bytes(c) for c in row).decode(errors='ignore').strip('\x00').strip() for row in v[:]]
diag = open(os.path.join(run,'morphorm_oc_optimizer_diagnostics.txt')).read()
rows = [l for l in diag.splitlines() if re.match(r'^\s*\d+\s+\d+\s', l)]
chk("diagnostics.iteration_rows_(0..50)", len(rows), 51)
chk("diagnostics.last_iteration", int(rows[-1].split()[0]), 50)
chk("diagnostics.stop_message_max_iterations", "exceeding maximum number of iterations" in diag, True)
chk("diagnostics.no_early_convergence_message", bool(re.search(r'stagnation|converged', diag, re.I)), False)
hist = open(os.path.join(run,'opt_criteria_history.csv')).read().strip()
vals = [v for v in hist.split(',')[1:] if v.strip()]
chk("opt_criteria_history.objective_values_(51)", len(vals), 51)
chk("opt_criteria_history.objective_decreased", float(vals[-1]) < float(vals[0]), True)
f50 = os.path.join(run,'analyze_id_2_output_scenario_id_1','iteration50.exo')
chk("final_analyze_output.exists", os.path.isfile(f50), True)
d = netCDF4.Dataset(f50)
nv = names(d,'name_nod_var') if 'name_nod_var' in d.variables else []
ev = names(d,'name_elem_var') if 'name_elem_var' in d.variables else []
res["final_analyze_output.nodal_vars"] = {"actual": nv, "pass": True}; res["final_analyze_output.elem_vars"] = {"actual": ev, "pass": True}
norm = lambda n: n.lower().replace(' ','_')
lowers = [norm(n) for n in nv+ev]
chk("final_analyze_output.has_displacement_x_y_z", all(any(k in n for n in lowers) for k in ("displacement_x","displacement_y","displacement_z")), True)
chk("final_analyze_output.has_density_or_topology_field", any(('topolog' in n) or ('densit' in n) or ('control' in n) for n in lowers), True)
chk("final_analyze_output.num_nodes", int(d.dimensions['num_nodes'].size), 15925)
chk("final_analyze_output.num_elem", int(d.dimensions['num_elem'].size), 13824)
x = d.variables['coordx'][:]; y = d.variables['coordy'][:]; z = d.variables['coordz'][:]
def nodal(name):
    i = [k for k,n in enumerate(nv) if norm(n)==name][0]+1; v = d.variables['vals_nod_var%d'%i]; return np.array(v[-1,:])
ux, uy, uz = nodal('displacement_x'), nodal('displacement_y'), nodal('displacement_z')
sym = np.abs(z-0.5) < 1e-6; fix = np.abs(x) < 1e-6; ld = (np.abs(x-2.0)<1e-6)&(np.abs(y)<1e-6)
chk("bc.ns_fix_all_displacements_zero", bool(max(np.abs(ux[fix]).max(), np.abs(uy[fix]).max(), np.abs(uz[fix]).max()) < 1e-12), True)
chk("bc.ss_sym_uz_zero_on_cut_plane_(1225 nodes)", bool(np.abs(uz[sym]).max() < 1e-12), True)
res["bc.ss_sym_node_count"] = {"actual": int(sym.sum()), "expected": 1225, "pass": int(sym.sum())==1225}; ok &= int(sym.sum())==1225
res["bc.max_abs_uz_off_plane"] = {"actual": float(np.abs(uz[~sym & ~fix]).max()), "pass": True}
res["bc.ns_load_mean_uy_(negative=loaded downward)"] = {"actual": float(uy[ld].mean()), "pass": bool(uy[ld].mean() < 0)}; ok &= bool(uy[ld].mean() < 0)
e = netCDF4.Dataset(os.path.join(run,'engine_output.exo'))
env = names(e,'name_nod_var') if 'name_nod_var' in e.variables else []
chk("engine_output.nodal_fields_control_and_topology", sorted(n.lower() for n in env), ["control","topology"])
nt = int(e.dimensions['time_step'].size) if 'time_step' in e.dimensions else 0
res["engine_output.time_steps"] = {"actual": nt, "pass": nt >= 1}; ok &= nt >= 1
tv = e.variables['time_whole'][:] if 'time_whole' in e.variables else []
res["engine_output.time_values"] = {"actual": [float(t) for t in tv], "pass": True}
chk("engine_output.num_nodes", int(e.dimensions['num_nodes'].size), 15925)
ti = [k for k,n in enumerate(env) if n.lower()=='topology'][0]+1
topo = np.array(e.variables['vals_nod_var%d'%ti][-1,:]); res["engine_output.final_topology_range"] = {"actual": [float(topo.min()), float(topo.max())], "pass": True}
res["engine_output.final_topology_mean"] = {"actual": float(topo.mean()), "pass": True}
res["_summary"] = {"run_dir": os.path.abspath(run), "utc": datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), "all_pass": bool(ok)}
with open(out,'w') as f:
    f.write("# Run-output verification record (E3-SPC-v1 §6 iterations/outputs, §5 BCs realized) -- work/scripts/verify_outputs.py\n"); f.write(json.dumps(res, indent=2)+"\n")
for k,v in res.items():
    if not v.get("pass",True): print("FAIL",k,v)
print(json.dumps({k:v for k,v in res.items() if 'actual' in v and k.startswith(('engine_output','bc.','final_analyze_output.nodal','final_analyze_output.elem'))}, indent=1))
print("ALL_PASS" if ok else "FAIL"); sys.exit(0 if ok else 1)
