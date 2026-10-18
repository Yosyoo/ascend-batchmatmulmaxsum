from pathlib import Path
import subprocess
r=Path('/home/developer/bmms_v3')
commands=[['python3',str(r/'work/solo17/validate.py'),'s17l']]
specs=['1_1280_4096_1536_1_0_0','1_1280_4096_1536_1_1_0','1_1280_4096_1536_2_0_1','1_1280_4096_1536_2_1_1']
for label,variants in [('pilot_l_base','s17l,s15i'),('pilot_base_l','s15i,s17l')]:
    commands.append(['python3',str(r/'work/solo17/scan.py'),label,variants,*specs])
commands.append(['python3',str(r/'work/solo18/pool18.py'),'s17l'])
hangs=['1_4096_4096_1024','1_8192_512_1024','1_4096_1024_512','1_2048_2048_1024','1_8192_256_512','2_4096_2048_512']
commands.append(['python3',str(r/'work/solo17/scan.py'),'hangs18_l','s17l',*hangs])
for command in commands:
    p=subprocess.run(command)
    if p.returncode:raise SystemExit(p.returncode)
print('PASS s17l final precision, exchanged pilots,100-pool and six hangs',flush=True)
