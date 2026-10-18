from pathlib import Path
import hashlib,json,zipfile
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
assert 'FINAL46_A_COMPLETE_NO_AUTOMATIC_SUBMISSION' in (d/'final46_a.log').read_text()
assert 'CONTINUE45_COMPLETE' in (d/'continue45_a.log').read_text()
files=set();hashes={}
for v in ('s45c','s46a'):
    for name in ('kernel.asc','build/bench_cases','build/bench_multi','build/bench'):
        p=r/'variants'/v/name;hashes[str(p.relative_to(r))]=hashlib.sha256(p.read_bytes()).hexdigest()
    files.add(r/'variants'/v/'kernel.asc')
roots=[r/'work/solo46',d/'validation_s46a',d/'stress28_s46a',*d.glob('extra42_*_s46a'),d/'new_precision45_s46a',d/'pool46_a_45c_abba',d/'hangs46_a']
roots.append(d/'continue45_a')
for root in roots:
    files.update(p for p in root.rglob('*') if p.is_file() and p.suffix in ('.asc','.json','.jsonl','.csv','.txt','.log','.py','.sh','.patch','.h'))
for name in ('compile32_s46a_cases.log','compile32_s46a_multi.log','final46_a.log','compile45_s46a_bench.log'):files.add(d/name)
for item in json.loads((d/'validation_s46a/precision_summary.json').read_text())['suites']:files.add(Path(item['manifest']))
files.add(d/'diagnostic42_s41c/cases.txt');files.add(r/'shapes_pool2.txt')
for name in ('bounds45.txt','bounds45/fixture_hashes.json','bounds46_s46a.log','continue45_a.log','gen_bounds45.log'):files.add(d/name)
files.update((d/'bounds45').glob('c*/gold.bin'))
for item in (d/'hangs46_a/s46a').iterdir():files.add(item/'output/y.bin');files.add(d/'pilot_inputs'/item.name/'gold.npy')
files.add(r/'variants/s45a/kernel.asc');files.add(d/'bounds45_s45a.log')
manifest=dict(source_and_exe_sha256=hashes,executable_bytes_included=False,files=[])
dst=Path('/tmp/bmms28_round46_a_final20261015.zip')
with zipfile.ZipFile(dst,'x',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(files):
        rel=str(p.relative_to(r));data=p.read_bytes();z.writestr(rel,data);manifest['files'].append(dict(path=rel,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
    z.writestr('collection_manifest.json',json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(path=str(dst),sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),bytes=dst.stat().st_size,files=len(files))))
