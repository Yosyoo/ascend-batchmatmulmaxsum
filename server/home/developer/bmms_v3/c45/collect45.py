from pathlib import Path
import hashlib
import json
import shutil
import tarfile

root = Path('/home/developer/bmms_v3')
out = root/'c45'
expected = {
    'clean137':'83bd98ed9574634530cf923e662c899bce34397c263e751f216250be1ba9f40c',
    'clean144':'c8bfdb7ea43d11384901c01f9aeef24ad0f40d1748a928622c6e0d71d62882b0',
    'clean145':'88ea93f419aa7abbda3460c87a21470de120ce524e6bb6fcbb2a1a3ad6949f17',
    'clean146':'f04ac7886b9090f9da48592c76dc4fd82ebd4d6026dadd5d00d8a8127b13b759',
    'clean147':'b26840cca205248a9f17e7af61c6feab31dd0f5da26750af552600054d367f32',
    'clean148':'9c569dde2e32e04553bb62cb5b2ee7d103b5739408d16a4df654b46d9bb7fbd8',
}
rows = json.loads((root/'c29/clean147_official15.json').read_text())
assert len(rows)==15 and all(x['passed'] and x['returncode']==0 and x['tasks']==123 for x in rows)
dest=out/'finalclean147'
dest.mkdir(exist_ok=True)
for x in rows:
    spec='_'.join(map(str,x['shape']))+'_'+str(x['dtype'])+'_'+str(int(x['ta']))+'_'+str(int(x['tb']))
    work=root/'variants/clean147/research/PipeUtilization'/spec
    profiles=sorted(work.glob('profile/PROF_*/mindstudio_profiler_output/op_summary_*.csv'))
    assert profiles
    shutil.copy2(profiles[-1],dest/('P'+str(x['case'])+'.csv'))
    for p,suffix in [(work/'output/y.bin','_y.bin'),(work/'msprof.log','_msprof.log')]:
        if p.exists():shutil.copy2(p,dest/('P'+str(x['case'])+suffix))
shutil.copy2(root/'c29/clean147_official15.json',out/'clean147_local15.json')
snap=out/'tested_sources'
snap.mkdir(exist_ok=True)
for name,digest in expected.items():
    p=root/'variants'/name/'kernel.asc'
    assert hashlib.sha256(p.read_bytes()).hexdigest()==digest,(name,'source changed')
    shutil.copy2(p,snap/(name+'.asc'))
(snap/'hashes.json').write_text(json.dumps(expected,indent=2)+'\n')
with tarfile.open(out/'evidence.tgz','w:gz') as archive:
    for p in sorted(out.rglob('*')):
        if p.is_file() and p.suffix!='.tgz':
            archive.add(p,arcname='c45/'+str(p.relative_to(out)),recursive=False)
print('CSV files:',len(list(out.rglob('*.csv'))))
