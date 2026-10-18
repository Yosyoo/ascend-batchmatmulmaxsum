from pathlib import Path
import subprocess,json,hashlib,fcntl
r=Path('/home/developer/bmms_v3');d=r/'solo17_data';v='s47a';sha='93432404a2c1676eb8f572237fb11f3f65dc9e07da6c8079402f8556a9c014f6'
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
def run(args):subprocess.run(args,cwd=r,check=True)
manifest=d/'bounds45.txt';exe=r/f'variants/{v}/build/bench_cases'
lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
p=subprocess.run([str(exe),str(manifest)],cwd=r,capture_output=True,text=True,timeout=300)
(d/'bounds47_s47a.log').write_text(p.stdout+p.stderr);rows=[json.loads(l) for l in p.stdout.splitlines() if l.startswith('{')]
fcntl.flock(lock,fcntl.LOCK_UN);lock.close()
assert p.returncode==0 and len(rows)==128 and all(x['passed'] and x['consistent'] for x in rows)
print('BOUNDS47_A_PASS128',flush=True)
with (d/'compile45_s47a_bench.log').open('w') as log:
    build=subprocess.Popen(['cmake','--build',f'variants/{v}/build','--target','bench','-j1'],cwd=r,stdout=log,stderr=subprocess.STDOUT)
    run(['python3','work/solo17/validate.py',v])
    run(['python3','work/solo28/run_stress.py',v,sha])
    run(['python3','work/solo42/extra_precision.py',v,sha])
    out=d/'new_precision45_s47a';out.mkdir(exist_ok=False)
    manifest=d/'diagnostic42_s41c/cases.txt';exe=r/f'variants/{v}/build/bench_cases'
    lock=(d/'.npu_serial.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
    p=subprocess.run([str(exe),str(manifest)],cwd=r,capture_output=True,text=True,timeout=600)
    (out/'precision.log').write_text(p.stdout+p.stderr);rows=[json.loads(l) for l in p.stdout.splitlines() if l.startswith('{')]
    good=p.returncode==0 and len(rows)==656 and all(z['passed'] and z['consistent'] for z in rows)
    (out/'summary.json').write_text(json.dumps(dict(variant=v,passed=good,expected=656,observed=len(rows),manifest=str(manifest),manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest(),failures=[z for z in rows if not z['passed'] or not z['consistent']]),indent=2))
    fcntl.flock(lock,fcntl.LOCK_UN);lock.close();assert good
    print('NEW_PRECISION47_A_PASS',len(rows),flush=True)
    assert build.wait()==0
run(['python3','work/solo28/pool_compare.py',v,'s46a','pool47_a_45c_abba'])
run(['python3','work/solo17/scan.py','hangs47_a',v,'1_4096_4096_1024','1_8192_512_1024','1_4096_1024_512','1_2048_2048_1024','1_8192_256_512','2_4096_2048_512'])
assert hashlib.sha256((r/f'variants/{v}/kernel.asc').read_bytes()).hexdigest()==sha
print('FINAL47_A_COMPLETE_NO_AUTOMATIC_SUBMISSION',flush=True)
