from pathlib import Path
import csv,hashlib,json,math,statistics,sys
r=Path(__file__).resolve().parents[2];w=Path(__file__).parent;letter=sys.argv[1];v='s42'+letter
tag=sys.argv[2] if len(sys.argv)>2 else 'round42_ab20261015'
label=sys.argv[3] if len(sys.argv)>3 else f'quick42_{letter}_00'
root=r/f'evidence/remote_round28_{tag}';p=root/f'solo17_data/{label}'
col=json.loads((root/'collection_manifest.json').read_text());comparison=json.loads((p/'comparison.json').read_text())
base_col=json.loads((root/'collection_manifest.json').read_text())
orders=[];kernel_hits={}
baseline=comparison['baseline']
for i,var in enumerate((baseline,v,v,baseline)):
 x=json.loads((p/f'{i}_{var}/summary.json').read_text());assert x['tasks']==160*len(x['shapes']) and x['kernels_per_call']==1
 assert x['hashes']['kernel.asc']==hashlib.sha256((r/f'variants/{var}/kernel.asc').read_bytes()).hexdigest()
 hashes=col if var==v else base_col
 if f'variants/{var}/build/bench_multi' not in hashes['source_and_exe_sha256']:
  hashes=json.loads((r/'evidence/remote_round28_round30_p_final20261014/collection_manifest.json').read_text())
 assert x['hashes']['bench_multi']==hashes['source_and_exe_sha256'][f'variants/{var}/build/bench_multi']
 csvpath=root/Path(x['profile']).relative_to('/home/developer/bmms_v3');raw=list(csv.DictReader(csvpath.open()))
 runtime=[z for z in raw if 'bmms_' not in z['Op Name']];assert all(z['Op Name']=='preload_stack_16KB' and int(z['Block Num'])==0 for z in runtime)
 rows=[z for z in raw if 'bmms_' in z['Op Name']];rows.sort(key=lambda z:float(z['Task Start Time(us)']));assert len(rows)==x['tasks']
 for j,item in enumerate(x['shapes']):
  seg=rows[j*160:(j+1)*160];times=[float(z['Task Duration(us)']) for z in seg]
  assert times==item['total_us'] and statistics.median(times[-80:])==item['total_warm_us']
  assert sorted({z['Op Name'] for z in seg})==item['op_names']
  for key,val in item['median_metrics'].items():
   actual=statistics.median(float(z[key]) for z in seg[-80:]);assert actual==val or math.isnan(actual) and math.isnan(val)
  if var==v:
   for name in item['op_names']:kernel_hits[name]=kernel_hits.get(name,0)+1
 orders.append(x)
ratios=[]
for a,b in ((orders[0],orders[1]),(orders[3],orders[2])):
 vals=[z['total_warm_us']/y['total_warm_us'] for y,z in zip(a['shapes'],b['shapes'])]
 ratios.append(math.exp(statistics.mean(map(math.log,vals))))
assert all(math.isclose(a,b,rel_tol=1e-14,abs_tol=0) for a,b in zip(ratios,[z['geometric_mean_ratio'] for z in comparison['orders']])) # libm rounding differs on Windows/Linux
out=dict(variant=v,raw_tasks_verified=sum(x['tasks'] for x in orders),shape_rows_verified=sum(len(x['shapes']) for x in orders),last80_medians_and_all_metrics_verified=True,one_kernel_per_call_verified=True,
 source_rehashed_and_recorded_exe_hashes_matched=True,ratios=ratios,kernel_trace_hits=kernel_hits)
(w/f'pool_verified_{v}_{label}.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
if len(sys.argv)<=3:(w/f'pool_verified_{v}.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:z for k,z in out.items() if k!='kernel_trace_hits'}))
