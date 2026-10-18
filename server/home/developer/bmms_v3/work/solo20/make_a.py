from pathlib import Path
import difflib,hashlib,json
r=Path(__file__).resolve().parents[2];w=r/'work/solo20';w.mkdir(exist_ok=True)
base=(r/'variants/s19i/kernel.asc').read_bytes();s=base.decode()
assert hashlib.sha256(base).hexdigest()=='314d61425771496515f98d3668d9559af1d6fcdab9df2e04f0a6dcc86e103a7f'
# Capacity is computed before editing any operator source. No L0 double buffering.
rows=[]
for tm in [16,32,64,128]:
    for tn in [16,32,64,128,256]:
        for k in range(16,1025,16):
            bk=min(k,(32768//max(tm,tn))//16*16)
            if k<=bk:continue
            row=dict(tileM=tm,tileN=tn,K=k,bk=bk,L1_bytes=4*(tm+tn)*bk,
                L0A_bytes=2*tm*bk,L0B_bytes=2*tn*bk,L0C_bytes=4*tm*tn,
                UB_bytes=4*tm*min(tn,128)+8*((tm+7)//8*8)+32768+8*8192)
            assert row['L1_bytes']<=524288 and row['L0A_bytes']<=65536 and row['L0B_bytes']<=65536
            assert row['L0C_bytes']<=131072 and row['UB_bytes']<=184320
            assert (tm//16)*(bk//16)<=255 and (tn//16)*(bk//16)<=255
            rows.append(row)
budget=dict(variant='s20a',parent='s19i',capacity_calculated_before_edit=True,combinations=len(rows),
    maxima={key:max(x[key] for x in rows) for key in ['L1_bytes','L0A_bytes','L0B_bytes','L0C_bytes','UB_bytes']},
    gate='Existing manual gate, M/N<=8192, tileM<=128, K>current bk. Existing manual gate already enforces K<=1024, K multiple16, workload<2^28, no packed inputs.',
    change='Two L1 banks; prefetch next chunk and refill bank after its MTE1 release. Same one L0A/B bank, same MAD accumulation order and one Fixpipe per output tile.',
    unchanged='AIV code, host tiling/workspace formulas, precision tolerance, real current input reads, one kernel launch.')
(w/'resource_s20a_before_edit.json').write_text(json.dumps(budget,indent=2),encoding='utf8')
(w/'resource_s20a_combinations.json').write_text(json.dumps(rows),encoding='utf8')
start=s.index('template<class T, bool TA, bool TB, int TM = 0, int TN = 0, int TK = 0>\n__global__ __aicore__ __mix__(1, 1) void bmms_manual(')
end=s.index('template<class T, bool TA, bool TB, int TM = 0, int TN = 0, int TK = 0>\n__global__ __aicore__ __mix__(1, 1) void bmms_manual_narrow(',start)
f=s[start:end].replace('void bmms_manual(','void bmms_manual_db(',1)
def once(old,new):
    global f
    assert f.count(old)==1,old
    f=f.replace(old,new)
once('''        LocalTensor<T> l1a(TPosition::A1, 0, mp * bk);
        LocalTensor<T> l1b(TPosition::B1, mp * bk * 2, np * bk);
''','''        const int32_t bankBytes=(mp+np)*bk*2;
''')
once('bool l1Busy = false, l0Busy = false, fixBusy = false;',
     'bool l1Busy[2]={false,false}; bool l0Busy=false,fixBusy=false;')
loopstart=f.index('                    for (int32_t k0 = 0; k0 < k; k0 += bk) {')
copyStart=f.index('                        // ---- GM(ND) -> L1(NZ) ----',loopstart)
copyEnd=f.index('                        WaitFlag<HardEvent::MTE2_MTE1>(EVENT_ID0);',copyStart)
copy=f[copyStart:copyEnd].replace('SetFlag<HardEvent::MTE2_MTE1>(EVENT_ID0);','SetFlag<HardEvent::MTE2_MTE1>(event);')
# All input offsets and ND-to-NZ layouts are copied unchanged from the validated manual path.
prefetch='''                    const auto prefetch=[&](int32_t k0,int32_t bank) {
                        const auto event=bank==0?EVENT_ID0:EVENT_ID1;
                        if(l1Busy[bank]) {
                            WaitFlag<HardEvent::MTE1_MTE2>(event);l1Busy[bank]=false;
                        }
                        LocalTensor<T> l1a(TPosition::A1,bank*bankBytes,mp*bk);
                        LocalTensor<T> l1b(TPosition::B1,bank*bankBytes+mp*bk*2,np*bk);
                        const int32_t kk=k0+bk<=k?bk:k-k0;
                        const int32_t kk16=(kk+15)/16*16;
'''+copy+'''                    };
                    prefetch(0,0);
                    if(bk<k) prefetch(bk,1);
                    for (int32_t k0 = 0; k0 < k; k0 += bk) {
                        const int32_t bank=(k0/bk)&1;
                        const auto event=bank==0?EVENT_ID0:EVENT_ID1;
                        LocalTensor<T> l1a(TPosition::A1,bank*bankBytes,mp*bk);
                        LocalTensor<T> l1b(TPosition::B1,bank*bankBytes+mp*bk*2,np*bk);
                        const int32_t kk=k0+bk<=k?bk:k-k0;
                        const int32_t kk16=(kk+15)/16*16;
                        WaitFlag<HardEvent::MTE2_MTE1>(event);
                        if(l0Busy) WaitFlag<HardEvent::M_MTE1>(EVENT_ID3);
                        if(fixBusy) { WaitFlag<HardEvent::FIX_M>(EVENT_ID0);fixBusy=false; }
'''
bodyStart=copyEnd+len('                        WaitFlag<HardEvent::MTE2_MTE1>(EVENT_ID0);\n')
f=f[:loopstart]+prefetch+f[bodyStart:]
once('SetFlag<HardEvent::MTE1_MTE2>(EVENT_ID0);   // L1 reusable\n                        l1Busy = true;',
     'SetFlag<HardEvent::MTE1_MTE2>(event);   // Current bank reusable\n                        l1Busy[bank] = true;')
once('''                        l0Busy = true;
                    }
''','''                        l0Busy = true;
                        if(k0+2*bk<k) prefetch(k0+2*bk,bank);
                    }
''')
once('if (l1Busy) WaitFlag<HardEvent::MTE1_MTE2>(EVENT_ID0);',
     'if(l1Busy[0]) WaitFlag<HardEvent::MTE1_MTE2>(EVENT_ID0);\n            if(l1Busy[1]) WaitFlag<HardEvent::MTE1_MTE2>(EVENT_ID1);')
# AIV is exactly the parent's AIV; only AIC prefetch was modified.
parent=s[start:end]
assert f[f.index('    if ASCEND_IS_AIV'):]==parent[parent.index('    if ASCEND_IS_AIV'):]
s=s[:end]+f+s[end:]
needle='#define BMMS_LAUNCH(T, A, B) do { \\\n    if (useManual) BMMS_MANUAL(T, A, B); \\'
assert s.count(needle)==1
guard='''    const int32_t manualBk=std::min(k,(32768/std::max(tileM,tileN))/16*16);
    const bool useManualDB=useManual && m<=8192 && n<=8192 && tileM<=128 && k>manualBk;
'''
s=s.replace(needle,guard+'#define BMMS_LAUNCH(T, A, B) do { \\\n    if(useManualDB) bmms_manual_db<T,A,B><<<cores,nullptr,stream>>>(x1,x2,matrix,maxima,y,b,m,n,k,ns,tileM,tileN); \\\n    else if (useManual) BMMS_MANUAL(T, A, B); \\')
dst=r/'variants/s20a';dst.mkdir(exist_ok=False);(dst/'kernel.asc').write_bytes(s.encode())
(w/'s20a_changes.patch').write_text(''.join(difflib.unified_diff(base.decode().splitlines(True),s.splitlines(True),fromfile='s19i/kernel.asc',tofile='s20a/kernel.asc')),encoding='utf8')
sha=hashlib.sha256(s.encode()).hexdigest()
dst=r/'delivery_round20/s20a';dst.mkdir(parents=True,exist_ok=False);(dst/'kernel.asc').write_bytes(s.encode())
(dst/'candidate_status.json').write_text(json.dumps(dict(variant='s20a',source_sha256=sha,source_bytes=len(s.encode()),compiled=False,precision_validated=False,performance_validated=False,official_submitted=False),indent=2),encoding='utf8')
compile=(r/'work/solo19/compile_i.sh').read_text(encoding='utf8').replace('s19i','s20a').replace('compiler19_i','compiler20_a').replace(hashlib.sha256(base).hexdigest(),sha)
(w/'compile_a.sh').write_bytes(compile.encode())
print(json.dumps(dict(source_sha256=sha,source_bytes=len(s.encode()),budget=budget)))
