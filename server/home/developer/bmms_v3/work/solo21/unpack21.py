from pathlib import Path
import hashlib,json,sys,zipfile
r=Path(__file__).resolve().parents[2];tag=sys.argv[1]
assert tag.replace('_','').isalnum()
parts=r/'evidence'/('round21_'+tag+'_chunks');m=json.loads((parts/'metadata.json').read_text());chunks=[]
for x in m['parts']:
    assert x['name'].startswith('part') and len(x['name'])==7 and x['name'][4:].isdigit()
    b=(parts/x['name']).read_bytes();assert len(b)==x['bytes'] and hashlib.sha256(b).hexdigest()==x['sha256'];chunks.append(b)
b=b''.join(chunks);assert len(b)==m['bytes'] and hashlib.sha256(b).hexdigest()==m['sha256']
archive=r/'evidence'/('remote_round21_'+tag+'_verified.zip');archive.write_bytes(b)
dest=r/'evidence'/('remote_round21_'+tag);dest.mkdir(exist_ok=False)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for n in z.namelist():assert (dest/n).resolve().is_relative_to(dest.resolve())
    z.extractall(dest)
print(json.dumps(dict(tag=tag,sha256=m['sha256'],bytes=len(b),files=m['files'])))
