from pathlib import Path
import subprocess,hashlib,json,datetime,os,time,psutil,sys
W=Path('C:/Users/mark_/Code/worktrees/wgpu-scry-release');P=Path('C:/Users/mark_/Code/repos/wgpu-scry');O=P/'docs/receipts/scry_release_readiness_20261007';G=Path('C:/Users/mark_/Code/repos/wgpu-graft');D=W/'registry-consumer-scry';prefix='release072-registry-win-'
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def git(root,*a):return subprocess.check_output(['git',*a],cwd=root,text=True).strip()
def save(n,v):
 with (O/(prefix+n)).open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2);f.write('\n')
assert git(W,'rev-parse','HEAD')=='4d8d1d3f8dd450b712960c90b74263a45b46e35b';assert not git(W,'status','--porcelain','--untracked-files=all','--ignored');assert not D.exists()
assert git(G,'rev-parse','HEAD')=='dcab3700cb8bbf208d1c4206433275c2c97cd715'
guards=json.loads((O/'release072-package-inputs.json').read_text(encoding='utf-8'))['primary_dirty_docs_before'];assert all(h(P/r['path'])==r['sha256'] for r in guards)
procs=[p.info for p in psutil.process_iter(['pid','name']) if (p.info['name'] or '').lower() in ['cargo.exe','rustc.exe','cl.exe','link.exe','demo-win.exe','turnstone.exe']];assert not procs,procs
save('initial-guards.json',{'recorded_utc':now(),'source_head':git(W,'rev-parse','HEAD'),'primary_head':git(P,'rev-parse','HEAD'),'worktree_status':'','destination':str(D),'destination_absent':True,'helper_head':git(G,'rev-parse','HEAD'),'primary_dirty_docs':guards,'build_native_processes':procs,'helper_sha256':{n:h(G/'scripts'/n) for n in ['stage_registry_triplet.py','verify_registry_triplet.py']}})
env=dict(os.environ,CARGO_TARGET_DIR='C:/t/cargo-targets/wgpu-scry',CARGO_BUILD_JOBS='1',RUSTUP_TOOLCHAIN='1.97.1',WGPU_BACKEND='dx12',GITHUB_SHA=git(G,'rev-parse','HEAD'),SCRY_SOURCE_REF=git(W,'rev-parse','HEAD'))
def run(label,cmd,cwd):
 t=time.monotonic();r={'command':cmd,'cwd':str(cwd),'started_utc':now(),'priority':'BelowNormal','environment':{k:env[k] for k in ['CARGO_TARGET_DIR','CARGO_BUILD_JOBS','RUSTUP_TOOLCHAIN','WGPU_BACKEND','GITHUB_SHA','SCRY_SOURCE_REF']}}
 with (O/(prefix+label+'.stdout.log')).open('xb') as a,(O/(prefix+label+'.stderr.log')).open('xb') as b:
  proc=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=a,stderr=b,creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS);r['owned_pid']=proc.pid;print('START',label,proc.pid,flush=True);r['actual_exit_code']=proc.wait()
 r.update(finished_utc=now(),elapsed_seconds=round(time.monotonic()-t,3));save(label+'.result.json',r);print('FINISH',label,r['actual_exit_code'],flush=True);assert r['actual_exit_code']==0
run('stage',['python',str(G/'scripts/stage_registry_triplet.py'),'--kind','scry-win','--source',str(W),'--destination',str(D),'--grafting-version','0.6.0','--scrying-version','0.7.2','--welding-version','0.14.1'],W)
run('verify',['python',str(G/'scripts/verify_registry_triplet.py'),'--consumer',str(D),'--receipt-dir',str(O/(prefix+'resolver')),'--grafting-version','0.6.0','--scrying-version','0.7.2','--welding-version','0.14.1'],D)
