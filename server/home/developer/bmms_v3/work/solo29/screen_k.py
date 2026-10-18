from pathlib import Path
import subprocess,time
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
assert 'SCREEN29_IJ_COMPLETE' in (d/'screen29_ij.log').read_text()
for v,sha in [('s29k','1e0810d76558dc38c6d9cd5645d3c84b418e60599ce9ac0001366c598144eab2')]:
    log=d/('compile29_'+v[-1]+'.log');deadline=time.monotonic()+900
    while 'COMPILE29_SCREEN_COMPLETE' not in log.read_text(errors='replace'):
        assert time.monotonic()<deadline
        assert 'error:' not in log.read_text(errors='replace')
        time.sleep(5)
    print('SCREEN_BEGIN',v,flush=True)
    p=subprocess.run(['python3',str(r/'work/solo28/diagnostic.py'),v,sha])
    if p.returncode:print('REJECT_DIAGNOSTIC',v,flush=True);continue
    p=subprocess.run(['python3',str(r/'work/solo28/quick_compare.py'),v,'s28d','quick29_'+v[-1],str(r/'work/solo29/quick_shapes.txt')])
    if p.returncode:print('REJECT_PERFORMANCE_CONTRACT',v,flush=True);continue
print('SCREEN29_K_COMPLETE',flush=True)
