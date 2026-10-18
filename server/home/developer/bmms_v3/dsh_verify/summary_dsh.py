import json
from pathlib import Path
R = Path('/home/developer/bmms_v3'); O = R/'dsh_verify'/'out'
d = json.loads((R/'c29'/'dsh131_official15.json').read_text())
mx = [x.get('maxrel') for x in d if x.get('maxrel') is not None]
print('full15: cases=%d passed=%d tasks_all=%d maxrel_max=%.6e' % (
    len(d), sum(1 for x in d if x.get('passed')), all(x.get('tasks', 0) > 0 for x in d), max(mx)))
s = json.loads((O/'dsh_summary.json').read_text())['summary']
print('P4: pooled_speedup=%.5f pooled_reduction=%.4f%% cand_median=%.4f ctrl_median=%.4f'
      % (s['pooled_speedup'], s['pooled_reduction_percent'], s['candidate_median'], s['control_median']))
print('P4: cand_spread=%.2f%% ctrl_spread=%.2f%% ranges_separated=%s'
      % (s['candidate_spread_percent'], s['control_spread_percent'], s['overlap']))
for b in s['blocks']:
    print('  block: %s reduction=%.4f%% drift=%.3f%%' % (b['times_ABBA_us'], b['reduction_percent'], b['drift_percent']))
print('artifacts: csv=%d y_bin=%d' % (len(list(O.glob('*_op_summary.csv'))), len(list(O.glob('*_y.bin')))))
