import csv,json,statistics,sys
from pathlib import Path
v,shape=sys.argv[1:3];root=Path('/home/developer/bmms_v3');files=list((root/'variants'/v/('research/PipeUtilization/'+shape+'/profile')).glob('PROF_*/mindstudio_profiler_output/op_summary_*.csv'));assert files
rows=list(csv.DictReader(files[-1].open()));warm=rows[-60:];d={'variant':v,'shape':shape,'tasks':len(rows),'warm_count':len(warm),'metrics':{}}
for k in rows[0]:
 if any(a in k.lower() for a in ['duration','time(us)','ratio','bandwidth','utilization','_mac','_scalar','_vector','_mte','_fixpipe']):
  try:d['metrics'][k]=statistics.median(float(x[k]) for x in warm)
  except (ValueError,TypeError):pass
(root/'c26'/('metrics_'+v+'_'+shape+'.json')).write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d))
