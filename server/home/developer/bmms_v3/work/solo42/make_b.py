from pathlib import Path
import hashlib, json, difflib, zipfile

r=Path(__file__).resolve().parents[2]
w=Path(__file__).parent
assert (w/'resource_b.json').is_file()
base=(r/'variants/s42a/kernel.asc').read_text(encoding='utf-8')
assert hashlib.sha256(base.encode()).hexdigest()=='dc7c037c671d8c921cbf093d322adfa53dde32b4d57513c7698e93c06e5bf3aa'
start=base.index('template<class T, bool TA, bool TB>\n__global__ __aicore__ __mix__(1, 1) void bmms_pair_a2resident256(')
end=base.index('\ntemplate<class T, bool TA, bool TB, bool PAIR=false, bool FULLA=false>',start)
old=base[start:end]
needle='    TPipe pipe;\n    if ASCEND_IS_AIC {\n'
assert old.count(needle)==1
new=old.replace(needle,'''    if ASCEND_IS_AIC {
        // Keep register defaults without TPipe's pre-seeded M_MTE1 event0/1/2.
        // All raw AIC buffers and explicit events below are owned by this kernel.
        InitSocState();
''',1)
aiv_marker='    if ASCEND_IS_AIV {\n'
assert new.count(aiv_marker)==1
new=new.replace(aiv_marker,aiv_marker+'        TPipe pipe;\n',1)
old_aiv=old[old.index(aiv_marker)+len(aiv_marker):]
new_aiv=new[new.index(aiv_marker)+len(aiv_marker+'        TPipe pipe;\n'):]
assert new_aiv==old_aiv, 'AIV instructions after pipe declaration must stay identical'
aic=new[:new.index(aiv_marker)]
assert 'TPipe pipe;' not in aic and 'pipe.' not in aic and 'GetTPipePtr' not in aic
source=base[:start]+new+base[end:]
v=r/'variants/s42b';v.mkdir(exist_ok=False)
(v/'kernel.asc').write_text(source,encoding='utf-8',newline='\n')
with zipfile.ZipFile(v/'s42b_kernel.zip','w',zipfile.ZIP_DEFLATED) as z:z.writestr('kernel.asc',source)
sha=hashlib.sha256(source.encode()).hexdigest()
(w/'source_b.json').write_text(json.dumps(dict(variant='s42b',baseline='s42a',sha256=sha,bytes=len(source.encode()),
    status='source only; not compiled or NPU tested by this subagent',
    fix='AIC raw-memory path uses InitSocState without TPipe implicit event tokens; AIV retains scoped TPipe',
    aiv_after_pipe_byte_identical=True),indent=2)+'\n')
(w/'diff_b.patch').write_text(''.join(difflib.unified_diff(base.splitlines(True),source.splitlines(True),
    fromfile='s42a/kernel.asc',tofile='s42b/kernel.asc')),encoding='utf-8')
print(json.dumps(dict(variant='s42b',sha256=sha,bytes=len(source.encode()))))
