#!/usr/bin/env python3
"""Profile many shapes in a single msprof session.

Usage: python3 multi.py <variant> <shapes-file> [iters] [dtype ta tb]
Prints JSON with per-shape task durations parsed from the msprof op_summary CSV.
"""
import csv
import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent
VAR = Path(os.environ.get('VARIANTS_ROOT', str(R.parent / 'variants')))


def main():
    variant = sys.argv[1]
    shapes_file = sys.argv[2]
    iters = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    dtype = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    ta = int(sys.argv[5]) if len(sys.argv) > 5 else 0
    tb = int(sys.argv[6]) if len(sys.argv) > 6 else 0
    vd = VAR / variant
    work = vd / 'work' / ('multi_' + Path(shapes_file).stem)
    work.mkdir(parents=True, exist_ok=True)
    shapes = []
    for line in Path(shapes_file).read_text().splitlines():
        p = line.split()
        if len(p) >= 4:
            shapes.append([int(x) for x in p[:4]])
    cmd = [str(vd / 'build/bench_multi'), str(Path(shapes_file).resolve()), str(iters), str(dtype), str(ta), str(tb)]
    env = dict(os.environ)
    env['BMMS_DEVICE_ID'] = os.environ.get('BMMS_DEVICE_ID', '0')
    import shutil
    if (work / 'profile').exists():
        shutil.rmtree(work / 'profile')
    p = subprocess.run(['msprof', '--application=' + ' '.join(cmd),
                        '--output=' + str(work / 'profile'),
                        '--aic-metrics=PipeUtilization', '--task-time=on'],
                       cwd=work, capture_output=True, text=True, timeout=3600, env=env)
    (work / 'msprof.log').write_text(p.stdout + p.stderr)
    files = sorted((work / 'profile').glob('PROF_*/mindstudio_profiler_output/op_summary_*.csv'))
    if not files:
        print(json.dumps({'error': (p.stdout + p.stderr)[-2000:]}))
        return 1
    rows = list(csv.DictReader(files[-1].open()))
    times = [float(x['Task Duration(us)']) for x in rows]
    UNIT_COLS = ['aic_mac_time(us)', 'aic_scalar_time(us)', 'aic_mte1_time(us)', 'aic_mte2_time(us)',
                 'aic_fixpipe_time(us)', 'aiv_vec_time(us)', 'aiv_scalar_time(us)',
                 'aiv_mte2_time(us)', 'aiv_mte3_time(us)', 'aic_icache_miss_rate', 'aiv_icache_miss_rate']
    out = {'variant': variant, 'iters': iters, 'ntasks': len(times), 'shapes': []}
    per = iters
    idx = 0
    for s in shapes:
        chunk = times[idx:idx + per]
        idx += per
        if not chunk:
            continue
        half = chunk[len(chunk) // 2:]
        halfrows = rows[idx - len(chunk) + len(chunk) // 2:idx]
        units = {}
        for c in UNIT_COLS:
            try:
                units[c] = round(float(np.median([float(r[c]) for r in halfrows])), 3)
            except Exception:
                pass
        out['shapes'].append({
            'units': units,
            'shape': s,
            'n': len(chunk),
            'median': round(float(np.median(chunk)), 3),
            'warm_median': round(float(np.median(half)), 3),
            'warm_mean': round(float(np.mean(half)), 3),
            'cold_median': round(float(np.median(chunk[:5])), 3),
            'mean': round(float(np.mean(chunk)), 3),
            'min': round(float(np.min(chunk)), 3),
            'max': round(float(np.max(chunk)), 3),
            'all': [round(t, 2) for t in chunk],
        })
    if idx != len(times):
        out['leftover'] = len(times) - idx
    print(json.dumps(out, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
