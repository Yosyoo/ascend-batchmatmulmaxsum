#include <cstdint>
#include <cstdio>
#include "acl/acl.h"
int main() {
    int64_t count=0;
    if (aclInit(nullptr) != ACL_SUCCESS || aclrtSetDevice(0) != ACL_SUCCESS) return 1;
    auto rc=aclrtGetDeviceInfo(0,ACL_DEV_ATTR_CUBE_CORE_NUM,&count);
    printf("logical_device=0 cube_cores=%ld rc=%d\n",count,rc);
    aclFinalize();
    return rc != ACL_SUCCESS;
}
