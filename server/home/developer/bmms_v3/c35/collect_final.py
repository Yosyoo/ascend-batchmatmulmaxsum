import csv,hashlib,json,shutil,statistics
from pathlib import Path
R=Path('/home/developer/bmms_v3');O=R/'c35'
full=json.loads((R/'c29/clean106_official15.json').read_text())
assert len(full)==15 and all(r.get('passed') and r.get('returncode')==0 for r in full)
shutil.copy2(R/'c29/clean106_official15.json',O/'clean106_15.json')
(O/'full15_csv').mkdir(exist_ok=True)
for row in full:
    spec='_'.join(map(str,row['shape']+[row['dtype'],row['ta'],row['tb']]))
    work=R/'variants/clean106/research/PipeUtilization'/spec
    files=sorted(work.glob('profile/PROF_*/mindstudio_profiler_output/op_summary_*.csv'))
    assert files
    shutil.copy2(files[-1],O/'full15_csv'/('P'+str(row['case'])+'.csv'))
summaries={};all_sessions=[];output_checks={}
for mode,point,variant in [('rows','P15','clean104'),('max','P14','clean105'),('prefetch','P2','clean106')]:
    rows=json.loads((O/mode/'results.json').read_text())
    assert len(rows)==8 and all(r.get('passed') and r.get('returncode')==0 for r in rows)
    all_sessions.extend(rows)
    summaries[mode]=json.loads((O/mode/'summary.json').read_text())
    controls=sorted((O/mode).glob('*_'+point+'_clean102_y.bin'))
    outputs=sorted((O/mode).glob('*_'+point+'_'+variant+'_y.bin'))
    assert len(controls)==len(outputs)==4
    ref=controls[0].read_bytes()
    output_checks[mode]={'baseline_outputs_identical':all(f.read_bytes()==ref for f in controls),'candidate_outputs_identical_to_baseline':all(f.read_bytes()==ref for f in outputs)}
prefetch=[r for r in all_sessions if r['point']=='P2']
pipes={v:{k:statistics.median(r['pipes'][k] for r in prefetch if r['variant']==v) for k in ['aiv_vec_time(us)','aiv_scalar_time(us)','aiv_mte2_time(us)']} for v in ['clean102','clean106']}
summary={'candidate':'clean106','sha256':hashlib.sha256((R/'variants/clean106/kernel.asc').read_bytes()).hexdigest(),'byte_size':len((R/'variants/clean106/kernel.asc').read_bytes()),'scope':'Only user-supplied15 shapes, focused ABBA repetitions at P2/P14/P15; zero OJ submissions','full15_passed':15,'all_returncodes_zero':True,'maxrel_full15':max(r['maxrel'] for r in full),'full15_warm_last60_us':[r['warm_us'] for r in full],'focused_profile_sessions':24,'focused_all_passed':True,'ABBA':summaries,'prefetch_session_pipe_medians_us':pipes,'saved_output_comparison':output_checks,'retained':'clean106 only; clean104 no gain, clean105 inconsistent result','score_prediction':None,'measurement_unit':'120 complete calls per session, last60 Task Duration median; independent sessions are the repeats'}
(O/'validation_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
