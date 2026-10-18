from pathlib import Path
import subprocess,json,time,hashlib
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s29m';sha='b2465388729e92bc38b678284b4f497f5d89ee6512fcbcaf92d93fc6adf92511'
assert 'SCREEN29_M_COMPLETE' in (d/'screen29_m.log').read_text()
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
comparison=json.loads((d/'quick29_m/comparison.json').read_text())
assert all(z['geometric_mean_ratio']<.995 for z in comparison['orders'])
for command in [
 ['python3','work/solo17/validate.py',v],
 ['python3','work/solo28/run_stress.py',v,sha],
 ['python3','work/solo28/pool_compare.py',v,'s28d','pool29_m_base_abba']]:
 print('START',command,flush=True);subprocess.run(command,cwd=r,check=True)
deadline=time.monotonic()+900
while 'BUILD29_M_BENCH_COMPLETE' not in (d/'compile29_m_bench.log').read_text(errors='replace'):
 assert time.monotonic()<deadline;time.sleep(5)
specs=['1_4096_4096_1024','1_8192_512_1024','1_4096_1024_512','1_2048_2048_1024','1_8192_256_512','2_4096_2048_512']
subprocess.run(['python3','work/solo17/scan.py','hangs29_m',v]+specs,cwd=r,check=True)
print('FINAL29_M_COMPLETE',flush=True)
