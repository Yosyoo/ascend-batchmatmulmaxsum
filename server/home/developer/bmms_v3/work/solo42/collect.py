from pathlib import Path
import hashlib,json,zipfile
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';label='round42_a20261015'
terminal=(d/'screen42_a.log').read_text()
assert 'SCREEN42_A_COMPLETE' in terminal or ('PRECISION42_A False' in terminal and 'AssertionError' in terminal)
files=set();hashes={}
for v in ('s41c','s42a'):
 for name in ('kernel.asc','build/bench_cases','build/bench_multi'):
  p=r/'variants'/v/name;hashes[str(p.relative_to(r))]=hashlib.sha256(p.read_bytes()).hexdigest()
 files.add(r/'variants'/v/'kernel.asc')
roots=[r/'work/solo42',d/'validation_s41c',d/'stress28_s41c',*d.glob('extra42_*'),*d.glob('diagnostic42_*'),*d.glob('quick42_*')]
for root in roots:
 if root.is_file():files.add(root);continue
 for p in root.rglob('*'):
  if p.is_file() and p.suffix in ('.asc','.json','.jsonl','.csv','.txt','.log','.py','.sh','.patch','.ini') and '/build/' not in str(p):files.add(p)
for f in ('screen42_a.log','compile32_s42a_cases.log','compile32_s42a_multi.log','baseline42_a.log','validate41_c.log','stress41_c.log','extra42_c.log','gen42.log','a2_stress42.txt','a2_stress42/fixture_hashes.json'):
 files.add(d/f)
for suite in json.loads((d/'validation_s41c/precision_summary.json').read_text())['suites']:files.add(Path(suite['manifest']))
for suite_name in ('balanced_stress23','kparallel_batch_stress23','kparallel_stress23','pair_stress23','long_stress21','tiny_stress23','narrow_stress33','pad_legal32','pad_stress32','batch_stress30','tile128_stress30','direct_stress32','whole_stress30','short_resident_stress31'):
 files.add(d/(suite_name+'.txt'));files.add(d/suite_name/'fixture_hashes.json')
for pattern in ('stress28_s41c','extra42_*_s41c'):
 for p in d.glob(pattern):
  if p.is_dir():
   for f in p.glob('*.json'):files.add(f)
meta=json.loads((d/'a2_stress42/fixture_hashes.json').read_text())
for item in meta:
 for name,h in item['files'].items():
  p=d/'a2_stress42'/f"c{item['case']:03d}"/name
  assert p.stat().st_size==h['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==h['sha256']
manifest=dict(label=label,source_and_exe_sha256=hashes,executable_bytes_included=False,all_160_new_fixtures_unchanged=True,files=[])
dst=Path('/tmp')/('bmms28_'+label+'.zip')
with zipfile.ZipFile(dst,'x',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(files):
  rel=str(p.relative_to(r));data=p.read_bytes();z.writestr(rel,data)
  manifest['files'].append(dict(path=rel,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
 z.writestr('collection_manifest.json',json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(path=str(dst),sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),bytes=dst.stat().st_size,files=len(files))))
