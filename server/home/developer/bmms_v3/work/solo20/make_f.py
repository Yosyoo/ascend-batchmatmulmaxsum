from pathlib import Path
import hashlib,json,difflib
r=Path(__file__).resolve().parents[2];w=r/'work/solo20'
base=(r/'variants/s20e/kernel.asc').read_bytes();s=base.decode();oldsha=hashlib.sha256(base).hexdigest()
assert oldsha=='2458dd18843d9de805968ffd61ccaa56c7d3687768374bc18424131901aae5f1'
rows=json.loads((w/'resource_s20a_combinations.json').read_text(encoding='utf8'))
pairs=[(128,128),(128,256),(64,128)]
selected=[x for x in rows if (x['tileM'],x['tileN']) in pairs]
assert selected and all(x['L1_bytes']<=524288 and x['L0A_bytes']<=65536 and x['L0B_bytes']<=65536 and x['L0C_bytes']<=131072 and x['UB_bytes']<=184320 for x in selected)
budget=json.loads((w/'resource_s20b_before_edit.json').read_text(encoding='utf8'))
budget.update(variant='s20f',parent='s20e',capacity_calculated_before_edit=True,
    change='Same DB kernel body, compile-time TM/TN for general 128x128/128x256/64x128 pairs under the existing DB gate. Complements s20e normal manual specialization, keeps runtime K and all host/workspace parameters unchanged.',
    specialization_combinations=len(selected),specialization_maxima={k:max(x[k] for x in selected) for k in budget['maxima']})
(w/'resource_s20f_before_edit.json').write_text(json.dumps(budget,indent=2),encoding='utf8')
old='    if(useManualDB) bmms_manual_db<T,A,B><<<cores,nullptr,stream>>>(x1,x2,matrix,maxima,y,b,m,n,k,ns,tileM,tileN); \\\n'
new='    if(useManualDB) { \\\n'+''.join(('        if' if i==0 else '        else if')+f'(tileM=={tm} && tileN=={tn}) bmms_manual_db<T,A,B,{tm},{tn}><<<cores,nullptr,stream>>>(x1,x2,matrix,maxima,y,b,m,n,k,ns,tileM,tileN); \\\n' for i,(tm,tn) in enumerate(pairs))+'        else bmms_manual_db<T,A,B><<<cores,nullptr,stream>>>(x1,x2,matrix,maxima,y,b,m,n,k,ns,tileM,tileN); \\\n    } \\\n'
assert s.count(old)==1;s=s.replace(old,new)
dst=r/'variants/s20f';dst.mkdir(exist_ok=False);(dst/'kernel.asc').write_bytes(s.encode());sha=hashlib.sha256(s.encode()).hexdigest()
(w/'s20f_changes.patch').write_text(''.join(difflib.unified_diff(base.decode().splitlines(True),s.splitlines(True),fromfile='s20e/kernel.asc',tofile='s20f/kernel.asc')),encoding='utf8')
dst=r/'delivery_round20/s20f';dst.mkdir(parents=True,exist_ok=False);(dst/'kernel.asc').write_bytes(s.encode())
(dst/'candidate_status.json').write_text(json.dumps(dict(variant='s20f',source_sha256=sha,source_bytes=len(s.encode()),compiled=False,precision_validated=False,performance_validated=False,official_submitted=False,state='local_candidate'),indent=2),encoding='utf8')
for old,new in [('run_e_final.py','run_f_final.py'),('verify20_e_final.py','verify20_f_final.py')]:
    text=(w/old).read_text(encoding='utf8')
    for a,b in [('s20e','s20f'),('diagnostic_20e','diagnostic_20f'),('hangs20_e','hangs20_f'),('remote_round20_e_final','remote_round20_f_final'),(oldsha,sha)]:text=text.replace(a,b)
    (w/new).write_bytes(text.encode())
text=(w/'compile_e.sh').read_text(encoding='utf8')
for a,b in [('s20e','s20f'),('diagnostic_20e','diagnostic_20f'),('compiler20_e','compiler20_f'),(oldsha,sha)]:text=text.replace(a,b)
(w/'compile_f.sh').write_bytes(text.encode())
print(json.dumps(dict(variant='s20f',source_sha256=sha,source_bytes=len(s.encode()),capacity=budget['specialization_maxima'])))
