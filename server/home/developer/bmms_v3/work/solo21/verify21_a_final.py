from pathlib import Path
import csv,hashlib,json,math,statistics,zipfile
r=Path(__file__).resolve().parents[2]
ev=r/'evidence/remote_round21_a_final'; d=ev/'solo17_data'
sha='198ee0bb6eca5a4503e734438da21a05a4ad962e5c7d53976b84552190b09f3c'
source=(r/'variants/s21a/kernel.asc').read_bytes()
assert hashlib.sha256(source).hexdigest()==sha
assert (ev/'variants/s21a/kernel.asc').read_bytes()==source
metadata=json.loads((ev/'capture_metadata.json').read_text())
captured={x['path'].removeprefix('/home/developer/bmms_v3/'):x['sha256'] for x in metadata['hashes']}
assert captured['variants/s15i/kernel.asc']==hashlib.sha256((r/'kernel.asc').read_bytes()).hexdigest()
assert (ev/'variants/s15i/kernel.asc').read_bytes()==(r/'kernel.asc').read_bytes()

def check_raw(path,times):
    raw=list(csv.DictReader((ev/path.removeprefix('/home/developer/bmms_v3/')).open()))
    assert len(raw)==len(times) and all('bmms_' in x['Op Name'] for x in raw)
    raw.sort(key=lambda x:float(x['Task Start Time(us)']))
    assert [float(x['Task Duration(us)']) for x in raw]==times
def read(p):return json.loads(p.read_text())
def rows(p):return [json.loads(x) for x in p.read_text().splitlines() if x.startswith('{')]
precision=read(d/'validation_s21a/precision_summary.json')
assert precision['passed'] and precision['total']==18378
assert precision['source_and_exe_sha256']['kernel.asc']==sha
assert precision['source_and_exe_sha256']['bench_cases']==captured['variants/s21a/build/bench_cases']
observed=0
for suite in precision['suites']:
    raw=rows(d/'validation_s21a'/f"{suite['suite']}.log")
    assert suite['passed'] and len(raw)==suite['expected']==suite['observed']
    assert all(x['passed'] and x['consistent'] for x in raw)
    observed+=len(raw)
assert observed==18378
diagnostic=read(d/'diagnostic_21a/summary.json')
for suite in diagnostic:
    raw=rows(d/'diagnostic_21a'/f"{suite['suite']}.log")
    assert suite['passed'] and len(raw)==suite['observed']
    assert all(x['passed'] and x['consistent'] for x in raw)
    assert suite['hashes']==precision['source_and_exe_sha256']
assert sum(x['observed'] for x in diagnostic)==648
pilots=[]
pool_summaries=[]
for order,variant in enumerate(['s15i','s21a','s21a','s15i']):
    x=read(d/'pool18_s21a'/f'{order}_{variant}'/'summary.json')
    pool_summaries.append(x)
    assert x['hashes']['kernel.asc']==captured['variants/'+variant+'/kernel.asc']
    assert x['tasks']==16000 and x['kernels_per_call']==1 and not x['runtime_startup_rows']
    assert len(x['shapes'])==100 and all(len(z['total_us'])==160 for z in x['shapes'])
    check_raw(x['profile'],[t for z in x['shapes'] for t in z['total_us']])
    assert all(statistics.median(z['total_us'][-80:])==z['total_warm_us'] for z in x['shapes'])
    assert x['hashes']['bench_multi']==captured['variants/'+variant+'/build/bench_multi']
    if variant=='s21a':assert x['hashes']['kernel.asc']==sha
pool=read(d/'pool18_s21a/comparison.json');assert pool['passed_task_contract']
for index,(base,candidate) in enumerate([(pool_summaries[0],pool_summaries[1]),(pool_summaries[3],pool_summaries[2])]):
    assert [x['shape'] for x in base['shapes']]==[x['shape'] for x in candidate['shapes']]
    ratios=[b['total_warm_us']/a['total_warm_us'] for a,b in zip(base['shapes'],candidate['shapes'])]
    assert pool['orders'][index]['geometric_mean_ratio']==math.exp(statistics.mean(map(math.log,ratios)))
    assert pool['orders'][index]['ratios']==[dict(shape=a['shape'],ratio=x) for a,x in zip(base['shapes'],ratios)]

hangs=rows(d/'hangs21_a/results.jsonl');assert len(hangs)==6
assert all(x['passed'] and x['kernels_per_call']==1 and x['tasks']==163 and x['source_and_exe_sha256']['kernel.asc']==sha for x in hangs)
for x in hangs:
    check_raw(x['saved_profile'],x['total_us'])
    assert statistics.median(x['total_us'][-80:])==x['total_warm_us']
    assert x['source_and_exe_sha256']['bench']==captured['variants/s21a/build/bench']
    assert not x['runtime_startup_rows']
out=r/'delivery_round21/s21a';out.mkdir(parents=True,exist_ok=True)
(out/'kernel.asc').write_bytes(source)
if not (out/'submission_s21a.zip').exists():
    entry=zipfile.ZipInfo('kernel.asc',(1980,1,1,0,0,0));entry.compress_type=zipfile.ZIP_DEFLATED
    with zipfile.ZipFile(out/'submission_s21a.zip','w') as z:z.writestr(entry,source)
with zipfile.ZipFile(out/'submission_s21a.zip') as z:assert z.namelist()==['kernel.asc'] and z.read('kernel.asc')==source
summary={'variant':'s21a','source_sha256':sha,'precision_cases':observed,'precision_suites':20,'diagnostic_cases':648,'historical_hangs':6,'pool_shapes':100,'pool_orders':['s15i','s21a','s21a','s15i'],'pool_geometric_ratios':[x['geometric_mean_ratio'] for x in pool['orders']],'pilots':pilots,'evidence_sha256':hashlib.sha256((r/'evidence/remote_round21_a_final_verified.zip').read_bytes()).hexdigest(),'submission_zip_sha256':hashlib.sha256((out/'submission_s21a.zip').read_bytes()).hexdigest()}
(out/'validation_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in summary.items() if k!='pilots'},indent=2))

