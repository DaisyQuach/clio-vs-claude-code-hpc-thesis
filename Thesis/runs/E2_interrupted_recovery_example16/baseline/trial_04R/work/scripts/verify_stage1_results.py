#!/usr/bin/env python3
"""Verify Stage-1 results of FROZEN-EX16-v1: iteration count, stopping message, checkpoint saved states.
Usage: verify_stage1_results.py <run_dir>
"""
import sys, os, re, json, datetime, hashlib
import numpy as np
from netCDF4 import Dataset
import numpy.ma as ma

run = sys.argv[1]
def sha(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()
def s(v):
    out = []
    for c in v:
        if ma.is_masked(c): continue
        out.append(c.decode() if isinstance(c, bytes) else str(c))
    return ''.join(out).strip('\x00').strip()
rec = {'run_dir': run, 'verified_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}
checks = {}
# --- optimizer diagnostics ---
diag = os.path.join(run, 'morphorm_oc_optimizer_diagnostics.txt')
checks['diagnostics file exists'] = os.path.exists(diag)
iters = []; stop_msg = None; rows = []
if os.path.exists(diag):
    for line in open(diag):
        m = re.match(r'^\s*(\d+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)', line)
        if m:
            iters.append(int(m.group(1))); rows.append({'iter': int(m.group(1)), 'fcount': int(m.group(2)), 'objective': float(m.group(3)), 'grad_norm': float(m.group(4)), 'H1': float(m.group(5)), 'abs_dX': float(m.group(6)), 'abs_dF': float(m.group(7))})
        if '******' in line: stop_msg = line.strip()
    rec['diagnostics_sha256'] = sha(diag)
rec['diagnostic_iterations'] = iters
rec['diagnostic_rows'] = rows
rec['stop_message'] = stop_msg
checks['diagnostics cover iterations 0..20'] = iters == list(range(21))
checks['last iteration == 20'] = bool(iters) and iters[-1] == 20
checks['stopping message = maximum number of iterations'] = bool(stop_msg) and 'maximum number of iterations' in stop_msg
# --- checkpoint: engine_output.exo ---
eo = os.path.join(run, 'engine_output.exo')
checks['engine_output.exo exists'] = os.path.exists(eo)
if os.path.exists(eo):
    d = Dataset(eo, 'r')
    nsteps = int(d.dimensions['time_step'].size) if 'time_step' in d.dimensions else 0
    times = [float(t) for t in d.variables['time_whole'][:]] if 'time_whole' in d.variables else []
    nod_names = [s(n) for n in d.variables['name_nod_var'][:]] if 'name_nod_var' in d.variables else []
    rec['engine_output'] = {'sha256': sha(eo), 'num_time_steps': nsteps, 'time_values': times, 'nodal_variables': nod_names,
                            'num_nodes': int(d.dimensions['num_nodes'].size), 'num_elem': int(d.dimensions['num_elem'].size)}
    checks['engine_output has 21 saved states'] = nsteps == 21
    checks['engine_output has control nodal field'] = 'control' in nod_names
    checks['engine_output has topology nodal field'] = 'topology' in nod_names
    checks['engine_output node/elem counts match mesh'] = rec['engine_output']['num_nodes'] == 30625 and rec['engine_output']['num_elem'] == 27648
    # per-state statistics of control and topology
    stats = []
    if 'control' in nod_names and 'topology' in nod_names:
        ic = nod_names.index('control') + 1; it = nod_names.index('topology') + 1
        for k in range(nsteps):
            c = np.array(d.variables[f'vals_nod_var{ic}'][k, :]); t = np.array(d.variables[f'vals_nod_var{it}'][k, :])
            stats.append({'state': k, 'control_min': float(c.min()), 'control_max': float(c.max()), 'control_mean': float(c.mean()),
                          'topology_min': float(t.min()), 'topology_max': float(t.max()), 'topology_mean': float(t.mean())})
        rec['engine_output']['field_stats'] = stats
        checks['state 0 control is uniform 0.15 (initial density)'] = abs(stats[0]['control_min']-0.15) < 1e-12 and abs(stats[0]['control_max']-0.15) < 1e-12
        checks['all states finite'] = all(np.isfinite([v for st in stats for v in st.values()]))
        checks['control field changes between states (not identical copies)'] = len({round(st['control_mean'], 12) for st in stats}) > 1
# --- restart file (if written separately) ---
er = os.path.join(run, 'engine_restart.exo')
rec['engine_restart_exists'] = os.path.exists(er)
if os.path.exists(er):
    d2 = Dataset(er, 'r')
    rec['engine_restart'] = {'sha256': sha(er), 'num_time_steps': int(d2.dimensions['time_step'].size) if 'time_step' in d2.dimensions else 0,
                             'nodal_variables': [s(n) for n in d2.variables['name_nod_var'][:]] if 'name_nod_var' in d2.variables else []}
# --- analyze outputs ---
import glob
cands = sorted(glob.glob(os.path.join(run, 'analyze_id_2_output*')))
vizdir = cands[0] if cands else os.path.join(run, 'analyze_id_2_output')
rec['analyze_output_dir'] = vizdir
rec['analyze_output_dir_exists'] = os.path.isdir(vizdir)
if os.path.isdir(vizdir):
    files = sorted(os.listdir(vizdir)); rec['analyze_output_files'] = files
    it20 = [f for f in files if re.search(r'iteration0*20\.exo$', f)]
    checks['analyze iteration20 output present'] = bool(it20)
    if it20:
        p = os.path.join(vizdir, it20[0]); d3 = Dataset(p, 'r')
        rec['final_analyze_output'] = {'file': it20[0], 'sha256': sha(p), 'nodal_variables': [s(n) for n in d3.variables['name_nod_var'][:]] if 'name_nod_var' in d3.variables else [],
                                       'num_time_steps': int(d3.dimensions['time_step'].size) if 'time_step' in d3.dimensions else 0}
        nv = rec['final_analyze_output']['nodal_variables']
        checks['final analyze output has displacement fields'] = any('disp' in n.lower() for n in nv)
hist = os.path.join(run, 'opt_criteria_history.csv')
if os.path.exists(hist):
    rec['opt_criteria_history'] = open(hist).read().strip().splitlines()
rec['checks'] = checks; rec['ALL_CHECKS_PASS'] = all(checks.values())
print(json.dumps(rec, indent=2))
sys.exit(0 if rec['ALL_CHECKS_PASS'] else 1)
