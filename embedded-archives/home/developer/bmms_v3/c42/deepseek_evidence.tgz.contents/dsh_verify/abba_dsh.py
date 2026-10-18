import importlib.util, json, math, os, shutil, statistics
from pathlib import Path
ROOT = Path('/home/developer/bmms_v3')
spec = importlib.util.spec_from_file_location('measure', ROOT/'c26/measure_research.py')
q = importlib.util.module_from_spec(spec); spec.loader.exec_module(q)
os.environ['AIC_METRIC'] = 'PipeUtilization'
OUT = ROOT/'dsh_verify'/'out'; OUT.mkdir(parents=True, exist_ok=True)
SPEC, CTRL, CAND, DEV = '4_8_16_128_2_1_1', 'dsh125', 'dsh131', 1
runs = []
for block in range(2):
    for pos, v in enumerate([CTRL, CAND, CAND, CTRL]):
        row = q.run_shape(v, SPEC, 'msprof', 120, 1, DEV)
        us = row.get('all_us') or []
        med = statistics.median(us[-60:]) if len(us) >= 60 else None
        rec = dict(block=block, pos=pos, variant=v, median_us=med, n=len(us),
                   passed=bool(row.get('passed')), rc=row.get('returncode'),
                   maxrel=row.get('maxrel'), error=row.get('error'))
        runs.append(rec)
        work = ROOT/'variants'/v/'research'/'PipeUtilization'/SPEC
        profs = sorted(work.glob('profile/PROF_*/mindstudio_profiler_output/op_summary_*.csv'))
        if profs: shutil.copy2(profs[-1], OUT/f'B{block}_{pos}_{v}_op_summary.csv')
        y = work/'output/y.bin'
        if y.exists(): shutil.copy2(y, OUT/f'B{block}_{pos}_{v}_y.bin')
        print(json.dumps(rec), flush=True)
        if row.get('returncode') != 0 or not row.get('passed'):
            print('VALIDATION FAILED - aborting', flush=True); raise SystemExit(2)
def gm(xs): return math.exp(sum(math.log(x) for x in xs)/len(xs))
blocks = []
for b in range(2):
    g = [r['median_us'] for r in runs if r['block'] == b]
    a, c = gm([g[0], g[3]]), gm([g[1], g[2]])
    blocks.append(dict(times_ABBA_us=g, control_geom=a, cand_geom=c,
                       speedup=a/c, reduction_percent=100*(1-c/a), drift_percent=100*(g[3]/g[0]-1)))
ctrl = [r['median_us'] for r in runs if r['variant'] == CTRL]
cand = [r['median_us'] for r in runs if r['variant'] == CAND]
summary = dict(spec=SPEC, control=CTRL, candidate=CAND, device=DEV, iters=120, warm=3,
               blocks=blocks, control_median=statistics.median(ctrl),
               candidate_median=statistics.median(cand),
               pooled_speedup=gm(ctrl)/gm(cand), pooled_reduction_percent=100*(1-gm(cand)/gm(ctrl)),
               control_spread_percent=100*(max(ctrl)/min(ctrl)-1),
               candidate_spread_percent=100*(max(cand)/min(cand)-1),
               overlap=(max(cand) < min(ctrl) or max(ctrl) < min(cand)))
(OUT/'dsh_summary.json').write_text(json.dumps(dict(summary=summary, runs=runs), indent=2)+'\n')
print(json.dumps(summary), flush=True)
