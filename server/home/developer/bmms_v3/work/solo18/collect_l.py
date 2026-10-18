from pathlib import Path
import hashlib,json,time,zipfile
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
for label in ['generic_l_g_base','generic_base_g_l']:
    rows=[json.loads(x) for x in (d/label/'results.jsonl').read_text().splitlines()]
    assert len(rows)==18 and all(x['passed'] for x in rows)
selected=[];hashes=[]
for label in ['diagnostic_l','generic_l_g_base','generic_base_g_l']:
    selected.extend(p for p in (d/label).rglob('*') if p.is_file() and p.suffix in {'.json','.jsonl','.log','.csv','.txt'})
for name in ['run_l_pilot.log','l_launcher.log']:
    selected.append(d/name)
for name in ['run_l_pilot.py','launch_l.sh','resource_s17l_before_edit.json']:
    selected.append(r/'work/solo18'/name)
selected.extend(p for p in (r/'work/solo18/full_probe').iterdir() if p.is_file())
for v in ['s15i','s17g','s17l']:
    base=r/'variants'/v
    for name in ['kernel.asc','build/bench','build/bench_cases','build/bench_multi']:
        p=base/name
        hashes.append(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size))
    selected.extend(p for p in base.iterdir() if p.is_file() and p.suffix in {'.asc','.log','.txt','.h'})
out=Path('/tmp/bmms18_l_20261009.zip');assert not out.exists()
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in selected:z.write(p,p.relative_to(r).as_posix())
    z.writestr('capture_metadata.json',json.dumps(dict(captured_unix=time.time(),hashes=hashes,files=len(selected)),indent=2))
with zipfile.ZipFile(out) as z:assert z.testzip() is None
chunkdir=Path('/tmp/bmms18_l_chunks_20261009');chunkdir.mkdir(exist_ok=False)
blob=out.read_bytes();parts=[]
for i,pos in enumerate(range(0,len(blob),1024*1024)):
    part=blob[pos:pos+1024*1024];name=f'part{i:03d}'
    (chunkdir/name).write_bytes(part);parts.append(dict(name=name,bytes=len(part),sha256=hashlib.sha256(part).hexdigest()))
metadata=dict(archive=str(out),bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest(),files=len(selected),chunks=str(chunkdir),parts=parts)
(chunkdir/'metadata.json').write_text(json.dumps(metadata,indent=2))
print(json.dumps(metadata))
