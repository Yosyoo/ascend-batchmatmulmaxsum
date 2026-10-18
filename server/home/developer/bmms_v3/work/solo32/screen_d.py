from pathlib import Path
import subprocess,time,json,hashlib,fcntl,sys
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s32d';sha=sys.argv[1]
deadline=time.monotonic()+1800
while 'COMPILE32_SCREEN_COMPLETE' not in (d/'compile32_d.log').read_text(errors='replace') or 'GENERATED_128_SHORT_RESIDENT_STRESS' not in (d/'gen31_stress.log').read_text(errors='replace'):
 assert time.monotonic()<deadline
 for name in ('compile31_s32d_cases.log','compile31_s32d_multi.log'):
  if (d/name).exists():assert 'error:' not in (d/name).read_text(errors='replace')
 time.sleep(5)
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
out=d/'diagnostic32_s32d';out.mkdir(exist_ok=False)
manifests=[r/'delivery4/validation/cases.txt',r/'solo13_data/generic_nt_cases.txt',r/'solo13_data/nt_cases.txt',r/'solo11_data/copy_cases.txt',d/'medium_cases.txt',r/'solo14_data/balanced_cases.txt',r/'work/solo18/fail_8.txt',d/'whole_stress30.txt',d/'short_resident_stress31.txt']
selected=[];origins=[]
for p in manifests:
 before=hashlib.sha256(p.read_bytes()).hexdigest();count=0
 for line in p.read_text().splitlines():
  b,m,n,k=map(int,line.split()[:4])
  keep=m>=256 and n>=256 and k<=128 and k%16==0 and m%64==0 and n%128==0 and (b*m*n*k >=1<<28 or n>=8*m)
  if p.name in ('fail_8.txt','whole_stress30.txt','short_resident_stress31.txt'):keep=True
  if keep:selected.append(line);count+=1
 origins.append(dict(path=str(p),sha256=before,selected=count));assert before==hashlib.sha256(p.read_bytes()).hexdigest()
fixture=d/'short_resident_stress31';meta=fixture/'fixture_hashes.json';metadata=json.loads(meta.read_text());meta_sha=hashlib.sha256(meta.read_bytes()).hexdigest()
def check():
 assert hashlib.sha256(meta.read_bytes()).hexdigest()==meta_sha
 for item in metadata:
  for name,z in item['files'].items():
   p=fixture/f"c{item['case']:03d}"/name
   assert p.stat().st_size==z['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==z['sha256']
check();manifest=out/'cases.txt';manifest.write_text('\n'.join(selected)+'\n');case_sha=hashlib.sha256(manifest.read_bytes()).hexdigest()
exe=r/f'variants/{v}/build/bench_cases';hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (exe,r/f'variants/{v}/kernel.asc')}
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX)
p=subprocess.run([str(exe),str(manifest)],cwd=r,capture_output=True,text=True,timeout=900)
(out/'precision.log').write_text(p.stdout+p.stderr);rows=[json.loads(z) for z in p.stdout.splitlines() if z.startswith('{')]
check();assert case_sha==hashlib.sha256(manifest.read_bytes()).hexdigest()
good=p.returncode==0 and len(rows)==len(selected) and all(z['passed'] and z['consistent'] for z in rows)
(out/'summary.json').write_text(json.dumps(dict(variant=v,hashes=hashes,origins=origins,manifest_sha256=case_sha,
 fixture_metadata_sha256=meta_sha,inputs_unchanged=True,expected=len(selected),observed=len(rows),passed=good,
 failures=[z for z in rows if not z['passed'] or not z['consistent']],returncode=p.returncode),indent=2)+'\n')
print('PRECISION32_D',good,len(rows),flush=True);fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
if not good:raise SystemExit(1)
for ta,tb in ((0,0),(0,1),(1,0),(1,1)):
 subprocess.run(['python3','work/solo31/quick_layout_compare.py',v,'s31k',f'quick32_d_{ta}{tb}','work/solo31/native_shapes.txt','1',str(ta),str(tb)],cwd=r,check=True)
print('SCREEN32_D_COMPLETE',flush=True)
