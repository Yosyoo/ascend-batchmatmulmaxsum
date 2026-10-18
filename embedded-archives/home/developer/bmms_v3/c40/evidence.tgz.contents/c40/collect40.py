from pathlib import Path
import sys,json,hashlib,shutil,tarfile
r=Path('/home/developer/bmms_v3');v=sys.argv[1];sha=sys.argv[2]
assert hashlib.sha256((r/'variants'/v/'kernel.asc').read_bytes()).hexdigest()==sha
rows=json.loads((r/'c29'/(v+'_official15.json')).read_text())
assert len(rows)==15 and all(x['passed'] and x['returncode']==0 for x in rows)
out=r/'c40'/('final'+v);out.mkdir(exist_ok=True)
for x in rows:
    spec='_'.join(map(str,x['shape']))+'_'+str(x['dtype'])+'_'+str(int(x['ta']))+'_'+str(int(x['tb']))
    w=r/'variants'/v/'research/PipeUtilization'/spec
    files=sorted(w.glob('profile/PROF_*/mindstudio_profiler_output/op_summary_*.csv'))
    assert files,(spec,'missingCSV')
    shutil.copy2(files[-1],out/('P'+str(x['case'])+'.csv'))
    for src,suffix in [(w/'output/y.bin','_y.bin'),(w/'msprof.log','_msprof.log')]:
        if src.exists():shutil.copy2(src,out/('P'+str(x['case'])+suffix))
shutil.copy2(r/'c29'/(v+'_official15.json'),r/'c40'/(v+'_official15.json'))
with tarfile.open(r/'c40/evidence.tgz','w:gz') as t:
    for p in (r/'c40').iterdir():
        if p.name!='evidence.tgz':t.add(p,arcname='c40/'+p.name)
print('saved',v,'full15CSV',len(list(out.glob('*.csv'))),'allCSV',len(list((r/'c40').rglob('*.csv'))))
