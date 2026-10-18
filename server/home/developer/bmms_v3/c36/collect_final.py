import hashlib,json,shutil
from pathlib import Path
R=Path('/home/developer/bmms_v3');O=R/'c36'
full=json.loads((R/'c29/clean109_official15.json').read_text())
assert len(full)==15 and all(r.get('passed') and r.get('returncode')==0 for r in full)
shutil.copy2(R/'c29/clean109_official15.json',O/'clean109_15.json')
(O/'full15_csv').mkdir(exist_ok=True)
for row in full:
 spec='_'.join(map(str,row['shape']+[row['dtype'],row['ta'],row['tb']]))
 files=sorted((R/'variants/clean109/research/PipeUtilization'/spec).glob('profile/PROF_*/mindstudio_profiler_output/op_summary_*.csv'))
 assert files
 shutil.copy2(files[-1],O/'full15_csv'/('P'+str(row['case'])+'.csv'))
summary={};all_rows=[];output_checks={}
for mode,variant,count in [('priority','clean107',8),('others','clean107',40),('fused','clean108',8),('reuse','clean109',8)]:
 rows=json.loads((O/mode/'results.json').read_text())
 assert len(rows)==count and all(r.get('passed') and r.get('returncode')==0 for r in rows)
 all_rows.extend(rows)
 summary[mode]=json.loads((O/mode/'summary.json').read_text())
 output_checks[mode]={}
 for point in sorted({r['point'] for r in rows}):
  controls=sorted((O/mode).glob('*_'+point+'_clean106_y.bin'))
  outputs=sorted((O/mode).glob('*_'+point+'_'+variant+'_y.bin'))
  assert len(controls)==len(outputs)==4
  ref=controls[0].read_bytes()
  output_checks[mode][point]={'control_outputs_identical':all(f.read_bytes()==ref for f in controls),'candidate_outputs_bitwise_equal_to_control':all(f.read_bytes()==ref for f in outputs)}
(O/'build_logs').mkdir(exist_ok=True)
for v in ['clean107','clean108','clean109']:
 shutil.copy2(R/'variants'/v/'build.log',O/'build_logs'/(v+'.log'))
result={'candidate':'clean109','sha256':hashlib.sha256((R/'variants/clean109/kernel.asc').read_bytes()).hexdigest(),'bytes':len((R/'variants/clean109/kernel.asc').read_bytes()),'scope':'Only user-supplied15 shapes; zero OJ submissions','full15_passed':15,'all_returncodes_zero':True,'maxrel_full15':max(r['maxrel'] for r in full),'full15_warm_last60_us':[r['warm_us'] for r in full],'focused_profile_sessions':len(all_rows),'focused_all_passed':True,'ABBA':summary,'saved_output_comparison':output_checks,'retained':'109 only: B row-group reuse, all other functions byte-identical106.107 migration bundle and108 MulAddDst are not included.','score_prediction':None,'measurement_unit':'120 true calls per session, last60 Task Duration median; independent sessions are repeats'}
(O/'validation_summary.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
