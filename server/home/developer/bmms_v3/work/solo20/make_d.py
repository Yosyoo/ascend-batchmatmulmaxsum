from pathlib import Path
import hashlib,json,difflib
r=Path(__file__).resolve().parents[2];w=r/'work/solo20'
base=(r/'variants/s20b/kernel.asc').read_bytes();s=base.decode()
oldsha=hashlib.sha256(base).hexdigest()
assert oldsha=='d0c2321563e205a69262209ed75fc54d8037f59a39e858acc17f8e675fdb8160'
# Check both compile-time tile pairs before any operator edit. Exact same dynamic
# tile/workspace arguments and loop ordering are retained; K remains runtime input.
budget=json.loads((w/'resource_s20b_before_edit.json').read_text(encoding='utf8'))
rows=json.loads((w/'resource_s20a_combinations.json').read_text(encoding='utf8'))
selected=[x for x in rows if (x['tileM'],x['tileN']) in {(128,256),(64,128)}]
assert selected and all(x['L1_bytes']<=524288 and x['L0A_bytes']<=65536 and x['L0B_bytes']<=65536 and x['L0C_bytes']<=131072 and x['UB_bytes']<=184320 for x in selected)
budget.update(variant='s20d',parent='s20b',capacity_calculated_before_edit=True,
    change='Compile-time tile specialization for 128x256 and 64x128 under the existing DB gate. No tensor sizes, host tiling, workspace, MAD order or output arithmetic changes.',
    specialization_combinations=len(selected),specialization_maxima={k:max(x[k] for x in selected) for k in budget['maxima']})
(w/'resource_s20d_before_edit.json').write_text(json.dumps(budget,indent=2),encoding='utf8')
old='    if(useManualDB) bmms_manual_db<T,A,B><<<cores,nullptr,stream>>>(x1,x2,matrix,maxima,y,b,m,n,k,ns,tileM,tileN); \\\n'
new='''    if(useManualDB) { \\
        if(tileM==128 && tileN==256) bmms_manual_db<T,A,B,128,256><<<cores,nullptr,stream>>>(x1,x2,matrix,maxima,y,b,m,n,k,ns,tileM,tileN); \\
        else if(tileM==64 && tileN==128) bmms_manual_db<T,A,B,64,128><<<cores,nullptr,stream>>>(x1,x2,matrix,maxima,y,b,m,n,k,ns,tileM,tileN); \\
        else bmms_manual_db<T,A,B><<<cores,nullptr,stream>>>(x1,x2,matrix,maxima,y,b,m,n,k,ns,tileM,tileN); \\
    } \\
'''
assert s.count(old)==1;s=s.replace(old,new)
dst=r/'variants/s20d';dst.mkdir(exist_ok=False);(dst/'kernel.asc').write_bytes(s.encode())
sha=hashlib.sha256(s.encode()).hexdigest()
(w/'s20d_changes.patch').write_text(''.join(difflib.unified_diff(base.decode().splitlines(True),s.splitlines(True),fromfile='s20b/kernel.asc',tofile='s20d/kernel.asc')),encoding='utf8')
dst=r/'delivery_round20/s20d';dst.mkdir(parents=True,exist_ok=False);(dst/'kernel.asc').write_bytes(s.encode())
(dst/'candidate_status.json').write_text(json.dumps(dict(variant='s20d',source_sha256=sha,source_bytes=len(s.encode()),compiled=False,precision_validated=False,performance_validated=False,official_submitted=False),indent=2),encoding='utf8')
for old,new in [('run_b_final.py','run_d_final.py'),('verify20_b_final.py','verify20_d_final.py')]:
    text=(w/old).read_text(encoding='utf8')
    for a,b in [('s20b','s20d'),('diagnostic_20b','diagnostic_20d'),('hangs20_b','hangs20_d'),('remote_round20_b_final','remote_round20_d_final'),(oldsha,sha)]:text=text.replace(a,b)
    (w/new).write_bytes(text.encode())
text=(w/'compile_c.sh').read_text(encoding='utf8')
for a,b in [('s20c','s20d'),('diagnostic_20c','diagnostic_20d'),('compiler20_c','compiler20_d'),('e3b429c07ee8a2d133151a4ee6c09f1621d5d82dc207560da4a1f7152c38ee8d',sha)]:text=text.replace(a,b)
(w/'compile_d.sh').write_bytes(text.encode())
print(json.dumps(dict(variant='s20d',source_sha256=sha,source_bytes=len(s.encode()),capacity=budget['specialization_maxima'])))
