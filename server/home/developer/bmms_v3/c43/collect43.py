from pathlib import Path
import sys,json,hashlib,shutil,tarfile
r=Path('/home/developer/bmms_v3');v=sys.argv[1];sha=sys.argv[2]
src=r/'variants'/v/'kernel.asc';assert hashlib.sha256(src.read_bytes()).hexdigest()==sha
rows=json.loads((r/'c29'/(v+'_official15.json')).read_text())
assert len(rows)==15 and all(x['passed'] and x['returncode']==0 for x in rows)
out=r/'c43'/('final'+v);out.mkdir(exist_ok=True)
shutil.copy2(src,out/'kernel.asc')
for x in rows:
 spec='_'.join(map(str,x['shape']))+'_'+str(x['dtype'])+'_'+str(int(x['ta']))+'_'+str(int(x['tb']))
 w=r/'variants'/v/'research/PipeUtilization'/spec
 files=sorted(w.glob('profile/PROF_*/mindstudio_profiler_output/op_summary_*.csv'));assert files
 shutil.copy2(files[-1],out/('P'+str(x['case'])+'.csv'))
 for p,suffix in [(w/'output/y.bin','_y.bin'),(w/'msprof.log','_msprof.log')]:
  if p.exists():shutil.copy2(p,out/('P'+str(x['case'])+suffix))
shutil.copy2(r/'c29'/(v+'_official15.json'),r/'c43'/(v+'_official15.json'))
expected={'clean132': '33ec27f9f0394842affbf8dae122165aa1d56d150e58c341ea26d098362075ce', 'clean133': 'b070ddc5211d406afa4076c656fef36ac611339e15d009b868ae978a0dba4fe7', 'clean134': '845d3fa68f436c0731b1bd3ac0aec980f4e670618b02479d6e81a49dd50e1dd4', 'clean135': '09a87da3b369c7baf18620d0848e5f8bb1ad7edff10ccf651d3b22c725b765fe', 'clean136': 'ba19f2e936a116ebfd569a4295260a26a918998b0db33141d7ec8bfc488a6ec5', 'clean137': '83bd98ed9574634530cf923e662c899bce34397c263e751f216250be1ba9f40c', 'clean131': '70848eebdabd555fe78085d1678bd06333db7f660267d10c160f26f61154e354'}
snap=r/'c43/tested_sources';snap.mkdir(exist_ok=True)
for name,digest in expected.items():
 p=r/'variants'/name/'kernel.asc';assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,(name,'source changed')
 shutil.copy2(p,snap/(name+'.asc'))
(snap/'hashes.json').write_text(json.dumps(expected,indent=2)+'\n')
with tarfile.open(r/'c43/evidence.tgz','w:gz') as t:
 for p in sorted((r/'c43').rglob('*')):
  if p.is_file() and p.suffix!='.tgz':t.add(p,arcname='c43/'+str(p.relative_to(r/'c43')),recursive=False)
print('saved',v,'full15CSV',len(list(out.glob('*.csv'))),'allCSV',len(list((r/'c43').rglob('*.csv'))))
