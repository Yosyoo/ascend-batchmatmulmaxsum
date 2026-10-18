#!/usr/bin/env python3
"""Shape benchmark driver for BatchMatmulMaxSum variants.

Usage:
  python3 measure.py <variant> <mode> <shape_spec...>
    variant : directory name under variants/ (must contain kernel.asc, built build/bench)
    mode    : msprof | event
    shape   : B_M_N_K[_dtype_ta_tb]

Prints one JSON line per (variant, shape, layout).
"""
import csv
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
import numpy as np
from ml_dtypes import bfloat16

R = Path("/home/developer/bmms_v3/harness")
VAR = Path(os.environ.get('VARIANTS_ROOT', str(R.parent / 'variants')))


def gen_data(d, B, M, N, K, dtype, ta, tb, seed=191726):
    (d / 'input').mkdir(parents=True, exist_ok=True)
    (d / 'output').mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    typ = np.float16 if dtype == 1 else bfloat16
    a = rng.uniform(-1, 1, (B, M, K)).astype(typ)
    b = rng.uniform(-1, 1, (B, K, N)).astype(typ)
    af = a.astype(np.float64)
    bf = b.astype(np.float64)
    gold = (af @ bf).max(-1).sum(-1).astype(np.float32)
    (a.transpose(0, 2, 1) if ta else a).copy().tofile(d / 'input/x1.bin')
    (b.transpose(0, 2, 1) if tb else b).copy().tofile(d / 'input/x2.bin')
    np.save(d / 'gold.npy', gold)
    return gold


def parse_shape(spec):
    p = spec.split('_')
    B, M, N, K = (int(x) for x in p[:4])
    dtype = int(p[4]) if len(p) > 4 else 1
    ta = int(p[5]) if len(p) > 5 else 0
    tb = int(p[6]) if len(p) > 6 else 0
    return B, M, N, K, dtype, ta, tb


def run_shape(variant, spec, mode, iters, rounds, device):
    B, M, N, K, dtype, ta, tb = parse_shape(spec)
    vd = VAR / variant
    work = vd / 'research' / os.environ.get('AIC_METRIC','Memory') / spec
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)
    gold = gen_data(work, B, M, N, K, dtype, ta, tb)
    cmd = [str(vd / 'build/bench'), str(B), str(M), str(N), str(K), str(dtype), str(ta), str(tb),
           str(iters), str(rounds)]
    row = {'variant': variant, 'shape': [B, M, N, K], 'dtype': dtype, 'ta': ta, 'tb': tb}
    if mode == 'msprof':
        env = dict(os.environ)
        env['BMMS_DEVICE_ID'] = str(device)
        p = subprocess.run(['msprof', '--application=' + ' '.join(cmd),
                            '--output=' + str(work / 'profile'),
                            '--aic-metrics=' + os.environ.get('AIC_METRIC','Memory'), '--task-time=on'],
                           cwd=work, capture_output=True, text=True, timeout=900, env=env)
        (work / 'msprof.log').write_text(p.stdout + p.stderr)
        files = sorted((work / 'profile').glob('PROF_*/mindstudio_profiler_output/op_summary_*.csv'))
        if not files:
            row['error'] = (p.stdout + p.stderr)[-800:]
            return row
        rows = list(csv.DictReader(files[-1].open()))
        times = [float(x['Task Duration(us)']) for x in rows]
        core = times[3:] if len(times) > 3 else times
        row['tasks'] = len(times)
        row['median_us'] = float(np.median(core))
        row['mean_us'] = float(np.mean(core))
        row['min_us'] = float(np.min(core))
        row['all_us'] = [round(t, 3) for t in times]
    else:
        env = dict(os.environ)
        env['BMMS_DEVICE_ID'] = str(device)
        p = subprocess.run(cmd, cwd=work, capture_output=True, text=True, timeout=900, env=env)
        (work / 'bench.log').write_text(p.stdout + p.stderr)
        lines = [l for l in p.stdout.splitlines() if l.startswith('{')]
        if not lines:
            row['error'] = (p.stdout + p.stderr)[-800:]
            return row
        j = json.loads(lines[-1])
        row.update(j)
        row['median_us'] = j['median']
    row['returncode'] = p.returncode
    yf = work / 'output/y.bin'
    if yf.exists():
        y = np.fromfile(yf, np.float32)
        if y.size == gold.size:
            row['passed'] = bool(np.allclose(y, gold, rtol=1e-4, atol=1e-4))
            row['maxrel'] = float(np.max(np.abs(y - gold) / np.maximum(np.abs(gold), 1e-5)))
        else:
            row['passed'] = False
            row['error'] = 'size mismatch %d vs %d' % (y.size, gold.size)
    return row


def main():
    variant = sys.argv[1]
    mode = sys.argv[2]
    specs = sys.argv[3:]
    iters = int(os.environ.get('ITERS', '20'))
    rounds = int(os.environ.get('ROUNDS', '5'))
    device = int(os.environ.get('BMMS_DEVICE_ID', '0'))
    out = []
    for spec in specs:
        row = run_shape(variant, spec, mode, iters, rounds, device)
        print(json.dumps(row), flush=True)
        out.append(row)
        Path(os.environ.get('RESULT', str(R / 'last_results.json'))).write_text(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
