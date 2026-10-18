import os
import subprocess
import sys
from pathlib import Path

root=Path('/home/developer/bmms_v3')
variant=sys.argv[1]
out=root/'solo10_data'/('final_'+variant)
specs=['1_8_16_128_1_1_0','1_8_16_128_1_1_1','21_8_16_128_2_1_1',
       '64_8_16_128_1_1_0','1_8_16_128_1_0_1']
for order,variants in [(1,'s9j,'+variant),(2,variant+',s9j')]:
    os.environ['BMMS_SCAN_LABEL']='solo10_layout'+str(order)
    print('START layouts',order,variants,flush=True)
    with (out/f'layout{order}.log').open('w') as f:
        subprocess.run(['python3','solo8_scan_single.py',variants,*specs],cwd=root,
                       stdout=f,stderr=subprocess.STDOUT,timeout=600,check=True)
    print('END layouts',order,flush=True)
