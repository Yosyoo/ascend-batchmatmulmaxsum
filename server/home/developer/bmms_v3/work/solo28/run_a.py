from pathlib import Path
import subprocess,hashlib,json
r=Path('/home/developer/bmms_v3');v='s28a';d=r/'solo17_data'
sha='78cf3efd9360610eb1e23edea66e7ac0195d9200b97f2f1b95a81914e4316513'
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
commands=[['python3',str(r/'work/solo28/diagnostic.py'),v,sha],['python3',str(r/'work/solo17/validate.py'),v]]
for cmd in commands:
 p=subprocess.run(cmd)
 if p.returncode:raise SystemExit(p.returncode)
print('PASS28A_FULL_PRECISION diagnostics648 + full18378; no automatic official submission',flush=True)
