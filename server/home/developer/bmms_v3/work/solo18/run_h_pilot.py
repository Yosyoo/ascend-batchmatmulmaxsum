from pathlib import Path
import fcntl,hashlib,json,os,subprocess,time
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
for _ in range(150):
    try:os.kill(32406,0);alive=True
    except ProcessLookupError:alive=False
    build=(r/'variants/s17h/build.log').read_text()
    if not alive and all('Built target '+x in build for x in ['bench','bench_cases','bench_multi']):break
    if 'error:' in build:raise SystemExit('h compile failed')
    time.sleep(10)
else:raise SystemExit('prerequisite not complete')
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
out=d/'diagnostic_h';out.mkdir(exist_ok=False)
exe=r/'variants/s17h/build/bench_cases';src=r/'variants/s17h/kernel.asc';summary=[]
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,src]}
for manifest in [r/'work/solo18/fail_8.txt',d/'resident_cases18.txt']:
    p=subprocess.run([str(exe),str(manifest)],capture_output=True,text=True,timeout=600)
    (out/(manifest.stem+'.log')).write_text(p.stdout+p.stderr)
    rows=[json.loads(x) for x in p.stdout.splitlines() if x.startswith('{')]
    good=p.returncode==0 and len(rows)==len(manifest.read_text().splitlines()) and all(x['passed'] and x['consistent'] for x in rows)
    item=dict(suite=manifest.stem,passed=good,observed=len(rows),hashes=hashes)
    summary.append(item);print(json.dumps(item),flush=True);(out/'summary.json').write_text(json.dumps(summary,indent=2))
    if not good:print((p.stdout+p.stderr)[-3000:],flush=True);raise SystemExit(1)
fcntl.flock(lock,fcntl.LOCK_UN)
specs=['1_1280_4096_1536_1_0_0','1_1280_4096_1536_1_1_0','1_1280_4096_1536_2_0_1','1_1280_4096_1536_2_1_1']
for label,variants in [('pilot_hi','s17h,s15i'),('pilot_ih','s15i,s17h')]:
    p=subprocess.run(['python3',str(r/'work/solo17/scan.py'),label,variants,*specs])
    if p.returncode:raise SystemExit(p.returncode)
print('PASS h targeted and exchanged pilots',flush=True)
