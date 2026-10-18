"""Sequential NPU checks: narrow precision, order-swapped pool, targeted timings, hangs."""
import json
import subprocess
import sys
from pathlib import Path

root = Path('/home/developer/bmms_v3')
v = sys.argv[1] if len(sys.argv)>1 else 's9h'
out = root / 'solo9_data' / ('final_'+v)
out.mkdir(exist_ok=True)

def run(label, command, filename, timeout=900):
    print('START', label, flush=True)
    with (out/filename).open('w') as f:
        p = subprocess.run(command,cwd=root,stdout=f,stderr=subprocess.STDOUT,timeout=timeout)
    print('END', label, 'RC', p.returncode, flush=True)
    if p.returncode:
        print((out/filename).read_text()[-4000:],flush=True)
        raise SystemExit(p.returncode)

for order,variants in [(1,['s6v',v]),(2,[v,'s6v'])]:
    for variant in variants:
        filename = f'pool{order}_{variant}.json'
        run(filename,['python3','harness/multi.py',variant,'shapes_pool2.txt','160'],filename)
        data = json.loads((out/filename).read_text())
        assert data['ntasks'] == 16000 and len(data['shapes']) == 100 and 'leftover' not in data

specs=['1_1_1_32_1_0_0','2_7_13_48_1_0_1','4_8_16_128_2_1_1',
       '8_16_32_128_1_0_0','13_23_73_192_2_0_1','16_32_128_256_1_1_0',
       '1_64_8192_128_2_0_1','1_64_64_8192_1_1_1','1_1025_1031_1032_2_1_1','1_8192_64_128_1_0_0',
       '1_3_5_40_2_1_0','1_2048_1536_1280_1_0_1','1_4096_1280_1152_2_0_0',
       '1_1536_2048_2048_1_1_1','1_1280_4096_1536_2_1_0']
for order,variants in [(1,'s6v,'+v),(2,v+',s6v')]:
    import os
    os.environ['BMMS_SCAN_LABEL']='solo9_final'+str(order)
    run('target '+variants,['python3','solo8_scan_single.py',variants,*specs],
        'target_'+variants.replace(',','_')+'.log')

hangs=['1_4096_4096_1024','1_8192_512_1024','1_4096_1024_512',
       '1_2048_2048_1024','1_8192_256_512','2_4096_2048_512']
for spec in hangs:
    run('hang '+spec,['timeout','120','python3','harness/one.py',v,spec],
        'hang_'+v+'_'+spec+'.log',timeout=150)
    assert 'passed= True' in (out/('hang_'+v+'_'+spec+'.log')).read_text(), spec
print('PASS: performance protocol and six historical hang shapes',flush=True)
