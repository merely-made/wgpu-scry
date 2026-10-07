from pathlib import Path
import datetime, hashlib, json, os, subprocess, sys, time, zipfile

REPO=Path('C:/Users/mark_/Code/worktrees/wgpu-scry-release')
PRIMARY=Path('C:/Users/mark_/Code/repos/wgpu-scry')
OUT=PRIMARY/'docs/receipts/scry_release_readiness_20261007'
TARGET=Path('C:/t/cargo-targets/wgpu-scry')
SHA='4d8d1d3f8dd450b712960c90b74263a45b46e35b'
PREFIX='release072-package-'
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*a): return subprocess.check_output(['git',*a],cwd=REPO,text=True,stderr=subprocess.DEVNULL).strip()
def save(name, obj):
    with (OUT/(PREFIX+name)).open('x',encoding='utf-8',newline='\n') as f:
        json.dump(obj,f,indent=2); f.write('\n')
assert git('rev-parse','HEAD')==SHA and not git('status','--porcelain','--untracked-files=all','--ignored')
original=json.loads((OUT/'m4-unlocked-windows-initial-guards.json').read_text(encoding='utf-8'))
assert all(sha(PRIMARY/x['path'])==x['sha256'] for x in original['dirty_docs_before'])
env=dict(os.environ,CARGO_TARGET_DIR=str(TARGET),CARGO_BUILD_JOBS='1',RUSTUP_TOOLCHAIN='1.92.0')
safe={k:env[k] for k in ['CARGO_TARGET_DIR','CARGO_BUILD_JOBS','RUSTUP_TOOLCHAIN','RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','CARGO_RESOLVER_INCOMPATIBLE_RUST_VERSIONS'] if k in env}
inputs=[]
with zipfile.ZipFile(OUT/(PREFIX+'source-inputs.zip'),'x',compression=zipfile.ZIP_DEFLATED) as z:
    for name in git('ls-files').splitlines():
        if name.startswith('docs/receipts/'): continue
        raw=(REPO/name).read_bytes(); inputs.append({'path':name,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}); z.writestr(name,raw)
save('inputs.json',{'recorded_utc':now(),'source_commit':SHA,'source_tree':git('rev-parse','HEAD^{tree}'),'source_clean':True,'version':'0.7.2','inputs':inputs,'source_archive_sha256':sha(OUT/(PREFIX+'source-inputs.zip')),'rustc':subprocess.check_output(['rustc','+1.92.0','-Vv'],text=True),'cargo':subprocess.check_output(['cargo','+1.92.0','-V'],text=True),'environment':safe,'priority':'BelowNormal','primary_dirty_docs_before':original['dirty_docs_before'],'scope':'Package list, package verification and publish dry-run only. No publish/tag/auth token reads. Stable target/Cargo home reused.'})
gates=[('list',['cargo','+1.92.0','package','--locked','-p','scrying','--list']),('verify',['cargo','+1.92.0','package','--locked','-p','scrying','-j1']),('dry-run',['cargo','+1.92.0','publish','--dry-run','--locked','-p','scrying','-j1'])]
results=[]
for label,cmd in gates:
    assert git('rev-parse','HEAD')==SHA and not git('status','--porcelain','--untracked-files=all','--ignored')
    r={'label':label,'command':cmd,'cwd':str(REPO),'source_commit':SHA,'started_utc':now(),'environment':safe,'priority':'BelowNormal'};start=time.monotonic()
    with (OUT/(PREFIX+label+'.stdout.log')).open('xb') as a,(OUT/(PREFIX+label+'.stderr.log')).open('xb') as b:
        process=subprocess.Popen(cmd,cwd=REPO,env=env,stdout=a,stderr=b,creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        r['owned_pid']=process.pid; print('START',label,process.pid,now(),flush=True); r['actual_exit_code']=process.wait()
    r.update(finished_utc=now(),elapsed_seconds=round(time.monotonic()-start,3),final_source_commit=git('rev-parse','HEAD'),source_status=git('status','--porcelain','--untracked-files=all','--ignored'),stdout_sha256=sha(OUT/(PREFIX+label+'.stdout.log')),stderr_sha256=sha(OUT/(PREFIX+label+'.stderr.log')))
    if label!='list':
        archive=TARGET/'package/scrying-0.7.2.crate'
        if archive.is_file():
            copy=OUT/(PREFIX+label+'.crate')
            with copy.open('xb') as f:f.write(archive.read_bytes())
            r['generated_crate']={'generated_path':str(archive),'preserved_path':copy.name,'bytes':copy.stat().st_size,'sha256':sha(copy)}
    save(label+'.result.json',r);results.append(r);print('FINISH',label,r['actual_exit_code'],r['elapsed_seconds'],flush=True)
    assert r['final_source_commit']==SHA and not r['source_status']
    assert all(sha(REPO/x['path'])==x['sha256'] for x in inputs)
    if r['actual_exit_code']!=0: break
dirty=[{'path':x['path'],'sha256':sha(PRIMARY/x['path']),'unchanged':sha(PRIMARY/x['path'])==x['sha256']} for x in original['dirty_docs_before']]
assert all(x['unchanged'] for x in dirty)
save('summary.json',{'recorded_utc':now(),'source_commit':SHA,'results':results,'all_three_gates_exit_zero':len(results)==3 and all(x['actual_exit_code']==0 for x in results),'source_inputs_unchanged':True,'source_status':git('status','--porcelain','--untracked-files=all','--ignored'),'primary_dirty_docs_after':dirty,'primary_head_after':subprocess.check_output(['git','rev-parse','HEAD'],cwd=PRIMARY,text=True).strip(),'retained_clean_worktree':str(REPO),'retained_stable_target':str(TARGET),'no_actual_publish_or_tag':True})
sys.exit(0 if len(results)==3 and all(x['actual_exit_code']==0 for x in results) else 1)
