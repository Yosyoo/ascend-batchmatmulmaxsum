from pathlib import Path
import difflib,hashlib,json
r=Path(__file__).resolve().parents[2];w=r/'work/solo23'
old=(r/'variants/s23m/kernel.asc').read_bytes();parent=json.loads((w/'source_m.json').read_text())['sha256']
assert hashlib.sha256(old).hexdigest()==parent
scope=json.loads((w/'probe_m/results.jsonl').read_text().splitlines()[0])
budget=dict(variant='s23p',parent='s23m',capacity_calculated_before_edit=True,
    scope='M fullBase scope112x128 only, NN B1, original128x128grid16,M>=N,K2048..8192 multiple32,20Cube available',
    UB_max=112*128*4+112*4+2*2048*4+512+32,L1_bytes=8*(112+128)*128*2,
    L0A_bytes=2*112*128*2,L0B_bytes=2*128*128*2,L0C_bytes=112*128*4,
    GM_C_max=20*112*128*4,GM_maxima_max=8192,
    change='Explicit8-bankL1 and2-bankL0 pipeline,2FP32 half-K sums,Fix overwrite thenatomic add,Vector valid max and paired-row sum in one mixedkernel',
    host_kernel_workspace_same_source=True,real_inputs_each_call=True)
for key,limit in [('UB_max',184320),('L1_bytes',524288),('L0A_bytes',65536),('L0B_bytes',65536),('L0C_bytes',131072)]:assert budget[key]<=limit
assert budget['UB_max']==74720 and budget['L1_bytes']==491520
(w/'resource_s23p_before_edit.json').write_bytes((json.dumps(budget,indent=2)+'\n').encode())
s=old.decode();needle='template<class T, bool TA, bool TB, int M, int N, int K>\n__global__ __aicore__ __mix__(1, 1) void bmms_full'
assert s.count(needle)==1;s=s.replace(needle,(w/'ring_pair.asc').read_text()+'\n'+needle)
needle='size_t matrixBytes = (useKParallel ? (size_t)tasks : (size_t)cores*2) * tileM * tileN * 4;';assert s.count(needle)==1
s=s.replace(needle,'size_t matrixBytes = (useKParallel ? (size_t)tasks : fullBase ? (size_t)cores : (size_t)cores*2) * tileM * tileN * 4;')
needle='    if(useKParallel) {\n        if(info_x1.tensors[0].dtype==2)';assert s.count(needle)==1
s=s.replace(needle,'''    if(fullBase) {
        if(info_x1.tensors[0].dtype==2)bmms_ring_pair<bfloat16_t><<<cores,nullptr,stream>>>(x1,x2,matrix,maxima,y,m,n,k,ns);
        else bmms_ring_pair<half><<<cores,nullptr,stream>>>(x1,x2,matrix,maxima,y,m,n,k,ns);
        return;
    }
'''+needle)
dst=r/'variants/s23p';dst.mkdir(exist_ok=False);(dst/'kernel.asc').write_bytes(s.encode())
sha=hashlib.sha256(s.encode()).hexdigest();(w/'source_p.json').write_bytes((json.dumps(dict(variant='s23p',sha256=sha,bytes=len(s.encode())),indent=2)+'\n').encode())
(w/'s23p_changes.patch').write_bytes(''.join(difflib.unified_diff(old.decode().splitlines(True),s.splitlines(True),fromfile='s23m/kernel.asc',tofile='s23p/kernel.asc')).encode())
for name in ['compile_m.sh','run_m_pilot.py']:
    x=(w/name).read_text().replace(parent,sha).replace('s23m','s23p').replace('23m','23p').replace('23_m','23_p').replace('pilot23_base_parent_m','pilot23_base_parent_p')
    (w/name.replace('_m','_p')).write_bytes(x.encode())
print(json.dumps(dict(variant='s23p',sha256=sha,budget=budget)))
