import csv,json,statistics
from pathlib import Path
root=Path('/home/developer/bmms_v3/variants')
keys=['Task Duration(us)','aic_mac_time(us)','aic_scalar_time(us)','aic_mte1_time(us)','aic_mte2_time(us)','aic_fixpipe_time(us)','aiv_vec_time(us)','aiv_scalar_time(us)','aiv_mte2_time(us)','Block Num']
for v in ['s5r','s6n','s6p','s6s']:
    for spec in ['1_4096_1280_1152_2_0_0','1_2048_1536_1280_1_0_1','1_1536_2048_2048_1_1_1','1_1280_4096_1536_2_1_0']:
        files=sorted((root/v/'work'/spec/'profile').glob('PROF_*/mindstudio_profiler_output/op_summary_*.csv'))
        if not files: continue
        rows=list(csv.DictReader(files[-1].open()))[-80:]
        r={k:round(statistics.median(float(x[k]) for x in rows),3) for k in keys}
        print(json.dumps({'variant':v,'spec':spec,'times':r}))
