import json, shutil
from pathlib import Path
R = Path('/home/developer/bmms_v3'); O = R/'dsh_verify'/'out'
d = json.loads((R/'c29'/'dsh137_official15.json').read_text())
mx = [x.get('maxrel') for x in d if x.get('maxrel') is not None]
print('full15: cases=%d passed=%d tasks_all=%d maxrel_max=%.6e' % (
    len(d), sum(1 for x in d if x.get('passed')), all(x.get('tasks',0)>0 for x in d), max(mx)))
p14 = [x['warm_us'] for x in d if x['case'] == 14][0]
print('P14 local warm_us = %.2f' % p14)
shutil.copy2(R/'c29'/'dsh137_official15.json', O/'dsh137_official15.json')
s = json.loads((O/'P14_summary.json').read_text())['summary']
print('P14: pooled_speedup=%.5f reduction=%.4f%% ctrl=%.4f cand=%.4f ranges_separated=%s'
      % (s['pooled_speedup'], s['pooled_reduction_percent'], s['control_median'],
         s['candidate_median'], s['ranges_separated']))
print('P14: ctrl_spread=%.2f%% cand_spread=%.2f%%' % (s['control_spread_percent'], s['candidate_spread_percent']))
r = 1.0/s['pooled_speedup']
t137 = 11.55*r
import math
L = math.log(1.5)
def sc(t,T): return 100.0 if t<=T else 100.0/(1.0+math.log(t/T)/L)
d1 = sc(t137,8.10)-sc(11.55,8.10)
print('ratio 137/131 = %.6f ; P14 11.55 -> %.3f us ; dscore=%+.2f per-case ; mean %+.4f' % (r,t137,d1,d1/15))
print('projected (anchor formula 58.495478) = %.4f' % (58.49547821278846 + d1/15))
print('artifacts: csv=%d y_bin=%d json=%d' % (len(list(O.glob('P14_*_op_summary.csv'))),
      len(list(O.glob('P14_*_y.bin'))), len(list(O.glob('*.json')))))
