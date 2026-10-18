#include <cstdio>
#include <algorithm>
#include "tiling/matrix/matmul_tiling.h"
int main(){
 matmul_tiling::PlatformInfo p; p.socVersion=platform_ascendc::SocVersion::ASCEND910B;
 p.l1Size=524288; p.l0CSize=131072; p.l0ASize=p.l0BSize=65536; p.ubSize=196608;
 for(int padded=0;padded<2;++padded){
 matmul_tiling::MatmulApiTiling api(p);
 api.SetAType(matmul_tiling::TPosition::GM,matmul_tiling::CubeFormat::ND,matmul_tiling::DataType::DT_FLOAT16,false);
 api.SetBType(matmul_tiling::TPosition::GM,matmul_tiling::CubeFormat::ND,matmul_tiling::DataType::DT_FLOAT16,false);
 api.SetCType(matmul_tiling::TPosition::GM,matmul_tiling::CubeFormat::ND,matmul_tiling::DataType::DT_FLOAT);
 api.SetBias(false); api.SetShape(padded?64:17,padded?128:19,72);api.SetOrgShape(17,19,72);
 api.SetFixSplit(64,128,-1); api.SetBufferSpace(524288,131072,0);
 AscendC::tiling::TCubeTiling t;
 auto ret=api.GetTiling(t); printf("padded=%d ret=%ld baseM=%d baseN=%d baseK=%d M=%d N=%d\n",padded,ret,t.baseM,t.baseN,t.baseK,t.M,t.N);
 }
}
