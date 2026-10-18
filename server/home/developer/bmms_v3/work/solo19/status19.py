from pathlib import Path
import json,sys
r=Path('/home/developer/bmms_v3');letter=sys.argv[1]
assert len(letter)==1 and letter.isalpha()
for label in ([f'pilot19_{letter}_l_base',f'pilot19_base_l_{letter}'] if letter!='h' else ['pilot19_h_f_base','pilot19_base_f_h']):
    p=r/'solo17_data'/label/'results.jsonl'
    if not p.exists():continue
    rows=[json.loads(x) for x in p.read_text().splitlines() if x.startswith('{')]
    print(label,'records',len(rows))
    for x in rows:
        if x['shape']==[1,1280,4096,1536]:
            print(x['variant'],x['spec'],x['total_warm_us'])
