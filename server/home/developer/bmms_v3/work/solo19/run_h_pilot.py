from pathlib import Path
import fcntl,hashlib,json,subprocess
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s19h'
out=d/'diagnostic_19h';out.mkdir(exist_ok=False)
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX)
exe=r/'variants'/v/'build/bench_cases';src=r/'variants'/v/'kernel.asc'
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,src]};items=[]
for manifest in [r/'work/solo18/fail_8.txt',d/'resident_cases18.txt',d/'manual_cases18.txt',d/'medium_cases.txt',r/'solo14_data/split16_cases.txt']:
    p=subprocess.run([str(exe),str(manifest)],capture_output=True,text=True,timeout=600)
    (out/(manifest.stem+'.log')).write_text(p.stdout+p.stderr)
    rows=[json.loads(x) for x in p.stdout.splitlines() if x.startswith('{')]
    good=p.returncode==0 and len(rows)==len(manifest.read_text().splitlines()) and all(x['passed'] and x['consistent'] for x in rows)
    item=dict(suite=manifest.stem,passed=good,observed=len(rows),expected=len(manifest.read_text().splitlines()),hashes=hashes);items.append(item)
    (out/'summary.json').write_text(json.dumps(items,indent=2));print(json.dumps(item),flush=True)
    if not good:print((p.stdout+p.stderr)[-3000:]);raise SystemExit(1)
assert hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,src]}
fcntl.flock(lock,fcntl.LOCK_UN)
specs=['1_1280_4096_1536_1_0_0', '1_1280_4096_1536_1_0_1', '1_1280_4096_1536_1_1_0', '1_1280_4096_1536_1_1_1', '1_1280_4096_1536_2_0_0', '1_1280_4096_1536_2_0_1', '1_1280_4096_1536_2_1_0', '1_1280_4096_1536_2_1_1', '1_512_256_1536_1_0_0', '1_256_512_1536_2_0_0', '1_4096_16_2048_1_0_0', '1_2048_32_4096_1_0_1', '1_512_512_1536_1_1_0']
for label,variants in [('pilot19_h_f_base','s19h,s19f,s15i'),('pilot19_base_f_h','s15i,s19f,s19h')]:
    p=subprocess.run(['python3',str(r/'work/solo17/scan.py'),label,variants,*specs])
    if p.returncode:raise SystemExit(p.returncode)
print('PASS s19h pilot only; full precision/100 pool/six hangs not yet run.',flush=True)
