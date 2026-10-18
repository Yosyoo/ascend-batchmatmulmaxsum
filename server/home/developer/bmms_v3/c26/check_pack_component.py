from pathlib import Path
import os,subprocess,json
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
import ml_dtypes
root=Path('/home/developer/bmms_v3')
work=root/'c26/pack_component'
(work/'input').mkdir(exist_ok=True);(work/'output').mkdir(exist_ok=True)
results=[]
for fixture,dtype in [(18,1),(22,2)]:
 z=np.load(root/f'variants/clean38/work/c25_regression_clean_padded_chunks/fail_{fixture}.npz')
 a=z['a'].swapaxes(-1,-2).copy();b=z['b'].copy()
 a.tofile(work/'input/x1.bin');b.tofile(work/'input/x2.bin')
 B,K,M=a.shape;N=b.shape[-1]
 for full in [0,1]:
  p=subprocess.run([str(work/'build/pack_component'),str(B),str(M),str(N),str(K),str(dtype),'1','0',str(full),'20'],cwd=work,capture_output=True,text=True,timeout=60)
  assert p.returncode==0,(p.returncode,p.stdout,p.stderr)
  mp=(M+127)//128*128 if full else (M+15)//16*16
  npad=(N+255)//256*256 if full else (N+15)//16*16
  kp=(K+15)//16*16
  for name,data,dr,dc in [('A',a,kp,mp),('B',b,kp,npad)]:
   padded=np.zeros((B,dr,dc),np.uint16)
   padded[:,:data.shape[1],:data.shape[2]]=data.view(np.uint16)
   expected=padded.reshape(B,dr//16,16,dc).transpose(0,1,3,2).copy()
   actual=np.fromfile(work/f'output/packed{name}.bin',np.uint16).reshape(expected.shape)
   idx=np.argwhere(expected!=actual)
   r=dict(fixture=fixture,dtype=dtype,full_padding=full,operand=name,mismatches=len(idx),first=[])
   for i in idx[:12]:
    q=tuple(i);r['first'].append(dict(index=i.tolist(),expected=int(expected[q]),actual=int(actual[q])))
   print(json.dumps(r),flush=True);results.append(r)
(work/'results.json').write_text(json.dumps(results,indent=2)+'\n')
