#!/usr/bin/env python3
"""Show per-unit profiler breakdown for a variant's warm tasks."""
import csv
import glob
import json
import sys
from pathlib import Path

import numpy as np

R = Path(__file__).resolve().parent


def load(variant, work, iters):
    files = sorted((R / 'variants' / variant / 'work' / work / 'profile').glob(
        'PROF_*/mindstudio_profiler_output/op_summary_*.csv'))
    rows = list(csv.DictReader(files[-1].open()))
    return rows


def main():
    variant = sys.argv[1]
    work = sys.argv[2]
    iters = int(sys.argv[3]) if len(sys.argv) > 3 else 30
    shapes = []
    for line in (R.parent / 'shapes_probe.txt').read_text().splitlines():
        p = line.split()
        if len(p) >= 4:
            shapes.append([int(x) for x in p[:4]])
    rows = load(variant, work, iters)
    cols_aic = ['aicore_time(us)', 'aic_mac_time(us)', 'aic_scalar_time(us)', 'aic_mte1_time(us)',
                'aic_mte2_time(us)', 'aic_fixpipe_time(us)', 'aic_icache_miss_rate']
    cols_aiv = ['aiv_time(us)', 'aiv_vec_time(us)', 'aiv_scalar_time(us)', 'aiv_mte2_time(us)',
                'aiv_mte3_time(us)', 'aiv_icache_miss_rate', 'aiv_total_cycles']
    idx = 0
    for s in shapes:
        chunk = rows[idx:idx + iters]
        idx += iters
        if not chunk:
            continue
        half = chunk[len(chunk) // 2:]
        dur = np.median([float(r['Task Duration(us)']) for r in half])
        print('shape', s, 'warm=%.2f' % dur)
        for group in (cols_aic, cols_aiv):
            vals = []
            for c in group:
                try:
                    vals.append('%s=%.3f' % (c.replace('(us)', '').replace('aic_', '').replace('aiv_', ''),
                                             np.median([float(r[c]) for r in half])))
                except Exception:
                    pass
            print('   ', '  '.join(vals))


if __name__ == '__main__':
    main()
