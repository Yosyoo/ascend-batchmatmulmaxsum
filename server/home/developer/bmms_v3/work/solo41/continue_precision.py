from pathlib import Path
import json,subprocess,fcntl,hashlib
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';out=d/'continue41_a';out.mkdir(exist_ok=False)
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
summary=[]
for v,manifest,first in [('s33a',d/'owned_stress41.txt',d/'diagnostic41_s41a/baseline_stress.log'),('s41a',d/'diagnostic41_s41a/cases.txt',d/'diagnostic41_s41a/precision.log')]:
 lines=manifest.read_text().splitlines();rows=[json.loads(x) for x in first.read_text().splitlines() if x.startswith('{')]
 for x in rows:x['global_case']=x['case']
 cursor=len(rows);attempt=0
 while cursor<len(lines):
  part=out/f'{v}_remaining_{cursor}.txt';part.write_text('\n'.join(lines[cursor:])+'\n')
  p=subprocess.run([str(r/f'variants/{v}/build/bench_cases'),str(part)],capture_output=True,text=True,timeout=900,cwd=r)
  (out/f'{v}_{attempt}.log').write_text(p.stdout+p.stderr)
  new=[json.loads(x) for x in p.stdout.splitlines() if x.startswith('{')]
  assert new and all(x['case']==i for i,x in enumerate(new)),(v,cursor,p.returncode)
  for x in new:x['global_case']=cursor+x['case']
  rows+=new;cursor+=len(new);attempt+=1
  print(v,'completed',cursor,'/',len(lines),flush=True)
 assert len(rows)==len(lines)
 result=dict(variant=v,manifest=str(manifest),manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),expected=len(lines),observed=len(rows),passed=all(x['passed'] and x['consistent'] for x in rows),failures=[x for x in rows if not x['passed'] or not x['consistent']],rows=rows)
 (out/f'{v}.json').write_text(json.dumps(result,indent=2)+'\n');summary.append({k:z for k,z in result.items() if k!='rows'})
(out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('CONTINUE41_COMPLETE',flush=True)
