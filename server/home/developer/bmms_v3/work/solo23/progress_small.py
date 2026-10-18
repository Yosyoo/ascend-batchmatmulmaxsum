from pathlib import Path
import json,sys
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
for tag in sys.argv[1:]:
    for label in [f'pilot23_{tag}_parent_base',f'pilot23_base_parent_{tag}']:
        p=d/label/'results.jsonl'
        if p.exists():
            rows=[json.loads(x) for x in p.read_text().splitlines()]
            print(json.dumps(dict(label=label,rows=len(rows),selected=[dict(v=x['variant'],spec=x['spec'],us=x['total_warm_us'],
                scalar=x['median_metrics'].get('aiv_scalar_time(us)'),vec=x['median_metrics'].get('aiv_vec_time(us)'),mte2=x['median_metrics'].get('aiv_mte2_time(us)')) for x in rows if x['spec'] in ['1_1_1_32_1_0_0','1_1_1_32_2_0_0']])))
    p=d/f'run23_{tag}_pilot.log'
    if p.exists():print(p.name,(p.read_text().splitlines() or ['waiting for previous complete NPU runner'])[-1][:180])
