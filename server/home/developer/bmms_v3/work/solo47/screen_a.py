from pathlib import Path
import json,hashlib,subprocess,fcntl,sys
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s47a';sha=sys.argv[1]
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
manifests=[Path(x['manifest']) for x in json.loads((d/'validation_s46a/precision_summary.json').read_text())['suites']]+[r/'work/solo18/fail_8.txt']
selected=[];origins=[]
for p in manifests:
 count=0
 for line in p.read_text().splitlines():
  b,m,n,k=map(int,line.split()[:4])
  if p.name=='fail_8.txt' or (m==1 and n==1 and k==32): selected.append(line);count+=1
 origins.append(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),count=count))
out=d/f'diagnostic47_{v}';out.mkdir(exist_ok=False);manifest=out/'cases.txt';manifest.write_text('\n'.join(selected)+'\n')
exe=r/f'variants/{v}/build/bench_cases';lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
p=subprocess.run([str(exe),str(manifest)],capture_output=True,text=True,cwd=r,timeout=900);(out/'precision.log').write_text(p.stdout+p.stderr)
rows=[json.loads(z) for z in p.stdout.splitlines() if z.startswith('{')];good=p.returncode==0 and len(rows)==len(selected) and all(z['passed'] and z['consistent'] for z in rows)
(out/'summary.json').write_text(json.dumps(dict(variant=v,expected=len(selected),observed=len(rows),passed=good,origins=origins,hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [r/f'variants/{v}/kernel.asc',exe]},manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),failures=[z for z in rows if not z['passed'] or not z['consistent']]),indent=2))
print('PRECISION47_A',good,len(rows),flush=True);fcntl.flock(lock,fcntl.LOCK_UN);lock.close();assert good
subprocess.run([str(r/'work/solo47/guard/build/guard'),str(manifest)],cwd=r,check=True)
for dtype in (1,2):
 subprocess.run(['python3','work/solo31/quick_layout_compare.py',v,'s46a',f'quick47_a_d{dtype}','work/solo47/shapes.txt',str(dtype),'0','0'],cwd=r,check=True)
print('SCREEN47_A_COMPLETE',flush=True)
