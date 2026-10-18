from pathlib import Path
import json
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
for label in ['pilot_gi','pilot_ig','pilot_hi','pilot_ih']:
    p=d/label/'results.jsonl'
    if p.exists():print(label,[(x['variant'],x['spec'],x['total_warm_us'],x['passed']) for x in map(json.loads,p.read_text().splitlines())])
for v in ['s17g','s17h']:
    p=d/('validation_'+v)/'precision_summary.json'
    if p.exists():
        x=json.loads(p.read_text());print(v,'precision',x['total'],x['passed'],len(x['suites']))
for label in ['diagnostic_h','pool18_s17h','pool18_s17g']:
    for name in ['summary.json','comparison.json']:
        p=d/label/name
        if p.exists():
            x=json.loads(p.read_text())
            if name=='comparison.json':print(label,[z['geometric_mean_ratio'] for z in x['orders']])
            else:print(label,x)
