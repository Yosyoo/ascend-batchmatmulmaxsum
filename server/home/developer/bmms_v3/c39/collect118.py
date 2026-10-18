from pathlib import Path
import hashlib,json,shutil,tarfile
r=Path('/home/developer/bmms_v3')
assert hashlib.sha256((r/'variants/clean118/kernel.asc').read_bytes()).hexdigest()=='c8e0f6eb71d701937f548803e7fa36efe02e56baf54aef3587a116cc85c1ef88'
rows=json.loads((r/'c29/clean118_official15.json').read_text())
assert len(rows)==15 and all(x['passed'] and x['returncode']==0 for x in rows)
out=r/'c39/final118';out.mkdir(exist_ok=True)
for x in rows:
    spec='_'.join(map(str,x['shape']))+'_'+str(x['dtype'])+'_'+str(int(x['ta']))+'_'+str(int(x['tb']))
    w=r/'variants/clean118/research/PipeUtilization'/spec
    files=sorted(w.glob('profile/PROF_*/mindstudio_profiler_output/op_summary_*.csv'))
    assert files,(spec,'missing CSV')
    shutil.copy2(files[-1],out/('P'+str(x['case'])+'.csv'))
    for source,suffix in [(w/'output/y.bin','_y.bin'),(w/'msprof.log','_msprof.log')]:
        if source.exists():shutil.copy2(source,out/('P'+str(x['case'])+suffix))
shutil.copy2(r/'c29/clean118_official15.json',r/'c39/clean118_official15.json')
with tarfile.open(r/'c39/evidence.tgz','w:gz') as t:
    for p in (r/'c39').iterdir():
        if p.name!='evidence.tgz':t.add(p,arcname='c39/'+p.name)
print('saved',len(list(out.glob('*.csv'))),'full CSVs and focused session evidence')
