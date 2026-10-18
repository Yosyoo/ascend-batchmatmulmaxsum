from pathlib import Path
import hashlib,json,zipfile
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';label='round40_a20261015'
assert 'SCREEN40_A_COMPLETE' in (d/'screen40_a.log').read_text()
files=set();hashes={}
for v in ('s33a','s40a'):
 for name in ('kernel.asc','build/bench_cases','build/bench_multi'):
  p=r/'variants'/v/name;hashes[str(p.relative_to(r))]=hashlib.sha256(p.read_bytes()).hexdigest()
 files.add(r/'variants'/v/'kernel.asc')
for root in [d/'diagnostic40_s40a',r/'work/solo40',*d.glob('quick40_a_*')]:
 for p in root.rglob('*'):
  if p.is_file() and p.suffix in ('.asc','.json','.jsonl','.csv','.txt','.log','.py','.sh') and '/build/' not in str(p):files.add(p)
for f in ('screen40_a.log','compile32_s40a_cases.log','compile32_s40a_multi.log'):files.add(d/f)
manifest=dict(label=label,variants=['s33a','s40a'],source_and_exe_sha256=hashes,files=[])
dst=Path('/tmp')/('bmms28_'+label+'.zip')
with zipfile.ZipFile(dst,'x',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(files):
  rel=str(p.relative_to(r));data=p.read_bytes();z.writestr(rel,data)
  manifest['files'].append(dict(path=rel,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
 z.writestr('collection_manifest.json',json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(path=str(dst),sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),bytes=dst.stat().st_size,files=len(files))))
