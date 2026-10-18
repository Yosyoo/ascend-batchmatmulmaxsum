from pathlib import Path
import csv,fcntl,hashlib,json,os,statistics,subprocess,sys
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v=sys.argv[1];label=sys.argv[2]
dtype,ta,tb=(int(x) for x in sys.argv[3:6])
out=d/label;out.mkdir(exist_ok=False)
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX)
shape_file=Path(sys.argv[6]).resolve();shape_sha=hashlib.sha256(shape_file.read_bytes()).hexdigest()
shapes=[list(map(int,l.split()[:4])) for l in shape_file.read_text().splitlines() if len(l.split())>=4]
exe=r/f'variants/{v}/build/bench_multi';src=r/f'variants/{v}/kernel.asc'
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (src,exe)}
cmd=[str(exe),str(shape_file),'160',str(dtype),str(ta),str(tb)];env=dict(os.environ);env['BMMS_DEVICE_ID']='0'
p=subprocess.run(['msprof','--application='+' '.join(cmd),'--output='+str(out/'profile'),'--aic-metrics=PipeUtilization','--task-time=on'],
 cwd=out,capture_output=True,text=True,timeout=900,env=env)
(out/'msprof.log').write_text(p.stdout+p.stderr)
files=sorted((out/'profile').glob('PROF_*/mindstudio_profiler_output/op_summary_*.csv'));assert p.returncode==0 and files,files
raw=list(csv.DictReader(files[-1].open()));rows=[x for x in raw if 'bmms_' in x['Op Name']]
rows.sort(key=lambda x:float(x['Task Start Time(us)']));assert len(rows)==160*len(shapes),len(rows)
keys=['aic_mac_time(us)','aic_scalar_time(us)','aic_mte2_time(us)','aic_fixpipe_time(us)','aiv_vec_time(us)','aiv_scalar_time(us)','aiv_mte2_time(us)','cube_utilization(%)']
items=[]
for i,s in enumerate(shapes):
    seg=rows[i*160:(i+1)*160];times=[float(x['Task Duration(us)']) for x in seg]
    med={k:statistics.median(float(x[k]) for x in seg[-80:]) for k in keys}
    items.append(dict(shape=s,us=statistics.median(times[-80:]),op=sorted({x['Op Name'] for x in seg}),metrics=med))
    print(s,round(items[-1]['us'],3),items[-1]['op'][0].split('bmms_')[-1].split('IDh')[0][:20],
          ' '.join(f'{k.split("(")[0].replace("aic_","A").replace("aiv_","V")}={med[k]:.2f}' for k in keys))
(out/'summary.json').write_text(json.dumps(dict(variant=v,dtype=dtype,ta=ta,tb=tb,hashes=hashes,shape_sha256=shape_sha,items=items),indent=2)+'\n')
print(json.dumps(dict(variant=v,tasks=len(rows),hashes=hashes)))
fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
