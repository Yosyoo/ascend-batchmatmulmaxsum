from pathlib import Path
import hashlib,json,sys,zipfile
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';label=sys.argv[1];variants=sys.argv[2].split(',');extras=sys.argv[3:]
assert label.replace('_','').isalnum() and all(z.startswith(('s26','s28','s29','s30','s31','s32')) and z.isalnum() for z in variants)
dest=Path('/tmp')/('bmms28_'+label+'.zip');assert not dest.exists()
files=set();hashes={}
for v in variants:
 for name in ('kernel.asc','bench','bench_cases','bench_multi'):
  p=r/'variants'/v/(name if name=='kernel.asc' else 'build/'+name)
  if p.exists():hashes[str(p.relative_to(r))]=hashlib.sha256(p.read_bytes()).hexdigest()
 for root in (r/'variants'/v,d/('diagnostic_28_'+v),d/('validation_'+v),d/('stress28_'+v)):
  if root.exists():
   for p in root.rglob('*'):
    if p.is_file() and p.suffix in ('.asc','.json','.jsonl','.log','.csv','.txt','.py','.sh') and '/CMakeFiles/' not in str(p):files.add(p)
 for p in d.glob('*28*'+v+'*.log'):files.add(p)
for p in d.glob('*32*.log'):files.add(p)
for x in extras:
 root=(d/x).resolve();root.relative_to(d.resolve())
 assert root.exists()
 for p in root.rglob('*'):
  if p.is_file() and p.suffix in ('.json','.jsonl','.log','.csv','.txt'):files.add(p)
for f in ('balanced_stress23','kparallel_batch_stress23','kparallel_stress23','pair_stress23','long_stress21','tiny_stress23'):
 files.add(d/f/'fixture_hashes.json')
manifest=dict(label=label,variants=variants,source_and_exe_sha256=hashes,files=[])
with zipfile.ZipFile(dest,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for p in sorted(files):
  rel=str(p.relative_to(r));data=p.read_bytes();z.writestr(rel,data)
  manifest['files'].append(dict(path=rel,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
 z.writestr('collection_manifest.json',json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(path=str(dest),bytes=dest.stat().st_size,files=len(files),sha256=hashlib.sha256(dest.read_bytes()).hexdigest())),flush=True)
