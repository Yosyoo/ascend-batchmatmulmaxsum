import sys, json, subprocess, os
from pathlib import Path
os.environ['VARIANTS_ROOT'] = '/home/developer/bmms_v3/variants'
sys.path.insert(0, '/home/developer/bmms_v3/harness')
from measure import run_shape
v = sys.argv[1]; spec = sys.argv[2]
r = run_shape(v, spec, 'event', 1, 1, 0)
print(v, spec, 'median=', r.get('median'), 'passed=', r.get('passed'), 'err=', str(r.get('error',''))[:120].replace('\n',' '))
