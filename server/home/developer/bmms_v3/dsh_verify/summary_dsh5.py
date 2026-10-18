import json, math, shutil
from pathlib import Path
R = Path('/home/developer/bmms_v3'); O = R/'dsh_verify'/'out'
d = json.loads((R/'c29'/'dsh172_official15.json').read_text())
mx = [x.get('maxrel') for x in d if x.get('maxrel') is not None]
print('full15: cases=%d passed=%d tasks_all=%d maxrel_max=%.6e' % (
    len(d), sum(1 for x in d if x.get('passed')), all(x.get('tasks',0)>0 for x in d), max(mx)))
shutil.copy2(R/'c29'/'dsh172_official15.json', O/'dsh172_official15.json')
for tag in ('S172_4x128', 'S172_1x40'):
    s = json.loads((O/f'{tag}_summary.json').read_text())['summary']
    print('%s: reduction=%.4f%% ctrl=%.4f cand=%.4f spreads=%.2f%%/%.2f%% separated=%s' % (
        tag, s['pooled_reduction_percent'], s['control_median'], s['candidate_median'],
        s['control_spread_percent'], s['candidate_spread_percent'], s['ranges_separated']))
L = math.log(1.5)
def sc(t, T): return 100.0 if t <= T else 100.0/(1.0+math.log(t/T)/L)
# 以 157 官方表为锚，仅计已确认的 P2/P4
a = json.loads((O/'S172_1x40_summary.json').read_text())['summary']
b = json.loads((O/'S172_4x128_summary.json').read_text())['summary']
r2 = 1.0/a['pooled_speedup']; r4 = 1.0/b['pooled_speedup']
t2, t4 = 2.41*r2, 3.78*r4
T2, T4 = 1.42, 2.13
d2 = sc(t2,T2)-sc(2.41,T2); d4 = sc(t4,T4)-sc(3.78,T4)
print('\nP2 2.41 -> %.4f (ratio %.5f) d=%+.2f ; P4 3.78 -> %.4f (ratio %.5f) d=%+.2f' % (t2,r2,d2,t4,r4,d4))
print('mean gain = %+.4f' % ((d2+d4)/15))
print('157 官方 formula = 58.5388 (我在上一轮重算)  => independent prediction = %.4f' % (58.5388+(d2+d4)/15))
