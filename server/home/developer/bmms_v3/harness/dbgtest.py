import numpy as np, subprocess, os, sys
from pathlib import Path
os.environ["VARIANTS_ROOT"]="/home/developer/bmms_v3/variants"
sys.path.insert(0,"/home/developer/bmms_v3/harness")
from measure import gen_data
v=sys.argv[1]
specs=sys.argv[2:]
worst=0
for spec in specs:
    p=[int(x) for x in spec.split('_')]
    B,M,N,K=p[0],p[1],p[2],p[3]
    dt=p[4] if len(p)>4 else 1; ta=p[5] if len(p)>5 else 0; tb=p[6] if len(p)>6 else 0
    d=Path("/home/developer/bmms_v3/variants/%s/work/dbg"%v); d.mkdir(parents=True,exist_ok=True)
    gold=gen_data(d,B,M,N,K,dt,ta,tb)
    r=subprocess.run(["/home/developer/bmms_v3/variants/%s/build/bench"%v,str(B),str(M),str(N),str(K),str(dt),str(ta),str(tb),"1","1"],cwd=d,capture_output=True,text=True)
    y=np.fromfile(d/"output/y.bin",np.float32)
    rel=float(np.max(np.abs(y-gold)/np.maximum(np.abs(gold),1e-5)))
    worst=max(worst,rel)
    print("  %-22s dt%d ta%d tb%d maxrel=%.6f %s"%(spec,dt,ta,tb,rel,"OK" if rel<1e-3 else "FAIL"))
print("WORST %.6f"%worst)
