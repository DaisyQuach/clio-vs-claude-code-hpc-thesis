#!/usr/bin/env python3
"""Continuation evidence for FROZEN-EX16-v1 (spec section 7): compare Stage-2's first evaluated compliance with Stage-1's
compliance at iteration 20, and compare the Stage-2 initial 'control' field (engine_output state 0) with the saved Stage-1 states.
Usage: continuation_evidence.py <stage1_run_dir> <stage2_run_dir>   (works on a partially written Stage-2 run too)
"""
import sys, os, re, json, datetime, hashlib
import numpy as np
from netCDF4 import Dataset
import numpy.ma as ma
import xml.etree.ElementTree as ET

s1, s2 = sys.argv[1], sys.argv[2]
def sha(p): return hashlib.sha256(open(p,'rb').read()).hexdigest()
def s(v):
    out = []
    for c in v:
        if ma.is_masked(c): continue
        out.append(c.decode() if isinstance(c, bytes) else str(c))
    return ''.join(out).strip('\x00').strip()
def diag(path):
    rows = []; stop = None
    if not os.path.exists(path): return rows, stop
    for line in open(path):
        m = re.match(r'^\s*(\d+)\s+(\d+)\s+(\S+)\s+(\S+)\s+(\S+)', line)
        if m: rows.append({'iter': int(m.group(1)), 'fcount': int(m.group(2)), 'objective_text': m.group(3), 'objective': float(m.group(3)), 'H1': float(m.group(5))})
        if '******' in line: stop = line.strip()
    return rows, stop
def hist(path):
    if not os.path.exists(path): return []
    txt = open(path).read().strip()
    vals = [v.strip() for v in txt.split(',')[1:] if v.strip()]
    return vals
rec = {'verified_utc': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'), 'stage1_run_dir': s1, 'stage2_run_dir': s2}
checks = {}
# restart settings actually in the Stage-2 generated configuration
ops = open(os.path.join(s2, 'engine_operations.xml')).read()
root = ET.fromstring('<root>' + re.sub(r'<\?xml[^>]*\?>', '', ops) + '</root>')
init = [op for op in root.iter('Operation') if (op.findtext('Function') or '') == 'InitializeField'][0]
ff = init.find('FromFieldOnInputMesh')
rec['stage2_restart_settings'] = {'method': init.findtext('Method'), 'file': ff.findtext('Name') if ff is not None else None,
                                  'field': ff.findtext('VariableName') if ff is not None else None, 'iteration_setting': ff.findtext('Iteration') if ff is not None else None}
checks['restart method FromFieldOnInputMesh'] = rec['stage2_restart_settings']['method'] == 'FromFieldOnInputMesh'
checks['restart field is control'] = rec['stage2_restart_settings']['field'] == 'control'
# checkpoint identity
ck = os.path.join(s1, 'engine_output.exo'); ri = os.path.join(s2, rec['stage2_restart_settings']['file'] or 'restart_input.exo')
rec['checkpoint'] = {'stage1_engine_output': ck, 'sha256': sha(ck), 'stage2_restart_input': ri, 'restart_input_sha256': sha(ri) if os.path.exists(ri) else None}
checks['restart_input.exo is byte-identical to Stage-1 checkpoint'] = rec['checkpoint']['sha256'] == rec['checkpoint']['restart_input_sha256']
# compliance comparison
r1, stop1 = diag(os.path.join(s1, 'morphorm_oc_optimizer_diagnostics.txt'))
r2, stop2 = diag(os.path.join(s2, 'morphorm_oc_optimizer_diagnostics.txt'))
h1 = hist(os.path.join(s1, 'opt_criteria_history.csv')); h2 = hist(os.path.join(s2, 'opt_criteria_history.csv'))
rec['stage1_last_iteration'] = r1[-1]['iter'] if r1 else None
rec['stage1_compliance_iter20_diagnostics'] = next((r['objective_text'] for r in r1 if r['iter'] == 20), None)
rec['stage1_compliance_iter20_history_csv'] = h1[20] if len(h1) > 20 else None
rec['stage2_first_compliance_diagnostics'] = r2[0]['objective_text'] if r2 else None
rec['stage2_first_compliance_history_csv'] = h2[0] if h2 else None
rec['stage2_iterations_so_far'] = [r['iter'] for r in r2]
rec['stage2_stop_message'] = stop2
if r2:
    f2 = r2[0]['objective']
    matches = [r['iter'] for r in r1 if r['objective_text'] == r2[0]['objective_text']]
    rec['stage1_iterations_whose_diagnostic_compliance_equals_stage2_first'] = matches
    checks['Stage-2 first compliance (diagnostics) == Stage-1 iteration-20 compliance'] = matches == [20]
    if h1 and h2:
        matches_h = [i for i, v in enumerate(h1) if v == h2[0]]
        rec['stage1_iterations_whose_history_csv_compliance_equals_stage2_first'] = matches_h
        rel = abs(float(h2[0]) - float(h1[20])) / abs(float(h1[20])) if len(h1) > 20 else None
        rec['relative_difference_history_csv_stage2_first_vs_stage1_iter20'] = rel
        checks['Stage-2 first compliance (criteria history, full precision) == Stage-1 iteration-20 compliance'] = (len(h1) > 20 and h2[0] == h1[20])
# saved-field comparison: Stage-2 engine_output state 0 'control' vs Stage-1 saved states
eo2 = os.path.join(s2, 'engine_output.exo')
if os.path.exists(eo2) and os.path.exists(ri):
    try:
        d1 = Dataset(ri, 'r'); d2 = Dataset(eo2, 'r')
        n1 = [s(n) for n in d1.variables['name_nod_var'][:]]; n2 = [s(n) for n in d2.variables['name_nod_var'][:]]
        ic1 = n1.index('control') + 1; ic2 = n2.index('control') + 1
        it1 = n1.index('topology') + 1; it2 = n2.index('topology') + 1
        nst1 = int(d1.dimensions['time_step'].size); nst2 = int(d2.dimensions['time_step'].size)
        c2 = np.array(d2.variables[f'vals_nod_var{ic2}'][0, :]); t2 = np.array(d2.variables[f'vals_nod_var{it2}'][0, :])
        diffs = []
        for k in range(nst1):
            c1 = np.array(d1.variables[f'vals_nod_var{ic1}'][k, :]); t1 = np.array(d1.variables[f'vals_nod_var{it1}'][k, :])
            diffs.append({'stage1_state_index': k, 'stage1_iteration': k, 'exodus_time_step': k + 1, 'time_value': float(d1.variables['time_whole'][k]),
                          'max_abs_diff_control': float(np.max(np.abs(c1 - c2))), 'max_abs_diff_topology': float(np.max(np.abs(t1 - t2)))})
        rec['stage1_checkpoint_num_states'] = nst1; rec['stage2_engine_output_num_states_so_far'] = nst2
        rec['stage2_state0_vs_stage1_states'] = diffs
        best = min(diffs, key=lambda d: d['max_abs_diff_control'])
        rec['stage1_state_matching_stage2_initial_control'] = best
        checks['Stage-2 initial control field == Stage-1 iteration-20 control field (exact)'] = best['stage1_iteration'] == 20 and best['max_abs_diff_control'] == 0.0
        checks['Stage-2 initial topology field == Stage-1 iteration-20 topology field (|diff| < 1e-10)'] = diffs[20]['max_abs_diff_topology'] < 1e-10 if len(diffs) > 20 else False
        rec['stage2_state0_control_stats'] = {'min': float(c2.min()), 'max': float(c2.max()), 'mean': float(c2.mean())}
    except Exception as e:
        rec['field_comparison_error'] = repr(e)
rec['checks'] = checks; rec['ALL_CHECKS_PASS'] = all(checks.values()) and bool(r2)
print(json.dumps(rec, indent=2))
sys.exit(0 if rec['ALL_CHECKS_PASS'] else 1)
