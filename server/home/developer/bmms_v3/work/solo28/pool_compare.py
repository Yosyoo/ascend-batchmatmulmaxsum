from pathlib import Path
import csv,fcntl,hashlib,json,math,os,statistics,subprocess,sys
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v=sys.argv[1];base=sys.argv[2];label=sys.argv[3]
precision=json.loads((d/('validation_'+v)/'precision_summary.json').read_text());assert precision['passed'] and precision['total']==18378
stress=json.loads((d/('stress28_'+v)/'summary.json').read_text());assert stress['passed'] and sum(z['observed'] for z in stress['items'])==672
out=d/label;out.mkdir(exist_ok=False)
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
shape_file=r/'shapes_pool2.txt';shape_sha=hashlib.sha256(shape_file.read_bytes()).hexdigest()
shapes=[list(map(int,l.split()[:4])) for l in shape_file.read_text().splitlines() if len(l.split())>=4];assert len(shapes)==100
summary=[]
for order,variant in enumerate([base,v,v,base]):
 work=out/(str(order)+'_'+variant);work.mkdir();src=r/f'variants/{variant}/kernel.asc';exe=r/f'variants/{variant}/build/bench_multi'
 hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (src,exe)}
 cmd=[str(exe),str(shape_file),'160','1','0','0'];env=dict(os.environ);env['BMMS_DEVICE_ID']='0'
 p=subprocess.run(['msprof','--application='+' '.join(cmd),'--output='+str(work/'profile'),'--aic-metrics=PipeUtilization','--task-time=on'],cwd=work,capture_output=True,text=True,timeout=3600,env=env)
 (work/'msprof.log').write_text(p.stdout+p.stderr)
 files=sorted((work/'profile').glob('PROF_*/mindstudio_profiler_output/op_summary_*.csv'));assert p.returncode==0 and files
 raw=list(csv.DictReader(files[-1].open()));runtime=[x for x in raw if 'bmms_' not in x['Op Name']]
 assert all(x['Op Name']=='preload_stack_16KB' and int(x['Block Num'])==0 for x in runtime),runtime
 rows=[x for x in raw if 'bmms_' in x['Op Name']];rows.sort(key=lambda x:float(x['Task Start Time(us)']));assert len(rows)==16000
 recorded=[list(map(int,l.split()[1:5])) for l in p.stdout.splitlines() if l.startswith('SHAPE ')];assert recorded==shapes
 items=[]
 for i,shape in enumerate(shapes):
  segment=rows[i*160:(i+1)*160];times=[float(x['Task Duration(us)']) for x in segment];metrics={}
  for key in segment[0]:
   if key.startswith(('aic_','aiv_','cube_')):
    try:metrics[key]=statistics.median(float(x[key]) for x in segment[-80:])
    except ValueError:pass
  items.append(dict(shape=shape,total_us=times,total_warm_us=statistics.median(times[-80:]),op_names=sorted({x['Op Name'] for x in segment}),median_metrics=metrics))
 item=dict(order=order,variant=variant,device=0,kernels_per_call=1,tasks=len(rows),runtime_startup_rows=runtime,hashes=hashes,profile=str(files[-1]),shape_sha256=shape_sha,shapes=items)
 assert hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (src,exe)}
 assert shape_sha==hashlib.sha256(shape_file.read_bytes()).hexdigest()
 summary.append(item);(work/'summary.json').write_text(json.dumps(item,indent=2)+'\n');print(json.dumps(dict(order=order,variant=variant,tasks=len(rows))),flush=True)
ratios=[]
for a,b in ((summary[0],summary[1]),(summary[3],summary[2])):
 vals=[z['total_warm_us']/y['total_warm_us'] for y,z in zip(a['shapes'],b['shapes'])]
 ratios.append(dict(geometric_mean_ratio=math.exp(statistics.mean(map(math.log,vals))),ratios=[dict(shape=s,ratio=z) for s,z in zip(shapes,vals)]))
(out/'comparison.json').write_text(json.dumps(dict(candidate=v,baseline=base,orders=ratios,passed_task_contract=True),indent=2)+'\n')
print(json.dumps(dict(candidate=v,baseline=base,geometric_mean_ratios=[z['geometric_mean_ratio'] for z in ratios])),flush=True)
