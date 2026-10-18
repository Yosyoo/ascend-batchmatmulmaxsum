"""Serial candidate checks; all original suites retained, no tolerance changes."""
from pathlib import Path
import fcntl,hashlib,json,subprocess,time
r=Path('/home/developer/bmms_v3');data=r/'solo17_data'
def waitbuild(v,log):
    for _ in range(100):
        text=(r/'variants'/v/log).read_text()
        if all('Built target '+x in text for x in ['bench','bench_cases','bench_multi']):return
        if 'error:' in text:raise SystemExit(v+' compile failed')
        time.sleep(10)
    raise SystemExit(v+' compile timeout')
waitbuild('s17f','build_fixed.log');waitbuild('s17g','build.log')
lock=(data/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX)
out=data/'diagnostic_fg';out.mkdir(exist_ok=False)
items=[]
for v,manifest in [('s17f',r/'work/solo18/fail_8.txt'),('s17g',r/'work/solo18/fail_8.txt'),('s17g',r/'solo14_data/long_sum_cases.txt')]:
    exe=r/'variants'/v/'build/bench_cases';src=r/'variants'/v/'kernel.asc'
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,src]}
    p=subprocess.run([str(exe),str(manifest)],capture_output=True,text=True,timeout=600)
    label=v+'_'+manifest.stem;(out/(label+'.log')).write_text(p.stdout+p.stderr)
    rows=[json.loads(x) for x in p.stdout.splitlines() if x.startswith('{')]
    passed=p.returncode==0 and len(rows)==len(manifest.read_text().splitlines()) and all(x['passed'] and x['consistent'] for x in rows)
    item=dict(variant=v,suite=manifest.stem,passed=passed,observed=len(rows),hashes=hashes,returncode=p.returncode)
    items.append(item);print(json.dumps(item),flush=True);(out/'summary.json').write_text(json.dumps(items,indent=2))
    if not passed:print((p.stdout+p.stderr)[-3000:],flush=True);raise SystemExit(1)
fcntl.flock(lock,fcntl.LOCK_UN)
p=subprocess.run(['python3',str(r/'work/solo17/validate.py'),'s17g'])
if p.returncode:raise SystemExit(p.returncode)
specs=['1_1280_4096_1536_1_0_0','1_1280_4096_1536_1_1_0','1_1280_4096_1536_2_0_1','1_1280_4096_1536_2_1_1']
for label,variants in [('pilot_gi','s17g,s15i'),('pilot_ig','s15i,s17g')]:
    p=subprocess.run(['python3',str(r/'work/solo17/scan.py'),label,variants,*specs])
    if p.returncode:raise SystemExit(p.returncode)
print('PASS run18 full precision and exchanged pilots',flush=True)
