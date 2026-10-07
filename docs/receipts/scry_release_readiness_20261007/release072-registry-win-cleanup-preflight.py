from pathlib import Path
import json,hashlib,zipfile,subprocess,psutil,datetime,os
W=Path('C:/Users/mark_/Code/worktrees/wgpu-scry-release');D=W/'registry-consumer-scry';P=Path('C:/Users/mark_/Code/repos/wgpu-scry');O=P/'docs/receipts/scry_release_readiness_20261007';PRE='release072-registry-win-'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(root,*a):return subprocess.check_output(['git',*a],cwd=root,text=True).strip()
f=json.loads((O/(PRE+'inputs.json')).read_text(encoding='utf-8'));g=json.loads((O/(PRE+'initial-guards.json')).read_text(encoding='utf-8'));archive=O/(PRE+'source-inputs.zip');assert h(archive)==f['zip_sha256']
with zipfile.ZipFile(archive) as z:assert all(hashlib.sha256(z.read(x['path'])).hexdigest()==x['sha256'] for x in f['inputs'])
assert all(h(Path(x['actual_path']))==x['sha256'] for x in f['inputs']);assert git(W,'rev-parse','HEAD')==g['source_head'];assert not git(W,'status','--porcelain','--untracked-files=no');assert all(h(P/x['path'])==x['sha256'] for x in g['primary_dirty_docs'])
paths=[str(W).lower().replace('\\','/'),str(D).lower().replace('\\','/'),'c:/t/cargo-targets/wgpu-scry/native-registry-runtime'];refs=[];limits=[];builds=[];observerids={os.getpid(),*[x.pid for x in psutil.Process().parents()]}
for proc in psutil.process_iter(['pid','name']):
 try:
  cmd=' '.join(proc.cmdline()).lower().replace('\\','/');cwd=proc.cwd().lower().replace('\\','/');matched=[s for s in paths if s in cmd or cwd.startswith(s)]
  if matched and proc.pid not in observerids:refs.append({'pid':proc.pid,'name':proc.info['name'],'matched_paths':matched})
  if (proc.info['name'] or '').lower() in ['cargo.exe','rustc.exe','cl.exe','link.exe','demo-win.exe','turnstone.exe']:builds.append(proc.info)
 except(psutil.AccessDenied,psutil.NoSuchProcess) as e:limits.append({'pid':proc.pid,'reason':type(e).__name__})
assert not refs and not builds,(refs,builds)
remote=git(P,'ls-remote','origin','refs/heads/main').split()[0];assert remote==g['source_head'];consumer=[x for x in f['inputs'] if x['path'].startswith('consumer/')];actual={x.relative_to(D).as_posix() for x in D.rglob('*') if x.is_file()};assert actual=={x['path'][9:] for x in consumer}
obj={'recorded_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'owned_worktree':str(W),'owned_generated_stage':str(D),'head':g['source_head'],'remote_main':remote,'detached':True,'tracked_source_clean':True,'staged_file_count':len(consumer),'staged_inputs':consumer,'source_archive':str(archive),'source_archive_sha256':h(archive),'all_source_inputs_and_raw_zip_verified':True,'primary_dirty_docs_guarded':g['primary_dirty_docs'],'worktree_primary_before':git(P,'worktree','list','--porcelain'),'matching_live_processes':refs,'build_native_processes':builds,'excluded_only_observer_ancestor_pids':sorted(observerids),'process_observer_limitations':limits,'scope':'Remove only archived generated stage, then normal Git remove exact clean detached owned worktree. Primary source/docs and retained runtime caches remain.'}
with (O/(PRE+'cleanup-preflight.json')).open('x',encoding='utf-8',newline='\n') as out:json.dump(obj,out,indent=2);out.write('\n')
print(json.dumps({'staged_files':len(consumer),'source_zip_sha256':h(archive),'owners':refs,'observer_limitations':len(limits),'remote':remote}))
