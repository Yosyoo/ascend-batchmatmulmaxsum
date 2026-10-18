from pathlib import Path
import subprocess
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
assert 'COMPILE29_SCREEN_COMPLETE' in (d/'compile29_f.log').read_text()
assert 'SCREEN29_E_COMPLETE' in (d/'screen29_e.log').read_text()
for cmd in [
    ['python3',str(r/'work/solo28/diagnostic.py'),'s29f','23c828910f7b436e256c06a1aee0866a3335bac7c8f86b49c2cfaca4177dd113'],
    ['python3',str(r/'work/solo28/quick_compare.py'),'s29f','s28d','quick29_f',str(r/'work/solo29/quick_shapes.txt')]]:
    p=subprocess.run(cmd)
    if p.returncode:raise SystemExit(p.returncode)
print('SCREEN29_F_COMPLETE',flush=True)
