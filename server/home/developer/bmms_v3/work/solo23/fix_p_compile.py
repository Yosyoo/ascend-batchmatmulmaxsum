from pathlib import Path
import hashlib,json,difflib
r=Path(__file__).resolve().parents[2];w=r/'work/solo23';p=r/'variants/s23p/kernel.asc'
old=p.read_bytes();original=json.loads((w/'source_p.json').read_text())
assert hashlib.sha256(old).hexdigest()==original['sha256']
(w/'kernel_p_compile1.asc').write_bytes(old);(w/'source_p_compile1.json').write_bytes((json.dumps(original,indent=2)+'\n').encode())
s=old.decode()
replacements={
 'Nd2NzParams pa{1,cm,kk,0,k,cm,1,0};':'Nd2NzParams pa{1,(uint16_t)cm,(uint16_t)kk,0,(uint16_t)k,(uint16_t)cm,1,0};',
 'Nd2NzParams pb{1,kk,TN,0,n,kk,1,0};':'Nd2NzParams pb{1,(uint16_t)kk,TN,0,(uint16_t)n,(uint16_t)kk,1,0};',
 'LoadData2dParams ap{0,kk/16,cm/16,0,0,false,0};':'LoadData2dParams ap{0,(uint8_t)(kk/16),(uint16_t)(cm/16),0,0,false,0};',
 'LoadData2dParams bp{0,TN/16,kk/16,0,0,true,0};':'LoadData2dParams bp{0,TN/16,(uint16_t)(kk/16),0,0,true,0};',
 'MmadParams mm{cm,TN,kk,0,false,i==0};':'MmadParams mm{(uint16_t)cm,TN,(uint16_t)kk,0,false,i==0};'}
for a,b in replacements.items():assert s.count(a)==1;s=s.replace(a,b)
p.write_bytes(s.encode());sha=hashlib.sha256(s.encode()).hexdigest()
(w/'source_p.json').write_bytes((json.dumps(dict(variant='s23p',sha256=sha,bytes=len(s.encode()),compile1_sha256=original['sha256']),indent=2)+'\n').encode())
for name in ['run_p_pilot.py','compile_p.sh']:
    a=(w/name).read_text();assert original['sha256'] in a;(w/name).write_bytes(a.replace(original['sha256'],sha).encode())
(w/'p_compile_fix.patch').write_bytes(''.join(difflib.unified_diff(old.decode().splitlines(True),s.splitlines(True))).encode())
(w/'ring_pair.asc').write_bytes(s[s.index('template<class T>\n__aicore__ inline __attribute__((always_inline)) void bmms_ring_prefetch'):s.index('template<class T, bool TA, bool TB, int M, int N, int K>\n__global__ __aicore__ __mix__(1, 1) void bmms_full')].encode())
retry=f'''set -eu
cd /home/developer/bmms_v3
source /opt/home/developer/Ascend/cann-9.0.0/set_env.sh >/dev/null 2>&1
if kill -0 466574 2>/dev/null; then exit 1; fi
test ! -d solo17_data/diagnostic_23p
test ! -f variants/s23p/build_compile1.log
test "$(sha256sum variants/s23p/kernel.asc | cut -d ' ' -f 1)" = {original['sha256']}
cp variants/s23p/kernel.asc variants/s23p/kernel_compile1.asc
cp variants/s23p/build.log variants/s23p/build_compile1.log
test "$(sha256sum variants/s23p/kernel_corrected.asc | cut -d ' ' -f 1)" = {sha}
cp variants/s23p/kernel_corrected.asc variants/s23p/kernel.asc
nohup bash -c 'cd /home/developer/bmms_v3; cmake --build variants/s23p/build -j2 >variants/s23p/build.log 2>&1' >solo17_data/compiler23_p_retry.log 2>&1 < /dev/null &
echo "P retry compiler $!"
'''
(w/'retry_p.sh').write_bytes(retry.encode());print(json.dumps(dict(sha256=sha,fixed='explicit integer narrowing conversions only, capacity/math unchanged')))
