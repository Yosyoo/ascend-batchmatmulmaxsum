from pathlib import Path
import subprocess,time
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
deadline=time.monotonic()+900
while 'COMPILE29_SCREEN_COMPLETE' not in (d/'compile29_d.log').read_text(errors='replace'):
    assert time.monotonic()<deadline
    assert 'error:' not in (d/'compile29_d.log').read_text(errors='replace')
    time.sleep(5)
assert 'SCREEN29_BC_COMPLETE' in (d/'screen29_bc.log').read_text()
sha='f682771ba123b468bd66fab7a33588209a2afd340ac9373fe065072160fb1648'
for cmd in [
    ['python3',str(r/'work/solo28/diagnostic.py'),'s29d',sha],
    ['python3',str(r/'work/solo28/quick_compare.py'),'s29d','s28d','quick29_d',str(r/'work/solo29/quick_shapes.txt')]]:
    p=subprocess.run(cmd)
    if p.returncode:raise SystemExit(p.returncode)
print('SCREEN29_D_COMPLETE',flush=True)
