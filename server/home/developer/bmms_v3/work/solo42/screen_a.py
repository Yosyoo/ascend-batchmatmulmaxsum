from pathlib import Path
import json,hashlib,subprocess,fcntl,sys
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s42a';sha=sys.argv[1]
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
manifests=[Path(x['manifest']) for x in json.loads((d/'validation_s33a/precision_summary.json').read_text())['suites']]+[r/'work/solo18/fail_8.txt',d/'owned_stress41.txt',d/'a2_stress42.txt']
selected=[];origins=[]
for p in manifests:
 count=0
 for line in p.read_text().splitlines():
  b,m,n,k=map(int,line.split()[:4])
  if p.name in ('fail_8.txt','owned_stress41.txt','a2_stress42.txt') or (m>=128 and n>=128 and m%128==0 and n%128==0 and k>=256 and k%64==0): selected.append(line);count+=1
 origins.append(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),count=count))
assert 'SCREEN41_C_PRECISION_COMPLETE' in (d/'screen41_c.log').read_text()
out=d/f'diagnostic42_{v}';out.mkdir(exist_ok=False);manifest=out/'cases.txt';manifest.write_text('\n'.join(selected)+'\n')
exe=r/f'variants/{v}/build/bench_cases';lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
p=subprocess.run([str(exe),str(manifest)],capture_output=True,text=True,cwd=r,timeout=180);(out/'precision.log').write_text(p.stdout+p.stderr)
rows=[json.loads(z) for z in p.stdout.splitlines() if z.startswith('{')];good=p.returncode==0 and len(rows)==len(selected) and all(z['passed'] and z['consistent'] for z in rows)
(out/'summary.json').write_text(json.dumps(dict(variant=v,expected=len(selected),observed=len(rows),passed=good,origins=origins,hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [r/f'variants/{v}/kernel.asc',exe]},manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),failures=[z for z in rows if not z['passed'] or not z['consistent']]),indent=2))
print('PRECISION42_A',good,len(rows),flush=True);fcntl.flock(lock,fcntl.LOCK_UN);lock.close();assert good
for ta,tb in ((0,0),(0,1),(1,0),(1,1)):
 subprocess.run(['python3','work/solo31/quick_layout_compare.py',v,'s41c',f'quick42_a_{ta}{tb}','work/solo42/shapes_a.txt','1',str(ta),str(tb)],cwd=r,check=True)
 if ta==0 and tb==0:
  comparison=json.loads((d/'quick42_a_00/comparison.json').read_text())
  left,right=comparison['orders'];wins=[x['shape'] for x,y in zip(left['ratios'],right['ratios']) if x['ratio']<.97 and y['ratio']<.97]
  print('WINNING_SHAPES42_A',wins,flush=True)
  if not wins:break
print('SCREEN42_A_COMPLETE',flush=True)
