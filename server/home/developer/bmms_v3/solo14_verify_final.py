"""Serial NPU protocol; preserve each pool's raw CSV before the next session."""
import json,os,shutil,subprocess,sys
from pathlib import Path
root=Path('/home/developer/bmms_v3')
v=sys.argv[1]
out=root/'solo14_data'/('final_'+v)
out.mkdir(exist_ok=False)

def run(label,command,timeout=900):
 print('START',label,flush=True)
 with (out/(label+'.log')).open('w') as f:
  p=subprocess.run(command,cwd=root,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
 print('END',label,'RC',p.returncode,flush=True)
 if p.returncode:
  print((out/(label+'.log')).read_text()[-4000:],flush=True)
  raise SystemExit(p.returncode)

for order,variants in [(1,['s13k',v]),(2,[v,'s13k'])]:
 for variant in variants:
  label=f'pool{order}_{variant}'
  run(label,['python3','harness/multi.py',variant,'shapes_pool2.txt','160'])
  data=json.loads((out/(label+'.log')).read_text())
  assert data['ntasks']==16000 and len(data['shapes'])==100 and 'leftover' not in data
  src=root/'variants'/variant/'work/multi_shapes_pool2'
  saved=out/label
  saved.mkdir()
  for file in src.rglob('*.csv'):
   dest=saved/file.relative_to(src);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,dest)
  shutil.copy2(src/'msprof.log',saved/'msprof.log')

# Historical table is corroborating evidence, not current public official case metadata.
specs=['1_8192_64_128_1_0_0','1_8192_64_128_2_0_0',
'1_8192_64_128_1_1_0','1_8192_64_128_2_0_1',
'4_4096_64_128_1_0_0','2_4096_64_128_1_0_0',
'4_8192_64_128_2_1_1','1_5133_47_48_2_1_0',
'4_8_16_128_2_1_1','1_64_64_8192_1_1_1','1_64_64_8176_1_1_1','1_8192_47_112_2_0_0']
for order,variants in [(1,'s13k,'+v),(2,v+',s13k')]:
 run('target'+str(order),['python3','solo14_scan.py','final_target'+str(order)+'_'+v,variants,*specs])

hangs=['1_4096_4096_1024','1_8192_512_1024','1_4096_1024_512',
       '1_2048_2048_1024','1_8192_256_512','2_4096_2048_512']
for spec in hangs:
 label='hang_'+v+'_'+spec
 run(label,['timeout','120','python3','harness/one.py',v,spec],150)
 assert 'passed= True' in (out/(label+'.log')).read_text(),spec
print('PASS: two-order 100-shape pool, 12 targets, six historical hang shapes',flush=True)
