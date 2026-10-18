from pathlib import Path
import hashlib,json,time,zipfile
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
selected=[];hashes=[]
for label in ['validation_s17j','diagnostic_j','pilot_j_base','pilot_base_j','pool18_s17j','hangs18_j','layout_gi','layout_ig']:
    selected.extend(p for p in (d/label).rglob('*') if p.is_file() and p.suffix in {'.json','.jsonl','.log','.csv','.txt'})
for name in ['run_j_final.log','j_launcher.log','j_launcher_retry.log','layout_gi.log','layout_ig.log']:
    p=d/name
    if p.exists():selected.append(p)
for name in ['run_j_final.py','launch_j.sh','resource_s17j_before_edit.json','s17j_missing_header_build.log']:
    selected.append(r/'work/solo18'/name)
for v in ['s15i','s17g','s17i','s17j']:
    base=r/'variants'/v
    for name in ['kernel.asc','build/bench','build/bench_cases','build/bench_multi']:
        p=base/name
        if p.exists():hashes.append(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size))
    selected.extend(p for p in base.iterdir() if p.is_file() and p.suffix in {'.asc','.log','.txt','.h'})
out=Path('/tmp')/('bmms18_j_'+time.strftime('%Y%m%d_%H%M%S')+'.zip')
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in selected:z.write(p,p.relative_to(r).as_posix())
    z.writestr('capture_metadata.json',json.dumps(dict(captured_unix=time.time(),hashes=hashes,files=len(selected)),indent=2))
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print(json.dumps(dict(archive=str(out),bytes=out.stat().st_size,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),files=len(selected))))
