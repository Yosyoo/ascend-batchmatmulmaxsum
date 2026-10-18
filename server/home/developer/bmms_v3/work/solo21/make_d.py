from pathlib import Path
import json,hashlib,difflib
r=Path(__file__).resolve().parents[2];w=r/'work/solo21'
rows=[json.loads(x) for x in (w/'probe_d/results.jsonl').read_text().splitlines()];assert len(rows)==1920
limits={'L1_bytes':524288,'L0A_bytes':65536,'L0B_bytes':65536,'L0C_bytes':131072,'UB_bytes':184320}
for x in rows:
    assert all(x[k]<=v for k,v in limits.items())
    assert (x['stepKa']%x['stepKb']==0 or x['stepKb']==x['old_stepKb']) and x['stepKb']>=x['old_stepKb']
    assert x['shareL1Size']==x['L1_bytes'] and x['shareMode']==0
budget=dict(variant='s21d',parent='s20f',capacity_calculated_before_edit=True,resource_probe_rows=len(rows),
    probe_sha256=hashlib.sha256((w/'probe_d/results.jsonl').read_bytes()).hexdigest(),
    maxima={k:max(x[k] for x in rows) for k in limits},limits=limits,
    scope='GM ND; K=2048..8192 multiple32; M=512..2432 multiple128; N=512..8192 multiple256; existing tile128x256; b*ceil(M/128)<availableCoreNum',
    change='Retain tile/baseK/arithmetic/workspace; choose larger stepKb dividing stepKa within remaining L1, depthB1=2*stepKb and shareL1Size=actual allocation; cache key includes the new flag',
    inference='Larger B prefetch may reduce GM transfer/scalar overhead; official shapes unknown. K128 API attempts actually returned64 and were never built as an operator.')
(w/'resource_s21d_before_edit.json').write_text(json.dumps(budget,indent=2)+'\n')
old=(r/'variants/s20f/kernel.asc').read_bytes();assert hashlib.sha256(old).hexdigest()=='198ee0bb6eca5a4503e734438da20f05a4ad962e5c7d53976b84552190b09f3c'
s=old.decode();anchor='    const bool pairK = !packed && k>1024 && k%2==0;';assert s.count(anchor)==1
extra='''    const bool useLongB = !packed && k>=2048 && k<=8192 && k%32==0 &&
        m>=512 && m<=2432 && m%128==0 && n>=512 && n<=8192 && n%256==0 &&
        tileM==128 && tileN==256 && (int64_t)b*((m+127)/128)<availableCoreNum;
'''
s=s.replace(anchor,extra+anchor)
needle='bool ta, tb, nz; TCubeTiling tiling;';assert s.count(needle)==1;s=s.replace(needle,'bool ta, tb, nz, longB; TCubeTiling tiling;')
needle='plan.nz == packed && plan.tileM';assert s.count(needle)==1;s=s.replace(needle,'plan.nz == packed && plan.longB == useLongB && plan.tileM')
needle='transposeX1, transposeX2, packed, tiling});';assert s.count(needle)==1;s=s.replace(needle,'transposeX1, transposeX2, packed, useLongB, tiling});')
anchor='        tiling.M = useFullA ? tileM : storeM;';assert s.count(anchor)==1
extra='''        if(useLongB && tiling.stepM==1 && tiling.stepN==1 && tiling.stepKa>0 && tiling.stepKb>0) {
            const int oldKb=tiling.stepKb;
            const int maxKb=(platform.l1Size-2*tiling.baseM*tiling.baseK*tiling.depthA1)/(4*tiling.baseN*tiling.baseK);
            for(int q=oldKb+1;q<=maxKb;++q)if(tiling.stepKa%q==0)tiling.stepKb=q;
            if(tiling.stepKb>oldKb) {
                tiling.depthB1=2*tiling.stepKb;
                tiling.shareL1Size=2*tiling.baseK*(tiling.baseM*tiling.depthA1+tiling.baseN*tiling.depthB1);
            }
        }
'''
s=s.replace(anchor,extra+anchor);dst=r/'variants/s21d';dst.mkdir(exist_ok=False);(dst/'kernel.asc').write_bytes(s.encode())
(w/'s21d_changes.patch').write_text(''.join(difflib.unified_diff(old.decode().splitlines(True),s.splitlines(True),fromfile='s20f/kernel.asc',tofile='s21d/kernel.asc')))
sha=hashlib.sha256(s.encode()).hexdigest();(w/'source_d.json').write_text(json.dumps(dict(variant='s21d',sha256=sha,bytes=len(s.encode())),indent=2))
sha_a=json.loads((w/'source_a.json').read_text())['sha256']
for src,dst in [('compile_a.sh','compile_d.sh'),('run_a_pilot.py','run_d_pilot.py'),('run_a_final.py','run_d_final.py'),('verify21_a_final.py','verify21_d_final.py'),('verify_pilot.py','verify_d_pilot.py')]:
    text=(w/src).read_text().replace(sha_a,sha).replace('s21a','s21d').replace('21a','21d').replace('21_a','21_d').replace('_f_a','_f_d').replace('a_pilot','d_pilot').replace('a_final','d_final').replace('pilot_a_verified','pilot_d_verified').replace('source_a.json','source_d.json')
    (w/dst).write_bytes(text.encode())
print(json.dumps(dict(sha256=sha,bytes=len(s.encode()),maxima=budget['maxima'],B_steps=sorted({(x['old_stepKb'],x['stepKb']) for x in rows}))))
