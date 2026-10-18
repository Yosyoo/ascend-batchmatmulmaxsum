from pathlib import Path
import json,hashlib,difflib
r=Path(__file__).resolve().parents[2];w=r/'work/solo21'
rows=[json.loads(x) for x in (w/'probe_b/results.jsonl').read_text().splitlines()];assert len(rows)==1920
limits={'L1_bytes':524288,'L0A_bytes':65536,'L0B_bytes':65536,'L0C_bytes':131072,'UB_bytes':184320}
for x in rows:assert all(x[k]<=v for k,v in limits.items())
budget=dict(variant='s21b',parent='s20f',capacity_calculated_before_edit=True,resource_probe_rows=len(rows),
    probe_sha256=hashlib.sha256((w/'probe_b/results.jsonl').read_bytes()).hexdigest(),
    maxima={k:max(x[k] for x in rows) for k in limits},limits=limits,
    scope='GM ND; K=2048..8192 multiple32; M=512..2048 multiple256; N=512..8192 multiple256; existing tile128x256; b*ceil(M/128)<availableCoreNum',
    change='tile128x256 to256x128 before UB guard, tiling, tasks, workspace and dispatch; preserves half-K arithmetic and ordered FP32 accumulation',
    inference='Larger M may reuse B more efficiently; official case shapes unknown. Tile64x256 (s21a) was measured slower and rejected.')
(w/'resource_s21b_before_edit.json').write_text(json.dumps(budget,indent=2)+'\n')
old=(r/'variants/s20f/kernel.asc').read_bytes();assert hashlib.sha256(old).hexdigest()=='198ee0bb6eca5a4503e734438da20f05a4ad962e5c7d53976b84552190b09f3c'
s=old.decode();anchor='    const bool useFullA = !packed && m>=512';assert s.count(anchor)==1
extra='''    // Balance paired long-K operand reuse with more N tasks, retaining the same two-half arithmetic.
    if (!packed && k>=2048 && k<=8192 && k%32==0 && m>=512 && m<=2048 && m%256==0 &&
        n>=512 && n<=8192 && n%256==0 && tileM==128 && tileN==256 &&
        (int64_t)b*((m+127)/128)<availableCoreNum) { tileM=256;tileN=128; }
'''
s=s.replace(anchor,extra+anchor);dst=r/'variants/s21b';dst.mkdir(exist_ok=False);(dst/'kernel.asc').write_bytes(s.encode())
(w/'s21b_changes.patch').write_text(''.join(difflib.unified_diff(old.decode().splitlines(True),s.splitlines(True),fromfile='s20f/kernel.asc',tofile='s21b/kernel.asc')))
sha=hashlib.sha256(s.encode()).hexdigest();(w/'source_b.json').write_text(json.dumps(dict(variant='s21b',sha256=sha,bytes=len(s.encode())),indent=2))
sha_a=json.loads((w/'source_a.json').read_text())['sha256']
for src,dst in [('compile_a.sh','compile_b.sh'),('run_a_pilot.py','run_b_pilot.py'),('run_a_final.py','run_b_final.py'),('verify21_a_final.py','verify21_b_final.py'),('verify_pilot.py','verify_b_pilot.py')]:
    text=(w/src).read_text().replace('s21a','s21b').replace('21a','21b').replace('21_a','21_b').replace('_f_a','_f_b').replace('a_pilot','b_pilot').replace('a_final','b_final').replace('pilot_a_verified','pilot_b_verified').replace(sha_a,sha)
    (w/dst).write_bytes(text.encode())
print(json.dumps(dict(sha256=sha,bytes=len(s.encode()),maxima=budget['maxima'])))
