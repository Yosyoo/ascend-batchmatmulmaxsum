from pathlib import Path
import hashlib,json,time,zipfile
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
selected=[d/'manual_cases18.txt'];hashes=[]
for label in ['validation_s17k','diagnostic_k','pilot_k_base','pilot_base_k','pool18_s17k','hangs18_k','manual_base_j','manual_k_base','manual_base_k']:
    selected.extend(p for p in (d/label).rglob('*') if p.is_file() and p.suffix in {'.json','.jsonl','.log','.csv','.txt'})
for name in ['run_k_final.log','k_launcher.log','k_launcher_retry.log','manual_base_j.log','gen_k_cases.log','manual_k_base.log','manual_base_k.log']:
    p=d/name
    if p.exists():selected.append(p)
for name in ['run_k_final.py','launch_k.sh','resource_s17k_before_edit.json','gen_k_cases.py']:
    selected.append(r/'work/solo18'/name)
for v in ['s15i','s17g','s17i','s17j','s17k']:
    base=r/'variants'/v
    for name in ['kernel.asc','build/bench','build/bench_cases','build/bench_multi']:
        p=base/name
        if p.exists():hashes.append(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size))
    selected.extend(p for p in base.iterdir() if p.is_file() and p.suffix in {'.asc','.log','.txt','.h'})
out=Path('/tmp')/('bmms18_k_'+time.strftime('%Y%m%d_%H%M%S')+'.zip')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in selected:z.write(p,p.relative_to(r).as_posix())
    z.writestr('capture_metadata.json',json.dumps(dict(captured_unix=time.time(),hashes=hashes,files=len(selected)),indent=2))
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print(json.dumps(dict(archive=str(out),bytes=out.stat().st_size,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),files=len(selected))))
