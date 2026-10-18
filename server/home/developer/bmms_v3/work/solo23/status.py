from pathlib import Path
import hashlib,json,sys
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
tags=sys.argv[1:] or ['a']
for tag in tags:
    for label in [f'pilot23_{tag}_parent_base',f'pilot23_base_parent_{tag}']:
        p=d/label/'results.jsonl'
        if p.exists():
            rows=[json.loads(x) for x in p.read_text().splitlines()]
            keys=['aic_mac_time(us)','aic_scalar_time(us)','aic_mte2_time(us)','aic_fixpipe_time(us)','aiv_vec_time(us)','aiv_scalar_time(us)','aiv_mte2_time(us)']
            print(json.dumps(dict(label=label,observed=len(rows),results=[dict(variant=x['variant'],spec=x['spec'],us=x['total_warm_us'],metrics={k:x['median_metrics'][k] for k in keys}) for x in rows])))
