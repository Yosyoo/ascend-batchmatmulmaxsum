"""Serial NPU protocol; preserve each pool's raw CSV before the next session."""
import json,os,shutil,subprocess,sys
from pathlib import Path
root=Path('/home/developer/bmms_v3')
v=sys.argv[1]
out=root/'solo13_data'/('final_'+v)
out.mkdir(exist_ok=False)

def run(label,command,timeout=900):
 print('START',label,flush=True)
 with (out/(label+'.log')).open('w') as f:
  p=subprocess.run(command,cwd=root,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
 print('END',label,'RC',p.returncode,flush=True)
 if p.returncode:
  print((out/(label+'.log')).read_text()[-4000:],flush=True)
  raise SystemExit(p.returncode)

for order,variants in [(1,['s12c',v]),(2,[v,'s12c'])]:
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
specs=['1_1_1_32_1_0_0','1_3_5_40_2_1_0','2_7_13_48_1_0_1',
       '4_8_16_128_2_1_1','8_16_32_128_1_0_0','13_23_73_192_2_0_1',
       '16_32_128_256_1_1_0','1_1025_1031_1032_2_1_1',
       '1_2048_1536_1280_1_0_1','1_4096_1280_1152_2_0_0',
       '1_1536_2048_2048_1_1_1','1_1280_4096_1536_2_1_0',
       '1_8192_64_128_1_0_0','1_64_8192_128_2_0_1','1_64_64_8192_1_1_1',
       '1_8_16_128_1_1_1','21_8_16_128_2_1_1','64_8_16_128_1_1_1',
       '4_8_16_128_2_1_0','41_8_16_128_2_1_1','1_7_13_48_1_0_1','21_7_13_48_1_0_1','41_7_13_48_2_0_1','64_7_13_48_1_0_1','2_7_13_48_2_0_1','2_7_13_48_1_0_0','20_7_13_48_1_0_1','21_8_8_32_1_0_1','41_4_16_64_2_0_1','21_3_13_40_2_0_1','1_3_5_40_1_1_0','1_3_5_40_1_0_0','1_3_5_40_2_0_1','1_3_5_40_1_1_1','41_3_5_40_2_1_0','64_3_5_40_1_1_0']
for order,variants in [(1,'s12c,'+v),(2,v+',s12c')]:
 run('target'+str(order),['python3','solo13_scan.py','final_target'+str(order)+'_'+v,variants,*specs])

hangs=['1_4096_4096_1024','1_8192_512_1024','1_4096_1024_512',
       '1_2048_2048_1024','1_8192_256_512','2_4096_2048_512']
for spec in hangs:
 label='hang_'+v+'_'+spec
 run(label,['timeout','120','python3','harness/one.py',v,spec],150)
 assert 'passed= True' in (out/(label+'.log')).read_text(),spec
print('PASS: two-order 100-shape pool, 36 targets, six historical hang shapes',flush=True)
