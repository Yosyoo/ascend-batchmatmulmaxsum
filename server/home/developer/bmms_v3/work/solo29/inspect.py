from pathlib import Path
import json,sys
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
for letter in sys.argv[1:]:
    p=d/('quick29_'+letter);z=json.loads((p/'comparison.json').read_text())
    baseline=json.loads((p/'0_s28d/summary.json').read_text())
    candidate=json.loads((p/f'1_s29{letter}/summary.json').read_text())
    print('VARIANT','s29'+letter)
    for i,(a,b) in enumerate(zip(z['orders'][0]['ratios'],z['orders'][1]['ratios'])):
        old=baseline['shapes'][i];new=candidate['shapes'][i]
        keys=('aic_mac_time(us)','aic_scalar_time(us)','aic_mte1_time(us)','aic_mte2_time(us)','aic_fixpipe_time(us)','aiv_scalar_time(us)')
        print(json.dumps(dict(shape=a['shape'],ratios=[round(a['ratio'],4),round(b['ratio'],4)],
            old_us=old['total_warm_us'],new_us=new['total_warm_us'],
            old_metrics={k:old['median_metrics'].get(k) for k in keys},
            new_metrics={k:new['median_metrics'].get(k) for k in keys})))
