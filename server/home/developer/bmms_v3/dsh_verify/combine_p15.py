import json, math, statistics
from pathlib import Path
O = Path('/home/developer/bmms_v3/dsh_verify/out')
runs = []
for tag in ('P15_152', 'P15_BAAB'):
    d = json.loads((O/f'{tag}_summary.json').read_text())
    runs += d['runs']
g = lambda xs: math.exp(sum(math.log(x) for x in xs)/len(xs))
c137 = [r['median_us'] for r in runs if r['variant'] == 'dsh137']
c152 = [r['median_us'] for r in runs if r['variant'] == 'dsh152']
print('P15 合并 4 块（2 ABBA + 2 BAAB，共 %d 次）' % len(runs))
print('  137: %s  median=%.4f' % (c137, statistics.median(c137)))
print('  152: %s  median=%.4f' % (c152, statistics.median(c152)))
print('  geo: 137=%.4f 152=%.4f  ratio=%.6f  reduction=%.4f%%' % (
    g(c137), g(c152), g(c152)/g(c137), 100*(1-g(c152)/g(c137))))
print('  spread: 137=%.2f%%  152=%.2f%%   ranges_separated=%s' % (
    100*(max(c137)/min(c137)-1), 100*(max(c152)/min(c152)-1),
    max(c152) < min(c137) or max(c137) < min(c152)))
print('  PASS/RC:', all(r['passed'] and r['rc'] == 0 for r in runs))
# P14 final
d = json.loads((O/'P14_152_summary.json').read_text())['summary']
print('\nP14 合并 2 块（8 次）: speedup=%.5f reduction=%.4f%% ranges_separated=%s spreads ctrl=%.2f%% cand=%.2f%%'
      % (d['pooled_speedup'], d['pooled_reduction_percent'], d['ranges_separated'],
         d['control_spread_percent'], d['candidate_spread_percent']))
