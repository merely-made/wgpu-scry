from pathlib import Path
import ctypes,datetime,hashlib,json,os,subprocess,sys,time,psutil,re
W=Path('C:/Users/mark_/Code/worktrees/wgpu-scry-release');D=W/'registry-consumer-scry';P=Path('C:/Users/mark_/Code/repos/wgpu-scry');O=P/'docs/receipts/scry_release_readiness_20261007';T=Path('C:/t/cargo-targets/wgpu-scry');R=T/'native-registry-runtime';E=T/'debug/demo-win.exe';PRE='release072-registry-win-'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):
 with (O/(PRE+n)).open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2);f.write('\n')
inputs=json.loads((O/(PRE+'inputs.json')).read_text(encoding='utf-8'));exe=json.loads((O/(PRE+'executable.json')).read_text(encoding='utf-8'));guards=json.loads((O/(PRE+'initial-guards.json')).read_text(encoding='utf-8'))
assert h(E)==exe['sha256'];assert all(h(Path(x['actual_path']))==x['sha256'] for x in inputs['inputs']);assert all(h(P/x['path'])==x['sha256'] for x in guards['primary_dirty_docs'])
procs=[p.info for p in psutil.process_iter(['pid','name']) if (p.info['name'] or '').lower() in ['cargo.exe','rustc.exe','cl.exe','link.exe','demo-win.exe','turnstone.exe']];assert not procs,procs
assert not R.exists();R.mkdir();(R/'CACHEDIR.TAG').write_text('Signature: 8a477f597d28d172789f06886806bc55\n# Registry-only Scry0.7.2 generated WebView2 runtime cache\n',encoding='utf-8');(R/'owner.json').write_text(json.dumps({'owner':'shared_weld_input','purpose':'Scry0.7.2 registry-only Windows consumer native gates','source_commit':guards['source_head']}),encoding='utf-8')
env=dict(os.environ,CARGO_TARGET_DIR=str(T),CARGO_BUILD_JOBS='1',RUSTUP_TOOLCHAIN='1.97.1',WGPU_BACKEND='dx12',TEMP=str(R),TMP=str(R),WEBVIEW_READBACK_VALIDATE='0')
safe=['CARGO_TARGET_DIR','CARGO_BUILD_JOBS','RUSTUP_TOOLCHAIN','WGPU_BACKEND','TEMP','TMP','WEBVIEW_READBACK_VALIDATE'];kernel=ctypes.WinDLL('kernel32',use_last_error=True);kernel.OpenProcess.argtypes=[ctypes.c_ulong,ctypes.c_bool,ctypes.c_ulong];kernel.OpenProcess.restype=ctypes.c_void_p;kernel.GetExitCodeProcess.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_ulong)];kernel.CloseHandle.argtypes=[ctypes.c_void_p];results=[]
def run(label,cmd,pixel=False):
 actual=dict(env,WEBVIEW_READBACK_VALIDATE='1') if pixel else env;t=time.monotonic();native={};limits=[];r={'command':cmd,'cwd':str(D),'started_utc':now(),'environment':{k:actual[k] for k in safe},'priority':'BelowNormal','executable_sha256':exe['sha256'],'default_per_mode_timeout_seconds':90,'timed_out':False}
 assert h(E)==exe['sha256']
 with (O/(PRE+label+'.stdout.log')).open('xb') as a,(O/(PRE+label+'.stderr.log')).open('xb') as b:
  proc=subprocess.Popen(cmd,cwd=D,env=actual,stdout=a,stderr=b,creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS);r['owned_pid']=proc.pid;print('START',label,proc.pid,flush=True)
  while proc.poll() is None:
   try:
    candidates=[psutil.Process(proc.pid)] if pixel else psutil.Process(proc.pid).children(recursive=True)
    for child in candidates:
     if child.name().lower()!='demo-win.exe' or child.pid in native:continue
     handle=kernel.OpenProcess(0x101000,False,child.pid);native[child.pid]={'pid':child.pid,'command':child.cmdline(),'observed_priority':int(child.nice()),'observed_utc':now(),'handle':handle}
   except (psutil.NoSuchProcess,psutil.AccessDenied) as e:limits.append({'utc':now(),'reason':type(e).__name__})
   if pixel and time.monotonic()-t>=90:proc.kill();r['timed_out']=True;break
   time.sleep(.02)
  r['actual_exit_code']=proc.wait()
 for x in native.values():
  handle=x.pop('handle');code=ctypes.c_ulong(259)
  if handle and kernel.GetExitCodeProcess(handle,ctypes.byref(code)):x['actual_exit_code']=code.value
  else:x['observer_limitation']='Own process access/exit race; maintained script exit/mode result authoritative'
  if handle:kernel.CloseHandle(handle)
 r.update(finished_utc=now(),elapsed_seconds=round(time.monotonic()-t,3),native_process_observations=list(native.values()),observer_limitations=limits,stdout_sha256=h(O/(PRE+label+'.stdout.log')),stderr_sha256=h(O/(PRE+label+'.stderr.log')));save(label+'.result.json',r);results.append(r);print('FINISH',label,r['actual_exit_code'],r['elapsed_seconds'],flush=True);assert h(E)==exe['sha256'];return r
run('pixels',[str(E),'--pixel-test'],True)
for suite in ['Core','Capture']:run(suite.lower(),['pwsh','-NoLogo','-NoProfile','-File',str(D/'scripts/test-win.ps1'),'-Suite',suite,'-SkipBuild'])
assert all(h(Path(x['actual_path']))==x['sha256'] for x in inputs['inputs']);assert all(h(P/x['path'])==x['sha256'] for x in guards['primary_dirty_docs'])
files=[f for f in R.rglob('*') if f.is_file()];save('native-summary.json',{'recorded_utc':now(),'executable_sha256':h(E),'all_native_command_exits_zero':all(x['actual_exit_code']==0 and not x['timed_out'] for x in results),'results':results,'source_inputs_unchanged':True,'primary_dirty_docs_unchanged':True,'runtime_cache':str(R),'runtime_cache_file_count':len(files),'runtime_cache_bytes':sum(f.stat().st_size for f in files),'runtime_cache_marker_sha256':h(R/'CACHEDIR.TAG'),'runtime_profiles_retained_for_evidence_review':True})
sys.exit(0 if all(x['actual_exit_code']==0 and not x['timed_out'] for x in results) else 1)
