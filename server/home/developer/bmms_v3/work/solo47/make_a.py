from pathlib import Path
import json,hashlib,difflib,zipfile
r=Path('.');w=r/'work/solo47';base=(r/'variants/s46a/kernel.asc').read_text(encoding='utf-8')
assert hashlib.sha256(base.encode()).hexdigest()=='edd7b57ca02c049b77017a21c3cfcdaa113f22e10739ebe133a6d1df3a069262'
# Written before source generation: actual 2201 effective limits from platform probe.
ledger=dict(UB=0,L1=2048,L0A=1024,L0B=1024,L0C=1024,workspace=0,limits=dict(UB=196352,L1=524032,L0A=65536,L0B=65536,L0C=131072),gate='M=N=1,K=32,1<=B<=availableAIC,input addresses aligned32B',layout='GM contiguous 64B -> two 32B NZ rows at L1 offsets0,512; only valid C(0,0) copied',math='one FP32-accumulating Mmad per real input pair; unused padding cannot contribute to C(0,0)',difference_from39a='GM to L1 ordinary strided DataCopy replaces Nd2Nz; no implicit padding/format conversion',contract='one Cube kernel per invocation, current real inputs, all output from NPU')
(w/'resource_a.json').write_text(json.dumps(ledger,indent=2)+'\n',encoding='utf-8')
kernel='''template<class T>
__global__ __aicore__ __cube__ void bmms_dot_packed32(GM_ADDR a, GM_ADDR b, GM_ADDR y)
{
    const int batch=GetBlockIdx();
    GlobalTensor<T> ag,bg; GlobalTensor<float> yg;
    ag.SetGlobalBuffer((__gm__ T*)a); bg.SetGlobalBuffer((__gm__ T*)b);
    yg.SetGlobalBuffer((__gm__ float*)y);
    LocalTensor<T> la(TPosition::A1,0,16*32),lb(TPosition::B1,1024,16*32);
    LocalTensor<T> aa(TPosition::A2,0,16*32),bb(TPosition::B2,0,16*32);
    LocalTensor<float> cc(TPosition::CO1,0,16*16);
    // Each vector is the valid row of two NZ fractals. Every 32B comes from this call's input.
    DataCopyParams cp{2,1,0,15};
    DataCopy(la,ag[batch*32],cp); DataCopy(lb,bg[batch*32],cp);
    SetFlag<HardEvent::MTE2_MTE1>(EVENT_ID0); WaitFlag<HardEvent::MTE2_MTE1>(EVENT_ID0);
    LoadData2dParams ld{0,2,1,0,0,false,0};
    LoadData(aa,la,ld); LoadData(bb,lb,ld);
    SetFlag<HardEvent::MTE1_M>(EVENT_ID0); WaitFlag<HardEvent::MTE1_M>(EVENT_ID0);
    MmadParams mm{16,16,32,0,false,true}; Mmad(cc,aa,bb,mm);
    SetFlag<HardEvent::M_FIX>(EVENT_ID0); WaitFlag<HardEvent::M_FIX>(EVENT_ID0);
    FixpipeParamsV220 fp; fp.mSize=1; fp.nSize=1; fp.srcStride=16; fp.dstStride=1;
    Fixpipe(yg[batch],cc,fp);
    PipeBarrier<PIPE_ALL>();
}

'''
anchor='template<class T, int KK = 0, bool ONCE = false>'
assert base.count(anchor)==1
s=base.replace(anchor,kernel+anchor)
anchor='    if (m == 1 && n == 1) {';assert s.count(anchor)==1
s=s.replace(anchor,'''    if (m == 1 && n == 1 && k == 32 && b >= 1 && b <= availableCoreNum &&
        ((reinterpret_cast<uintptr_t>(x1) | reinterpret_cast<uintptr_t>(x2)) & 31) == 0) {
        if(info_x1.tensors[0].dtype==2) bmms_dot_packed32<bfloat16_t><<<b,nullptr,stream>>>(x1,x2,y);
        else bmms_dot_packed32<half><<<b,nullptr,stream>>>(x1,x2,y);
        return;
    }
'''+anchor)
v=r/'variants/s47a';v.mkdir(exist_ok=False);(v/'kernel.asc').write_text(s,encoding='utf-8',newline='\n')
sha=hashlib.sha256(s.encode()).hexdigest()
with zipfile.ZipFile(v/'s47a_kernel.zip','x',zipfile.ZIP_DEFLATED) as f:f.writestr('kernel.asc',s)
(w/'source_a.json').write_text(json.dumps(dict(variant='s47a',sha256=sha,baseline='s46a'),indent=2)+'\n')
(w/'diff_a.patch').write_text(''.join(difflib.unified_diff(base.splitlines(True),s.splitlines(True),fromfile='s46a',tofile='s47a')),encoding='utf-8',newline='\n')
guard=w/'guard';guard.mkdir(exist_ok=False)
(guard/'guard.asc').write_text((r/'work/solo39/guard/guard.asc').read_text(encoding='utf-8').replace('variants/s39a','variants/s47a'),encoding='utf-8',newline='\n')
(guard/'CMakeLists.txt').write_text((r/'work/solo39/guard/CMakeLists.txt').read_text(),newline='\n')
screen=(r/'work/solo39/screen_a.py').read_text().replace('s39a','s47a').replace('s33a','s46a').replace('39_','47_').replace('PRECISION39_A','PRECISION47_A').replace('SCREEN39_A','SCREEN47_A').replace('quick47_a','quick47_a').replace('work/solo39','work/solo47')
mark="for dtype in (1,2):"
screen=screen.replace(mark,"subprocess.run([str(r/'work/solo47/guard/build/guard'),str(manifest)],cwd=r,check=True)\n"+mark)
(w/'screen_a.py').write_text(screen,newline='\n')
(w/'shapes.txt').write_text('1 1 1 32\n2 1 1 32\n4 1 1 32\n8 1 1 32\n16 1 1 32\n20 1 1 32\n',newline='\n')
final=(r/'work/solo46/final_a.py').read_text().replace('s46a','s47a').replace("v,'s45c'","v,'s46a'").replace('edd7b57ca02c049b77017a21c3cfcdaa113f22e10739ebe133a6d1df3a069262',sha).replace('46_', '47_').replace('46_A','47_A')
(w/'final_a.py').write_text(final,newline='\n')
(w/'start_a.sh').write_text(f'''set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
bash work/solo32/compile_screen.sh s47a {sha}
cmake -S work/solo47/guard -B work/solo47/guard/build
cmake --build work/solo47/guard/build --target guard -j1 >solo17_data/compile47_guard.log 2>&1
python3 work/solo47/screen_a.py {sha}
python3 work/solo47/final_a.py
''',newline='\n')
print(sha)
