"""Read-only comparison of actual 2201 Cube entry machine code."""
import struct,json,hashlib
from pathlib import Path
root=Path('/home/developer/bmms_v3')
def sections(data):
 assert data[:6]==b'\x7fELF\x02\x01'
 off=struct.unpack_from('<Q',data,40)[0];size,num,strings=struct.unpack_from('<HHH',data,58)
 hs=[struct.unpack_from('<IIQQQQIIQQ',data,off+i*size) for i in range(num)]
 ns=data[hs[strings][4]:hs[strings][4]+hs[strings][5]]
 return [(ns[h[0]:].split(b'\0',1)[0].decode(errors='replace'),h,data[h[4]:h[4]+h[5]]) for h in hs]
out={}
for variant in ['clean44','clean46']:
 obj=root/'variants'/variant/'build/CMakeFiles/bench.dir/bench.asc.o'
 blob=next(d for n,h,d in sections(obj.read_bytes()) if n=='.aicore_binary')
 cursor=0;fs={}
 while True:
  cursor=blob.find(b'\x7fELF\x02\x01',cursor)
  if cursor<0:break
  try:ss=sections(blob[cursor:])
  except Exception:cursor+=6;continue
  elf=root/'c26'/('device_'+variant+'.elf');elf.write_bytes(blob[cursor:])
  for n,h,d in ss:
   if h[1]!=2 or h[9]!=24:continue
   strings=ss[h[6]][2]
   for i in range(0,len(d),24):
    name,info,other,shidx,value,length=struct.unpack_from('<IBBHQQ',d,i)
    if info&15!=2 or length==0 or shidx>=len(ss):continue
    label=strings[name:].split(b'\0',1)[0].decode(errors='replace')
    if 'bmms_single_tile' not in label:continue
    sn,sh,sd=ss[shidx];pos=value-sh[3];code=sd[pos:pos+length]
    fs[label]={'size':length,'sha256_raw':hashlib.sha256(code).hexdigest()}
  cursor+=6
 out[variant]=fs
common=sorted(set(out['clean44'])&set(out['clean46']))
summary=[{'symbol':s,'before_bytes':out['clean44'][s]['size'],'after_bytes':out['clean46'][s]['size'],'identical_raw':out['clean44'][s]['sha256_raw']==out['clean46'][s]['sha256_raw']} for s in common]
(root/'c26/small_instruction_audit.json').write_text(json.dumps({'variants':out,'summary':summary},indent=2)+'\n')
print('entries',len(common))
for x in summary:
 if 'Li32ELi80E' in x['symbol'] or 'Li16ELi32E' in x['symbol']:print(json.dumps(x))
