from pathlib import Path
import hashlib, json, difflib, zipfile

r = Path(__file__).resolve().parents[2]
w = Path(__file__).parent
assert (w / 'resource_a.json').is_file(), 'Save resource/event budget before constructing source'
base = (r / 'variants/s41c/kernel.asc').read_text(encoding='utf-8')
assert hashlib.sha256(base.encode()).hexdigest() == '5fc87dcd3f6e8eff0c036274369af504b2951ae2a1c186a88d107e5e398b3494'

start = base.index('template<class T, bool TA, bool TB, int BM, int BN, int BK>\n__global__ __aicore__ __mix__(1, 1) void bmms_pair_static')
end = base.index('\ntemplate<class T, bool TA, bool TB, bool PAIR=false, bool FULLA=false>', start)
parent_kernel = base[start:end]
aiv = parent_kernel[parent_kernel.index('    if ASCEND_IS_AIV {'):]

added = r'''
// Fixed K256: keep four individually packed BK64 A2 slices across all N tiles.
// Full-tile guards are host-side. The two independent half-K products and FP32
// GM atomic merge are identical to the original static pair arithmetic.
template<class T, bool TB>
__aicore__ inline void bmms_pair256_copy_b(const LocalTensor<T>& dst,
    const GlobalTensor<T>& src, int batch, int n, int ni)
{
    constexpr int TN=256, K=256;
    Nd2NzParams p{1, (uint16_t)(TB?TN:K), (uint16_t)(TB?K:TN), 0,
        (uint16_t)(TB?K:n), (uint16_t)(TB?TN:K), 1, 0};
    DataCopy(dst, src[(int64_t)batch*n*K+(TB?(int64_t)ni*K:ni)], p);
}

template<class T, bool TB>
__aicore__ inline void bmms_pair256_load_b(const LocalTensor<T>& dst,
    const LocalTensor<T>& src, int chunk)
{
    constexpr int TN=256, K=256, BK=64;
    if constexpr(TB) {
        // NZ is [K/16,N,16]; a BK64 slice is contiguous.
        LoadData2dParams p{0,TN*BK/256,1,0,0,false,0};
        LoadData(dst, src[chunk*BK*TN], p);
    } else {
        // One rectangle, matching the existing validated public Load3D path.
        LoadData3DParamsV2<T> p;
        p.l1H=1; p.l1W=K; p.channelSize=TN;
        p.kExtension=TN; p.mExtension=BK;
        p.kStartPt=0; p.mStartPt=chunk*BK;
        LoadData(dst,src,p);
    }
}

template<class T, bool TA, bool TB>
__global__ __aicore__ __mix__(1, 1) void bmms_pair_a2resident256(
    GM_ADDR a, GM_ADDR b, GM_ADDR scratch, GM_ADDR maxima, GM_ADDR y,
    int32_t batches, int32_t m, int32_t n, int32_t k, int32_t ns, TCubeTiling tiling)
{
    constexpr int TM=128, TN=256, K=256, BK=64;
    static_assert(TM*K*2==65536, "full A2 fits exactly");
    static_assert(2*TN*BK*2==65536, "B2 double buffer fits exactly");
    static_assert((TM*K+2*TN*K)*2<=512*1024, "L1 capacity");
    static_assert(TM*TN*4<=128*1024, "L0C capacity");
    const int32_t tileM=TM, tileN=TN, mt=m/TM, nt=n/TN;
    const int32_t core=GetBlockIdx();
    const int64_t coreOffset=(int64_t)core*2*TM*TN;
    TPipe pipe;
    if ASCEND_IS_AIC {
        // SDK Init uses ND traversal with unitFlag; match it before issuing Mmad.
        SetMMLayoutTransform(true);
        GlobalTensor<T> ag,bg; GlobalTensor<float> sg;
        ag.SetGlobalBuffer((__gm__ T*)a); bg.SetGlobalBuffer((__gm__ T*)b);
        sg.SetGlobalBuffer((__gm__ float*)scratch);
        LocalTensor<T> la(TPosition::A1,0,TM*K);
        LocalTensor<T> lb(TPosition::B1,TM*K*2,2*TN*K);
        LocalTensor<T> aa(TPosition::A2,0,TM*K);
        LocalTensor<T> bb(TPosition::B2,0,2*TN*BK);
        LocalTensor<float> cc(TPosition::CO1,0,TM*TN);
        bool aL1Busy=false;
        bool bL1Busy[2]={false,false}, bL0Busy[2]={false,false};
        int32_t step=0;
        for(int32_t task=core;task<batches*mt*ns;task+=GetBlockNum()) {
            const int batch=task/(mt*ns), part=task%ns, mi=(task/ns)%mt*TM;
            const int begin=nt*part/ns, end=nt*(part+1)/ns;
            // M->MTE1 protects every resident A2 slice before the next row replaces it.
            for(int bank=0;bank<2;++bank) {
                if(bL0Busy[bank]) {
                    WaitFlag<HardEvent::M_MTE1>(bank?EVENT_ID1:EVENT_ID0);
                    bL0Busy[bank]=false;
                }
            }
            if(aL1Busy) WaitFlag<HardEvent::MTE1_MTE2>(EVENT_ID0);
            Nd2NzParams ap{1,(uint16_t)(TA?K:TM),(uint16_t)(TA?TM:K),0,
                (uint16_t)(TA?m:K),(uint16_t)(TA?K:TM),1,0};
            DataCopy(la,ag[(int64_t)batch*m*K+(TA?mi:(int64_t)mi*K)],ap);
            SetFlag<HardEvent::MTE2_MTE1>(EVENT_ID0);
            WaitFlag<HardEvent::MTE2_MTE1>(EVENT_ID0);
            #pragma unroll
            for(int r=0;r<K/BK;++r) {
                LoadData3DParamsV2<T> p;
                p.l1H=1; p.l1W=TA?K:TM; p.channelSize=TA?TM:K;
                p.kExtension=TA?TM:BK; p.mExtension=TA?BK:TM;
                p.kStartPt=TA?0:r*BK; p.mStartPt=TA?r*BK:0;
                p.enTranspose=TA;
                LoadData(aa[r*TM*BK],la,p);
            }
            SetFlag<HardEvent::MTE1_MTE2>(EVENT_ID0); aL1Busy=true;
            SetFlag<HardEvent::MTE1_M>(EVENT_ID2);
            WaitFlag<HardEvent::MTE1_M>(EVENT_ID2);

            // First full B tile. Each following tile is prefetched into the other L1 bank.
            if(bL1Busy[0]) {
                WaitFlag<HardEvent::MTE1_MTE2>(EVENT_ID1); bL1Busy[0]=false;
            }
            bmms_pair256_copy_b<T,TB>(lb,bg,batch,n,begin*TN);
            SetFlag<HardEvent::MTE2_MTE1>(EVENT_ID1);
            for(int t=begin;t<end;++t) {
                const int bank=(t-begin)&1, slot=step&1;
                WaitFlag<HardEvent::MTE2_MTE1>(bank?EVENT_ID2:EVENT_ID1);
                if(t+1<end) {
                    const int next=bank^1;
                    if(bL1Busy[next]) {
                        WaitFlag<HardEvent::MTE1_MTE2>(next?EVENT_ID2:EVENT_ID1);
                        bL1Busy[next]=false;
                    }
                    bmms_pair256_copy_b<T,TB>(lb[next*TN*K],bg,batch,n,(t+1)*TN);
                    SetFlag<HardEvent::MTE2_MTE1>(next?EVENT_ID2:EVENT_ID1);
                }
                if(step>=2) CrossCoreWaitFlag(slot==0?10:15);
                // Prime B2 bank 0; thereafter load the next chunk while the previous
                // bank's Mmad runs. A2 slices stay resident throughout this row task.
                if(bL0Busy[0]) {
                    WaitFlag<HardEvent::M_MTE1>(EVENT_ID0); bL0Busy[0]=false;
                }
                bmms_pair256_load_b<T,TB>(bb,lb[bank*TN*K],0);
                SetFlag<HardEvent::MTE1_M>(EVENT_ID0);
                #pragma unroll
                for(int r=0;r<K/BK;++r) {
                    const int l0bank=r&1;
                    if(r+1<K/BK) {
                        const int next=l0bank^1;
                        if(bL0Busy[next]) {
                            WaitFlag<HardEvent::M_MTE1>(next?EVENT_ID1:EVENT_ID0);
                            bL0Busy[next]=false;
                        }
                        bmms_pair256_load_b<T,TB>(bb[next*TN*BK],lb[bank*TN*K],r+1);
                        SetFlag<HardEvent::MTE1_M>(next?EVENT_ID1:EVENT_ID0);
                    }
                    WaitFlag<HardEvent::MTE1_M>(l0bank?EVENT_ID1:EVENT_ID0);
                    MmadParams p;
                    p.m=TM; p.n=TN; p.k=BK; p.isBias=false;
                    p.cmatrixSource=false; p.cmatrixInitVal=(r%2==0);
                    // Same SDK sequence: check L0C on first BK64, set on half completion.
                    p.unitFlag=(r%2==0)?2:3;
                    Mmad(cc,aa[r*TM*BK],bb[l0bank*TN*BK],p);
                    SetFlag<HardEvent::M_MTE1>(l0bank?EVENT_ID1:EVENT_ID0);
                    bL0Busy[l0bank]=true;
                    if(r%2==1) {
                        FixpipeParamsV220 fp;
                        fp.mSize=TM; fp.nSize=TN; fp.srcStride=TM; fp.dstStride=TN;
                        fp.unitFlag=3;
                        if(r==3) SetAtomicAdd<float>(); else DisableDmaAtomic();
                        Fixpipe(sg[coreOffset+(int64_t)slot*TM*TN],cc,fp);
                        DisableDmaAtomic();
                    }
                }
                SetFlag<HardEvent::MTE1_MTE2>(bank?EVENT_ID2:EVENT_ID1);
                bL1Busy[bank]=true;
                CrossCoreSetFlag<2,PIPE_FIX>(slot==0?8:9);
                ++step;
            }
        }
        if(aL1Busy) WaitFlag<HardEvent::MTE1_MTE2>(EVENT_ID0);
        for(int bank=0;bank<2;++bank) {
            if(bL1Busy[bank]) WaitFlag<HardEvent::MTE1_MTE2>(bank?EVENT_ID2:EVENT_ID1);
            if(bL0Busy[bank]) WaitFlag<HardEvent::M_MTE1>(bank?EVENT_ID1:EVENT_ID0);
        }
        if(step>0) CrossCoreWaitFlag(10);
        if(step>1) CrossCoreWaitFlag(15);
        PipeBarrier<PIPE_ALL>();
        SetMMLayoutTransform(false);
    }
'''+aiv

source=base[:end]+added+base[end:]
marker='#define BMMS_LAUNCH(T, A, B) do { \\\n'
assert source.count(marker)==1
gate='''    const bool pairA2Resident256 = pairStaticKey == 1 && k == 256 && ns == 1 &&
        tileM == 128 && tileN == 256 && nt >= 4 && m <= 8192 && n <= 65535;
'''
source=source.replace(marker,gate+marker)
launch='    else if (pairStaticKey == 1) bmms_pair_static<T,A,B,128,256,64><<<cores,nullptr,stream>>>(x1,x2,matrix,maxima,y,b,m,n,k,ns,tiling); \\\n'
assert source.count(launch)==1
source=source.replace(launch,'    else if (pairA2Resident256) bmms_pair_a2resident256<T,A,B><<<cores,nullptr,stream>>>(x1,x2,matrix,maxima,y,b,m,n,k,ns,tiling); \\\n'+launch)
assert source.count(aiv)==base.count(aiv)+1, 'Candidate AIV must be byte-identical to parent'
v=r/'variants/s42a'
v.mkdir(exist_ok=True)
(v/'kernel.asc').write_text(source,encoding='utf-8',newline='\n')
with zipfile.ZipFile(v/'s42a_kernel.zip','w',zipfile.ZIP_DEFLATED) as z:
    z.writestr('kernel.asc',source)
sha=hashlib.sha256(source.encode()).hexdigest()
(w/'source_a.json').write_text(json.dumps(dict(variant='s42a',baseline='s41c',sha256=sha,
    bytes=len(source.encode()),status='source-only, not compiled or NPU tested',
    change='K256 A2 four-BK64 resident slices with B2 double buffer, original two-half FP32 merge',
    aiv_byte_identical=True),indent=2)+'\n')
(w/'diff_a.patch').write_text(''.join(difflib.unified_diff(base.splitlines(True),source.splitlines(True),
    fromfile='s41c/kernel.asc',tofile='s42a/kernel.asc')),encoding='utf-8')
print(json.dumps(dict(variant='s42a',sha256=sha,bytes=len(source.encode()))))
