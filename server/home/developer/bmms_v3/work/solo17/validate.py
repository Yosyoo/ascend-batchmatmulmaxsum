"""Run preserved full precision manifests plus new legal medium-K stress on NPU."""
from pathlib import Path
import fcntl,hashlib,json,subprocess,sys
root=Path('/home/developer/bmms_v3');data=root/'solo17_data';v=sys.argv[1]
history_only='--historical-only' in sys.argv
out=data/('validation_'+v+('_historical' if history_only else ''));out.mkdir(exist_ok=False)
lock=(data/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
exe=root/'variants'/v/'build/bench_cases';source=root/'variants'/v/'kernel.asc'
hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,source]}
suites=[('medium_256',data/'medium_cases.txt'),
 ('split_stress_160',root/'solo14_data/split16_cases.txt'),('narrow_legal_120',root/'solo14_data/narrow_legal_cases.txt'),
 ('balanced_384',root/'solo14_data/balanced_cases.txt'),('pair_edge_312',root/'solo14_data/pair_edge_cases.txt'),
 ('dot_once_576',data/'dot_once_cases.txt'),('long_sum',root/'solo14_data/long_sum_cases.txt'),
 ('generic_nt_2970',root/'solo13_data/generic_nt_cases.txt'),('nt_2352',root/'solo13_data/nt_cases.txt'),
 ('copy_1728',root/'solo11_data/copy_cases.txt'),('vector_192',root/'solo10_data/vector_cases.txt'),
 ('micro_precision',root/'solo9_data/micro_cases.txt'),('nz_precision',root/'solo8_data/nz_cases.txt'),
 ('regression_5712',root/'delivery4/validation/cases.txt'),('split_precision',root/'variants/s5d/split_cases.txt'),
 ('direct_precision',root/'variants/s5p/direct_cases.txt'),('tail_precision',root/'variants/s5r/tail_cases.txt'),
 ('large_precision',root/'solo6_data/large_cases.txt'),('narrow_precision',root/'solo8_data/narrow_cases.txt'),
 ('narrow_extra_precision',root/'solo8_data/narrow_extra_cases.txt')]
if history_only:suites=[(label,p) for label,p in suites if label!='medium_256']
summary=[]
for label,manifest in suites:
    expected=len(manifest.read_text().splitlines());assert expected>0
    p=subprocess.run([str(exe),str(manifest)],capture_output=True,text=True,timeout=600)
    (out/(label+'.log')).write_text(p.stdout+p.stderr)
    rows=[json.loads(line) for line in p.stdout.splitlines() if line.startswith('{')]
    good=p.returncode==0 and len(rows)==expected and all(r['passed'] and r['consistent'] for r in rows)
    item=dict(suite=label,manifest=str(manifest),expected=expected,observed=len(rows),passed=good,
        max_absolute=max((r['absolute'] for r in rows),default=None),max_relative=max((r['relative'] for r in rows),default=None))
    summary.append(item);print(json.dumps(item),flush=True)
    (out/'precision_summary.json').write_text(json.dumps(dict(variant=v,total=sum(i['observed'] for i in summary),
        suites=summary,source_and_exe_sha256=hashes,passed=all(i['passed'] for i in summary),
        scope='historical precision only; new medium cancellation diagnostic separately failed for baseline' if history_only else 'historical plus medium diagnostic'),indent=2)+'\n')
    if not good:print((p.stdout+p.stderr)[-4000:],flush=True);raise SystemExit(p.returncode or 1)
assert hashes=={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [exe,source]}
print('PASS:',sum(i['observed'] for i in summary),'cases, 3 identical executions each',flush=True)
