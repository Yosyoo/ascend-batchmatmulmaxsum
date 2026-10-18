from pathlib import Path
import subprocess,time,os,json
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
for v,sha,log,mark in [
    ('s29b','f2c81cc63a63c4858e7166b05046c20708b18e1ae03f0810e63be24ed4258196','compile29_b.log','COMPILE28_COMPLETE'),
    ('s29c','b6cfaa2e69d3b04e25ca109129e7f1e5eb244ea757ced718c81f97f5570d1038','compile29_c_retry1.log','COMPILE29_SCREEN_COMPLETE')]:
    deadline=time.monotonic()+900
    while mark not in (d/log).read_text(errors='replace'):
        assert time.monotonic()<deadline,('compile timeout',v)
        if 'error:' in (d/log).read_text(errors='replace'):raise RuntimeError(('compile failed',v))
        time.sleep(5)
    print('SCREEN_BEGIN',v,flush=True)
    p=subprocess.run(['python3',str(r/'work/solo28/diagnostic.py'),v,sha])
    if p.returncode:print('REJECT_DIAGNOSTIC',v,flush=True);continue
    if v=='s29c':
        p=subprocess.run(['python3',str(r/'work/solo28/run_stress.py'),v,sha])
        if p.returncode:print('REJECT_STRESS',v,flush=True);continue
    p=subprocess.run(['python3',str(r/'work/solo28/quick_compare.py'),v,'s28d','quick29_'+v[-1],str(r/'work/solo29/quick_shapes.txt')])
    if p.returncode:print('REJECT_PERFORMANCE_CONTRACT',v,flush=True);continue
print('SCREEN29_BC_COMPLETE',flush=True)
