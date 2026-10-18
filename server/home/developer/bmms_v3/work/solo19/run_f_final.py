from pathlib import Path
import hashlib, subprocess
r=Path('/home/developer/bmms_v3')
source=r/'variants/s19f/kernel.asc'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='da69df97529ad80885a26c428b04146576bfd63a1cc43354a782fb611e13d9a1'
assert 'PASS s19f pilot only' in (r/'solo17_data/run19_f_pilot.log').read_text()
commands=[['python3',str(r/'work/solo17/validate.py'),'s19f'],
          ['python3',str(r/'work/solo18/pool18.py'),'s19f']]
hangs=['1_4096_4096_1024','1_8192_512_1024','1_4096_1024_512','1_2048_2048_1024','1_8192_256_512','2_4096_2048_512']
commands.append(['python3',str(r/'work/solo17/scan.py'),'hangs19_f','s19f',*hangs])
for command in commands:
    p=subprocess.run(command)
    if p.returncode:raise SystemExit(p.returncode)
assert hashlib.sha256(source.read_bytes()).hexdigest()=='da69df97529ad80885a26c428b04146576bfd63a1cc43354a782fb611e13d9a1'
print('PASS s19f final precision,100-pool and six hangs; official submission still requires evidence verification',flush=True)
