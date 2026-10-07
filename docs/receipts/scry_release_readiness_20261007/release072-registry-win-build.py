from pathlib import Path
import hashlib,json,os,subprocess,sys,time,datetime,zipfile,psutil,tomllib
W=Path('C:/Users/mark_/Code/worktrees/wgpu-scry-release');D=W/'registry-consumer-scry';P=Path('C:/Users/mark_/Code/repos/wgpu-scry');O=P/'docs/receipts/scry_release_readiness_20261007';T=Path('C:/t/cargo-targets/wgpu-scry');G=Path('C:/Users/mark_/Code/repos/wgpu-graft');PRE='release072-registry-win-';SHA='4d8d1d3f8dd450b712960c90b74263a45b46e35b'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):
 with (O/(PRE+n)).open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2);f.write('\n')
def git(*a):return subprocess.check_output(['git',*a],cwd=W,text=True).strip()
assert git('rev-parse','HEAD')==SHA and not git('status','--porcelain','--untracked-files=no')
meta=json.loads((O/(PRE+'resolver/metadata.json')).read_text(encoding='utf-8'));assert all(x['id'] in meta['workspace_members'] or (x.get('source') or '').startswith('registry+') for x in meta['packages'])
lock=tomllib.loads((D/'Cargo.lock').read_text(encoding='utf-8'))['package'];selected=[]
for name,version in [('grafting','0.6.0'),('scrying','0.7.2'),('welding','0.14.1')]:
 matches=[x for x in meta['packages'] if x['name']==name];assert len(matches)==1 and matches[0]['version']==version;pkg=matches[0];root=Path(pkg['manifest_path']).parent;cs={'package':next(x['checksum'] for x in lock if x['name']==name and x['version']==version)};cache=root.parent.parent.parent/'cache'/root.parent.name/(name+'-'+version+'.crate');assert cache.is_file(),cache;assert h(cache)==cs['package'];dest=O/(PRE+name+'-'+version+'.crate');dest.open('xb').write(cache.read_bytes());selected.append({'name':name,'version':version,'source':pkg['source'],'manifest_path':pkg['manifest_path'],'package_checksum':cs['package'],'preserved_archive':dest.name,'bytes':dest.stat().st_size,'source_root':str(root)})
assert next(x for x in selected if x['name']=='scrying')['package_checksum']=='74486b58a87ac1ea36ba33e24ffaf513570845bcd1d1c099cc872923dc83d740'
wgpu=[x for x in meta['packages'] if x['name']=='wgpu'];assert len(wgpu)==1 and wgpu[0]['version']=='30.0.1';assert '[patch' not in (D/'Cargo.toml').read_text(encoding='utf-8')
inputs=[]
with zipfile.ZipFile(O/(PRE+'source-inputs.zip'),'x',compression=zipfile.ZIP_DEFLATED) as z:
 for f in sorted(D.rglob('*')):
  if f.is_file():
   raw=f.read_bytes();n='consumer/'+f.relative_to(D).as_posix();z.writestr(n,raw);inputs.append({'path':n,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'actual_path':str(f)})
 for rec in selected:
  root=Path(rec['source_root'])
  for f in sorted(root.rglob('*')):
   if f.is_file() and f.name!='.cargo-ok':
    raw=f.read_bytes();n='registry/'+root.name+'/'+f.relative_to(root).as_posix();z.writestr(n,raw);inputs.append({'path':n,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'actual_path':str(f)})
 for n in ['stage_registry_triplet.py','verify_registry_triplet.py']:
  f=G/'scripts'/n;raw=f.read_bytes();z.writestr('helpers/'+n,raw);inputs.append({'path':'helpers/'+n,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'actual_path':str(f)})
with zipfile.ZipFile(O/(PRE+'source-inputs.zip')) as z:assert all(hashlib.sha256(z.read(x['path'])).hexdigest()==x['sha256'] for x in inputs)
env=dict(os.environ,CARGO_TARGET_DIR=str(T),CARGO_BUILD_JOBS='1',RUSTUP_TOOLCHAIN='1.97.1',WGPU_BACKEND='dx12');safe={k:env[k] for k in ['CARGO_TARGET_DIR','CARGO_BUILD_JOBS','RUSTUP_TOOLCHAIN','WGPU_BACKEND']}
save('inputs.json',{'recorded_utc':now(),'fixture_source_commit':SHA,'helper_commit':'dcab3700cb8bbf208d1c4206433275c2c97cd715','inputs':inputs,'zip_sha256':h(O/(PRE+'source-inputs.zip')),'selected_registry_packages':selected,'one_wgpu':wgpu[0]['version'],'all_external_packages_registry_only':True,'no_patch_override':True,'rustc':subprocess.check_output(['rustc','+1.97.1','-Vv'],text=True),'environment':safe})
procs=[p.info for p in psutil.process_iter(['pid','name']) if (p.info['name'] or '').lower() in ['cargo.exe','rustc.exe','cl.exe','link.exe','demo-win.exe','turnstone.exe']];assert not procs,procs
cmd=['cargo','+1.97.1','build','--locked','-j1'];r={'command':cmd,'cwd':str(D),'started_utc':now(),'environment':safe,'priority':'BelowNormal'};start=time.monotonic()
with (O/(PRE+'build.stdout.log')).open('xb') as a,(O/(PRE+'build.stderr.log')).open('xb') as b:
 p=subprocess.Popen(cmd,cwd=D,env=env,stdout=a,stderr=b,creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS);r['owned_pid']=p.pid;print('START build',p.pid,flush=True);r['actual_exit_code']=p.wait()
r.update(finished_utc=now(),elapsed_seconds=round(time.monotonic()-start,3));save('build.result.json',r);print('FINISH build',r['actual_exit_code'],flush=True)
assert all(h(Path(x['actual_path']))==x['sha256'] for x in inputs)
if r['actual_exit_code']==0:
 exe=T/'debug/demo-win.exe';save('executable.json',{'recorded_utc':now(),'path':str(exe),'sha256':h(exe),'bytes':exe.stat().st_size,'build_command':cmd,'selected_registry_packages':selected,'frozen_input_zip_sha256':h(O/(PRE+'source-inputs.zip'))})
sys.exit(r['actual_exit_code'])
