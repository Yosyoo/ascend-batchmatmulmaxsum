#include <cstdio>
#include <cstdlib>
#include "tiling/matmul/matmul_tiling.h"
int main(int argc, char** argv) {
    if (argc != 10) return 2;
    int m=atoi(argv[1]), n=atoi(argv[2]), k=atoi(argv[3]), tm=atoi(argv[4]), tn=atoi(argv[5]);
    int bm=atoi(argv[6]), bn=atoi(argv[7]), ta=atoi(argv[8]), tb=atoi(argv[9]);
    matmul_tiling::PlatformInfo p;
    p.socVersion=platform_ascendc::SocVersion::ASCEND910B;
    p.l1Size=512*1024; p.l0ASize=p.l0BSize=64*1024; p.l0CSize=128*1024; p.ubSize=192*1024;
    matmul_tiling::MatmulApiTiling a(p);
    using namespace matmul_tiling;
    a.SetAType(TPosition::GM,CubeFormat::ND,DataType::DT_BF16,ta);
    a.SetBType(TPosition::GM,CubeFormat::ND,DataType::DT_BF16,tb);
    a.SetCType(TPosition::GM,CubeFormat::ND,DataType::DT_FLOAT);
    a.SetBias(false); a.SetShape(tm,tn,k); a.SetOrgShape(m,n,k);
    a.SetFixSplit(bm,bn,-1); a.SetBufferSpace(p.l1Size,p.l0CSize,0);
    AscendC::tiling::TCubeTiling t;
    int rc=a.GetTiling(t);
    printf("rc=%d macro=%d,%d base=%d,%d,%d depth=%d,%d stepMN=%d,%d stepK=%d,%d DB=%d,%d,%d L1=%d L0C=%d iterate=%d\n",
        rc,tm,tn,t.baseM,t.baseN,t.baseK,t.depthA1,t.depthB1,t.stepM,t.stepN,t.stepKa,t.stepKb,t.dbL0A,t.dbL0B,t.dbL0C,t.shareL1Size,t.shareL0CSize,t.iterateOrder);
    return rc != 0;
}
