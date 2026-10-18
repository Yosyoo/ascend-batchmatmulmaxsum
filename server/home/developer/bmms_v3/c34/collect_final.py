import hashlib,json,shutil,struct
from pathlib import Path
R=Path('/home/developer/bmms_v3')
O=R/'c34'
full=json.loads((R/'c29/clean102_official15.json').read_text())
assert len(full)==15 and all(r.get('passed') and r.get('returncode')==0 for r in full)
shutil.copy2(R/'c29/clean102_official15.json',O/'clean102_15.json')
sessions=[]
for mode in ['split','fence']:
    rows=json.loads((O/mode/'results.json').read_text())
    assert len(rows)==(12 if mode=='split' else 16)
    assert all(r.get('passed') and r.get('returncode')==0 for r in rows)
    sessions.extend(rows)
bitwise={}
for mode,point,variant in [('split','P15','clean102'),('fence','P2','clean103'),('fence','P4','clean103')]:
    controls=sorted((O/mode).glob('*_'+point+'_clean101_y.bin'))
    vals=sorted((O/mode).glob('*_'+point+'_'+variant+'_y.bin'))
    ref=controls[0].read_bytes()
    bitwise[point]={'all_controls_bitwise_equal':all(f.read_bytes()==ref for f in controls),'all_candidate_outputs_bitwise_equal_to_control':all(f.read_bytes()==ref for f in vals),'candidate_calls_recorded':len(vals),'baseline_values':struct.unpack('<'+'f'*(len(ref)//4),ref),'candidate_values':[struct.unpack('<'+'f'*(len(f.read_bytes())//4),f.read_bytes()) for f in vals]}
summary={'candidate':'clean102','sha256':hashlib.sha256((R/'variants/clean102/kernel.asc').read_bytes()).hexdigest(),'scope':'Only user-supplied15 shapes. Focused repetitions at P2/P4/P15. No OJ submissions.','full15_passed':len(full),'all_returncodes_zero':True,'maxrel_full15':max(r['maxrel'] for r in full),'full15_warm_last60_us':[r['warm_us'] for r in full],'focused_profile_sessions':len(sessions),'focused_checks_all_passed':True,'ABBA':{mode:json.loads((O/mode/'summary.json').read_text()) for mode in ['split','fence']},'saved_output_comparison':bitwise,'retained':'clean102 only; clean103 rejected for no reproducible total duration benefit','measurement_unit':'120 complete operator calls per session; last60 median; independent sessions are repeats, not individual iterations','score_prediction':None}
(O/'validation_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
