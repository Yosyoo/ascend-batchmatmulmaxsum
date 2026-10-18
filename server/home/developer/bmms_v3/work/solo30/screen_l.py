from pathlib import Path
import subprocess,time,json,hashlib,fcntl
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s30l';sha='0c62bc301bda9c9faa351f4252891fb8ab4fc0050d9163533f95ed137c9c1263'
deadline=time.monotonic()+1500
while 'COMPILE29_SCREEN_COMPLETE' not in (d/'compile30_l.log').read_text(errors='replace'):
 assert time.monotonic()<deadline
 assert 'error:' not in (d/'compile30_l.log').read_text(errors='replace')
 time.sleep(5)
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
out=d/'diagnostic30_s30l';out.mkdir(exist_ok=False)
manifests=[r/'delivery4/validation/cases.txt',r/'solo13_data/generic_nt_cases.txt',r/'solo13_data/nt_cases.txt',r/'solo11_data/copy_cases.txt',r/'solo17_data/manual_cases18.txt',r/'solo17_data/medium_cases.txt',r/'solo14_data/balanced_cases.txt',r/'work/solo18/fail_8.txt']
selected=[];origins=[]
for p in manifests:
 before=hashlib.sha256(p.read_bytes()).hexdigest();count=0
 for line in p.read_text().splitlines():
  b,m,n,k=map(int,line.split()[:4]);mp=64 if m<=64 else 128 if m<=128 else 256;np=64 if n<=64 else 128 if n<=128 else 256
  keep=32<m<=256 and 32<n<=256 and k<=1024 and k%16==0 and mp*np<=32768
  if p.name=='fail_8.txt':keep=True
  if keep:selected.append(line);count+=1
 origins.append(dict(path=str(p),sha256=before,selected=count));assert before==hashlib.sha256(p.read_bytes()).hexdigest()
assert len(selected)>=32
manifest=out/'cases.txt';manifest.write_text('\n'.join(selected)+'\n');case_sha=hashlib.sha256(manifest.read_bytes()).hexdigest()
exe=r/f'variants/{v}/build/bench_cases';hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (exe,r/f'variants/{v}/kernel.asc')}
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX)
p=subprocess.run([str(exe),str(manifest)],cwd=r,capture_output=True,text=True,timeout=900)
(out/'precision.log').write_text(p.stdout+p.stderr);rows=[json.loads(z) for z in p.stdout.splitlines() if z.startswith('{')]
good=p.returncode==0 and len(rows)==len(selected) and all(z['passed'] and z['consistent'] for z in rows)
result=dict(variant=v,hashes=hashes,origins=origins,manifest_sha256=case_sha,expected=len(selected),observed=len(rows),passed=good,
 failures=[z for z in rows if not z['passed'] or not z['consistent']],returncode=p.returncode)
(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
assert case_sha==hashlib.sha256(manifest.read_bytes()).hexdigest();fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
if not good:raise SystemExit(1)
subprocess.run(['python3','work/solo28/quick_compare.py',v,'s29m','quick30_l','work/solo30/l_shapes.txt'],cwd=r,check=True)
print('SCREEN30_L_COMPLETE',flush=True)
