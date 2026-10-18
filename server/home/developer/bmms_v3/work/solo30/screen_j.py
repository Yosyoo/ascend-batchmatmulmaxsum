from pathlib import Path
import subprocess,time,json,hashlib,fcntl,sys,os
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v=sys.argv[1];sha=sys.argv[2];letter=v[-1]
log=d/f'compile30_{letter}.log';deadline=time.monotonic()+1200
while 'COMPILE29_SCREEN_COMPLETE' not in log.read_text(errors='replace'):
 assert time.monotonic()<deadline
 assert 'error:' not in log.read_text(errors='replace')
 time.sleep(5)
assert 'FINAL30_F_COMPLETE' in (d/'final30_f.log').read_text()
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
out=d/f'diagnostic30_{v}';out.mkdir(exist_ok=False)
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX)
manifests=[r/'delivery4/validation/cases.txt',r/'solo14_data/narrow_legal_cases.txt',r/'solo8_data/narrow_cases.txt',r/'solo8_data/narrow_extra_cases.txt',
 r/'solo17_data/pair_stress23.txt',r/'solo17_data/manual_cases18.txt',r/'solo17_data/medium_cases.txt',r/'solo14_data/balanced_cases.txt',r/'solo10_data/vector_cases.txt',r/'work/solo18/fail_8.txt']
selected=[];origins=[]
for p in manifests:
 before=hashlib.sha256(p.read_bytes()).hexdigest();count=0
 for line in p.read_text().splitlines():
  fields=line.split();b,m,n,k=map(int,fields[:4])
  keep=(m>=1024 and n<=32 and k%16==0 and k<=128) if letter=='a' else (m>=1024 and 32<n<=64 and 32<=k<=128 and k%8==0)
  if p.name=='fail_8.txt':keep=True
  if keep:selected.append(line);count+=1
 origins.append(dict(path=str(p),sha256=before,selected=count))
 assert before==hashlib.sha256(p.read_bytes()).hexdigest()
assert len(selected)>=16
manifest=out/'cases.txt';manifest.write_text('\n'.join(selected)+'\n');manifest_sha=hashlib.sha256(manifest.read_bytes()).hexdigest()
exe=r/f'variants/{v}/build/bench_cases';hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (exe,r/f'variants/{v}/kernel.asc')}
env=dict(os.environ);env['BMMS_DEVICE_ID']='0'
p=subprocess.run([str(exe),str(manifest)],cwd=r,capture_output=True,text=True,timeout=600,env=env)
(out/'precision.log').write_text(p.stdout+p.stderr)
rows=[json.loads(z) for z in p.stdout.splitlines() if z.startswith('{')]
good=p.returncode==0 and len(rows)==len(selected) and all(z['passed'] and z['consistent'] for z in rows)
result=dict(variant=v,hashes=hashes,origins=origins,manifest_sha256=manifest_sha,expected=len(selected),observed=len(rows),passed=good,
 failures=[z for z in rows if not z['passed'] or not z['consistent']],returncode=p.returncode,scope='affected preserved cases plus all failure8; screening only')
(out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
assert manifest_sha==hashlib.sha256(manifest.read_bytes()).hexdigest()
fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
if not good:raise SystemExit(1)
subprocess.run(['python3','work/solo28/quick_compare.py',v,'s30f','quick30_'+letter,'work/solo30/g_shapes.txt'],cwd=r,check=True)
print('SCREEN30_COMPLETE '+v,flush=True)
