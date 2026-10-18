from pathlib import Path
import importlib.util
import json
import os
import statistics
import sys

root=Path('/home/developer/bmms_v3')
spec=importlib.util.spec_from_file_location('guarded_measure',root/'c46/measure153.py')
# Import only the common runner prefix, not the focused ABBA execution.
context={'__name__':'guarded_full15','__file__':str(spec.origin)}
source=Path(spec.origin).read_text().split("points=['P2','P3','P4']; candidate='clean153'",1)[0]
source=source.replace('MODE = sys.argv[1]',"MODE = 'final'+sys.argv[1]")
exec(compile(source,str(spec.origin),'exec'),context)
variant=sys.argv[1]
shapes=[
 '1_1_1_32_1_0_0','1_3_5_40_2_1_0','2_7_13_48_1_0_1',
 '4_8_16_128_2_1_1','8_16_32_128_1_0_0','13_23_73_192_2_0_1',
 '16_32_128_256_1_1_0','1_1025_1031_1032_2_1_1','1_2048_1536_1280_1_0_1',
 '1_4096_1280_1152_2_0_0','1_1536_2048_2048_1_1_1','1_1280_4096_1536_2_1_0',
 '1_8192_64_128_1_0_0','1_64_8192_128_2_0_1','1_64_64_8192_1_1_1']
for i,s in enumerate(shapes,1):context['SPECS']['P'+str(i)]=s
rows=[]
for i in range(1,16):
 row=context['run']('P'+str(i),variant,'final15')
 row.update(case=i)
 rows.append(row)
 (root/'c46'/(variant+'_local15.json')).write_text(json.dumps(rows,indent=2)+'\n')
print('FULL15 PASS',variant,flush=True)
