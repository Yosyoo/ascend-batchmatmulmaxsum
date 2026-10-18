from pathlib import Path
import json,hashlib,difflib
r=Path(__file__).resolve().parents[2];w=r/'work/solo21'
rows=[json.loads(x) for x in (w/'probe/results.jsonl').read_text().splitlines()]
assert len(rows)==1920
limits={'L1_bytes':524288,'L0A_bytes':65536,'L0B_bytes':65536,'L0C_bytes':131072,'UB_bytes':184320}
for x in rows:assert all(x[k]<=v for k,v in limits.items())
budget=dict(variant='s21a',parent='s20f',capacity_calculated_before_edit=True,resource_probe_rows=len(rows),
    probe_sha256=hashlib.sha256((w/'probe/results.jsonl').read_bytes()).hexdigest(),
    maxima={k:max(x[k] for x in rows) for k in limits},limits=limits,
    scope='GM ND; K=2048..8192 multiple32; M=512..2432 multiple128; N=512..8192 multiple256; existing tile128x256; b*ceil(M/128)<availableCoreNum',
    change='tileM128 to64 before UB guard, tiling, tasks, workspace and dispatch; no change to half-K computation or ordered FP32 accumulation',
    inference='More independent row tasks may offset long-K paired overhead; official case shapes unknown. Prior half-K resource replan was slower and is not repeated.')
(w/'resource_s21a_before_edit.json').write_text(json.dumps(budget,indent=2)+'\n')
old=(r/'variants/s20f/kernel.asc').read_bytes()
assert hashlib.sha256(old).hexdigest()=='198ee0bb6eca5a4503e734438da20f05a4ad962e5c7d53976b84552190b09f3c'
s=old.decode()
anchor='    const bool useFullA = !packed && m>=512'
assert s.count(anchor)==1
extra='''    // Increase row parallelism for long-K pairs while retaining the same two-half arithmetic.
    if (!packed && k>=2048 && k<=8192 && k%32==0 && m>=512 && m<=2432 && m%128==0 &&
        n>=512 && n<=8192 && n%256==0 && tileM==128 && tileN==256 &&
        (int64_t)b*((m+127)/128)<availableCoreNum) tileM=64;
'''
s=s.replace(anchor,extra+anchor)
dst=r/'variants/s21a';dst.mkdir(exist_ok=False);(dst/'kernel.asc').write_bytes(s.encode())
(w/'s21a_changes.patch').write_text(''.join(difflib.unified_diff(old.decode().splitlines(True),s.splitlines(True),fromfile='s20f/kernel.asc',tofile='s21a/kernel.asc')))
sha=hashlib.sha256(s.encode()).hexdigest()
(w/'source_a.json').write_text(json.dumps(dict(variant='s21a',sha256=sha,bytes=len(s.encode())),indent=2))
print(json.dumps(dict(sha256=sha,bytes=len(s.encode()),maxima=budget['maxima'])))
