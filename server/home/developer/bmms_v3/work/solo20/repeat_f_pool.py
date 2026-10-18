"""100-shape performance pool, exactly160 calls/shape and last80 Task Duration median."""
from pathlib import Path
import csv,fcntl,hashlib,json,math,os,statistics,subprocess,sys
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v=sys.argv[1]

assert v=='s20f'
src=r/'variants'/v/'kernel.asc'
assert hashlib.sha256(src.read_bytes()).hexdigest()=='198ee0bb6eca5a4503e734438da20f05a4ad962e5c7d53976b84552190b09f3c'
precision=json.loads((d/('validation_'+v)/'precision_summary.json').read_text())
assert precision['passed'] and precision['total']==18378
assert sum(x['observed'] for x in json.loads((d/'diagnostic_20f/summary.json').read_text()))==648
assert len((d/'hangs20_f/results.jsonl').read_text().splitlines())==6
assert 'PASS s20f complete' in (d/'run20_f_final.log').read_text()
initial=json.loads((d/('pool18_'+v)/'comparison.json').read_text())
assert all(x['geometric_mean_ratio']<=0.995 for x in initial['orders'])
out=d/('pool20_repeat_'+v);out.mkdir(exist_ok=False)
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
shapes=[list(map(int,l.split()[:4])) for l in (r/'shapes_pool2.txt').read_text().splitlines() if len(l.split())>=4]
assert len(shapes)==100
summary=[]
for order,variant in enumerate(['s15i',v,v,'s15i']):
    work=out/(str(order)+'_'+variant);work.mkdir()
    src=r/'variants'/variant/'kernel.asc';exe=r/'variants'/variant/'build/bench_multi'
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [src,exe]}
    cmd=[str(exe),str(r/'shapes_pool2.txt'),'160','1','0','0']
    env=dict(os.environ);env['BMMS_DEVICE_ID']='0'
    p=subprocess.run(['msprof','--application='+' '.join(cmd),'--output='+str(work/'profile'),
        '--aic-metrics=PipeUtilization','--task-time=on'],cwd=work,capture_output=True,text=True,timeout=3600,env=env)
    (work/'msprof.log').write_text(p.stdout+p.stderr)
    files=sorted((work/'profile').glob('PROF_*/mindstudio_profiler_output/op_summary_*.csv'))
    assert p.returncode==0 and files,(variant,p.returncode,p.stderr[-1000:])
    raw=list(csv.DictReader(files[-1].open()));runtime=[x for x in raw if 'bmms_' not in x['Op Name']]
    assert all(x['Op Name']=='preload_stack_16KB' and int(x['Block Num'])==0 for x in runtime),runtime
    rows=[x for x in raw if 'bmms_' in x['Op Name']];rows.sort(key=lambda x:float(x['Task Start Time(us)']))
    assert len(rows)==len(shapes)*160,len(rows)
    recorded=[list(map(int,l.split()[1:5])) for l in p.stdout.splitlines() if l.startswith('SHAPE ')]
    assert recorded==shapes
    items=[]
    for i,shape in enumerate(shapes):
        times=[float(x['Task Duration(us)']) for x in rows[i*160:(i+1)*160]]
        items.append(dict(shape=shape,total_us=times,total_warm_us=statistics.median(times[-80:])))
    item=dict(order=order,variant=variant,device=0,kernels_per_call=1,tasks=len(rows),runtime_startup_rows=runtime,
        hashes=hashes,profile=str(files[-1]),shapes=items,scope='performance only; full precision validated separately')
    assert hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [src,exe]}
    summary.append(item);(work/'summary.json').write_text(json.dumps(item,indent=2))
    print(json.dumps(dict(order=order,variant=variant,tasks=len(rows))),flush=True)
ratios=[]
for base,cand in [(summary[0],summary[1]),(summary[3],summary[2])]:
    values=[b['total_warm_us']/a['total_warm_us'] for a,b in zip(base['shapes'],cand['shapes'])]
    ratios.append(dict(geometric_mean_ratio=math.exp(statistics.mean(map(math.log,values))),
        ratios=[dict(shape=s,ratio=x) for s,x in zip(shapes,values)]))
(out/'comparison.json').write_text(json.dumps(dict(candidate=v,orders=ratios,passed_task_contract=True),indent=2))
print(json.dumps(dict(candidate=v,geometric_mean_ratios=[x['geometric_mean_ratio'] for x in ratios])),flush=True)
