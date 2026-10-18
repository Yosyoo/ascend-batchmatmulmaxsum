from pathlib import Path
import subprocess,hashlib,sys
r=Path('/home/developer/bmms_v3');v=sys.argv[1];sha=sys.argv[2]
assert v.startswith('s28') and hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
commands=[['python3',str(r/'work/solo28/diagnostic.py'),v,sha],['python3',str(r/'work/solo17/validate.py'),v]]
for cmd in commands:
 p=subprocess.run(cmd)
 if p.returncode:raise SystemExit(p.returncode)
print('PASS28_FULL_PRECISION '+v+' diagnostics648 + full18378; no automatic official submission',flush=True)
