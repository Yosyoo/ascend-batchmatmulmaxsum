from pathlib import Path
import subprocess,hashlib,json
r=Path("/home/developer/bmms_v3");v="s21d"
assert hashlib.sha256((r/"variants/s21d/kernel.asc").read_bytes()).hexdigest()=="00601d4b917ad487200cc7907e6a6adfdbf76d9a820bb8a8e6c47df56f2c272d"
p=json.loads((r/"solo17_data/diagnostic_21d/summary.json").read_text());assert sum(x["observed"] for x in p)==648 and all(x["passed"] for x in p)
for command in [
    ['python3',str(r/'work/solo17/validate.py'),v],
    ['python3',str(r/'work/solo18/pool18.py'),v],
    ['python3',str(r/'work/solo17/scan.py'),'hangs21_d',v,
        '1_4096_4096_1024','1_8192_512_1024','1_4096_1024_512',
        '1_2048_2048_1024','1_8192_256_512','2_4096_2048_512']]:
    p=subprocess.run(command)
    if p.returncode:raise SystemExit(p.returncode)
print('PASS s21d complete648,18378,100pool,six hangs; official requires raw evidence and submission gate.',flush=True)
