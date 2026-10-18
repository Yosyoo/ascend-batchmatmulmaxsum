from pathlib import Path
import sys,json,hashlib,shutil,tarfile
r=Path('/home/developer/bmms_v3');v=sys.argv[1];sha=sys.argv[2]
src=r/'variants'/v/'kernel.asc';assert hashlib.sha256(src.read_bytes()).hexdigest()==sha
rows=json.loads((r/'c29'/(v+'_official15.json')).read_text())
assert len(rows)==15 and all(x['passed'] and x['returncode']==0 for x in rows)
out=r/'c42'/('final'+v);out.mkdir(exist_ok=True)
shutil.copy2(src,out/'kernel.asc')
for x in rows:
 spec='_'.join(map(str,x['shape']))+'_'+str(x['dtype'])+'_'+str(int(x['ta']))+'_'+str(int(x['tb']))
 w=r/'variants'/v/'research/PipeUtilization'/spec
 files=sorted(w.glob('profile/PROF_*/mindstudio_profiler_output/op_summary_*.csv'));assert files
 shutil.copy2(files[-1],out/('P'+str(x['case'])+'.csv'))
 for p,suffix in [(w/'output/y.bin','_y.bin'),(w/'msprof.log','_msprof.log')]:
  if p.exists():shutil.copy2(p,out/('P'+str(x['case'])+suffix))
shutil.copy2(r/'c29'/(v+'_official15.json'),r/'c42'/(v+'_official15.json'))
with tarfile.open(r/'c42/evidence.tgz','w:gz') as t:
 for p in sorted((r/'c42').rglob('*')):
  if p.is_file() and p.suffix!='.tgz':t.add(p,arcname='c42/'+str(p.relative_to(r/'c42')),recursive=False)
print('saved',v,'full15CSV',len(list(out.glob('*.csv'))),'allCSV',len(list((r/'c42').rglob('*.csv'))))
