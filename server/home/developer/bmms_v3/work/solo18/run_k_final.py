from pathlib import Path
import fcntl,hashlib,json,subprocess,time
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
for _ in range(120):
    text=(r/'variants/s17k/build.log').read_text()
    if all(any(line.endswith('Built target '+x) for line in text.splitlines()) for x in ['bench','bench_cases','bench_multi']):break
    if 'error:' in text:raise SystemExit('i compile failed')
    time.sleep(10)
else:raise SystemExit('compile not complete')
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX)
out=d/'diagnostic_k';out.mkdir(exist_ok=False)
exe=r/'variants/s17k/build/bench_cases';src=r/'variants/s17k/kernel.asc';items=[]
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,src]}
for manifest in [r/'work/solo18/fail_8.txt',d/'resident_cases18.txt',d/'manual_cases18.txt']:
    p=subprocess.run([str(exe),str(manifest)],capture_output=True,text=True,timeout=600)
    (out/(manifest.stem+'.log')).write_text(p.stdout+p.stderr)
    rows=[json.loads(x) for x in p.stdout.splitlines() if x.startswith('{')]
    good=p.returncode==0 and len(rows)==len(manifest.read_text().splitlines()) and all(x['passed'] and x['consistent'] for x in rows)
    item=dict(suite=manifest.stem,passed=good,observed=len(rows),hashes=hashes);items.append(item)
    print(json.dumps(item),flush=True);(out/'summary.json').write_text(json.dumps(items,indent=2))
    if not good:print((p.stdout+p.stderr)[-3000:]);raise SystemExit(1)
fcntl.flock(lock,fcntl.LOCK_UN)
manual_specs=['1_512_256_1536_1_0_0','1_256_512_1536_2_0_0','1_4096_16_2048_1_0_0','1_4096_16_2048_2_1_0','1_2048_32_4096_1_0_1','1_2048_32_4096_2_1_1']
for label,variants in [('manual_k_base','s17k,s15i'),('manual_base_k','s15i,s17k')]:
    p=subprocess.run(['python3',str(r/'work/solo17/scan.py'),label,variants,*manual_specs])
    if p.returncode:raise SystemExit(p.returncode)
p=subprocess.run(['python3',str(r/'work/solo17/validate.py'),'s17k'])
if p.returncode:raise SystemExit(p.returncode)
specs=['1_1280_4096_1536_1_0_0','1_1280_4096_1536_1_1_0','1_1280_4096_1536_2_0_1','1_1280_4096_1536_2_1_1']
for label,variants in [('pilot_k_base','s17k,s15i'),('pilot_base_k','s15i,s17k')]:
    p=subprocess.run(['python3',str(r/'work/solo17/scan.py'),label,variants,*specs])
    if p.returncode:raise SystemExit(p.returncode)
p=subprocess.run(['python3',str(r/'work/solo18/pool18.py'),'s17k'])
if p.returncode:raise SystemExit(p.returncode)
hangs=['1_4096_4096_1024','1_8192_512_1024','1_4096_1024_512','1_2048_2048_1024','1_8192_256_512','2_4096_2048_512']
p=subprocess.run(['python3',str(r/'work/solo17/scan.py'),'hangs18_k','s17k',*hangs])
if p.returncode:raise SystemExit(p.returncode)
print('PASS s17k final precision, exchanged pilots,100-pool and six hangs',flush=True)
