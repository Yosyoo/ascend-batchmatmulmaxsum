from pathlib import Path
import json,subprocess,sys
root=Path('/home/developer/bmms_v3')
v=sys.argv[1]
exe=root/'variants'/v/'build/bench_cases'
out=root/'solo6_data'/('validation_'+v)
out.mkdir(exist_ok=True)
suites=[('regression_5712',root/'delivery4/validation/cases.txt'),
    ('split_precision',root/'variants/s5d/split_cases.txt'),
    ('direct_precision',root/'variants/s5p/direct_cases.txt'),
    ('tail_precision',root/'variants/s5r/tail_cases.txt'),
    ('large_precision',root/'solo6_data/large_cases.txt')]
summary=[]
for label,manifest in suites:
    expected=len(manifest.read_text().splitlines())
    p=subprocess.run([str(exe),str(manifest)],capture_output=True,text=True,timeout=600)
    (out/(label+'.log')).write_text(p.stdout+p.stderr)
    rows=[json.loads(line) for line in p.stdout.splitlines() if line.startswith('{')]
    passed=p.returncode==0 and len(rows)==expected and all(r['passed'] and r['consistent'] for r in rows)
    item={'suite':label,'expected':expected,'observed':len(rows),'passed':passed,
        'max_absolute':max((r['absolute'] for r in rows),default=None),
        'max_relative':max((r['relative'] for r in rows),default=None)}
    summary.append(item); print(json.dumps(item),flush=True)
    (out/'precision_summary.json').write_text(json.dumps(summary,indent=2))
    if not passed:
        print((p.stdout+p.stderr)[-3000:]); raise SystemExit(p.returncode or 1)
print('PASS:',sum(s['observed'] for s in summary),'cases, 3 identical executions each',flush=True)
