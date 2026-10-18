from pathlib import Path
import subprocess,json,hashlib
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s42b';sha='b405e207e962cf691ca813a76604c4811ed6628a90e104f683aa23df0b2f196d'
assert 'SCREEN42_B_COMPLETE' in (d/'screen42_b.log').read_text()
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
assert json.loads((d/f'diagnostic42_{v}/summary.json').read_text())['passed']
def run(args):subprocess.run(args,cwd=r,check=True)
for ta,tb in ((0,0),(0,1),(1,0),(1,1)):
 run(['python3','work/solo31/quick_layout_compare.py',v,'s33a',f'quick42_b33_{ta}{tb}','work/solo42/shapes_a.txt','1',str(ta),str(tb)])
run(['python3','work/solo17/validate.py',v])
run(['python3','work/solo28/run_stress.py',v,sha])
run(['python3','work/solo42/extra_precision.py',v,sha])
run(['cmake','--build',f'variants/{v}/build','--target','bench','-j1'])
run(['python3','work/solo28/pool_compare.py',v,'s33a','pool42_b_33_abba'])
pool=json.loads((d/'pool42_b_33_abba/comparison.json').read_text())
ratios=[x['geometric_mean_ratio'] for x in pool['orders']]
print('POOL42_B_RATIOS',ratios,flush=True)
run(['python3','work/solo17/scan.py','hangs42_b',v,'1_4096_4096_1024','1_8192_512_1024','1_4096_1024_512','1_2048_2048_1024','1_8192_256_512','2_4096_2048_512'])
if all(x<=.995 for x in ratios):
 run(['python3','work/solo28/pool_compare.py',v,'s33a','pool42_b_33_repeat_abba'])
else:print('POOL42_B_NO_STABLE_PROMOTION',flush=True)
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
print('FINAL42_B_COMPLETE',flush=True)
