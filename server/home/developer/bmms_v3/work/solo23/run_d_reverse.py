from pathlib import Path
import hashlib,json,subprocess
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
assert not Path('/proc/328006').exists()
assert hashlib.sha256((r/'variants/s23d/kernel.asc').read_bytes()).hexdigest()=='f0aab8ebf32d2f71314baadc98359ed18e0ab42177e99aaf2a153de9ba886a5b'
rows=[json.loads(x) for x in (d/'pilot23_d_parent_base/results.jsonl').read_text().splitlines()]
assert len(rows)==30 and all(x['passed'] and x['tasks']==163 and x['kernels_per_call']==1 for x in rows)
assert not (d/'pilot23_base_parent_d').exists()
specs=['1_64_512_8192_1_0_0', '1_64_512_8192_2_0_0', '1_256_256_8192_1_0_0', '1_256_256_8192_2_0_0', '1_512_512_8192_1_0_0', '1_512_512_8192_2_0_0', '1_64_512_1056_1_0_0', '1_64_512_1536_1_0_0', '1_256_256_4096_1_0_0', '2_128_128_1536_1_0_0']
p=subprocess.run(['python3',str(r/'work/solo17/scan.py'),'pilot23_base_parent_d','s15i,s22a,s23d',*specs])
if p.returncode:raise SystemExit(p.returncode)
print('PASS s23d reverse30 completed; original forward30 retained, no source changes.',flush=True)
