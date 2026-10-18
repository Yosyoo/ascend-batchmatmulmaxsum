from pathlib import Path
import hashlib, subprocess
r=Path('/home/developer/bmms_v3')
source=r/'variants/s19c/kernel.asc'
assert hashlib.sha256(source.read_bytes()).hexdigest()=='7266fd43e903656a57539a0a5d0753c482b48b302a41e2bef844ec912a4690c2'
assert 'PASS s19c pilot only' in (r/'solo17_data/run19_c_pilot.log').read_text()
commands=[['python3',str(r/'work/solo17/validate.py'),'s19c'],
          ['python3',str(r/'work/solo18/pool18.py'),'s19c']]
hangs=['1_4096_4096_1024','1_8192_512_1024','1_4096_1024_512','1_2048_2048_1024','1_8192_256_512','2_4096_2048_512']
commands.append(['python3',str(r/'work/solo17/scan.py'),'hangs19_c','s19c',*hangs])
for command in commands:
    p=subprocess.run(command)
    if p.returncode:raise SystemExit(p.returncode)
assert hashlib.sha256(source.read_bytes()).hexdigest()=='7266fd43e903656a57539a0a5d0753c482b48b302a41e2bef844ec912a4690c2'
print('PASS s19c final precision,100-pool and six hangs; official submission still requires evidence verification',flush=True)
