from pathlib import Path
import json,math,statistics,sys
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';p=d/sys.argv[1]
c=json.loads((p/'comparison.json').read_text());a=json.loads((p/'1_s29m/summary.json').read_text())
items=[]
for i,item in enumerate(a['shapes']):
 ratios=[z['ratios'][i]['ratio'] for z in c['orders']]
 affected=any('pair_static' in z or 'resident' in z for z in item['op_names'])
 items.append(dict(shape=item['shape'],ratios=ratios,affected=affected,op_names=item['op_names']))
result=dict(label=p.name,all_ratios=[z['geometric_mean_ratio'] for z in c['orders']],groups=[])
for group in (True,False):
 xs=[z for z in items if z['affected']==group]
 result['groups'].append(dict(affected=group,count=len(xs),ratios=[math.exp(statistics.mean(math.log(z['ratios'][i]) for z in xs)) for i in (0,1)]))
print(json.dumps(result),flush=True)
print(json.dumps(dict(worst=sorted(items,key=lambda z:max(z['ratios']),reverse=True)[:8])),flush=True)
