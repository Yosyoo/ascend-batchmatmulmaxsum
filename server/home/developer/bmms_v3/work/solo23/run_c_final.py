from pathlib import Path
import hashlib,json,subprocess
r=Path('/home/developer/bmms_v3');v='s23c';d=r/'solo17_data'
assert hashlib.sha256((r/'variants/s23c/kernel.asc').read_bytes()).hexdigest()=='44b93c8f5d864c1a2caab02d71d4696ae73be7c3ebc52414ab65d0ea3f789e2f'
diag=json.loads((d/'diagnostic_23c/summary.json').read_text());assert sum(x['observed'] for x in diag)==648 and all(x['passed'] for x in diag)
long=json.loads((d/'long_accuracy23c/summary.json').read_text());assert long['passed'] and long['observed']==96 and long['all_fixture_hashes_unchanged']
assert 'PASS candidate diagnostics648,newstress96,longstress96,kparallelstress96,pilots36' in (d/'run23_c_pilot.log').read_text()
for label in ['pair_accuracy23c','kparallel_accuracy23c','kparallel_batch_accuracy23c']:
    x=json.loads((d/label/'summary.json').read_text());assert x['passed'] and x['observed']==96 and x['all_fixture_hashes_unchanged']
assert not Path('/proc/318239').exists()
for command in [
    ['python3',str(r/'work/solo17/validate.py'),v],
    ['python3',str(r/'work/solo18/pool18.py'),v],
    ['python3',str(r/'work/solo17/scan.py'),'hangs23_c',v,
     '1_4096_4096_1024','1_8192_512_1024','1_4096_1024_512',
     '1_2048_2048_1024','1_8192_256_512','2_4096_2048_512']]:
    p=subprocess.run(command)
    if p.returncode:raise SystemExit(p.returncode)
print('PASS s23c full precision18378/100pool/six hangs; no official upload before raw verification and independent repeat.',flush=True)
