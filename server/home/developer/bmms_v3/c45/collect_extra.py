from pathlib import Path
import hashlib
import json
import shutil
import tarfile

root=Path('/home/developer/bmms_v3');source=root/'c45';out=root/'c45_extra'
out.mkdir(exist_ok=True)
expected={
 'clean149':'8ba694f6ee092db4032d803b525ac4d4e43243cc44e5e340a8886ced94add8af',
 'clean150':'dae7f543594e663a3e1e9c6471bbca96eec00479d753b5b296b5b22b32570337',
 'clean151':'3084f798e1fb3232576364427c989fb26824267fe2c51029a30434fbc430f09a',
 'clean152':'d93e586881a336068bdf073b961dfc4987a0f05409212813be1b9073b651195d',
}
for name,digest in expected.items():
 p=root/'variants'/name/'kernel.asc'
 assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
 shutil.copy2(p,out/(name+'.asc'))
(out/'hashes.json').write_text(json.dumps(expected,indent=2)+'\n')
for name in ('k_preload','wide_transposed','wide_balanced','wide_stream','wide_stream_reverse'):
 if (source/name).exists():shutil.copytree(source/name,out/name,dirs_exist_ok=True)
for name in ('k_preload.log','wide_transposed.log','wide_balanced.log','wide_stream.log','wide_stream_reverse.log'):
 if (source/name).exists():shutil.copy2(source/name,out/name)
for variant in expected:
 shutil.copy2(source/('build_'+variant+'.log'),out/('build_'+variant+'.log'))
final=root/'c29/clean152_official15.json'
if final.exists():
 rows=json.loads(final.read_text())
 assert len(rows)==15 and all(x['passed'] and x['returncode']==0 and x['tasks']==123 for x in rows)
 dest=out/'finalclean152';dest.mkdir(exist_ok=True)
 shutil.copy2(final,out/'clean152_local15.json')
 for x in rows:
  spec='_'.join(map(str,x['shape']))+'_'+str(x['dtype'])+'_'+str(int(x['ta']))+'_'+str(int(x['tb']))
  work=root/'variants/clean152/research/PipeUtilization'/spec
  files=sorted(work.glob('profile/PROF_*/mindstudio_profiler_output/op_summary_*.csv'));assert files
  shutil.copy2(files[-1],dest/('P'+str(x['case'])+'.csv'))
  for p,suffix in [(work/'output/y.bin','_y.bin'),(work/'msprof.log','_msprof.log')]:
   if p.exists():shutil.copy2(p,dest/('P'+str(x['case'])+suffix))
with tarfile.open(source/'extra_evidence.tgz','w:gz') as archive:
 for p in sorted(out.rglob('*')):
  if p.is_file():archive.add(p,arcname='c45_extra/'+str(p.relative_to(out)),recursive=False)
print('extraCSV',len(list(out.rglob('*.csv'))))
