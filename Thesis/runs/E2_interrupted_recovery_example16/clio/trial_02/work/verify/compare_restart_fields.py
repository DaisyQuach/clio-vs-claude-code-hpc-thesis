# Compare the design fields saved in the Stage-1 checkpoint (last state) with the first state of the Stage-2 engine output.
# Usage: python3 compare_restart_fields.py STAGE1_ENGINE_OUTPUT STAGE2_ENGINE_OUTPUT
import sys, json
import numpy as np
from netCDF4 import Dataset

def fields(path):
    d = Dataset(path)
    names = [''.join(b.decode() for b in row if b).strip() for row in d.variables['name_nod_var'][:]]
    times = d.variables['time_whole'][:]
    out = {}
    for i, n in enumerate(names):
        out[n] = np.array(d.variables['vals_nod_var%d' % (i + 1)][:])
    return times, out

t1, f1 = fields(sys.argv[1])
t2, f2 = fields(sys.argv[2])
res = {'stage1_file': sys.argv[1], 'stage2_file': sys.argv[2],
       'stage1_num_states': int(len(t1)), 'stage2_num_states': int(len(t2)),
       'stage1_last_time_value': float(t1[-1]), 'stage2_first_time_value': float(t2[0]), 'fields': {}}
for n in ('control', 'topology'):
    a = f1[n][-1]; b = f2[n][0]
    diff = np.abs(a - b)
    # also report which Stage-1 state is closest to the Stage-2 first state
    dists = [float(np.max(np.abs(f1[n][k] - b))) for k in range(len(t1))]
    res['fields'][n] = {'stage1_last_state_min_max': [float(a.min()), float(a.max())],
                        'stage2_first_state_min_max': [float(b.min()), float(b.max())],
                        'max_abs_diff_last1_vs_first2': float(diff.max()),
                        'num_nodes_differing_gt_1e-12': int((diff > 1e-12).sum()),
                        'closest_stage1_state_index_0based': int(np.argmin(dists)),
                        'closest_stage1_state_iteration': int(np.argmin(dists)),
                        'max_abs_diff_per_stage1_state': dists}
print(json.dumps(res, indent=1))
