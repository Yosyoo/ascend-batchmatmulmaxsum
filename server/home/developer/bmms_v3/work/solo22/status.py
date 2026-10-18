from pathlib import Path
import hashlib,json
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
for label in ['pilot22_fulla_forward','pilot22_fulla_reverse']:
    p=d/label/'results.jsonl'
    if p.exists():
        rows=[json.loads(x) for x in p.read_text().splitlines()]
        print(json.dumps(dict(label=label,observed=len(rows),results=[dict(variant=x['variant'],spec=x['spec'],us=x['total_warm_us']) for x in rows])))
result={'observed_original_BF16_failures':12,'official_submissions_this_round':0,
        'runners':{str(pid):Path('/proc/'+str(pid)).exists() for pid in [270681,271551,281294,281419,288225,294339,294772]}}
for name,p in [('full_precision',d/'validation_s22a/precision_summary.json'),('diagnostics',d/'diagnostic_22a/summary.json'),('long96',d/'long_accuracy22a/summary.json'),('pool',d/'pool18_s22a/comparison.json'),('repeat_pool',d/'pool22_repeat_s22a/comparison.json')]:
    if p.exists():
        x=json.loads(p.read_text())
        if name in ['pool','repeat_pool']:result[name]=[z['geometric_mean_ratio'] for z in x['orders']]
        elif name=='diagnostics':result[name]={'cases':sum(z['observed'] for z in x),'passed':all(z['passed'] for z in x)}
        else:result[name]={k:x[k] for k in ['total','passed','observed','expected'] if k in x}
result['sources']={v:hashlib.sha256((r/'variants'/v/'kernel.asc').read_bytes()).hexdigest() for v in ['s15i','s21d','s22a']}
(r/'work/solo22/remote_state.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
