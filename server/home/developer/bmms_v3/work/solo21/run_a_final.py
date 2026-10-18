from pathlib import Path
import subprocess,hashlib,json
r=Path("/home/developer/bmms_v3");v="s21a"
assert hashlib.sha256((r/"variants/s21a/kernel.asc").read_bytes()).hexdigest()=="0bced8bd0556b8d2bde4055a94e981f9dd95e7f1bffb3f101b2b94f501cc6dc4"
p=json.loads((r/"solo17_data/diagnostic_21a/summary.json").read_text());assert sum(x["observed"] for x in p)==648 and all(x["passed"] for x in p)
for command in [
    ['python3',str(r/'work/solo17/validate.py'),v],
    ['python3',str(r/'work/solo18/pool18.py'),v],
    ['python3',str(r/'work/solo17/scan.py'),'hangs21_a',v,
        '1_4096_4096_1024','1_8192_512_1024','1_4096_1024_512',
        '1_2048_2048_1024','1_8192_256_512','2_4096_2048_512']]:
    p=subprocess.run(command)
    if p.returncode:raise SystemExit(p.returncode)
print('PASS s21a complete648,18378,100pool,six hangs; official requires raw evidence and submission gate.',flush=True)
