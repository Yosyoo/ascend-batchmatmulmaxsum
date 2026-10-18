from pathlib import Path
import hashlib
r=Path(__file__).resolve().parents[2];w=r/'work/solo20'
sha=hashlib.sha256((r/'variants/s20a/kernel.asc').read_bytes()).hexdigest()
assert sha=='b4141a3e0bd792a6f953454924af68bcb4e49e7b195c4f74892b98de8d162f6c'
s=(r/'work/solo19/run_i_final.py').read_text(encoding='utf8').replace('s19i','s20a').replace('diagnostic_19i','diagnostic_20a').replace('hangs19_i','hangs20_a')
s=s.replace("hashes={p.name:","assert hashlib.sha256(src.read_bytes()).hexdigest()=='"+sha+"'\nhashes={p.name:")
(w/'run_a_final.py').write_bytes(s.encode())
s=(w/'compile_a.sh').read_text(encoding='utf8')
s=s.replace("cmake --build variants/s20a/build -j2 >>variants/s20a/build.log 2>&1'", "cmake --build variants/s20a/build -j2 >>variants/s20a/build.log 2>&1 && python3 work/solo20/run_a_final.py >solo17_data/run20_a_final.log 2>&1'")
s=s.replace('COMPILE ONLY PID','COMPILE AND FINAL PID')
s=s.replace('test ! -d variants/s20a/build','flock -n solo17_data/.npu_serial.lock true\ntest ! -d variants/s20a/build\ntest ! -d solo17_data/diagnostic_20a')
(w/'launch_a.sh').write_bytes(s.encode())
# Reuse rigorously checked raw verifier, only change concrete variant and evidence path.
s=(r/'work/solo19/verify19_i_final.py').read_text(encoding='utf8')
for old,new in [('s19i','s20a'),('remote_round19_i_final','remote_round20_a_final'),('diagnostic_19i','diagnostic_20a'),('hangs19_i','hangs20_a'),('delivery_round19','delivery_round20'),('314d61425771496515f98d3668d9559af1d6fcdab9df2e04f0a6dcc86e103a7f',sha)]:
    assert old in s,old;s=s.replace(old,new)
(w/'verify20_a_final.py').write_bytes(s.encode())
s=(r/'work/solo19/submission_gate.py').read_text(encoding='utf8').replace("v.startswith('s19')","v.startswith('s20')").replace('delivery_round19','delivery_round20')
(w/'submission_gate.py').write_text(s,encoding='utf8')
s=(r/'work/solo19/collect19.py').read_text(encoding='utf8').replace('bmms19_','bmms20_').replace('work/solo19','work/solo20').replace('run19_','run20_')
(w/'collect20.py').write_bytes(s.encode())
s=(r/'work/solo19/unpack19.py').read_text(encoding='utf8').replace('bmms19_','bmms20_').replace('round19_','round20_')
(w/'unpack20.py').write_text(s,encoding='utf8')
s=(r/'work/solo19/download19.ps1').read_text(encoding='utf8').replace('bmms19_','bmms20_').replace('round19_','round20_').replace('unpack19.py','unpack20.py')
(w/'download20.ps1').write_text(s,encoding='utf8')
print('Prepared compile+full diagnostics/precision100pool6hangs, raw verifiers and rejection gate. No official submission.')
