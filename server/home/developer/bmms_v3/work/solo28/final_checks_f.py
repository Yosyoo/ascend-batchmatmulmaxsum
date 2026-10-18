from pathlib import Path
import hashlib,json,subprocess
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s28f'
assert hashlib.sha256((r/'variants/s28f/kernel.asc').read_bytes()).hexdigest()=='621e2567046e70c288c878df037e8c6a63171763c481516880f6dc32e0c634ef'
p=json.loads((d/'validation_s28f/precision_summary.json').read_text());assert p['passed'] and p['total']==18378
s=json.loads((d/'stress28_s28f/summary.json').read_text());assert s['passed'] and sum(z['observed'] for z in s['items'])==672
cmd=['python3',str(r/'work/solo17/scan.py'),'hangs28_f',v,
 '1_4096_4096_1024','1_8192_512_1024','1_4096_1024_512','1_2048_2048_1024','1_8192_256_512','2_4096_2048_512']
p=subprocess.run(cmd)
if p.returncode:raise SystemExit(p.returncode)
p=subprocess.run(['python3',str(r/'work/solo28/pool_compare.py'),v,'s26b','pool28_f_repeat_abba'])
if p.returncode:raise SystemExit(p.returncode)
print('PASS28F_FINAL_CHECKS six historical hangs and independent100 pool ABBA complete; no automatic official submission',flush=True)
