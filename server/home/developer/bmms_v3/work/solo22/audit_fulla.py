from pathlib import Path
import hashlib,json,subprocess
r=Path('/home/developer/bmms_v3');d=r/'solo17_data'
expected={'s15i':'b67d45e1b270ad416e403cd18a7e9f0cd06341f26e8e734f1dee4fdc8e37c4f6',
          's17l':'4d979aa725dfbedbd60b64000ff2c97b274b084976352d3678ed6a397a84b368',
          's21d':'00601d4b917ad487200cc7907e6a6adfdbf76d9a820bb8a8e6c47df56f2c272d'}
assert (d/'baseline_bf16_22/summary.json').exists()
for v,h in expected.items():assert hashlib.sha256((r/'variants'/v/'kernel.asc').read_bytes()).hexdigest()==h
specs=['1_1024_1024_1152_1_0_0','1_1024_1024_1152_2_0_0',
       '1_2048_2048_1536_1_0_0','1_2048_2048_1536_2_0_0',
       '1_1024_1024_1152_1_0_1','1_1024_1024_1152_2_0_1']
for label,variants in [('pilot22_fulla_forward','s21d,s17l,s15i'),('pilot22_fulla_reverse','s15i,s17l,s21d')]:
    p=subprocess.run(['python3',str(r/'work/solo17/scan.py'),label,variants,*specs])
    if p.returncode:raise SystemExit(p.returncode)
for v,h in expected.items():assert hashlib.sha256((r/'variants'/v/'kernel.asc').read_bytes()).hexdigest()==h
print('PASS FullA scope audit only; no official submission authorized by this audit.',flush=True)
