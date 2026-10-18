from pathlib import Path
import fcntl,hashlib,json,subprocess,sys
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s33b';sha=sys.argv[1]
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
manifests=[r/'delivery4/validation/cases.txt',r/'solo13_data/generic_nt_cases.txt',r/'solo13_data/nt_cases.txt',r/'solo11_data/copy_cases.txt',d/'medium_cases.txt',r/'solo14_data/balanced_cases.txt',r/'solo14_data/narrow_legal_cases.txt',r/'solo14_data/split16_cases.txt',r/'solo14_data/pair_edge_cases.txt',r/'solo14_data/long_sum_cases.txt',r/'solo8_data/narrow_cases.txt',r/'solo8_data/narrow_extra_cases.txt',r/'solo6_data/large_cases.txt',r/'work/solo18/fail_8.txt']
selected=[];origins=[]
for p in manifests:
 before=hashlib.sha256(p.read_bytes()).hexdigest();count=0
 for line in p.read_text().splitlines():
  b,m,n,k=map(int,line.split()[:4])
  if p.name=='fail_8.txt' or (1024<=m<=8192 and 8<n<=32 and 32<=k<=128 and k%8==0):selected.append(line);count+=1
 origins.append(dict(path=str(p),sha256=before,count=count));assert before==hashlib.sha256(p.read_bytes()).hexdigest()
selected.extend((d/'narrow_stress33.txt').read_text().splitlines())
fixture=d/'narrow_stress33';metadata=json.loads((fixture/'fixture_hashes.json').read_text())
def check():
 for item in metadata:
  for name,z in item['files'].items():
   assert hashlib.sha256((fixture/f"c{item['case']:03d}"/name).read_bytes()).hexdigest()==z['sha256']
check()
out=d/f'diagnostic33_{v}';out.mkdir(exist_ok=False);manifest=out/'cases.txt';manifest.write_text('\n'.join(selected)+'\n')
exe=r/f'variants/{v}/build/bench_cases';hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (r/f'variants/{v}/kernel.asc',exe)}
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
p=subprocess.run([str(exe),str(manifest)],cwd=r,capture_output=True,text=True,timeout=900)
(out/'precision.log').write_text(p.stdout+p.stderr);check();rows=[json.loads(z) for z in p.stdout.splitlines() if z.startswith('{')]
good=p.returncode==0 and len(rows)==len(selected) and all(z['passed'] and z['consistent'] for z in rows)
(out/'summary.json').write_text(json.dumps(dict(variant=v,expected=len(selected),observed=len(rows),passed=good,origins=origins,hashes=hashes,manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),failures=[z for z in rows if not z['passed'] or not z['consistent']]),indent=2)+'\n')
print('PRECISION33_B',good,len(rows),flush=True);fcntl.flock(lock,fcntl.LOCK_UN);lock.close();assert good
for ta,tb in ((0,0),(0,1),(1,0),(1,1)):
 subprocess.run(['python3','work/solo31/quick_layout_compare.py',v,'s32j',f'quick33_b_{ta}{tb}','work/solo33/shapes.txt','1',str(ta),str(tb)],cwd=r,check=True)
print('SCREEN33_B_COMPLETE',flush=True)
