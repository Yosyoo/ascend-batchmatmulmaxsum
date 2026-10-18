from pathlib import Path
import hashlib,json,fcntl,subprocess,time,sys,re
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s32a';sha=sys.argv[1]
deadline=time.monotonic()+1800
while 'COMPILE32_SCREEN_COMPLETE' not in (d/'compile32_a.log').read_text(errors='replace'):
 assert time.monotonic()<deadline
 for name in ('compile32_s32a_cases.log','compile32_s32a_multi.log'):
  if (d/name).exists():assert 'error:' not in (d/name).read_text(errors='replace')
 time.sleep(5)
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
out=d/f'diagnostic32_{v}';out.mkdir(exist_ok=False)
validate=(r/'work/solo17/validate.py').read_text();block=validate[validate.index('suites=['):validate.index('if history_only:suites=')]
manifests=[(r if prefix=='root' else d)/path for prefix,path in re.findall(r"(root|data)/'([^']+)'",block)]
assert len(manifests)==20
selected=[];origins=[]
for p in manifests+[r/'work/solo18/fail_8.txt',d/'whole_stress30.txt',d/'short_resident_stress31.txt',d/'direct_stress32.txt']:
 old=hashlib.sha256(p.read_bytes()).hexdigest();count=0
 for line in p.read_text().splitlines():
  b,m,n,k,typ,ta,tb=map(int,line.split()[:7])
  keep=m<=32 and 32<n<=128 and m*n>32 and 64<=k<=256 and k%16==0
  if p.name in ('fail_8.txt','whole_stress30.txt','short_resident_stress31.txt','direct_stress32.txt'):keep=True
  if keep:selected.append(line);count+=1
 origins.append(dict(path=str(p),sha256=old,selected=count));assert old==hashlib.sha256(p.read_bytes()).hexdigest()
def check():
 for label in ('direct_stress32','short_resident_stress31'):
  fixture=d/label;metadata=json.loads((fixture/'fixture_hashes.json').read_text())
  for item in metadata:
   for name,z in item['files'].items():
    p=fixture/f"c{item['case']:03d}"/name
    assert p.stat().st_size==z['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==z['sha256']
check();manifest=out/'cases.txt';manifest.write_text('\n'.join(selected)+'\n');case_sha=hashlib.sha256(manifest.read_bytes()).hexdigest()
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (r/f'variants/{v}/kernel.asc',r/f'variants/{v}/build/bench_cases')}
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
p=subprocess.run([str(r/f'variants/{v}/build/bench_cases'),str(manifest)],cwd=r,capture_output=True,text=True,timeout=900)
(out/'precision.log').write_text(p.stdout+p.stderr);rows=[json.loads(z) for z in p.stdout.splitlines() if z.startswith('{')]
check();assert case_sha==hashlib.sha256(manifest.read_bytes()).hexdigest()
good=p.returncode==0 and len(rows)==len(selected) and all(z['passed'] and z['consistent'] for z in rows)
(out/'summary.json').write_text(json.dumps(dict(variant=v,hashes=hashes,origins=origins,manifest_sha256=case_sha,
 expected=len(selected),observed=len(rows),passed=good,inputs_unchanged=True,returncode=p.returncode,
 failures=[z for z in rows if not z['passed'] or not z['consistent']]),indent=2)+'\n')
print('PRECISION32_A',good,len(rows),flush=True);fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
if not good:raise SystemExit(1)
for ta in (0,1):
 subprocess.run(['python3','work/solo31/quick_layout_compare.py',v,'s31k',f'quick32_a_{ta}0','work/solo32/a_shapes.txt','1',str(ta),'0'],cwd=r,check=True)
print('SCREEN32_A_COMPLETE',flush=True)
