from pathlib import Path
import subprocess,time
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
assert 'SCREEN29_H_COMPLETE' in (d/'screen29_h.log').read_text()
for v,sha in [('s29i','b0e5c964f51cc0fd91d16e4189690b70079ed6bf1a1eb45824b9145eef445e29'),
    ('s29j','3f182ac8451eabd781c0756eb2b5a6a3e20da0bd2757ccd6ab31ecc7c95d3fab')]:
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
print('SCREEN29_IJ_COMPLETE',flush=True)
