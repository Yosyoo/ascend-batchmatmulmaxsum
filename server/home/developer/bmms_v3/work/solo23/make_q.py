from pathlib import Path
import hashlib,json,difflib
r=Path(__file__).resolve().parents[2];w=r/'work/solo23';old=(r/'variants/s23p/kernel.asc').read_bytes()
parent=json.loads((w/'source_p.json').read_text())['sha256'];assert hashlib.sha256(old).hexdigest()==parent
budget=json.loads((w/'resource_s23p_before_edit.json').read_text())
budget.update(variant='s23q',parent='s23p',capacity_calculated_before_edit=True,
    L1_bytes=4*(112+128)*256*2,L0A_bytes=112*256*2,L0B_bytes=128*256*2,
    change='Only pipeline geometry changes:BK256,4L1banks,1L0bank; same halfKFP32Fixatomic and paired-row final reduction',
    reason='Measured M512squareK8192 AICMTE2=24.2175us >scalar19.8715us >MAC17.24us. Increase ND2NZ row transfer length256->512B to test transfer efficiency; CPU must never calculate output')
assert budget['L1_bytes']==491520 and budget['L0A_bytes']==57344 and budget['L0B_bytes']==65536
(w/'resource_s23q_before_edit.json').write_bytes((json.dumps(budget,indent=2)+'\n').encode())
s=old.decode();begin=s.index('template<class T>\n__aicore__ inline __attribute__((always_inline)) void bmms_ring_prefetch')
end=s.index('template<class T, bool TA, bool TB, int M, int N, int K>\n__global__ __aicore__ __mix__(1, 1) void bmms_full')
code=s[begin:end].replace('BK=128','BK=256').replace('BANKS=8','BANKS=4')
code=code.replace('bool l1Busy[BANKS]={false,false,false,false,false,false,false,false};','bool l1Busy[BANKS]={false,false,false,false};')
code=code.replace('bool l0Busy[2]={false,false}','bool l0Busy[1]={false}').replace('slot=i&1','slot=0').replace('slot<2','slot<1')
assert 'BK=128' not in code and 'slot=i&1' not in code and code.count('BK=256')==2
s=s[:begin]+code+s[end:];dst=r/'variants/s23q';dst.mkdir(exist_ok=False);(dst/'kernel.asc').write_bytes(s.encode())
sha=hashlib.sha256(s.encode()).hexdigest();(w/'source_q.json').write_bytes((json.dumps(dict(variant='s23q',sha256=sha,bytes=len(s.encode())),indent=2)+'\n').encode())
(w/'s23q_changes.patch').write_bytes(''.join(difflib.unified_diff(old.decode().splitlines(True),s.splitlines(True),fromfile='s23p/kernel.asc',tofile='s23q/kernel.asc')).encode())
for name in ['compile_p.sh','run_p_pilot.py']:
    x=(w/name).read_text().replace(parent,sha).replace('s23p','s23q').replace('23p','23q').replace('23_p','23_q').replace('pilot23_base_parent_p','pilot23_base_parent_q')
    (w/name.replace('_p','_q',1)).write_bytes(x.encode())
print(json.dumps(dict(variant='s23q',sha256=sha,budget=budget)))
