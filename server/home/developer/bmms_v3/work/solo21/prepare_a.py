from pathlib import Path
import json
r=Path(__file__).resolve().parents[2];w=r/'work/solo21';old=r/'work/solo20'
sha=json.loads((w/'source_a.json').read_text())['sha256']
s=(old/'compile_f.sh').read_text().replace('s20f','s21a').replace('solo20','solo21').replace('diagnostic_20f','diagnostic_21a').replace('compiler20_f','compiler21_a').replace('198ee0bb6eca5a4503e734438da20f05a4ad962e5c7d53976b84552190b09f3c',sha)
(w/'compile_a.sh').write_bytes(s.encode())
s=(old/'run_f_final.py').read_text().replace('s20f','s21a').replace('diagnostic_20f','diagnostic_21a').replace('hangs20_f','hangs21_a').replace('198ee0bb6eca5a4503e734438da20f05a4ad962e5c7d53976b84552190b09f3c',sha)
# Preserve a complete runner for use after evaluating the pilot, without rerunning diagnostics.
idx=s.index('for command in [')
full='from pathlib import Path\nimport subprocess,hashlib,json\nr=Path("/home/developer/bmms_v3");v="s21a"\n'
full+=f'assert hashlib.sha256((r/"variants/s21a/kernel.asc").read_bytes()).hexdigest()=="{sha}"\n'
full+='p=json.loads((r/"solo17_data/diagnostic_21a/summary.json").read_text());assert sum(x["observed"] for x in p)==648 and all(x["passed"] for x in p)\n'
full+=s[idx:]
(w/'run_a_final.py').write_bytes(full.encode())
pilot=s[:idx]+'''specs=['1_512_512_8192_1_0_0','1_1024_1024_8192_1_0_0','1_1024_1024_4096_2_1_1','1_2048_512_8192_1_0_0']
for label,variants in [('pilot21_a_f_base','s21a,s20f,s15i'),('pilot21_base_f_a','s15i,s20f,s21a')]:
    p=subprocess.run(['python3',str(r/'work/solo17/scan.py'),label,variants,*specs])
    if p.returncode:raise SystemExit(p.returncode)
print('PASS pilot only; not submission ready.',flush=True)
'''
(w/'run_a_pilot.py').write_bytes(pilot.encode())
# Template archival/verification logic is unchanged except for the round, variant and source hash.
for src,dst in [('collect20.py','collect21.py'),('unpack20.py','unpack21.py'),('download20.ps1','download21.ps1'),('verify20_f_final.py','verify21_a_final.py')]:
    s=(old/src).read_text().replace('s20f','s21a').replace('20f','21a').replace('round20','round21').replace('solo20','solo21').replace('bmms20','bmms21').replace('run20_','run21_').replace('hangs20_f','hangs21_a').replace('remote_round21_f_final','remote_round21_a_final').replace('198ee0bb6eca5a4503e734438da20f05a4ad962e5c7d53976b84552190b09f3c',sha).replace('unpack20.py','unpack21.py')
    (w/dst).write_bytes(s.encode())
print('Prepared offline compile, diagnostic pilot, full runner, immutable collection and verification.')
