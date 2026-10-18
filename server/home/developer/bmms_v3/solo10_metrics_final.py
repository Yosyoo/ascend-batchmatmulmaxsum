import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import csv,json,statistics,subprocess
from pathlib import Path
import numpy as np

root=Path('/home/developer/bmms_v3')
out=root/'solo10_data/metrics_final';out.mkdir(parents=True,exist_ok=True)
specs=['4_8_16_128_2_1_1']
summary=[]
for metric in ['PipeUtilization','MemoryAccess']:
 for variant in ['s9j','s10g']:
  for spec in specs:
   print('START',metric,spec,flush=True)
   work=out/metric/variant/spec;work.mkdir(parents=True,exist_ok=True)
   original=root/'variants'/variant/'work'/spec
   if not (work/'input').exists():(work/'input').symlink_to(original/'input',target_is_directory=True)
   (work/'output').mkdir(exist_ok=True)
   app=' '.join([str(root/'variants'/variant/'build/bench'),*spec.split('_'),'160','1'])
   env=dict(os.environ,BMMS_DEVICE_ID='0')
   p=subprocess.run(['msprof','--application='+app,'--output='+str(work/'profile'),
                     '--aic-metrics='+metric,'--task-time=on'],cwd=work,env=env,
                    capture_output=True,text=True,timeout=900)
   (work/'msprof.log').write_text(p.stdout+p.stderr)
   files=sorted((work/'profile').glob('PROF_*/mindstudio_profiler_output/op_summary_*.csv'))
   item={'variant':variant,'metric':metric,'spec':spec,'returncode':p.returncode}
   if not files:
    item['error']=(p.stdout+p.stderr)[-1200:]
   else:
    rows=list(csv.DictReader(files[-1].open()))
    assert len(rows)==163,len(rows)
    rows.sort(key=lambda r:float(r['Task Start Time(us)']))
    tail=rows[-80:]; med={}
    for key in rows[0]:
     if key in ['Task Duration(us)'] or key.startswith(('aic_', 'aiv_', 'cube_')) or any(x in key.lower() for x in ['bw','data','cache','hit','miss','memory']):
      try:med[key]=statistics.median(float(r[key]) for r in tail)
      except ValueError:pass
    y=np.fromfile(work/'output/y.bin',np.float32);gold=np.load(original/'gold.npy')
    item.update({'profile':str(files[-1]),'kernels_per_call':1,
                 'passed':bool(np.allclose(y,gold,atol=1e-4,rtol=1e-4)),'median_metrics':med})
    assert item['passed'],item
   summary.append(item)
   (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
   print(json.dumps(item),flush=True)
