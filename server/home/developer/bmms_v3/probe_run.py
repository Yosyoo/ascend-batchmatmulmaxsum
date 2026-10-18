import numpy as np, subprocess, os, sys
from pathlib import Path
os.environ["VARIANTS_ROOT"]="/home/developer/bmms_v3/variants"
sys.path.insert(0,"/home/developer/bmms_v3/harness")
from measure import gen_data
v=sys.argv[1]
d=Path("/home/developer/bmms_v3/variants/%s/work/probe"%v); d.mkdir(parents=True,exist_ok=True)
gen_data(d,128,32,32,32,1,0,0)
r=subprocess.run(["/home/developer/bmms_v3/variants/%s/build/bench"%v,"128","32","32","32","1","0","0","1","1"],cwd=d,capture_output=True,text=True)
print("rc",r.returncode)
y=np.fromfile(d/"output/y.bin",np.float32)
print("A) WholeReduceSum(dstRepStride=1, repeat=4, mask=64) -> y[0..15]:")
print("  ", [round(float(x),1) for x in y[:16]])
print("   correct sums are 2080, 6176, 10272, 14368")
print("   PACKED  => [2080, 6176, 10272, 14368, -7, -7, ...]")
print("   DATABLK => [2080, -7, -7, -7, -7, -7, -7, -7, 6176, ...]")
print("B) same but dstRepStride=8 -> y[64..79]:")
print("  ", [round(float(x),1) for x in y[64:80]])
