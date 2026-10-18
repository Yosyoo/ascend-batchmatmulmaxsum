import csv
import glob
import json
import statistics
from pathlib import Path

import numpy as np

root = Path('/home/developer/bmms_v3')
records = []
pipe_keys = [
    'aic_mac_time(us)', 'aic_scalar_time(us)', 'aic_mte1_time(us)',
    'aic_mte2_time(us)', 'aic_fixpipe_time(us)', 'aiv_vec_time(us)',
    'aiv_scalar_time(us)', 'aiv_mte2_time(us)',
]
for filename in sorted((root / 'c33').glob('clean*_p*.json')):
    data = json.loads(filename.read_text())
    row = data[0] if isinstance(data, list) else data
    if not isinstance(row, dict) or not row.get('shape'):
        continue
    variant = row['variant']
    spec = '_'.join(map(str, row['shape'] + [row['dtype'], row['ta'], row['tb']]))
    item = {
        'file': filename.name, 'variant': variant, 'spec': spec,
        'passed': row.get('passed'), 'returncode': row.get('returncode'),
        'maxrel': row.get('maxrel'), 'tasks': row.get('tasks'),
        'warm_us': statistics.median(row['all_us'][-60:]) if row.get('all_us') else None,
    }
    profile_root = root / 'variants' / variant / 'research/PipeUtilization' / spec
    files = sorted(profile_root.glob('profile/PROF_*/mindstudio_profiler_output/op_summary_*.csv'))
    if files:
        with files[-1].open() as f:
            rows = list(csv.DictReader(f))[-60:]
        metrics = {}
        for key in pipe_keys:
            try:
                metrics[key] = statistics.median(float(r[key]) for r in rows)
            except (KeyError, ValueError, statistics.StatisticsError):
                pass
        item['pipes'] = metrics
    baseline_file = root / 'variants/clean93/research/PipeUtilization' / spec / 'output/y.bin'
    variant_file = profile_root / 'output/y.bin'
    if baseline_file.exists() and variant_file.exists():
        item['output_bitwise_equal_to93'] = bool(np.array_equal(
            np.fromfile(baseline_file, np.uint32), np.fromfile(variant_file, np.uint32)))
    records.append(item)

result = {'scope': 'user-supplied 15 shapes only; zero OJ submissions', 'records': records}
(root / 'c33/collected_evidence.json').write_text(json.dumps(result, indent=2) + '\n')
for row in records:
    print(json.dumps({key: row[key] for key in [
        'variant', 'spec', 'warm_us', 'passed', 'returncode',
    ]} | {'bitwise_equal_to93': row.get('output_bitwise_equal_to93'), 'pipes': row.get('pipes')}))
