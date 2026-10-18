from pathlib import Path
import hashlib,json,zipfile
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
assert 'FINAL43_A_COMPLETE_NO_AUTOMATIC_SUBMISSION' in (d/'final43_a.log').read_text()
files=set();hashes={}
for v in ('s41c','s43a'):
    for name in ('kernel.asc','build/bench_cases','build/bench_multi','build/bench'):
        if v=='s41c' and name=='build/bench':continue
        p=r/'variants'/v/name;hashes[str(p.relative_to(r))]=hashlib.sha256(p.read_bytes()).hexdigest()
    files.add(r/'variants'/v/'kernel.asc')
for root in [r/'work/solo43',d/'diagnostic43_s43a',*d.glob('quick43_a_*'),d/'validation_s43a',d/'stress28_s43a',*d.glob('extra42_*_s43a'),d/'new_precision43_s43a',d/'pool43_a_33_abba',d/'hangs43_a']:
    files.update(p for p in root.rglob('*') if p.is_file() and p.suffix in ('.asc','.json','.jsonl','.csv','.txt','.log','.py','.sh','.patch'))
for name in ('screen43_a.log','compile32_s43a_cases.log','compile32_s43a_multi.log','final43_a.log','compile43_s43a_bench.log'):files.add(d/name)
for origin in json.loads((r/'work/solo43/experiment_a_lock.json').read_text())['origins']:files.add(Path(origin['manifest']))
for item in json.loads((d/'validation_s43a/precision_summary.json').read_text())['suites']:files.add(Path(item['manifest']))
files.add(d/'diagnostic42_s41c/cases.txt')
files.add(r/'shapes_pool2.txt')
for item in (d/'hangs43_a/s43a').iterdir():
    files.add(item/'output/y.bin');files.add(d/'pilot_inputs'/item.name/'gold.npy')
manifest=dict(source_and_exe_sha256=hashes,executable_bytes_included=False,files=[])
dst=Path('/tmp/bmms_round43_a_final20261015.zip')
with zipfile.ZipFile(dst,'x',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(files):
        rel=str(p.relative_to(r));data=p.read_bytes();z.writestr(rel,data)
        manifest['files'].append(dict(path=rel,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    z.writestr('collection_manifest.json',json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(path=str(dst),sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),bytes=dst.stat().st_size,files=len(files))))
