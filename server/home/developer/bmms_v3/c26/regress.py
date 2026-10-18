import json,os,subprocess,sys,time
from pathlib import Path
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
from ml_dtypes import bfloat16
variant=sys.argv[1]; root=Path('/home/developer/bmms_v3/variants')/variant
mode=sys.argv[2] if len(sys.argv)>2 else 'standard'
work=root/('work/c25_regression_'+mode);work.mkdir(parents=True,exist_ok=True)
(work/'input').mkdir(exist_ok=True);(work/'output').mkdir(exist_ok=True)
rng=np.random.default_rng(1032026)
shapes=[(1,1,1,32),(2,3,7,40),(3,17,19,72),(1,65,129,128),(2,129,257,256),(1,31,513,8192),(1,8192,17,32),(1,16,8192,64),(2,8,8,64),(3,1,8,8),(2,8,1,56),(1,8191,33,72),(1,511,64,128)]
if mode=='ay_smoke':shapes=[(8,16,32,128),(13,23,73,192),(16,32,128,256),(20,23,73,192)]
if mode=='ba_smoke':shapes=[(1,2048,1536,1280),(1,4096,1280,1152)]
if mode=='ax_smoke':shapes=[(15,7,13,48),(4,8,16,128),(8,16,32,128),(16,32,128,256)]
if mode=='av_smoke':shapes=[(1,3,5,40),(41,3,5,40)]
if mode=='aw_smoke':shapes=[(13,23,73,192),(1,23,73,192),(20,23,73,192)]
if mode=='at_smoke':shapes=[(1,16,32,128),(8,16,32,128),(41,16,32,128)]
if mode=='ao_smoke':shapes=[(1,3,5,40),(4,8,16,128)]
if mode=='am_smoke':shapes=[(13,23,73,192),(11,19,65,128),(12,9,79,64)]
if mode=='al_smoke':shapes=[(1,1536,2048,2048)]
if mode=='ak_smoke':shapes=[(1,1025,1031,1032),(1,513,769,776)]
if mode=='aj_smoke':shapes=[(1,64,8192,128),(1,32,8192,64)]
if mode=='ai_smoke':shapes=[(13,23,73,192),(2,7,13,48)]
if mode=='ag_smoke':shapes=[(4,8,16,128)]
if mode=='af_smoke':shapes=[(1,1025,1031,1032)]
if mode=='ae_smoke':shapes=[(1,1,1,32),(20,1,1,32)]
if mode=='ad_smoke':shapes=[(2,7,13,48),(2,7,13,40)]
if mode=='ac_smoke':shapes=[(13,23,73,192)]
if mode=='direct_tight':shapes=[(1,23,73,192),(3,17,33,128),(2,9,49,64),(1,32,81,256),(1,31,97,248),(1,5,113,72),(2,23,73,200)]
if mode=='medium_tail':shapes=[(1,1025,1031,1032),(1,1024,1024,1032),(1,1025,1031,520),(1,513,769,1032),(2,257,511,776),(1,2048,2048,1032),(1,1025,1031,1800)]
if mode=='tail_extra':shapes=[(1,1,65,40),(2,7,13,40),(3,17,19,72),(1,32,32,1016),(2,16,16,520),(3,31,31,264),(1,65,129,72),(1,129,257,40),(1,31,513,520),(2,256,128,264),(1,512,512,520),(20,31,127,248)]
if mode=='split':shapes=[(1,64,64,8192),(1,64,64,16384),(2,64,64,8192),(4,64,64,8192)]
if mode=='rows':shapes=[(3,17,19,72),(2,9,9,24),(1,31,31,56),(1,32,32,40)]
if mode=='pad':shapes=[(3,17,19,72),(2,7,13,40),(13,23,73,200),(1,31,127,255)]
if mode=='outer':shapes=[(2,7,13,48),(1,8,16,32),(41,8,16,64),(3,3,13,16)]
if mode=='target':shapes=[(1,512,1024,512),(1,1024,1024,8192),(1,2048,1536,1280)]
if mode=='clean_small':shapes=[(1,1,1,16),(3,1,1,48),(2,3,5,40),(4,5,11,56),(2,7,13,48),(3,8,16,128),(1,6,9,72),(8,16,32,128),(3,23,73,192),(2,31,127,248)]
if mode=='clean_split':shapes=[(1,64,64,8192),(2,49,37,2064),(1,17,9,2080),(1,1,1,2048)]
if mode=='clean_large':shapes=[(1,1025,1031,1032),(1,2048,1536,1280),(1,4096,1280,1152),(1,1536,2048,2048),(1,1280,4096,1536),(1,8192,64,128),(1,64,8192,128)]
if mode=='clean_vector':shapes=[(2,3,5,40),(4,5,11,56),(3,8,16,128),(1,6,9,72),(41,5,7,8),(2,8,1,56)]
if mode=='clean_coalesce':shapes=[(3,15,17,112),(11,21,63,200),(20,32,127,248)]
if mode=='clean_kmajor':shapes=[(2,2,6,24),(1,3,5,40),(41,7,7,56),(2,8,8,64),(1,1,8,8)]
if mode=='clean_kmajor_tt':shapes=[(3,6,9,72),(2,8,16,128),(41,5,11,104),(1,1,3,80)]
if mode=='clean_packed':shapes=[(1,1025,1031,1032),(2,777,899,1000),(1,1537,513,776),(1,520,512,2040),(1,512,1025,1032)]
if mode=='clean_no_sdk':shapes=[(1,1025,1031,1032),(1,64,8192,128)]
if mode=='clean_dot':shapes=[(1,1,1,8),(1,1,1,32),(7,1,1,40),(41,1,1,56),(2,1,1,256),(1,1,1,8192)]
if mode=='clean_consumer':shapes=[(2,33,35,40),(1,1025,1031,1032),(1,2048,1536,1280),(1,4096,1280,1152),(1,1536,2048,2048),(1,1280,4096,1536)]
if mode=='clean_bresident':shapes=[(1,1536,512,1024),(1,4096,1280,1152),(3,512,1280,1152),(1,2048,640,1536),(2,1024,2560,1792)]
if mode=='clean_smallcube':shapes=[(4,8,16,128),(2,5,11,80),(20,16,16,256),(3,3,7,112),(1,15,1,240)]
if mode=='clean_tailhybrid':shapes=[(2,129,257,520),(1,1025,1031,1032),(2,777,899,1000),(1,512,512,2040),(1,128,128,520)]
if mode=='clean_staged_debug':shapes=[(1,1025,1031,1032)]
rows=[]
for shape in shapes:
 for dtype in (1,2):
  for ta,tb in ([(0,0),(1,1)] if mode=='clean_dot' else [(1,1)] if mode=='clean_kmajor_tt' else [(1,0)] if mode=='clean_kmajor' else [(0,0),(0,1),(1,0),(1,1)]):
   B,M,N,K=shape;typ=np.float16 if dtype==1 else bfloat16
   a=rng.uniform(-1,1,(B,M,K)).astype(typ);b=rng.uniform(-1,1,(B,K,N)).astype(typ)
   if shape in [(2,3,7,40),(2,7,13,40),(8,16,32,128),(20,23,73,192),(41,3,5,40),(41,5,7,8),(11,21,63,200),(41,7,7,56),(41,5,11,104),(2,777,899,1000),(41,1,1,56),(2,33,35,40)]:a=np.abs(a).astype(typ);b=-np.abs(b).astype(typ)
   golden=(a.astype(np.float64)@b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
   (a.swapaxes(-1,-2).copy() if ta else a).tofile(work/'input/x1.bin')
   (b.swapaxes(-1,-2).copy() if tb else b).tofile(work/'input/x2.bin')
   yfile=work/'output/y.bin'
   if yfile.exists():yfile.unlink()
   env=dict(os.environ);env['BMMS_DEVICE_ID']='0';start=time.monotonic()
   try:
    proc=subprocess.run([str(root/'build/bench'),*map(str,shape),str(dtype),str(ta),str(tb),'1','1'],cwd=work,capture_output=True,text=True,timeout=60,env=env)
    y=np.fromfile(yfile,np.float32) if yfile.exists() else np.empty(0)
    ok=proc.returncode==0 and y.shape==golden.shape and np.isfinite(y).all() and np.allclose(y,golden,atol=1e-4,rtol=1e-4)
    rel=float(np.max(np.abs(y-golden)/np.maximum(np.abs(golden),1e-5))) if y.shape==golden.shape else None
    row={'shape':shape,'dtype':dtype,'ta':ta,'tb':tb,'passed':bool(ok),'relative':rel,'returncode':proc.returncode,'seconds':time.monotonic()-start}
    if not ok:
     row['stdout']=proc.stdout[-3000:];row['stderr']=proc.stderr[-1000:];row['actual']=y.tolist();row['golden']=golden.tolist()
     np.savez(work/('fail_'+str(len(rows))+'.npz'),a=a,b=b,golden=golden,actual=y)
   except subprocess.TimeoutExpired:
    row={'shape':shape,'dtype':dtype,'ta':ta,'tb':tb,'passed':False,'timeout':True}
   rows.append(row);print(json.dumps(row),flush=True)
   (work/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
   if row.get('timeout'):raise SystemExit('timeout: stop to avoid concurrent stalled NPU work')
print('PASS:',sum(r['passed'] for r in rows),'/',len(rows),'cases',flush=True)
raise SystemExit(0 if all(r['passed'] for r in rows) else 1)
