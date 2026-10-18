from pathlib import Path
import json,hashlib,subprocess,fcntl,sys
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s41a';sha=sys.argv[1]
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
manifests=[Path(x['manifest']) for x in json.loads((d/'validation_s33a/precision_summary.json').read_text())['suites']]+[r/'work/solo18/fail_8.txt',d/'owned_stress41.txt']
selected=[];origins=[]
for p in manifests:
 count=0
 for line in p.read_text().splitlines():
  b,m,n,k=map(int,line.split()[:4])
  if p.name in ('fail_8.txt','owned_stress41.txt') or (b>=10 and m>=256 and m%128==0 and n%128==0 and 256<=k<=1024 and k%64==0): selected.append(line);count+=1
 origins.append(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),count=count))
out=d/f'diagnostic41_{v}';out.mkdir(exist_ok=False);manifest=out/'cases.txt';manifest.write_text('\n'.join(selected)+'\n')
exe=r/f'variants/{v}/build/bench_cases';lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
ref_manifest=d/'owned_stress41.txt'
base_run=subprocess.run([str(r/'variants/s33a/build/bench_cases'),str(ref_manifest)],capture_output=True,text=True,cwd=r,timeout=900)
(out/'baseline_stress.log').write_text(base_run.stdout+base_run.stderr)
base_rows=[json.loads(z) for z in base_run.stdout.splitlines() if z.startswith('{')]
base_good=base_run.returncode==0 and len(base_rows)==160 and all(z['passed'] and z['consistent'] for z in base_rows)
(out/'baseline_summary.json').write_text(json.dumps(dict(passed=base_good,observed=len(base_rows),failures=[z for z in base_rows if not z['passed'] or not z['consistent']]),indent=2))
print('BASE_STRESS41',base_good,len(base_rows),flush=True)
p=subprocess.run([str(exe),str(manifest)],capture_output=True,text=True,cwd=r,timeout=900);(out/'precision.log').write_text(p.stdout+p.stderr)
rows=[json.loads(z) for z in p.stdout.splitlines() if z.startswith('{')];good=p.returncode==0 and len(rows)==len(selected) and all(z['passed'] and z['consistent'] for z in rows)
(out/'summary.json').write_text(json.dumps(dict(variant=v,expected=len(selected),observed=len(rows),passed=good,origins=origins,hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [r/f'variants/{v}/kernel.asc',exe]},manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),failures=[z for z in rows if not z['passed'] or not z['consistent']]),indent=2))
print('PRECISION41_A',good,len(rows),flush=True);fcntl.flock(lock,fcntl.LOCK_UN);lock.close();assert good
subprocess.run(['python3','work/solo31/quick_layout_compare.py',v,'s33a','quick41_a_00','work/solo41/shapes.txt','1','0','0'],cwd=r,check=True)
c=json.loads((d/'quick41_a_00/comparison.json').read_text())
wins=[a['shape'] for a,b in zip(c['orders'][0]['ratios'],c['orders'][1]['ratios']) if a['ratio']<0.97 and b['ratio']<0.97]
print('STABLE_NN_WINNERS',json.dumps(wins),flush=True)
if wins:
 for ta,tb in ((0,1),(1,0),(1,1)):
  subprocess.run(['python3','work/solo31/quick_layout_compare.py',v,'s33a',f'quick41_a_{ta}{tb}','work/solo41/shapes.txt','1',str(ta),str(tb)],cwd=r,check=True)
print('SCREEN41_A_COMPLETE',flush=True)
