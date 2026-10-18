from pathlib import Path
import hashlib,json,difflib
r=Path(__file__).resolve().parents[2];w=r/'work/solo20'
base=(r/'variants/s20b/kernel.asc').read_bytes();s=base.decode()
oldsha=hashlib.sha256(base).hexdigest()
assert oldsha=='d0c2321563e205a69262209ed75fc54d8037f59a39e858acc17f8e675fdb8160'
# Non-DB manual path specialization. No new allocation or change to tile planning.
pairs=[(128,128),(128,256),(256,32),(64,128)];rows=[]
for tm,tn in pairs:
    for k in range(16,1025,16):
        bk=min(k,(32768//max(tm,tn))//16*16)
        x=dict(tileM=tm,tileN=tn,K=k,L1_bytes=2*(tm+tn)*bk,L0A_bytes=2*tm*bk,L0B_bytes=2*tn*bk,L0C_bytes=4*tm*tn,UB_bytes=4*tm*min(tn,128)+8*((tm+7)//8*8)+32768+8*8192)
        assert x['L1_bytes']<=524288 and x['L0A_bytes']<=65536 and x['L0B_bytes']<=65536 and x['L0C_bytes']<=131072 and x['UB_bytes']<=184320
        assert tm//16*(bk//16)<=255 and tn//16*(bk//16)<=255
        rows.append(x)
budget=dict(variant='s20e',parent='s20b',capacity_calculated_before_edit=True,combinations=len(rows),maxima={key:max(x[key] for x in rows) for key in ['L1_bytes','L0A_bytes','L0B_bytes','L0C_bytes','UB_bytes']},
    change='Only compile-time TM/TN for four general tile pairs in the existing BMMS_MANUAL fallback. Same host tiling/workspace values, input offsets, buffer layout, K chunk size, MAD order, AIV math and one launch. Existing narrow/full/small/64x128x128 precedence unchanged.',
    K_gate='Existing useManual enforces no paired/packed inputs, K multiple16. PairedK covers unpacked even K>1024; the specializations are additionally gated K<=1024 explicitly.')
(w/'resource_s20e_before_edit.json').write_text(json.dumps(budget,indent=2),encoding='utf8')
needle='    else bmms_manual<T, A, B><<<cores, nullptr, stream>>>(x1, x2, matrix, maxima, y, b, m, n, k, ns, tileM, tileN); \\\n'
assert s.count(needle)==1
new=''.join(f'    else if(k<=1024 && tileM=={tm} && tileN=={tn}) bmms_manual<T,A,B,{tm},{tn}><<<cores,nullptr,stream>>>(x1,x2,matrix,maxima,y,b,m,n,k,ns,tileM,tileN); \\\n' for tm,tn in pairs)+needle
s=s.replace(needle,new)
dst=r/'variants/s20e';dst.mkdir(exist_ok=False);(dst/'kernel.asc').write_bytes(s.encode());sha=hashlib.sha256(s.encode()).hexdigest()
(w/'s20e_changes.patch').write_text(''.join(difflib.unified_diff(base.decode().splitlines(True),s.splitlines(True),fromfile='s20b/kernel.asc',tofile='s20e/kernel.asc')),encoding='utf8')
dst=r/'delivery_round20/s20e';dst.mkdir(parents=True,exist_ok=False);(dst/'kernel.asc').write_bytes(s.encode())
(dst/'candidate_status.json').write_text(json.dumps(dict(variant='s20e',source_sha256=sha,source_bytes=len(s.encode()),compiled=False,precision_validated=False,performance_validated=False,official_submitted=False,state='local_candidate'),indent=2),encoding='utf8')
for old,new in [('run_b_final.py','run_e_final.py'),('verify20_b_final.py','verify20_e_final.py')]:
    text=(w/old).read_text(encoding='utf8')
    for a,b in [('s20b','s20e'),('diagnostic_20b','diagnostic_20e'),('hangs20_b','hangs20_e'),('remote_round20_b_final','remote_round20_e_final'),(oldsha,sha)]:text=text.replace(a,b)
    (w/new).write_bytes(text.encode())
text=(w/'compile_c.sh').read_text(encoding='utf8')
for a,b in [('s20c','s20e'),('diagnostic_20c','diagnostic_20e'),('compiler20_c','compiler20_e'),('e3b429c07ee8a2d133151a4ee6c09f1621d5d82dc207560da4a1f7152c38ee8d',sha)]:text=text.replace(a,b)
# This script performs pure compilation only, independent of the serial NPU runner.
text=text.replace('flock -n solo17_data/.npu_serial.lock true\n','')
(w/'compile_e.sh').write_bytes(text.encode())
print(json.dumps(dict(variant='s20e',source_sha256=sha,source_bytes=len(s.encode()),capacity=budget['maxima'])))
