from pathlib import Path
import json, subprocess, sys

root=Path('/home/developer/bmms_v3')
v=sys.argv[1]
out=root/'solo14_data'/('precheck_'+v+'_v2')
out.mkdir(exist_ok=False)
suites=[('balanced_384',root/'solo14_data/balanced_cases.txt'),
        ('pair_edge_312',root/'solo14_data/pair_edge_cases.txt'),
        ('narrow_legal_120',root/'solo14_data/narrow_legal_cases.txt'),
        ('split_stress_160',root/'solo14_data/split16_cases.txt'),
        ('narrow_precision',root/'solo8_data/narrow_cases.txt'),
        ('narrow_extra_precision',root/'solo8_data/narrow_extra_cases.txt')]
if len(sys.argv)>2:
    dtype=sys.argv[2]
    selected=[x for x in suites[0][1].read_text().splitlines() if x.split()[4]==dtype]
    dest=out/'selected_balanced.txt'
    dest.write_text('\n'.join(selected)+'\n')
    suites=[('balanced_dtype'+dtype,dest)]
summary=[]
for label,manifest in suites:
    p=subprocess.run([str(root/'variants'/v/'build/bench_cases'),str(manifest)],capture_output=True,text=True,timeout=600)
    (out/(label+'.log')).write_text(p.stdout+p.stderr)
    rows=[json.loads(x) for x in p.stdout.splitlines() if x.startswith('{')]
    expected=len(manifest.read_text().splitlines())
    good=p.returncode==0 and len(rows)==expected and all(x['passed'] and x['consistent'] for x in rows)
    item={'label':label,'variant':v,'expected':expected,'observed':len(rows),'passed':good,'returncode':p.returncode,'max_absolute':max((x['absolute'] for x in rows),default=None)}
    summary.append(item)
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(item),flush=True)
    if not good:
        print((p.stdout+p.stderr)[-4000:],flush=True)
        raise SystemExit(p.returncode or 1)
