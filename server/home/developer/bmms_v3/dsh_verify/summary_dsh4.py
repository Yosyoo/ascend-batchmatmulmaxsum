import json, math, statistics, shutil
from pathlib import Path
R = Path('/home/developer/bmms_v3'); O = R/'dsh_verify'/'out'
d = json.loads((R/'c29'/'dsh157_official15.json').read_text())
mx = [x.get('maxrel') for x in d if x.get('maxrel') is not None]
print('full15: cases=%d passed=%d tasks_all=%d maxrel_max=%.6e' % (
    len(d), sum(1 for x in d if x.get('passed')), all(x.get('tasks',0)>0 for x in d), max(mx)))
shutil.copy2(R/'c29'/'dsh157_official15.json', O/'dsh157_official15.json')
for tag, T in (('C157_4x128', 2.22), ('C157_16x256', 6.26)):
    s = json.loads((O/f'{tag}_summary.json').read_text())['summary']
    print('%s: reduction=%.4f%% ctrl_med=%.4f cand_med=%.4f spreads=%.2f%%/%.2f%% separated=%s' % (
        tag, s['pooled_reduction_percent'], s['control_median'], s['candidate_median'],
        s['control_spread_percent'], s['candidate_spread_percent'], s['ranges_separated']))
L = math.log(1.5)
def sc(t, T): return 100.0 if t <= T else 100.0/(1.0+math.log(t/T)/L)
# P4-only prediction from the user's 137 anchor
s = json.loads((O/'C157_4x128_summary.json').read_text())['summary']
r = 1.0/s['pooled_speedup']
t0 = 4.03
print('\nP4 only: ratio=%.6f  4.03 -> %.4f us ; score %.2f -> %.2f ; mean %+.4f' % (
    r, t0*r, sc(t0,2.22), sc(t0*r,2.22), (sc(t0*r,2.22)-sc(t0,2.22))/15))
print('anchor formula 58.570759 => independent conservative prediction = %.4f' % (
    58.57075945283445 + (sc(t0*r,2.22)-sc(t0,2.22))/15))
print('csv=%d y_bin=%d json=%d' % (len(list(O.glob('C157_*_op_summary.csv'))), len(list(O.glob('C157_*_y.bin'))), len(list(O.glob('*.json')))))
