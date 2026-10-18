from pathlib import Path
import difflib,hashlib,json
r=Path(__file__).resolve().parents[2];w=r/'work/solo23'
old=(r/'variants/s23l/kernel.asc').read_bytes()
assert hashlib.sha256(old).hexdigest()==json.loads((w/'source_l.json').read_text())['sha256']
budget=dict(variant='s23o',parent='s23l',capacity_calculated_before_edit=True,
    scope='M=N8,K32/64,B<=min(20,availableCube),aligned32B,TA or not TB; NT stays parentD',
    UB_bytes=2*64*16*2+16*16*4+64,L1_max=4096,L0A_max=2048,L0B_max=2048,L0C_bytes=1024,
    GM_scratch_max=20*(1024+2*64*16*2),host_kernel_workspace_same_source=True,
    change='Vector copies each real short row8 to row16 with zero padding, writes current input to GM, Cube reads wider aligned rows; one mixed kernel with crosscore flags7/8',
    precision='FP32 Mmad and valid8-column max/8-row sum; no CPU output, no cached input/output')
assert budget['UB_bytes']==5184 and budget['GM_scratch_max']==102400
(w/'resource_s23o_before_edit.json').write_bytes((json.dumps(budget,indent=2)+'\n').encode())
s=old.decode().replace('bmms_tiny_cube','bmms_tiny_packed_cube')
s=s.replace('    constexpr int MP=16,NP=16;\n    const int core=GetBlockIdx();\n    GlobalTensor<float> sg;sg.SetGlobalBuffer((__gm__ float*)scratch);', '''    constexpr int MP=16,NP=16,PACK=K*16,PACKBYTES=PACK*2;
    constexpr int STEP=MP*NP*4+2*PACKBYTES;
    const int core=GetBlockIdx();
    GM_ADDR cs=scratch+core*STEP;
    GlobalTensor<float> sg;sg.SetGlobalBuffer((__gm__ float*)cs);
    GlobalTensor<T> pag,pbg;pag.SetGlobalBuffer((__gm__ T*)(cs+MP*NP*4));
    pbg.SetGlobalBuffer((__gm__ T*)(cs+MP*NP*4+PACKBYTES));
    if ASCEND_IS_AIV {
        LocalTensor<T> ax(TPosition::VECIN,0,PACK),bx(TPosition::VECIN,PACKBYTES,PACK);
        GlobalTensor<T> ag,bg;ag.SetGlobalBuffer((__gm__ T*)a);bg.SetGlobalBuffer((__gm__ T*)b);
        DataCopyExtParams cp{K,16,0,0,0};
        DataCopyPadExtParams<T> pad{true,0,8,(T)0};
        if constexpr(TA)DataCopyPad(ax,ag[core*8*K],cp,pad);
        if constexpr(!TB)DataCopyPad(bx,bg[core*8*K],cp,pad);
        SetFlag<HardEvent::MTE2_MTE3>(EVENT_ID0);WaitFlag<HardEvent::MTE2_MTE3>(EVENT_ID0);
        if constexpr(TA)DataCopy(pag,ax,PACK);
        if constexpr(!TB)DataCopy(pbg,bx,PACK);
        CrossCoreSetFlag<2,PIPE_MTE3>(7);
    }''',1)
needle='''        Nd2NzParams pa{1,TA?K:8,TA?8:K,0,TA?8:K,TA?K:MP,1,0};
        Nd2NzParams pb{1,TB?8:K,TB?K:8,0,TB?K:8,TB?NP:K,1,0};
        DataCopy(la,ag[core*8*K],pa);DataCopy(lb,bg[core*8*K],pb);'''
assert s.count(needle)==1
s=s.replace(needle,'''        CrossCoreWaitFlag(7);
        Nd2NzParams pa{1,TA?K:8,TA?MP:K,0,TA?MP:K,TA?K:MP,1,0};
        Nd2NzParams pb{1,TB?8:K,TB?K:NP,0,TB?K:NP,TB?NP:K,1,0};
        if constexpr(TA)DataCopy(la,pag,pa);else DataCopy(la,ag[core*8*K],pa);
        if constexpr(!TB)DataCopy(lb,pbg,pb);else DataCopy(lb,bg[core*8*K],pb);''',1)
s=s.replace('Fixpipe(sg[core*MP*NP],cc,fp);CrossCoreSetFlag<2,PIPE_FIX>(8);','Fixpipe(sg,cc,fp);CrossCoreSetFlag<2,PIPE_FIX>(8);',1)
s=s.replace('LocalTensor<float> vx(TPosition::VECIN,0,MP*NP);','LocalTensor<float> vx(TPosition::VECIN,2*PACKBYTES,MP*NP);',1)
s=s.replace('LocalTensor<float> rm(TPosition::VECCALC,MP*NP*4,8);','LocalTensor<float> rm(TPosition::VECCALC,2*PACKBYTES+MP*NP*4,8);',1)
s=s.replace('LocalTensor<float> out(TPosition::VECOUT,MP*NP*4+32,8);','LocalTensor<float> out(TPosition::VECOUT,2*PACKBYTES+MP*NP*4+32,8);',1)
s=s.replace('CrossCoreWaitFlag(8);DataCopy(vx,sg[core*MP*NP],MP*NP);','CrossCoreWaitFlag(8);DataCopy(vx,sg,MP*NP);',1)
needle='    if (m == 8 && n == 8 && (k == 32 || k == 64) && b <= std::min<int64_t>(20,availableCoreNum) &&'
assert s.count(needle)==1
s=s.replace(needle,'    if ((transposeX1 || !transposeX2) && m == 8 && n == 8 && (k == 32 || k == 64) && b <= std::min<int64_t>(20,availableCoreNum) &&')
needle='const size_t bytes=(size_t)b*16*16*4;';assert s.count(needle)==1
s=s.replace(needle,'const size_t bytes=(size_t)b*(16*16*4+2*k*16*2);')
dst=r/'variants/s23o';dst.mkdir(exist_ok=False);(dst/'kernel.asc').write_bytes(s.encode())
sha=hashlib.sha256(s.encode()).hexdigest();(w/'source_o.json').write_bytes((json.dumps(dict(variant='s23o',sha256=sha,bytes=len(s.encode())),indent=2)+'\n').encode())
(w/'s23o_changes.patch').write_bytes(''.join(difflib.unified_diff(old.decode().splitlines(True),s.splitlines(True),fromfile='s23l/kernel.asc',tofile='s23o/kernel.asc')).encode())
oldsha=json.loads((w/'source_n.json').read_text())['sha256']
for name in ['compile_n.sh','run_n_pilot.py']:
    x=(w/name).read_text().replace(oldsha,sha).replace('s23n','s23o').replace('23n','23o').replace('23_n','23_o').replace('pilot23_base_parent_n','pilot23_base_parent_o')
    if name=='run_n_pilot.py':
        specs=[f'1_8_8_{k}_{dt}_{ta}_{tb}' for k in [32,64] for dt in [1,2] for ta,tb in [(0,0),(1,0),(1,1)]]+['8_8_8_32_1_1_1','20_8_8_64_2_1_1','1_8_8_32_1_0_1','1_8_8_64_2_0_1']
        begin=x.index('specs=');end=x.index('\nfor label,variants',begin)
        x=x[:begin]+'specs='+repr(specs)+x[end:];x=x.replace('pilots72','pilots96')
    (w/name.replace('_n','_o')).write_bytes(x.encode())
print(json.dumps(dict(variant='s23o',sha256=sha,resources=budget)))
