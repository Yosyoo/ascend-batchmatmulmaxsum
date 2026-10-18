from pathlib import Path
import hashlib,json,zipfile,sys
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';label=sys.argv[1];extra=sys.argv[2]
assert label.replace('_','').isalnum() and extra.replace('_','').isalnum()
dest=Path('/tmp')/('bmms28_'+label+'.zip');assert not dest.exists()
root=d/extra;assert (root/'comparison.json').exists()
files={p for p in root.rglob('*') if p.is_file() and p.suffix in ('.json','.jsonl','.csv','.log','.txt')}
hashes={}
for v in ('s28d','s29m'):
 src=r/f'variants/{v}/kernel.asc';exe=r/f'variants/{v}/build/bench_multi';files.add(src)
 for p in (src,exe):hashes[str(p.relative_to(r))]=hashlib.sha256(p.read_bytes()).hexdigest()
manifest=dict(label=label,source_and_exe_sha256=hashes,files=[])
with zipfile.ZipFile(dest,'x',zipfile.ZIP_DEFLATED) as z:
 for p in sorted(files):
  name=str(p.relative_to(r));b=p.read_bytes();z.writestr(name,b)
  manifest['files'].append(dict(path=name,bytes=len(b),sha256=hashlib.sha256(b).hexdigest()))
 z.writestr('collection_manifest.json',json.dumps(manifest,indent=2)+'\n')
print(json.dumps(dict(path=str(dest),bytes=dest.stat().st_size,files=len(files),sha256=hashlib.sha256(dest.read_bytes()).hexdigest())))
