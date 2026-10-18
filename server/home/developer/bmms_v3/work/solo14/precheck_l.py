from pathlib import Path
import json, subprocess

root=Path('/home/developer/bmms_v3')
out=root/'solo14_data/precheck_s14l'
out.mkdir(exist_ok=False)
balanced=(root/'solo14_data/balanced_cases.txt').read_text().splitlines()
(out/'baseline_cancel_k.txt').write_text(balanced[12]+'\n')
(out/'balanced_bf16.txt').write_text('\n'.join(x for x in balanced if x.split()[4]=='2')+'\n')
checks=[
    ('baseline_cancel_k', 's13k', out/'baseline_cancel_k.txt', False),
    ('balanced_bf16', 's14k', out/'balanced_bf16.txt', True),
    ('balanced_384', 's14l', root/'solo14_data/balanced_cases.txt', True),
    ('narrow_legal_120', 's14l', root/'solo14_data/narrow_legal_cases.txt', True),
    ('split_stress_160', 's14l', root/'solo14_data/split16_cases.txt', True),
    ('narrow_precision', 's14l', root/'solo8_data/narrow_cases.txt', True),
    ('narrow_extra_precision', 's14l', root/'solo8_data/narrow_extra_cases.txt', True),
]
summary=[]
for label,variant,manifest,required in checks:
    p=subprocess.run([str(root/'variants'/variant/'build/bench_cases'),str(manifest)],capture_output=True,text=True,timeout=600)
    (out/(label+'.log')).write_text(p.stdout+p.stderr)
    rows=[json.loads(x) for x in p.stdout.splitlines() if x.startswith('{')]
    expected=len(manifest.read_text().splitlines())
    good=p.returncode==0 and len(rows)==expected and all(x['passed'] and x['consistent'] for x in rows)
    item={'label':label,'variant':variant,'expected':expected,'observed':len(rows),'passed':good,'returncode':p.returncode,'max_absolute':max((x['absolute'] for x in rows),default=None)}
    summary.append(item)
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    print(json.dumps(item),flush=True)
    if required and not good:
        print((p.stdout+p.stderr)[-4000:],flush=True)
        raise SystemExit(p.returncode or 1)
