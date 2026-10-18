from pathlib import Path
import subprocess,json,hashlib
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s31k'
assert json.loads((d/'diagnostic31_s31k/summary.json').read_text())['passed']
assert hashlib.sha256((r/'variants/s31k/kernel.asc').read_bytes()).hexdigest()=='50d4445620d44eb382f687ceb05dc9268420220bb921918958357f9b48d51eee'
result=[]
for ta,tb in [(0,0),(0,1),(1,0),(1,1)]:
 label=f'quick31_k_layout{ta}{tb}'
 subprocess.run(['python3','work/solo31/quick_layout_compare.py',v,'s30p',label,'work/solo31/native_shapes.txt','1',str(ta),str(tb)],cwd=r,check=True)
 x=json.loads((d/label/'comparison.json').read_text());assert x['dtype']==1 and x['ta']==ta and x['tb']==tb
 result.append(dict(label=label,dtype=1,ta=ta,tb=tb,ratios=[z['geometric_mean_ratio'] for z in x['orders']]))
 print(json.dumps(result[-1]),flush=True)
(d/'layouts31_k_summary.json').write_text(json.dumps(result,indent=2)+'\n')
print('LAYOUTS31_K_COMPLETE',flush=True)
