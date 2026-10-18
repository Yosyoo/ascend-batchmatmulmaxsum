from pathlib import Path
import hashlib,json,subprocess
r=Path('/home/developer/bmms_v3');v='s22a';d=r/'solo17_data'
assert hashlib.sha256((r/'variants/s22a/kernel.asc').read_bytes()).hexdigest()=='ac2be87e7efdf9e50aa7d923b8d14bada8ebd2dc461945203746ed62b006e0ca'
diag=json.loads((d/'diagnostic_22a/summary.json').read_text());assert sum(x['observed'] for x in diag)==648 and all(x['passed'] for x in diag)
long=json.loads((d/'long_accuracy22a/summary.json').read_text());assert long['passed'] and long['observed']==96 and long['all_fixture_hashes_unchanged']
assert 'PASS candidate diagnostics648,stress96,pilots36' in (d/'run22_a_pilot.log').read_text()
for command in [
    ['python3',str(r/'work/solo17/validate.py'),v],
    ['python3',str(r/'work/solo18/pool18.py'),v],
    ['python3',str(r/'work/solo17/scan.py'),'hangs22_a',v,
     '1_4096_4096_1024','1_8192_512_1024','1_4096_1024_512',
     '1_2048_2048_1024','1_8192_256_512','2_4096_2048_512']]:
    p=subprocess.run(command)
    if p.returncode:raise SystemExit(p.returncode)
print('PASS s22a full precision18378/100pool/six hangs; no official upload before raw verification and independent repeat.',flush=True)
