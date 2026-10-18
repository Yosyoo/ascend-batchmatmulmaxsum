#!/usr/bin/env python3
"""Shape x variant sweep for BatchMatmulMaxSum using the fast in-process bench.

Usage (on server):
  python3 sweep.py --variants baseline,conservative,final,balanced --shapes all
  python3 sweep.py --variants balanced --shapes 1_8192_64_128
"""
import argparse, json, os, shutil, subprocess, sys, time
from pathlib import Path

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
import numpy as np
from ml_dtypes import bfloat16

ROOT = Path('/home/developer/bmms_opt')
HERE = Path(__file__).resolve().parent
WORK = ROOT / 'sweepdata'

# (B, M, N, K)
FAMILY_A = [   # n<=64, k<=128, m>=256  -> tileM=256 branch
    (1, 8192, 64, 128), (1, 4096, 64, 128), (1, 16384, 64, 64),
    (1, 8192, 32, 64), (2, 8192, 64, 128), (4, 4096, 64, 128),
    (1, 2048, 64, 128), (1, 32768, 64, 128), (1, 8192, 64, 32),
    (1, 6144, 48, 96), (1, 12288, 64, 128), (8, 2048, 64, 64),
]
FAMILY_B = [   # n>128 -> tileN=256 branch
    (1, 1024, 1024, 1024), (1, 512, 512, 512), (1, 256, 4096, 1024),
    (1, 2048, 2048, 1024), (1, 1024, 4096, 2048), (1, 512, 8192, 512),
    (1, 128, 8192, 1024), (1, 2048, 512, 512), (1, 4096, 1024, 512),
    (1, 1024, 2048, 4096), (2, 1024, 1024, 1024), (1, 768, 3072, 768),
    (1, 1024, 1536, 1536), (1, 3072, 768, 768),
]
FAMILY_C = [   # existing local bench shapes + odd tails
    (1, 31, 513, 8192), (1, 8192, 17, 32), (1, 16, 8192, 64),
    (4, 256, 256, 128), (1, 65, 129, 128), (2, 129, 257, 256),
    (1, 8191, 33, 72), (1, 511, 64, 128), (1, 511, 512, 128),
    (1, 8191, 512, 128), (1, 256, 256, 8192), (1, 8192, 64, 8192),
    (1, 33, 8192, 64), (1, 64, 8192, 64), (1, 128, 8192, 64),
    (1, 8192, 128, 64), (1, 8192, 129, 64), (1, 256, 1024, 2048),
]
ALL_SHAPES = FAMILY_A + FAMILY_B + FAMILY_C


def random_shapes(count, seed=777):
    """Biased random shapes aimed at the tile-enlargement conditions."""
    rng = np.random.default_rng(seed)
    ms = [1, 7, 15, 16, 17, 31, 32, 33, 48, 63, 64, 65, 96, 127, 128, 129, 192,
          255, 256, 257, 384, 511, 512, 513, 768, 1023, 1024, 1025, 1536, 2048,
          3072, 4096, 6144, 8191, 8192, 8193, 12288, 16384, 32768]
    ns_ = [1, 7, 15, 16, 17, 31, 32, 33, 48, 63, 64, 65, 96, 127, 128, 129, 192,
           255, 256, 257, 384, 511, 512, 513, 768, 1024, 1025, 1536, 2048, 3072,
           4096, 8191, 8192, 8193, 16384]
    ks = [1, 2, 3, 7, 8, 15, 16, 31, 32, 33, 63, 64, 65, 96, 127, 128, 129, 192,
          255, 256, 257, 384, 512, 768, 1024, 1536, 2048, 3072, 4096, 8192, 16384]
    bs = [1, 1, 1, 1, 2, 2, 3, 4, 8, 16]
    out, seen = [], set()
    budget = 3.0e8  # cap on b*m*k and b*n*k elements (x2 bytes)
    guard = 0
    while len(out) < count and guard < count * 400:
        guard += 1
        B = int(rng.choice(bs))
        M = int(rng.choice(ms))
        N = int(rng.choice(ns_))
        K = int(rng.choice(ks))
        if B * M * K > budget or B * N * K > budget or B * M * N > 4.0e8:
            continue
        if (B, M, N, K) in seen:
            continue
        seen.add((B, M, N, K))
        out.append((B, M, N, K))
    return out


def parse_shape(text):
    return tuple(int(x) for x in text.split('_'))


def build(variant):
    src = ROOT / variant
    bdir = WORK / variant
    bdir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src / 'kernel.asc', bdir / 'kernel.asc')
    # data_utils.h is identical across variants; fall back to a sibling that has it.
    du = src / 'data_utils.h'
    if not du.exists():
        for alt in ROOT.iterdir():
            if (alt / 'data_utils.h').exists():
                du = alt / 'data_utils.h'
                break
    shutil.copy2(du, bdir / 'data_utils.h')
    shutil.copy2(HERE / 'bench.asc', bdir / 'bench.asc')
    shutil.copy2(HERE / 'CMakeLists.txt', bdir / 'CMakeLists.txt')
    exe = bdir / 'build' / 'bench'
    # Rebuild whenever bench.asc / kernel.asc / CMakeLists.txt change.
    import hashlib
    h = hashlib.sha256()
    for f in ('bench.asc', 'kernel.asc', 'data_utils.h', 'CMakeLists.txt'):
        h.update((bdir / f).read_bytes())
    stamp = h.hexdigest()
    marker = bdir / '.built'
    if marker.exists() and exe.exists() and marker.read_text().strip() == stamp:
        return exe
    if (bdir / 'build').exists():
        shutil.rmtree(bdir / 'build')
    env = dict(os.environ)
    r = subprocess.run(['cmake', '-S', str(bdir), '-B', str(bdir / 'build')],
                       capture_output=True, text=True, env=env)
    if r.returncode:
        print(r.stdout, r.stderr, file=sys.stderr)
        raise RuntimeError(f'cmake failed for {variant}')
    r = subprocess.run(['cmake', '--build', str(bdir / 'build'), '-j8'],
                       capture_output=True, text=True, env=env)
    if r.returncode:
        print(r.stdout, r.stderr, file=sys.stderr)
        raise RuntimeError(f'build failed for {variant}')
    marker.write_text(stamp)
    return exe


def make_input(shape, dtype):
    B, M, N, K = shape
    rng = np.random.default_rng(20261003)
    typ = np.float16 if dtype == 1 else bfloat16
    a = rng.uniform(-1, 1, (B, M, K)).astype(typ)
    b = rng.uniform(-1, 1, (B, K, N)).astype(typ)
    golden = (a.astype(np.float64) @ b.astype(np.float64)).max(-1).sum(-1).astype(np.float32)
    d = WORK / 'input' / '_'.join(map(str, shape))
    (d / 'input').mkdir(parents=True, exist_ok=True)
    (d / 'output').mkdir(parents=True, exist_ok=True)
    a.tofile(d / 'input' / 'x1.bin')
    b.tofile(d / 'input' / 'x2.bin')
    return d, golden


def run_one(exe, shape, dtype, ta, tb, iters, rounds):
    B, M, N, K = shape
    d, golden = make_input(shape, dtype)
    cmd = [str(exe), *map(str, shape), str(dtype), str(ta), str(tb), str(iters), str(rounds)]
    p = subprocess.run(cmd, capture_output=True, text=True, cwd=d, timeout=600)
    if p.returncode == 2:
        return {'error': 'nondeterministic'}
    if p.returncode:
        return {'error': (p.stdout + p.stderr)[-400:]}
    line = [l for l in p.stdout.strip().splitlines() if l.startswith('{')]
    if not line:
        return {'error': 'no output: ' + p.stdout[-300:]}
    res = json.loads(line[-1])
    y = np.fromfile(d / 'output' / 'y.bin', np.float32)
    ok = y.shape == golden.shape and np.isfinite(y).all() and np.allclose(y, golden, atol=1e-4, rtol=1e-4)
    rel = float(np.max(np.abs(y - golden) / np.maximum(np.abs(golden), 1e-5))) if y.shape == golden.shape else float('inf')
    res['passed'] = bool(ok)
    res['relative'] = rel
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--variants', default='baseline,conservative,final,balanced')
    ap.add_argument('--shapes', default='all')
    ap.add_argument('--dtype', type=int, default=1)
    ap.add_argument('--ta', type=int, default=0)
    ap.add_argument('--tb', type=int, default=0)
    ap.add_argument('--iters', type=int, default=20)
    ap.add_argument('--rounds', type=int, default=5)
    ap.add_argument('--out', default='')
    ap.add_argument('--random', type=int, default=0)
    ap.add_argument('--seed', type=int, default=777)
    args = ap.parse_args()

    variants = [v for v in args.variants.split(',') if v]
    if args.shapes == 'all':
        shapes = ALL_SHAPES
    elif args.shapes.startswith('A'):
        shapes = FAMILY_A
    elif args.shapes.startswith('B'):
        shapes = FAMILY_B
    elif args.shapes.startswith('C'):
        shapes = FAMILY_C
    elif args.shapes == 'random':
        shapes = random_shapes(args.random or 60, args.seed)
    else:
        shapes = [parse_shape(s) for s in args.shapes.split(',')]

    WORK.mkdir(parents=True, exist_ok=True)
    exes = {v: build(v) for v in variants}

    rows = []
    for shape in shapes:
        row = {'shape': list(shape)}
        for v in variants:
            t0 = time.time()
            r = run_one(exes[v], shape, args.dtype, args.ta, args.tb, args.iters, args.rounds)
            r['wall'] = round(time.time() - t0, 1)
            row[v] = r
            print(json.dumps({'shape': list(shape), 'variant': v,
                              'min': r.get('min'), 'median': r.get('median'),
                              'rounds': r.get('rounds'), 'passed': r.get('passed'),
                              'rel': r.get('relative'), 'error': r.get('error')}), flush=True)
        base = row[variants[0]].get('min')
        for v in variants[1:]:
            cur = row[v].get('min')
            row[v]['ratio'] = round(cur / base, 4) if base and cur else None
        rows.append(row)
        if args.out:
            Path(args.out).write_text(json.dumps(rows, indent=1))
    print('DONE', flush=True)


if __name__ == '__main__':
    main()
