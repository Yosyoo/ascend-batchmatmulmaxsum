from pathlib import Path
import subprocess,time
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
deadline=time.monotonic()+900
while 'COMPILE29_SCREEN_COMPLETE' not in (d/'compile29_h.log').read_text(errors='replace'):
    assert time.monotonic()<deadline
    assert 'error:' not in (d/'compile29_h.log').read_text(errors='replace')
    time.sleep(5)
assert 'SCREEN29_G_COMPLETE' in (d/'screen29_g.log').read_text()
for cmd in [
    ['python3',str(r/'work/solo28/diagnostic.py'),'s29h','e83bdbf870521a8141fcbab7f4ecfafb7800ed8feec563cfe2688f01225def43'],
    ['python3',str(r/'work/solo28/quick_compare.py'),'s29h','s28d','quick29_h',str(r/'work/solo29/quick_shapes.txt')]]:
    p=subprocess.run(cmd)
    if p.returncode:raise SystemExit(p.returncode)
print('SCREEN29_H_COMPLETE',flush=True)
