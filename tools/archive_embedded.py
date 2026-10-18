from pathlib import Path,PurePosixPath
import importlib.util,hashlib,io,json,os,tarfile,zipfile
spec=importlib.util.spec_from_file_location('archive','/tmp/bmms_archive_server_20261018.py')
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
out=Path('/tmp/bmms-github-archive-20261018');rows=[];containers=[];findings=[];skipped=[]
def save(data,name,origin,mode,tar):
    parts=PurePosixPath(name)
    if parts.is_absolute() or '..' in parts.parts:return
    if any(mod.pruned(p) for p in parts.parts[:-1]):return
    if parts.suffix.lower() not in mod.SUFFIXES and parts.name not in mod.SPECIAL:return
    if parts.name in mod.SECRET_NAMES or len(data)>25*1024*1024:return
    if b'\0' in data[:8192]:return
    try:data.decode('utf-8')
    except UnicodeDecodeError:return
    for kind,pattern in mod.PATTERNS.items():
        hits=list(pattern.finditer(data))
        if hits:findings.append({'archive':origin,'member':name,'kind':kind,'line_numbers':[data[:h.start()].count(b'\n')+1 for h in hits][:20]})
    stored='embedded-archives/home/developer/'+origin+'.contents/'+str(parts)
    entry=tarfile.TarInfo(stored);entry.size=len(data);entry.mode=mode&0o777
    tar.addfile(entry,io.BytesIO(data))
    rows.append({'archive':origin,'member':name,'stored_path':stored,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
with tarfile.open(out/'embedded-source.tar.gz','w:gz') as target:
    for project in mod.PROJECTS:
        for root,dirs,files in os.walk(project,followlinks=False):
            dirs[:]=[d for d in dirs if not mod.pruned(d) and not (Path(root)/d).is_symlink()]
            for name in sorted(files):
                p=Path(root)/name
                if p.is_symlink() or p.suffix.lower() not in {'.tgz','.gz','.zip'}:continue
                origin=p.relative_to(mod.HOME_ROOT).as_posix();before=len(rows)
                if zipfile.is_zipfile(p):
                    with zipfile.ZipFile(p) as z:
                        for info in z.infolist():
                            if info.is_dir() or info.file_size>25*1024*1024:continue
                            suffix=PurePosixPath(info.filename).suffix.lower()
                            if suffix not in mod.SUFFIXES and PurePosixPath(info.filename).name not in mod.SPECIAL:continue
                            save(z.read(info),info.filename,origin,(info.external_attr>>16) or 0o644,target)
                elif tarfile.is_tarfile(p):
                    with tarfile.open(p,'r:*') as z:
                        for info in z:
                            if not info.isfile() or info.size>25*1024*1024:continue
                            suffix=PurePosixPath(info.name).suffix.lower()
                            if suffix not in mod.SUFFIXES and PurePosixPath(info.name).name not in mod.SPECIAL:continue
                            stream=z.extractfile(info)
                            if stream:save(stream.read(),info.name,origin,info.mode,target)
                else:skipped.append(origin);continue
                containers.append({'path':origin,'bytes':p.stat().st_size,'selected_files':len(rows)-before})
report={'containers':containers,'file_count':len(rows),'bytes':sum(x['bytes'] for x in rows),'credential_findings':findings,'skipped_non_archive_gzip':skipped,'files':rows}
(out/'embedded-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in {'files','containers'}},indent=2))
if findings:raise SystemExit(2)
