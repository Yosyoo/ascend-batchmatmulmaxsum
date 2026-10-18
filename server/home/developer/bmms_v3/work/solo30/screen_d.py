from pathlib import Path
import subprocess,time
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
assert 'FINAL30_B_COMPLETE' in (d/'final30_b.log').read_text()
deadline=time.monotonic()+1200
while 'COMPILE29_SCREEN_COMPLETE' not in (d/'compile30_d.log').read_text(errors='replace'):
 assert time.monotonic()<deadline
 assert 'error:' not in (d/'compile30_d.log').read_text(errors='replace')
 time.sleep(5)
subprocess.run(['python3','work/solo28/diagnostic.py','s30d','121232f858ab611ed044f6dba44260cd2963afa8a18ae9a38b2ff6b89dce9162'],cwd=r,check=True)
subprocess.run(['python3','work/solo28/quick_compare.py','s30d','s29m','quick30_d','work/solo30/d_shapes.txt'],cwd=r,check=True)
print('SCREEN30_D_COMPLETE',flush=True)
