from pathlib import Path
import hashlib
import json
import re
import shutil
import sys
import tarfile

r=Path('/home/developer/bmms_v3');w=r/'c46'
expected={
 'clean152':'d93e586881a336068bdf073b961dfc4987a0f05409212813be1b9073b651195d',
 'clean153':'65d153783048b54ed13ef7442815e22e8d3d4b25a857b888472cb4b25e8da790',
 'clean154':'e163480bff36db43f416b215d30fbae3281e2ee27afbfb9c7f9a13975804aeaf',
 'clean155':'09cb7ffda875dfadc5c690267d90dd4a3a364bf26272f33b0b7bbc080ccd1365',
 'clean156':'1c4b91548c992f25b94ed9265ac3fc0478f856775794d5a32d39d74399c59bf5',
 'clean157':'ec6a87699ee3db6e1c2a5a22310466c0a89435bf8803022c7ccb8ac71e4546f0',
 'clean158':'adcf830f510859420784e71d59311b182162770f91d42752b69fc7efeba2ae38',
 'clean159':'12233dffe83fe3b527b34f6e70eccd175a95e03ff63a3e91e15745473d4aa3b7',
 'clean160':'3de7e6474034abd0da9904eddfffdd45f70a9af1a35772180a99bc8d28ccde67',
 'clean161':'ed026ba2d20107be6cdc5735d7198a1d5c59ab9c370ffe5ecdfde7a2cfee5426',
 'clean162':'0cffd12fd56854751143486bd978562a4dc8c1d1f4c3a033a96c8d266d95b8aa',
 'clean163':'1b26e385a4cd54da013e629928a3983ffbbdc4a8e660f3f6c5492e0417572369',
 'clean164':'d4fba48e6a33174453c769b85895eaf74f898788ed69b483610a23c862daab34',
 'clean165':'4578a5dc3faa3591ca6fbffbb79425be0d70a511c934f2a3154725aacf205aa5',
 'clean166':'6bf2075cc772d2469f0e59571edc9a70a2ae6cd342b95e6a14aab129a7aab296',
 'clean167':'3abd6e9c33b2faca4d7ad57c8f6c543c7f90f9cd4f26113e2ab934b91ebd5b5e',
 'clean168':'326a4a6d771b484fc59c37a57b81353ff471d6f8cef4f52c7dc2a050f314d4c5',
 'clean169':'dc8e32f4f760d49ba0bf088633211d852d9e31e53c04aa8b030b1b92b4243cbb',
 'clean170':'ac1c937f5b9ec1cc6dcaaf7607764a3c494a5e8590b5cc8b0370a7ddd37c544d',
 'clean171':'f6ef0e96c6023a98183028c8a51999255bbf0d70e812135fc282158adc0b0f76',
 'clean172':'2cb8d1575f424b7652b61e31fef1a2932c5b3541882ee318d887ba9a7bcfb68e',
 'clean173':'51d76e2c4aa4e06192552e8ba0022b84da9b4a546627dfcad9b1de931712f112',
 'clean174':'27a894cb52e1b9b7011ce80f2f6c1a53fee6bde792860984d42414e568267948',
 'clean175':'4b46c1cfeda567bb09b741d02714a4f726d7275b22770617a4de0240c5454851',
 'clean176':'838a069622d52bfa46dbdbe230873104e53246db48aaf095db6603ab94841558',
 'clean177':'94aab006411a17db3626da37d9f2b83cff5d939c2fcd603f0d0733bf07e4bb9c',
 'clean178':'38667ba772d2f530aa291a599855c158bc34a47542f20ba8d8dac8d4220a001c',
 'clean179':'60b77b7115d72062eaa6f72eca82a5380144da8b696ad4323dc59617d8ad7d90',
 'clean180':'15381c9d9e71b27e8c8277084e00cd3875bf4f39db52dd5870c5ac8d7c1522c9',
 'clean182':'7071e5c12fe6307a2cda5ddae476217fb5e702843888accb9da25b5e13f68025',
 'clean181':'309e09a597737ecefa877498a3fa261395e853d5fdd8e1bb5bd118b5b6a3bb1c',
 'clean183':'bcfd410e73c2ce5e209da143b7982167aa4b97cb32f9fd04872c6c343fec9067',
 'clean184':'7f21a1aafe6437751a869866c864fbfb6bf686d119604c2e038dcf277bb10bed',
 'clean185':'0a6bf495e7d1f537f65106f717128bbd57056511ab62b5c4f6ed268d0be2fd45',
 'clean186':'08a165a3c98359187f69010f632c78a717c047af976057c39c5d065865df143d',
 'clean187':'02f7eafd59f7dc0cb16a1004532d208868cdaed405a3b9f2f779cd1c69e3296a',
 'clean188':'25cc3c8157348198c5ef4c1d49df038298883d66fb9c37cab82f39c6fec9045d',
 'clean189':'6b20884bafc92c95aa5addee68409c3c07d18a31d7830b18058a4ca6df795bf1',
 'clean190':'c7a130a10bac43654b2ee4847a1aa85b6a4d8132e719de32dfb4d2d58b411651',
 'clean191':'8d7463f98094f30dad91568afb4b8a580562cc8e8cf905c98ba5bdc2975880df',
 'clean192':'4ae534b2a1987835f2e5af95ed5d84c3e3f06204bc33d850775d4d06a36f790f',
 'clean193':'5ef83ab881bcc386ca90541d8c4bb1e301a7c747af83cf87e4c835b5de68ff3e',
 'clean194':'6bb838f22cad46b6a5fedab1034e5d7191e21956fdbb531cec43ba72ea851f2c',
 'clean195':'638e7dce583e38f975ee57c481a3c9f7e311087772864c93b8057a8cb514eb56',
 'clean196':'fac259dfc11f5ca5660f78db409aa49730c78e5664a6dff58a3bd4d87186e265',
 'clean197':'34825221d6820a628ada14c3ab334d04669979a4934fe52ab7f570f8fd3ba844',
 'clean198':'8114cca79f83d4e4415abb5c18f32fda4d247dfba87e59669193bd3e892c2437',
 'clean199':'17f0848794e0cb3ae344c4e4fdfdbfcea17b3cfb0dab2556880ced50edb337e9',
 'clean201':'507dc6972de023d84e58aa22d43a6af6815d63d544e7d32006d986ffd020c48c',
 'clean202':'0407bf42efb933055c98f4ce6cc09e70c645571b4fcc64587ec5436a15d24725',
}
assert (len(sys.argv)-1)%2==0
for v,digest in zip(sys.argv[1::2],sys.argv[2::2]):
 assert re.fullmatch(r'clean\d+',v) and re.fullmatch(r'[a-f0-9]{64}',digest)
 expected[v]=digest
 rows=json.loads((w/(v+'_local15.json')).read_text())
 assert len(rows)==15 and all(x['passed'] and x['returncode']==0 and x['tasks']==123 for x in rows)
 dest=w/('final'+v);dest.mkdir(exist_ok=True)
 for x in rows:
  s='_'.join(map(str,x['shape']))+'_'+str(x['dtype'])+'_'+str(int(x['ta']))+'_'+str(int(x['tb']))
  p=r/'variants'/v/'research/PipeUtilization'/s
  captured=dest/('final15_P'+str(x['case'])+'_'+v+'.csv')
  assert captured.exists()
  for origin,suffix in [(p/'output/y.bin','_y.bin'),(p/'msprof.log','_msprof.log')]:
   # A later focused control can reuse this research directory. Preserve the
   # already captured full15 output/log instead of relabeling a later call.
   captured_aux=dest/('P'+str(x['case'])+suffix)
   if origin.exists() and not captured_aux.exists():shutil.copy2(origin,captured_aux)
 snap=w/'tested_sources';snap.mkdir(exist_ok=True)
 shutil.copy2(r/'variants'/v/'kernel.asc',dest/'kernel.asc')
snap=w/'tested_sources';snap.mkdir(exist_ok=True)
for v,digest in expected.items():
 p=r/'variants'/v/'kernel.asc';assert hashlib.sha256(p.read_bytes()).hexdigest()==digest
 shutil.copy2(p,snap/(v+'.asc'))
(snap/'hashes.json').write_text(json.dumps(expected,indent=2)+'\n')
with tarfile.open(w/'evidence.tgz','w:gz') as t:
 for p in sorted(w.rglob('*')):
  if p.is_file() and p.suffix!='.tgz':t.add(p,arcname='c46/'+str(p.relative_to(w)),recursive=False)
print('CSV',len(list(w.rglob('*.csv'))))
