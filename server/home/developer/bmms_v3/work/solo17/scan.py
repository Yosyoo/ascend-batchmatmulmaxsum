"""Serial NPU pilots: 160 calls, last 80 Task Duration medians, raw CSV preserved."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
import csv,fcntl,hashlib,json,shutil,statistics,subprocess,sys,time
import numpy as np
root=Path('/home/developer/bmms_v3');data=root/'solo17_data'
sys.path.insert(0,str(root/'harness'))
from measure import gen_data,parse_shape
label=sys.argv[1];variants=sys.argv[2].split(',');specs=sys.argv[3:]
out=data/label;out.mkdir(exist_ok=False)
lock=(data/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
with (out/'results.jsonl').open('w') as result:
    for v in variants:
        for spec in specs:
            B,M,N,K,d,ta,tb=parse_shape(spec)
            fixture=data/'pilot_inputs'/spec
            if not (fixture/'gold.npy').exists():gen_data(fixture,B,M,N,K,d,ta,tb)
            gold=np.load(fixture/'gold.npy')
            work=out/v/spec;work.mkdir(parents=True)
            shutil.copytree(fixture/'input',work/'input');(work/'output').mkdir()
            source=root/'variants'/v/'kernel.asc';exe=root/'variants'/v/'build/bench'
            hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,exe]}
            command=[str(exe),str(B),str(M),str(N),str(K),str(d),str(ta),str(tb),'160','1']
            env=dict(os.environ);env['BMMS_DEVICE_ID']='0'
            p=subprocess.run(['msprof','--application='+' '.join(command),'--output='+str(work/'profile'),
                '--aic-metrics=PipeUtilization','--task-time=on'],cwd=work,capture_output=True,text=True,timeout=180,env=env)
            (work/'msprof.log').write_text(p.stdout+p.stderr)
            files=sorted((work/'profile').glob('PROF_*/mindstudio_profiler_output/op_summary_*.csv'))
            assert p.returncode==0 and files,(v,spec,p.returncode,(p.stdout+p.stderr)[-1200:])
            raw_rows=list(csv.DictReader(files[-1].open()))
            runtime_rows=[r for r in raw_rows if 'bmms_' not in r['Op Name']]
            assert all(r['Op Name']=='preload_stack_16KB' and int(r['Block Num'])==0 for r in runtime_rows),runtime_rows
            rows=[r for r in raw_rows if 'bmms_' in r['Op Name']]
            rows.sort(key=lambda r:float(r['Task Start Time(us)']))
            assert len(rows)==163,('expected exactly one kernel per call',len(rows),v,spec)
            times=[float(r['Task Duration(us)']) for r in rows]
            y=np.fromfile(work/'output/y.bin',np.float32)
            assert y.size==gold.size
            good=bool(np.allclose(y,gold,rtol=1e-4,atol=1e-4))
            metrics={}
            for key in rows[0]:
                if key.startswith(('aic_','aiv_','cube_')):
                    try:metrics[key]=statistics.median(float(r[key]) for r in rows[-80:])
                    except ValueError:pass
            row=dict(variant=v,spec=spec,shape=[B,M,N,K],dtype=d,ta=ta,tb=tb,passed=good,
                kernels_per_call=1,tasks=163,device=0,runtime_startup_rows=runtime_rows,total_warm_us=statistics.median(times[-80:]),
                total_us=times,median_metrics=metrics,source_and_exe_sha256=hashes,
                saved_profile=str(files[-1]),max_relative=float(np.max(np.abs(y-gold)/np.maximum(np.abs(gold),1e-5))))
            result.write(json.dumps(row)+'\n');result.flush()
            print(json.dumps({k:val for k,val in row.items() if k not in ('total_us','median_metrics')}),flush=True)
            assert good,(v,spec,y,gold)
            assert hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [source,exe]}
print('PASS pilot',label,flush=True)
