from pathlib import Path
import subprocess
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
assert 'COMPILE29_SCREEN_COMPLETE' in (d/'compile29_g.log').read_text()
assert 'SCREEN29_F_COMPLETE' in (d/'screen29_f.log').read_text()
for cmd in [
    ['python3',str(r/'work/solo28/diagnostic.py'),'s29g','8cf448950e3130575e545139815e6aa012c68348b0a881a264cffbd065eecd11'],
    ['python3',str(r/'work/solo28/quick_compare.py'),'s29g','s28d','quick29_g',str(r/'work/solo29/quick_shapes.txt')]]:
    p=subprocess.run(cmd)
    if p.returncode:raise SystemExit(p.returncode)
print('SCREEN29_G_COMPLETE',flush=True)
