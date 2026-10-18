from pathlib import Path
import subprocess,os,json,sys
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
root=Path('/home/developer/bmms_v3')
variant=sys.argv[1]
source=root/'variants/clean38/work/c25_regression_clean_padded_chunks'
work=root/'variants'/variant/'research/chunk_replay'
(work/'input').mkdir(parents=True,exist_ok=True);(work/'output').mkdir(exist_ok=True)
out=[]
for index,dtype in [(18,1),(22,2)]:
 z=np.load(source/f'fail_{index}.npz');a,b,gold=z['a'],z['b'],z['golden']
 a.swapaxes(-1,-2).copy().tofile(work/'input/x1.bin');b.tofile(work/'input/x2.bin')
 B,M,K=a.shape;N=b.shape[-1];env=dict(os.environ,BMMS_DEVICE_ID='0')
 p=subprocess.run([str(root/'variants'/variant/'build/bench'),str(B),str(M),str(N),str(K),str(dtype),'1','0','1','1'],cwd=work,env=env,capture_output=True,text=True,timeout=60)
 y=np.fromfile(work/'output/y.bin',np.float32)
 row=dict(variant=variant,fixture=index,returncode=p.returncode,actual=y.tolist(),golden=gold.tolist(),passed=bool(p.returncode==0 and np.allclose(y,gold,rtol=1e-4,atol=1e-4)))
 out.append(row);print(json.dumps(row),flush=True)
(work/'results.json').write_text(json.dumps(out,indent=2)+'\n')
