from pathlib import Path
import subprocess,time
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
deadline=time.monotonic()+900
while 'COMPILE29_SCREEN_COMPLETE' not in (d/'compile29_e.log').read_text(errors='replace'):
    assert time.monotonic()<deadline
    assert 'error:' not in (d/'compile29_e.log').read_text(errors='replace')
    time.sleep(5)
assert 'SCREEN29_D_COMPLETE' in (d/'screen29_d.log').read_text()
sha='76d6d0265c3d81855add4dd45465a5a44802768275c68f4ddf5641504c0cd833'
for cmd in [
    ['python3',str(r/'work/solo28/diagnostic.py'),'s29e',sha],
    ['python3',str(r/'work/solo28/quick_compare.py'),'s29e','s28d','quick29_e',str(r/'work/solo29/wide_shapes.txt')]]:
    p=subprocess.run(cmd)
    if p.returncode:raise SystemExit(p.returncode)
print('SCREEN29_E_COMPLETE',flush=True)
