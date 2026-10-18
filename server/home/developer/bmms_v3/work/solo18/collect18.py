"""Snapshot raw text/CSV evidence and source without running or modifying NPU work."""
from pathlib import Path
import hashlib,json,time,zipfile
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
out=Path('/tmp')/('bmms18_evidence_'+time.strftime('%Y%m%d_%H%M%S')+'.zip')
selected=[];skipped=[];hashes=[]
for base in [d,r/'work/solo18']:
    for p in sorted(base.rglob('*')):
        if not p.is_file() or p.suffix.lower() not in {'.json','.jsonl','.log','.csv','.txt','.py','.asc'}:continue
        if any(x in {'pilot_inputs','medium_cases','dot_once_cases','resident_cases18','build'} for x in p.relative_to(base).parts):continue
        if p.stat().st_size>50*1024*1024:skipped.append(str(p));continue
        selected.append(p)
for v in ['s15i','s17d','s17e','s17f','s17g','s17h','s17i']:
    base=r/'variants'/v
    for name in ['kernel.asc','build/bench','build/bench_cases','build/bench_multi']:
        p=base/name
        if p.is_file():hashes.append(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size))
    selected.extend(p for p in base.iterdir() if p.is_file() and p.suffix in {'.asc','.log','.txt','.h'})
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in selected:z.write(p,p.relative_to(r).as_posix())
    z.writestr('capture_metadata.json',json.dumps(dict(captured_unix=time.time(),hashes=hashes,skipped=skipped,
        scope='Original raw evidence snapshot. Active logs may be incomplete; no pass inferred.'),indent=2))
with zipfile.ZipFile(out) as z:assert z.testzip() is None
print(json.dumps(dict(archive=str(out),bytes=out.stat().st_size,sha256=hashlib.sha256(out.read_bytes()).hexdigest(),files=len(selected),skipped=skipped)))
