from pathlib import Path
import hashlib,json,zipfile
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';label='round41_acde20261015'
assert 'CONTINUE41_COMPLETE' in (d/'continue41.log').read_text()
assert 'SCREEN41_D_COMPLETE' in (d/'screen41_d.log').read_text()
assert 'SCREEN41_E_COMPLETE' in (d/'screen41_e.log').read_text()
files=set();hashes={}
for v in ('s33a','s41a','s41c','s41d','s41e'):
 for name in ('kernel.asc','build/bench_cases','build/bench_multi'):
  p=r/'variants'/v/name;hashes[str(p.relative_to(r))]=hashlib.sha256(p.read_bytes()).hexdigest()
 files.add(r/'variants'/v/'kernel.asc')
roots=[r/'work/solo41',d/'continue41_a',*d.glob('diagnostic41_*'),*d.glob('quick41_*')]
for root in roots:
 for p in root.rglob('*'):
  if p.is_file() and p.suffix in ('.asc','.json','.jsonl','.csv','.txt','.log','.py','.sh') and '/build/' not in str(p):files.add(p)
for v in ('a','c','d','e'):
 for f in (f'screen41_{v}.log',f'compile32_s41{v}_cases.log',f'compile32_s41{v}_multi.log'):files.add(d/f)
for f in ('continue41.log','gen41.log','owned_stress41.txt','owned_stress41/fixture_hashes.json'):files.add(d/f)
# Keep original first-failure tensors locally; all 160 immutable fixtures remain on server.
for p in (d/'owned_stress41/c012').iterdir():files.add(p)
meta=json.loads((d/'owned_stress41/fixture_hashes.json').read_text())
for item in meta:
 for name,h in item['files'].items():
  p=d/'owned_stress41'/f"c{item['case']:03d}"/name
  assert p.stat().st_size==h['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==h['sha256']
manifest=dict(label=label,variants=['s33a','s41a','s41c','s41d','s41e'],source_and_exe_sha256=hashes,all_160_fixtures_unchanged=True,files=[])
dst=Path('/tmp')/('bmms28_'+label+'.zip')
with zipfile.ZipFile(dst,'x',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(files):
  rel=str(p.relative_to(r));data=p.read_bytes();z.writestr(rel,data)
  manifest['files'].append(dict(path=rel,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
 z.writestr('collection_manifest.json',json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(path=str(dst),sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),bytes=dst.stat().st_size,files=len(files))))
