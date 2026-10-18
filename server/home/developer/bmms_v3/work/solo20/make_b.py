from pathlib import Path
import hashlib,json,difflib
r=Path(__file__).resolve().parents[2];w=r/'work/solo20'
base=(r/'variants/s20a/kernel.asc').read_bytes();s=base.decode()
assert hashlib.sha256(base).hexdigest()=='b4141a3e0bd792a6f953454924af68bcb4e49e7b195c4f74892b98de8d162f6c'
budget=json.loads((w/'resource_s20a_before_edit.json').read_text(encoding='utf8'))
assert budget['capacity_calculated_before_edit'] and budget['maxima']['L1_bytes']==262144
budget.update(variant='s20b',parent='s20a_compile_failed',change='Same L1 ping-pong algorithm; replace unsupported implicit-host lambda with explicitly aicore always_inline helper. No buffer/tile/precision changes.')
(w/'resource_s20b_before_edit.json').write_text(json.dumps(budget,indent=2),encoding='utf8')
begin=s.index('                    const auto prefetch=[&](int32_t k0,int32_t bank) {')
end=s.index('                    };',begin)
body=s[begin+len('                    const auto prefetch=[&](int32_t k0,int32_t bank) {\n'):end]
body=body.replace('l1Busy[bank]','busy')
helper='''template<class T,bool TA,bool TB>
__aicore__ inline __attribute__((always_inline)) void bmms_l1_prefetch(
    GlobalTensor<T>& ag,GlobalTensor<T>& bg,int64_t aBase,int64_t bBase,
    int32_t m,int32_t n,int32_t k,int32_t cm,int32_t cn,int32_t cm16,int32_t cn16,
    int32_t mp,int32_t np,int32_t bk,int32_t bankBytes,int32_t k0,int32_t bank,bool& busy)
{
'''+''.join(line[20:]+'\n' if line.startswith(' '*20) else line+'\n' for line in body.splitlines())+'}\n\n'
s=s[:begin]+s[end+len('                    };\n'):]
common='ag,bg,aBase,bBase,m,n,k,cm,cn,cm16,cn16,mp,np,bk,bankBytes,'
for old,new in [('prefetch(0,0);',f'bmms_l1_prefetch<T,TA,TB>({common}0,0,l1Busy[0]);'),
                ('prefetch(bk,1);',f'bmms_l1_prefetch<T,TA,TB>({common}bk,1,l1Busy[1]);'),
                ('prefetch(k0+2*bk,bank);',f'bmms_l1_prefetch<T,TA,TB>({common}k0+2*bk,bank,l1Busy[bank]);')]:
    assert s.count(old)==1;s=s.replace(old,new)
at=s.index('template<class T, bool TA, bool TB, int TM = 0, int TN = 0, int TK = 0>\n__global__ __aicore__ __mix__(1, 1) void bmms_manual_db(')
s=s[:at]+helper+s[at:]
dst=r/'variants/s20b';dst.mkdir(exist_ok=False);(dst/'kernel.asc').write_bytes(s.encode())
sha=hashlib.sha256(s.encode()).hexdigest()
(w/'s20b_changes.patch').write_text(''.join(difflib.unified_diff(base.decode().splitlines(True),s.splitlines(True),fromfile='s20a/kernel.asc',tofile='s20b/kernel.asc')),encoding='utf8')
dst=r/'delivery_round20/s20b';dst.mkdir(parents=True,exist_ok=False);(dst/'kernel.asc').write_bytes(s.encode())
(dst/'candidate_status.json').write_text(json.dumps(dict(variant='s20b',source_sha256=sha,source_bytes=len(s.encode()),compiled=False,precision_validated=False,performance_validated=False,official_submitted=False),indent=2),encoding='utf8')
for old,new in [('launch_a.sh','launch_b.sh'),('run_a_final.py','run_b_final.py'),('verify20_a_final.py','verify20_b_final.py')]:
    text=(w/old).read_text(encoding='utf8')
    for a,b in [('s20a','s20b'),('diagnostic_20a','diagnostic_20b'),('hangs20_a','hangs20_b'),('compiler20_a','compiler20_b'),('run_a_final','run_b_final'),('run20_a_final','run20_b_final'),('remote_round20_a_final','remote_round20_b_final'),(hashlib.sha256(base).hexdigest(),sha)]:
        text=text.replace(a,b)
    (w/new).write_bytes(text.encode())
print(json.dumps(dict(variant='s20b',source_sha256=sha,source_bytes=len(s.encode()),capacity=budget['maxima'])))
