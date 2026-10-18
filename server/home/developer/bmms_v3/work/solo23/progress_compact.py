from pathlib import Path
import json,sys
d=Path('/home/developer/bmms_v3/solo17_data')
for tag in sys.argv[1:]:
    for label in [f'pilot23_{tag}_parent_base',f'pilot23_base_parent_{tag}']:
        p=d/label/'results.jsonl'
        if not p.exists():continue
        a=[json.loads(x) for x in p.read_text().splitlines()]
        print(json.dumps(dict(label=label,rows=len(a),results=[dict(v=x['variant'],spec=x['spec'],us=x['total_warm_us'],
            metrics={k:x['median_metrics'].get(k) for k in ['aic_mac_time(us)','aic_scalar_time(us)','aic_fixpipe_time(us)','aiv_vec_time(us)','aiv_scalar_time(us)']}) for x in a if x['dtype']==1])))
