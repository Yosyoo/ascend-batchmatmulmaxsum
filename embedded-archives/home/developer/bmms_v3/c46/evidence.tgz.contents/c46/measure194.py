import csv
import shlex
import importlib.util
import json
import math
import os
import shutil
import statistics
import sys
import subprocess
from pathlib import Path

ROOT = Path('/home/developer/bmms_v3')
spec = importlib.util.spec_from_file_location('measure', ROOT/'c26/measure_research.py')
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
os.environ['AIC_METRIC'] = 'PipeUtilization'
SPECS = {'P8':'1_1025_1031_1032_2_1_1','P12':'1_1280_4096_1536_2_1_0','P9':'1_2048_1536_1280_1_0_1','P10':'1_4096_1280_1152_2_0_0','P1':'1_1_1_32_1_0_0','P3':'2_7_13_48_1_0_1','P5':'8_16_32_128_1_0_0','P6':'13_23_73_192_2_0_1','P7':'16_32_128_256_1_1_0','P2':'1_3_5_40_2_1_0', 'P4':'4_8_16_128_2_1_1', 'P14':'1_64_8192_128_2_0_1', 'P15':'1_64_64_8192_1_1_1', 'P13':'1_8192_64_128_1_0_0'}
DEVICE=int(os.environ.get('BMMS_MEASURE_DEVICE','0'))
MODE = sys.argv[1]
OUT = ROOT/'c46'/MODE
OUT.mkdir(exist_ok=True)
rows=[]

def run(point, variant, label):
    active=subprocess.check_output(['ps','-eo','pid=,stat=,comm=,args='],text=True).splitlines()
    competing=[]
    for line in active:
        fields=line.strip().split(None,3)
        if len(fields)!=4:continue
        pid,state,comm,args=fields
        if state.startswith('Z'):continue
        actual=Path(comm).name
        if actual in {'bisheng','clang','clang++','make','gmake','cmake','ld.lld'}:
            competing.append({'pid':pid,'compiler':actual})
        if actual in {'bench','msprof'}:
            try:
                # Read only this profiling harness device selector; never print other env values.
                env=dict(x.split(b'=',1) for x in Path('/proc/'+pid+'/environ').read_bytes().split(b'\0') if b'=' in x)
                dev=env.get(b'BMMS_DEVICE_ID')
            except FileNotFoundError:continue
            except PermissionError:dev=None
            if dev is None or dev.decode()!=str(DEVICE):
                if dev is not None:continue
            competing.append({'pid':pid,'NPU_job':actual,'device':dev.decode() if dev is not None else 'unknown'})
    if competing:raise RuntimeError('Selected NPU or compiler busy; wait: '+repr(competing))
    row=q.run_shape(variant, SPECS[point], 'msprof', 120, 1, DEVICE)
    row.update(measurement_device=DEVICE, point=point, label=label, warm_us=statistics.median(row['all_us'][-60:]) if row.get('all_us') else None)
    work=ROOT/'variants'/variant/'research/PipeUtilization'/SPECS[point]
    profiles=sorted(work.glob('profile/PROF_*/mindstudio_profiler_output/op_summary_*.csv'))
    if profiles:
        dest=OUT/(label+'_'+point+'_'+variant+'.csv')
        shutil.copy2(profiles[-1], dest)
        with dest.open() as f: pipe=list(csv.DictReader(f))[-60:]
        row['pipes']={}
        for key in ['aic_mac_time(us)','aic_scalar_time(us)','aic_mte1_time(us)','aic_mte2_time(us)','aic_fixpipe_time(us)','aiv_vec_time(us)','aiv_scalar_time(us)','aiv_mte2_time(us)']:
            try: row['pipes'][key]=statistics.median(float(r[key]) for r in pipe)
            except (KeyError,ValueError,statistics.StatisticsError): pass
    y=work/'output/y.bin'
    if y.exists(): shutil.copy2(y,OUT/(label+'_'+point+'_'+variant+'_y.bin'))
    rows.append(row)
    (OUT/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(json.dumps({key:row.get(key) for key in ['point','variant','label','warm_us','passed','returncode','maxrel']}),flush=True)
    if row.get('returncode') != 0 or not row.get('passed'): raise RuntimeError('validation failed')
    return row

points=['P6']; candidate='clean194'
for point in points:
    for block in range(2):
        for pos,variant in enumerate(['clean181',candidate,candidate,'clean181']):
            run(point,variant,'B'+str(block)+'_'+str(pos))
summary=[]
for point in points:
    controls=[r['warm_us'] for r in rows if r['point']==point and r['variant']=='clean181']
    blocks=[]
    for block in range(2):
        group=[r['warm_us'] for r in rows if r['point']==point and r['label'].startswith('B'+str(block)+'_')]
        a=(math.log(group[0])+math.log(group[3]))/2
        b=(math.log(group[1])+math.log(group[2]))/2
        blocks.append({'times_ABBA':group,'speedup_geomean':math.exp(a-b),'time_reduction_percent':100*(1-math.exp(b-a)),'control_drift_percent':100*(group[3]/group[0]-1)})
    summary.append({'point':point,'control_sessions_us':controls,'control_range_percent':100*(max(controls)/min(controls)-1),'blocks':blocks})
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary),flush=True)
