from pathlib import Path
import hashlib,json,zipfile
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
assert 'SCREEN43_A_COMPLETE' in (d/'screen43_a.log').read_text()
files=set();hashes={}
for v in ('s41c','s43a'):
    for name in ('kernel.asc','build/bench_cases','build/bench_multi'):
        p=r/'variants'/v/name;hashes[str(p.relative_to(r))]=hashlib.sha256(p.read_bytes()).hexdigest()
    files.add(r/'variants'/v/'kernel.asc')
for root in [r/'work/solo43',d/'diagnostic43_s43a',*d.glob('quick43_a_*')]:
    files.update(p for p in root.rglob('*') if p.is_file() and p.suffix in ('.asc','.json','.jsonl','.csv','.txt','.log','.py','.sh','.patch'))
for name in ('screen43_a.log','compile32_s43a_cases.log','compile32_s43a_multi.log'):files.add(d/name)
for origin in json.loads((r/'work/solo43/experiment_a_lock.json').read_text())['origins']:files.add(Path(origin['manifest']))
manifest=dict(source_and_exe_sha256=hashes,executable_bytes_included=False,files=[])
dst=Path('/tmp/bmms_round43_a20261015.zip')
with zipfile.ZipFile(dst,'x',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(files):
        rel=str(p.relative_to(r));data=p.read_bytes();z.writestr(rel,data)
        manifest['files'].append(dict(path=rel,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    z.writestr('collection_manifest.json',json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(path=str(dst),sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),bytes=dst.stat().st_size,files=len(files))))
