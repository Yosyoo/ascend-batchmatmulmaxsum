from pathlib import Path
import hashlib,json,sys
label=sys.argv[1];assert label.replace('_','').isalnum()
p=Path('/tmp')/('bmms28_'+label+'.zip');b=p.read_bytes();d=Path('/tmp')/('bmms28_'+label+'_chunks');d.mkdir(exist_ok=False)
parts=[]
for i,start in enumerate(range(0,len(b),1024*1024)):
 x=b[start:start+1024*1024];name=f'part{i:03d}';(d/name).write_bytes(x)
 parts.append(dict(name=name,bytes=len(x),sha256=hashlib.sha256(x).hexdigest()))
m=dict(label=label,bytes=len(b),sha256=hashlib.sha256(b).hexdigest(),parts=parts)
(d/'metadata.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(dict(path=str(d),sha256=m['sha256'],parts=len(parts))))
