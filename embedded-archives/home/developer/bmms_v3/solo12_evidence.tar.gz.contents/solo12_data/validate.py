from pathlib import Path
import json,subprocess,sys
root=Path('/home/developer/bmms_v3');v=sys.argv[1]
out=root/'solo12_data'/('validation_'+v);out.mkdir(exist_ok=True)
exe=root/'variants'/v/'build/bench_cases'
suites=[('copy_1728',root/'solo11_data/copy_cases.txt'),
 ('vector_192',root/'solo10_data/vector_cases.txt'),
 ('micro_precision',root/'solo9_data/micro_cases.txt'),
 ('nz_precision',root/'solo8_data/nz_cases.txt'),
 ('regression_5712',root/'delivery4/validation/cases.txt'),
 ('split_precision',root/'variants/s5d/split_cases.txt'),
 ('direct_precision',root/'variants/s5p/direct_cases.txt'),
 ('tail_precision',root/'variants/s5r/tail_cases.txt'),
 ('large_precision',root/'solo6_data/large_cases.txt'),
 ('narrow_precision',root/'solo8_data/narrow_cases.txt'),
 ('narrow_extra_precision',root/'solo8_data/narrow_extra_cases.txt')]
summary=[]
for label,manifest in suites:
 expected=len(manifest.read_text().splitlines())
 p=subprocess.run([str(exe),str(manifest)],capture_output=True,text=True,timeout=600)
 (out/(label+'.log')).write_text(p.stdout+p.stderr)
 rows=[json.loads(line) for line in p.stdout.splitlines() if line.startswith('{')]
 good=p.returncode==0 and len(rows)==expected and all(r['passed'] and r['consistent'] for r in rows)
 item={'suite':label,'expected':expected,'observed':len(rows),'passed':good,'max_absolute':max((r['absolute'] for r in rows),default=None),'max_relative':max((r['relative'] for r in rows),default=None)}
 summary.append(item);print(json.dumps(item),flush=True)
 (out/'precision_summary.json').write_text(json.dumps({'total':sum(i['observed'] for i in summary),'suites':summary},indent=2))
 if not good:
  print((p.stdout+p.stderr)[-4000:]);raise SystemExit(p.returncode or 1)
print('PASS:',sum(i['observed'] for i in summary),'cases, 3 identical executions each',flush=True)
