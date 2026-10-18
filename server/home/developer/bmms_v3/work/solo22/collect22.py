from pathlib import Path
import hashlib,json,sys,time,zipfile
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
tag,variants,labels=sys.argv[1:4]
assert tag.replace('_','').isalnum()
selected=[];hashes=[]
for label in labels.split(','):
    assert '/' not in label
    selected.extend(p for p in (d/label).rglob('*') if p.is_file() and p.suffix in {'.json','.jsonl','.log','.csv','.txt'})
for v in variants.split(','):
    base=r/'variants'/v
    for name in ['kernel.asc','build/bench','build/bench_cases','build/bench_multi']:
        p=base/name;hashes.append(dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size))
    selected.extend(p for p in base.iterdir() if p.is_file() and p.suffix in {'.asc','.log','.txt','.h'})
selected.extend(p for p in (r/'work/solo22').rglob('*') if p.is_file() and 'build' not in p.parts and p.suffix in {'.py','.sh','.json','.jsonl','.asc','.log','.txt'})
for pattern in ['*_22.log','run22_*.log']:
    selected.extend(p for p in d.glob(pattern))
selected.extend(p for p in d.glob('long_stress21.txt'))
selected.append(d/'long_stress21/fixture_hashes.json')
selected=list(dict.fromkeys(selected))
out=Path('/tmp')/('bmms22_'+tag+'.zip');assert not out.exists()
with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
    for p in selected:z.write(p,p.relative_to(r).as_posix())
    z.writestr('capture_metadata.json',json.dumps(dict(captured_unix=time.time(),hashes=hashes,files=len(selected)),indent=2))
with zipfile.ZipFile(out) as z:assert z.testzip() is None
chunkdir=Path('/tmp')/('bmms22_'+tag+'_chunks');chunkdir.mkdir(exist_ok=False)
blob=out.read_bytes();parts=[]
for i,pos in enumerate(range(0,len(blob),1024*1024)):
    part=blob[pos:pos+1024*1024];name=f'part{i:03d}';(chunkdir/name).write_bytes(part)
    parts.append(dict(name=name,bytes=len(part),sha256=hashlib.sha256(part).hexdigest()))
m=dict(archive=str(out),bytes=len(blob),sha256=hashlib.sha256(blob).hexdigest(),files=len(selected),chunks=str(chunkdir),parts=parts)
(chunkdir/'metadata.json').write_text(json.dumps(m,indent=2));print(json.dumps(m))
