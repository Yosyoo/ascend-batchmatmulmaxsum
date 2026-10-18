from pathlib import Path
import hashlib
import json
import shutil
import sys
import tarfile

ROOT=Path('/home/developer/bmms_v3')
OUT=ROOT/'c44'
variant=sys.argv[1] if len(sys.argv)>1 else None
expected={
    'clean137':'83bd98ed9574634530cf923e662c899bce34397c263e751f216250be1ba9f40c',
    'clean138':'084fcf201fbe1c4dcda33b02c906cf802824db69717e04cd7867453cce4c699e',
    'clean139':'826657f756cde3342a709ac5166a201869b99be7ee80cef0665c4ffe5364d66e',
    'clean140':'05dd134a6b4a71de90b5757d68c934648b998e90159674f3ae3f68245192047a',
    'clean141':'f177106b010ea9d5338e5ebe0d00d551e4a7abea2285fa2d27a0cb7a8a36b0c6',
    'clean142':'4ed835286de23e1bd8320a7314dbee0ccf953db63cbbc9972e73df3fb6733a0a',
}
if variant:
    expected[variant]=sys.argv[2]
    rows=json.loads((ROOT/'c29'/(variant+'_official15.json')).read_text())
    assert len(rows)==15 and all(x['passed'] and x['returncode']==0 and x['tasks']==123 for x in rows)
    dest=OUT/('final'+variant)
    dest.mkdir(exist_ok=True)
    shutil.copy2(ROOT/'variants'/variant/'kernel.asc',dest/'kernel.asc')
    for x in rows:
        spec='_'.join(map(str,x['shape']))+'_'+str(x['dtype'])+'_'+str(int(x['ta']))+'_'+str(int(x['tb']))
        work=ROOT/'variants'/variant/'research/PipeUtilization'/spec
        files=sorted(work.glob('profile/PROF_*/mindstudio_profiler_output/op_summary_*.csv'))
        assert files
        shutil.copy2(files[-1],dest/('P'+str(x['case'])+'.csv'))
        for p,suffix in [(work/'output/y.bin','_y.bin'),(work/'msprof.log','_msprof.log')]:
            if p.exists():shutil.copy2(p,dest/('P'+str(x['case'])+suffix))
    shutil.copy2(ROOT/'c29'/(variant+'_official15.json'),OUT/(variant+'_official15.json'))
snap=OUT/'tested_sources'
snap.mkdir(exist_ok=True)
for name,digest in expected.items():
    p=ROOT/'variants'/name/'kernel.asc'
    assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,(name,'source changed')
    shutil.copy2(p,snap/(name+'.asc'))
(snap/'hashes.json').write_text(json.dumps(expected,indent=2)+'\n')
with tarfile.open(OUT/'evidence.tgz','w:gz') as archive:
    for p in sorted(OUT.rglob('*')):
        if p.is_file() and p.suffix!='.tgz':
            archive.add(p,arcname='c44/'+str(p.relative_to(OUT)),recursive=False)
print('allCSV',len(list(OUT.rglob('*.csv'))))
