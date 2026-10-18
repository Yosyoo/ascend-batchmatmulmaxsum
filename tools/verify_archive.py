from pathlib import Path
import hashlib,json,os

root=Path(__file__).resolve().parents[1]
manifest=json.loads((root/'metadata/server-manifest.json').read_text())
checked=0
for entry in manifest['files']:
    path=root/'server/home/developer'/entry['path']
    assert path.is_file() and not path.is_symlink(),entry['path']
    data=path.read_bytes()
    assert len(data)==entry['bytes'],entry['path']
    assert hashlib.sha256(data).hexdigest()==entry['sha256'],entry['path']
    checked+=1
for entry in manifest['symlinks']:
    path=root/'server/home/developer'/entry['path']
    assert path.is_symlink() and os.readlink(path)==entry['relative_target'],entry['path']
embedded=json.loads((root/'metadata/embedded-manifest.json').read_text())
for entry in embedded['files']:
    path=root/entry['stored_path'];data=path.read_bytes()
    assert len(data)==entry['bytes'] and hashlib.sha256(data).hexdigest()==entry['sha256'],entry['stored_path']
local=json.loads((root/'metadata/local-delivery-manifest.json').read_text())
for entry in local:
    path=root/entry['path'];data=path.read_bytes()
    assert len(data)==entry['bytes'] and hashlib.sha256(data).hexdigest()==entry['sha256'],entry['path']
source=root/'final-delivery/kernel.asc'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='9feb4e97863b23d014f85f59393629ebb775b9b755dbd0262bd9847aa65c4a3e'
assert source.read_bytes()==(root/'server/home/developer/bmms_v3/variants/clean203/kernel.asc').read_bytes()
print(json.dumps({'regular_files_verified':checked,'symlinks_verified':len(manifest['symlinks']),
                  'embedded_files_verified':len(embedded['files']),'local_delivery_files_verified':len(local),
                  'final_source_exact':True,'credential_findings':len(manifest['credential_findings'])+len(embedded['credential_findings'])},indent=2))
