import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import json
import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path('/home/developer/bmms_v3/harness')))
from measure import run_shape

variants = sys.argv[1].split(',')
specs = sys.argv[2:]
path = Path('/home/developer/bmms_v3') / ('solo6_scan_' + '_'.join(variants) + '.jsonl')
with path.open('w') as f:
    for variant in variants:
        for spec in specs:
            x = run_shape(variant, spec, 'msprof', 160, 1, 0)
            f.write(json.dumps(x) + '\n'); f.flush()
            concise = {k: v for k, v in x.items() if k != 'all_us'}
            if 'all_us' in x:
                concise['warm_tail'] = statistics.median(x['all_us'][-80:])
            print(json.dumps(concise), flush=True)
