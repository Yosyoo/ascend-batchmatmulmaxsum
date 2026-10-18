#!/usr/bin/env python3
"""Collate sweep log into a shape x variant table with ratios vs a reference variant."""
import json, sys
from collections import OrderedDict

log = sys.argv[1]
ref = sys.argv[2] if len(sys.argv) > 2 else 'baseline'
variants = sys.argv[3].split(',') if len(sys.argv) > 3 else ['baseline', 'conservative', 'final', 'balanced']

rows = [json.loads(l) for l in open(log) if l.startswith('{')]
d = OrderedDict()
for r in rows:
    d.setdefault(tuple(r['shape']), {})[r['variant']] = r

hdr = f"{'B,M,N,K':<26}" + ''.join(f"{v[:8]:>10}" for v in variants)
print(hdr)
print('-' * len(hdr))
worst = []
for k, v in d.items():
    if any(x not in v for x in variants):
        print(f"{str(k):<26} incomplete: {sorted(v)}")
        continue
    line = f"{str(k):<26}"
    b = v[ref].get('min')
    for x in variants:
        m = v[x].get('min')
        line += f"{m:10.2f}" if m else f"{'ERR':>10}"
    if b:
        line += '   ' + '  '.join(f"{v[x]['min']/b:5.2f}" if v[x].get('min') else '  ERR' for x in variants)
    bad = [x for x in variants if v[x].get('passed') is not True]
    if bad:
        line += '  FAIL:' + ','.join(bad)
    print(line)
    for x in variants:
        if x != ref and v[x].get('min') and b:
            worst.append((v[x]['min'] / b, k, x))
print()
print('=== worst regressions vs', ref, '(sorted) ===')
for r, k, x in sorted(worst, reverse=True)[:15]:
    print(f"  {r:6.2f}x  {x:<12} {k}")
print('=== best speedups ===')
for r, k, x in sorted(worst)[:10]:
    print(f"  {r:6.2f}x  {x:<12} {k}")
