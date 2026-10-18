"""Reproduce the FP64-golden regression with one ACL context.

Build bench_cases first with the accompanying CMakeLists.txt, then run this file.
Each case is executed three times; the executable verifies bitwise consistency.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--executable', default='build/bench_cases')
    args = parser.parse_args()
    os.chdir(Path(__file__).resolve().parent)
    subprocess.run([sys.executable, 'gen_cases.py'], check=True)
    executable = Path(args.executable).resolve()
    proc = subprocess.run([str(executable), str(Path('cases.txt').resolve())],
                          capture_output=True, text=True, timeout=600)
    Path('precision.log').write_text(proc.stdout + proc.stderr)
    rows = [json.loads(line) for line in proc.stdout.splitlines() if line.startswith('{')]
    Path('test_results.json').write_text(json.dumps(rows, indent=2) + '\n')
    expected = len(Path('cases.txt').read_text().splitlines())
    if proc.returncode or len(rows) != expected or not all(
            row['passed'] and row['consistent'] for row in rows):
        print((proc.stdout + proc.stderr)[-4000:])
        raise SystemExit(proc.returncode or 1)
    print(f'PASS: {len(rows)} cases, 3 identical executions each')


if __name__ == '__main__':
    main()
