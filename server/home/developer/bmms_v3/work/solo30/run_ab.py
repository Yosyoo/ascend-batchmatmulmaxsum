from pathlib import Path
import subprocess
r=Path('/home/developer/bmms_v3')
for v,sha in [('s30a','92bbac2006f1fa6df22114d14f2f2b1914abb2add7103415c213a0ad8c36482a'),('s30b','277434e25e6353ef8a695544253cf43c2eced14b97e3cfe9c5dbe03ab5878a34')]:
 print('SCREEN_START',v,flush=True)
 code=subprocess.call(['python3','work/solo30/screen.py',v,sha],cwd=r)
 print('SCREEN_EXIT',v,code,flush=True)
print('ROUND30_AB_COMPLETE',flush=True)
