from pathlib import Path
import subprocess,time
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
assert 'SCREEN29_K_COMPLETE' in (d/'screen29_k.log').read_text()
for v,sha in [('s29l','113b0b73c41702be073a67369002398a12b6dddeb7547c53fb7019a0fb38d7e4')]:
    log=d/('compile29_'+v[-1]+'.log');deadline=time.monotonic()+900
    while 'COMPILE29_SCREEN_COMPLETE' not in log.read_text(errors='replace'):
        assert time.monotonic()<deadline
        assert 'error:' not in log.read_text(errors='replace')
        time.sleep(5)
    print('SCREEN_BEGIN',v,flush=True)
    p=subprocess.run(['python3',str(r/'work/solo28/diagnostic.py'),v,sha])
    if p.returncode:print('REJECT_DIAGNOSTIC',v,flush=True);continue
    p=subprocess.run(['python3',str(r/'work/solo28/quick_compare.py'),v,'s28d','quick29_'+v[-1],str(r/'work/solo29/resident_shapes.txt')])
    if p.returncode:print('REJECT_PERFORMANCE_CONTRACT',v,flush=True);continue
print('SCREEN29_L_COMPLETE',flush=True)
