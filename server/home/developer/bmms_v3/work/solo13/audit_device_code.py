"""Read-only ELF section comparison; no NPU execution or test data access."""
import struct,json,hashlib
from pathlib import Path
root=Path('/home/developer/bmms_v3')

def sections(data):
 assert data[:6]==b'\x7fELF\x02\x01'
 shoff=struct.unpack_from('<Q',data,40)[0]
 size,num,strings=struct.unpack_from('<HHH',data,58)
 headers=[struct.unpack_from('<IIQQQQIIQQ',data,shoff+i*size) for i in range(num)]
 names=data[headers[strings][4]:headers[strings][4]+headers[strings][5]]
 return [(names[h[0]:].split(b'\0',1)[0].decode(errors='replace'),h,data[h[4]:h[4]+h[5]]) for h in headers]

allvariants={}
for v in ['s12c','s13k']:
 obj=root/'variants'/v/'build/CMakeFiles/bench_multi.dir/bench_multi.asc.o'
 blob=next(d for n,h,d in sections(obj.read_bytes()) if n=='.aicore_binary')
 offset=0;images=[];texts={}
 while True:
  offset=blob.find(b'\x7fELF\x02\x01',offset)
  if offset<0:break
  try:secs=sections(blob[offset:])
  except Exception:offset+=6;continue
  (root/'solo13_data'/('device_'+v+'.elf')).write_bytes(blob[offset:])
  labels=[]
  for n,h,d in secs:
   if n.startswith('.text') and h[5]:
    texts.setdefault(n,[]).append({'sha256':hashlib.sha256(d).hexdigest(),'size':len(d)})
    labels.append(n)
  for n,h,d in secs:
   if h[1]==2 and h[9]==24:
    strings=secs[h[6]][2]
    for i in range(0,len(d),24):
     name,info,other,shidx,value,length=struct.unpack_from('<IBBHQQ',d,i)
     if info&15!=2 or length==0 or shidx>=len(secs):continue
     sn,sh,sd=secs[shidx]
     if not sn.startswith('.text'):continue
     label=strings[name:].split(b'\0',1)[0].decode(errors='replace')
     pos=value-sh[3];code=sd[pos:pos+length]
     texts.setdefault('.function::'+label,[]).append({'sha256':hashlib.sha256(code).hexdigest(),'size':len(code)})
     normalized=bytearray(code);relocations=[]
     for rn,rh,rd in secs:
      if rh[1]!=4 or rh[7]!=shidx:continue
      syms=secs[rh[6]]
      symbolnames=secs[syms[1][6]][2]
      for j in range(0,len(rd),24):
       address,rinfo,addend=struct.unpack_from('<QQq',rd,j)
       relative=address-value
       if 0<=relative<length:
        st=struct.unpack_from('<IBBHQQ',syms[2],(rinfo>>32)*24)
        target=symbolnames[st[0]:].split(b'\0',1)[0].decode(errors='replace')
        relocations.append([relative,rinfo&0xffffffff,target,addend])
        normalized[relative:relative+4]=b'\0'*4
     digest=hashlib.sha256(bytes(normalized)+json.dumps(relocations,sort_keys=True).encode()).hexdigest()
     texts.setdefault('.normalized_relocations::'+label,[]).append({'sha256':digest,'size':len(code),'relocations':relocations})
  images.append({'offset':offset,'text_sections':labels})
  offset+=6
 allvariants[v]={'object':str(obj),'images':images,'texts':texts}
shared=set(allvariants['s12c']['texts'])&set(allvariants['s13k']['texts'])
result={'variants':allvariants,'shared_sections':len(shared),
        'equal_sections':[n for n in sorted(shared) if allvariants['s12c']['texts'][n]==allvariants['s13k']['texts'][n]],
        'changed_sections':[n for n in sorted(shared) if allvariants['s12c']['texts'][n]!=allvariants['s13k']['texts'][n]]}
import csv
poolfiles=list((root/'solo13_data/final_s13k/pool1_s12c').glob('**/op_summary_*.csv'))
if poolfiles:
 names=sorted(set(r['Op Name'] for r in csv.DictReader(poolfiles[0].open())))
 pool=[]
 for name in names:
  matches=[n for n in allvariants['s12c']['texts'] if n.startswith('.normalized_relocations::') and n.split('::',1)[1] in [name,name+'_mix_aic',name+'_mix_aiv']]
  pool.append({'op_name':name,'entry_functions':matches,'same_instructions_after_relocations':bool(matches) and all(n in result['equal_sections'] for n in matches)})
 result['pool_entries']=pool
 result['all_pool_entries_equal']=all(x['same_instructions_after_relocations'] for x in pool)
(root/'solo13_data/device_code_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print('Images:',{v:len(d['images']) for v,d in allvariants.items()})
print('Text sections:',{v:len(d['texts']) for v,d in allvariants.items()})
print('Equal:',len(result['equal_sections']),'Changed:',len(result['changed_sections']))
print('Changed names:',result['changed_sections'][:8])
print('Example text names:',list(allvariants['s13k']['texts'])[:8])
