from pathlib import Path
import hashlib,json,difflib
r=Path(__file__).resolve().parents[2];w=r/'work/solo20'
base=(r/'variants/s20b/kernel.asc').read_bytes();s=base.decode()
oldsha=hashlib.sha256(base).hexdigest()
assert oldsha=='d0c2321563e205a69262209ed75fc54d8037f59a39e858acc17f8e675fdb8160'
budget=json.loads((w/'resource_s20b_before_edit.json').read_text(encoding='utf8'))
assert budget['capacity_calculated_before_edit'] and budget['maxima']['UB_bytes']==164864
budget.update(variant='s20c',parent='s20b',change='Replace (k0/bk)&1 with a chunk counter&1. No tensor/buffer/tiling/workspace/arithmetic-order changes. For positive bk and loop k0+=bk, bank IDs are identical.',
    capacity_calculated_before_edit=True)
(w/'resource_s20c_before_edit.json').write_text(json.dumps(budget,indent=2),encoding='utf8')
old='''                    for (int32_t k0 = 0; k0 < k; k0 += bk) {
                        const int32_t bank=(k0/bk)&1;'''
new='''                    for (int32_t k0=0,chunk=0; k0<k; k0+=bk,++chunk) {
                        const int32_t bank=chunk&1;'''
assert s.count(old)==1;s=s.replace(old,new)
dst=r/'variants/s20c';dst.mkdir(exist_ok=False);(dst/'kernel.asc').write_bytes(s.encode())
sha=hashlib.sha256(s.encode()).hexdigest()
(w/'s20c_changes.patch').write_text(''.join(difflib.unified_diff(base.decode().splitlines(True),s.splitlines(True),fromfile='s20b/kernel.asc',tofile='s20c/kernel.asc')),encoding='utf8')
dst=r/'delivery_round20/s20c';dst.mkdir(parents=True,exist_ok=False);(dst/'kernel.asc').write_bytes(s.encode())
(dst/'candidate_status.json').write_text(json.dumps(dict(variant='s20c',source_sha256=sha,source_bytes=len(s.encode()),compiled=False,precision_validated=False,performance_validated=False,official_submitted=False),indent=2),encoding='utf8')
for old,new in [('run_b_final.py','run_c_final.py'),('verify20_b_final.py','verify20_c_final.py')]:
    text=(w/old).read_text(encoding='utf8')
    for a,b in [('s20b','s20c'),('diagnostic_20b','diagnostic_20c'),('hangs20_b','hangs20_c'),('remote_round20_b_final','remote_round20_c_final'),(oldsha,sha)]:text=text.replace(a,b)
    (w/new).write_bytes(text.encode())
text=(w/'launch_b.sh').read_text(encoding='utf8')
for a,b in [('s20b','s20c'),('diagnostic_20b','diagnostic_20c'),('compiler20_b','compiler20_c'),(oldsha,sha)]:text=text.replace(a,b)
text=text.replace(' && python3 work/solo20/run_b_final.py >solo17_data/run20_b_final.log 2>&1','').replace('COMPILE AND FINAL PID','COMPILE ONLY PID')
(w/'compile_c.sh').write_bytes(text.encode())
print(json.dumps(dict(variant='s20c',source_sha256=sha,source_bytes=len(s.encode()),capacity=budget['maxima'])))
