from pathlib import Path
import json
r=Path(__file__).resolve().parents[2];w=Path(__file__).parent
g=(r/'work/solo41/gen_stress.py').read_text()
g=g.replace('owned_stress41','a2_stress42').replace('2026101541','2026101542')
g=g.replace('[(16,256,256,256),(20,256,128,512),(32,256,256,512),(16,512,256,512),(21,256,128,512)]','[(1,1024,1024,256),(1,4096,1024,256),(1,1024,4096,256),(4,512,1024,256),(16,256,1024,256)]')
(w/'gen_stress.py').write_text(g,encoding='utf-8',newline='\n')
shapes=['1 2048 1024 256','1 4096 1024 256','1 2048 4096 256','4 512 1024 256','16 256 1024 256']
(w/'shapes_a.txt').write_text('\n'.join(shapes)+'\n',encoding='utf-8',newline='\n')
s=(r/'work/solo41/screen_d.py').read_text()
s=s.replace("v='s41d'","v='s42a'").replace("d/'owned_stress41.txt']","d/'owned_stress41.txt',d/'a2_stress42.txt']")
s=s.replace("('fail_8.txt','owned_stress41.txt')","('fail_8.txt','owned_stress41.txt','a2_stress42.txt')")
s=s.replace("diagnostic41_","diagnostic42_").replace("PRECISION41_D","PRECISION42_A")
s=s.replace("timeout=900","timeout=180")
s=s[:s.index("for base in ('s41c','s33a'):")]+'''for ta,tb in ((0,0),(0,1),(1,0),(1,1)):
 subprocess.run(['python3','work/solo31/quick_layout_compare.py',v,'s41c',f'quick42_a_{ta}{tb}','work/solo42/shapes_a.txt','1',str(ta),str(tb)],cwd=r,check=True)
 if ta==0 and tb==0:
  comparison=json.loads((d/'quick42_a_00/comparison.json').read_text())
  left,right=comparison['orders'];wins=[x['shape'] for x,y in zip(left['ratios'],right['ratios']) if x['ratio']<.97 and y['ratio']<.97]
  print('WINNING_SHAPES42_A',wins,flush=True)
  if not wins:break
print('SCREEN42_A_COMPLETE',flush=True)
'''
(w/'screen_a.py').write_text(s,encoding='utf-8',newline='\n')
print(json.dumps({'new_validation_cases':160,'precision_screen_cases':656,'shapes':shapes,'performance':'160 calls, last80 median, ABBA; expand layouts only if NN stable winner'}))
