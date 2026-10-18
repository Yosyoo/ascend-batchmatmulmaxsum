from pathlib import Path
r=Path(__file__).resolve().parents[2];w=r/'work/solo23';dst=w/'probe';dst.mkdir(exist_ok=False)
s=(r/'work/solo22/probe_fulla/tiling_pair_probe.asc').read_text()
assert s.count('128*128*4+32768')==1
s=s.replace('128*128*4+32768','2*128*64*4+32768')
(dst/'tiling_pair_probe.asc').write_bytes(s.encode())
(dst/'CMakeLists.txt').write_bytes((r/'work/solo22/probe_fulla/CMakeLists.txt').read_bytes())
(w/'probe.sh').write_bytes((r/'work/solo22/probe_fulla.sh').read_text().replace('solo22/probe_fulla','solo23/probe').encode())
print('Prepared SDK resource audit before source edit: 200 NN shapes, two64-column AIV inputs instead of one128-column input.')
