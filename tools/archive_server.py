from pathlib import Path
from collections import Counter
import argparse, hashlib, io, json, os, re, tarfile, time

HOME_ROOT=Path('/home/developer')
PROJECTS=sorted(p for p in HOME_ROOT.glob('bmms*') if p.is_dir())
SUFFIXES={'.asc','.cpp','.cc','.c','.cce','.cu','.h','.hpp','.inl','.py','.sh','.bash',
          '.cmake','.json','.yaml','.yml','.toml','.ini','.cfg','.md','.rst','.txt',
          '.patch','.diff','.csv','.tsv','.xml','.inc','.hh','.hxx','.cuh','.ipp','.tpp',
          '.s','.asm','.js','.jsx','.ts','.tsx','.css','.html','.vue','.rs','.go','.java',
          '.kt','.ipynb','.proto','.sql','.gradle','.bazel','.bzl','.ninja','.jinja',
          '.j2','.tmpl','.tpl','.in','.jsonl','.bak','.orig','.old'}
SPECIAL={'Makefile','Dockerfile','LICENSE','NOTICE','.gitignore','.gitattributes','.gitmodules'}
PRUNE={'.git','__pycache__','node_modules','.venv','venv','site-packages','CMakeFiles',
       'kernel_meta','.cache','.ssh','.vscode','.idea'}
SECRET_NAMES={'.env','.env.local','.env.production','credentials','credentials.json',
              'token','token.json','secrets.json','id_rsa','id_ed25519','known_hosts'}
PATTERNS={
 'private_key':re.compile(rb'-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----'),
 'github_token':re.compile(rb'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})\b'),
 'aws_access_key':re.compile(rb'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b'),
 'api_key':re.compile(rb'\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}\b'),
 'credential_assignment':re.compile(rb'''(?i)(?:api[_-]?key|access[_-]?token|secret[_-]?key|password|authorization)\s*[=:]\s*["'][^"'\r\n]{8,}["']'''),
 'credential_url':re.compile(rb'https?://[^\s/:@]+:[^\s/@]{5,}@'),
}

def pruned(name):
    return (name in PRUNE or (name.startswith('.') and name!='.github') or
            name=='build' or name.startswith(('build_','cmake-build-','PROF_')))

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--pack',action='store_true');args=ap.parse_args()
    out=Path('/tmp/bmms-github-archive-20261018');out.mkdir(exist_ok=True)
    files=[];excluded=Counter();unknown=Counter();symlinks=[];findings=[];stats=Counter();total=0
    tar=tarfile.open(out/'server-source.tar.gz','w:gz') if args.pack else None
    try:
        def link_entry(p):
            raw=os.readlink(p);target=p.resolve()
            try:target.relative_to(HOME_ROOT)
            except ValueError:
                excluded['external_symlink']+=1;return
            if not any(target==q or q in target.parents for q in PROJECTS):
                excluded['nonproject_symlink']+=1;return
            if not target.exists():excluded['broken_symlink']+=1;return
            rel=p.relative_to(HOME_ROOT).as_posix();relative_target=os.path.relpath(target,p.parent)
            symlinks.append({'path':rel,'original_target':raw,'relative_target':relative_target,
                             'is_directory':target.is_dir()})
            if tar:
                entry=tarfile.TarInfo('server/home/developer/'+rel);entry.type=tarfile.SYMTYPE
                entry.linkname=relative_target;entry.mode=0o777;tar.addfile(entry)
        for project in PROJECTS:
            for root,dirs,names in os.walk(project,followlinks=False):
                keep=[]
                for name in sorted(dirs):
                    p=Path(root)/name
                    if p.is_symlink():link_entry(p)
                    elif pruned(name):excluded['generated_or_tool_directory']+=1
                    else:keep.append(name)
                dirs[:]=keep
                for name in sorted(names):
                    p=Path(root)/name
                    if p.is_symlink():link_entry(p);continue
                    if name in SECRET_NAMES or p.suffix.lower() in {'.pem','.key','.p12','.pfx'}:
                        excluded['credential_filename']+=1;continue
                    if p.suffix.lower() not in SUFFIXES and name not in SPECIAL:
                        excluded['non_source_extension']+=1;unknown[p.suffix.lower() or '<none>']+=1;continue
                    size=p.stat().st_size
                    if size>25*1024*1024:
                        excluded['over_25MiB']+=1;continue
                    data=p.read_bytes()
                    if b'\x00' in data[:8192]:excluded['binary_content']+=1;continue
                    try:data.decode('utf-8')
                    except UnicodeDecodeError:excluded['non_utf8']+=1;continue
                    rel=p.relative_to(HOME_ROOT).as_posix()
                    hits=[]
                    for label,pattern in PATTERNS.items():
                        matches=list(pattern.finditer(data))
                        if matches:hits.append({'kind':label,'line_numbers':[data[:m.start()].count(b'\n')+1 for m in matches][:20]})
                    if hits:findings.append({'path':rel,'findings':hits})
                    digest=hashlib.sha256(data).hexdigest()
                    files.append({'path':rel,'bytes':len(data),'sha256':digest,'mode':oct(p.stat().st_mode&0o777)})
                    total+=len(data);stats[project.name]+=1
                    if tar:
                        entry=tarfile.TarInfo('server/home/developer/'+rel)
                        entry.size=len(data);entry.mode=p.stat().st_mode&0o777;entry.mtime=int(p.stat().st_mtime)
                        tar.addfile(entry,io.BytesIO(data))
    finally:
        if tar:tar.close()
    report={'captured_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
            'source_home':'/home/developer','project_roots':[p.name for p in PROJECTS],
            'file_count':len(files),'bytes':total,'per_project_files':dict(stats),
            'excluded_counts':dict(excluded),'non_source_extensions':dict(unknown),
            'symlink_count':len(symlinks),'symlinks':symlinks,'credential_findings':findings,
            'scope':'Source, scripts, documentation, configs, text performance records in every bmms* project. System SDK/IDE, Git internals, binaries, datasets and generated build/profiler trees excluded.',
            'files':files}
    (out/'server-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in {'files','symlinks'}},ensure_ascii=False,indent=2))
    if findings:raise SystemExit(2)

if __name__=='__main__':main()
