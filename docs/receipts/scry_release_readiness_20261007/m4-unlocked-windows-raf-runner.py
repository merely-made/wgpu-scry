from pathlib import Path
import ctypes, datetime, hashlib, json, os, re, subprocess, sys, time, zipfile
import psutil

REPO = Path('C:/Users/mark_/Code/worktrees/wgpu-scry-release')
PRIMARY = Path('C:/Users/mark_/Code/repos/wgpu-scry')
OUT = PRIMARY / 'docs/receipts/scry_release_readiness_20261007'
TARGET = Path('C:/t/cargo-targets/wgpu-scry')
RUNTIME = TARGET / 'native-render-tick-runtime'
SHA = '4771072a6827695dfaba9db104cd48b87e6cd543'
EXE = TARGET / 'debug/demo-win.exe'
PREFIX = 'm4-unlocked-windows-raf-'
OWNED = {'Cargo.lock','scrying/Cargo.toml','scrying/src/webview2_composition_producer.rs','scrying/src/webview2_composition_producer/navigation.rs','demo-win/src/main.rs','demo-win/src/probe.rs','demo-win/src/smokes/network.rs','scripts/test-win.ps1'}
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args): return subprocess.check_output(['git', *args], cwd=REPO, text=True).strip()
def save(name, value):
    with (OUT / (PREFIX + name)).open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2); f.write('\n')

assert git('rev-parse', 'HEAD') == SHA and set(git('diff','--name-only').splitlines()) == OWNED
with (OUT/(PREFIX+'source.patch')).open('xb') as f: f.write(subprocess.check_output(['git','diff','--binary'],cwd=REPO))
assert not RUNTIME.exists()
RUNTIME.mkdir()
(RUNTIME / 'CACHEDIR.TAG').write_bytes(b'Signature: 8a477f597d28d172789f06886806bc55\n# Owned standalone Scry Windows native qualification profiles and temporary files.\n')
(RUNTIME / 'owner.json').write_text(json.dumps({'owner':'shared_weld_input', 'source_commit':SHA, 'purpose':'Bounded acknowledged-render-tick candidate, hidden navigation control, Core23/Capture2 and unchanged startup pixel validation', 'created_utc':now()}), encoding='utf-8')
env = dict(os.environ, CARGO_TARGET_DIR=str(TARGET), CARGO_BUILD_JOBS='1', RUSTUP_TOOLCHAIN='1.97.1', WGPU_BACKEND='dx12', TEMP=str(RUNTIME), TMP=str(RUNTIME), WEBVIEW_READBACK_VALIDATE='0')
safe_keys = ['CARGO_TARGET_DIR','CARGO_BUILD_JOBS','RUSTUP_TOOLCHAIN','WGPU_BACKEND','TEMP','TMP','WEBVIEW_READBACK_VALIDATE','RUSTFLAGS','CARGO_ENCODED_RUSTFLAGS','WGPU_ADAPTER_NAME']
inputs = []
archive = OUT / (PREFIX + 'source-inputs.zip')
with zipfile.ZipFile(archive, 'x', compression=zipfile.ZIP_DEFLATED) as z:
    for name in git('ls-files').splitlines():
        if name.startswith('docs/receipts/'): continue
        raw = (REPO / name).read_bytes()
        inputs.append({'path':name, 'bytes':len(raw), 'sha256':hashlib.sha256(raw).hexdigest()})
        z.writestr(name, raw)
with zipfile.ZipFile(archive) as z:
    assert all(hashlib.sha256(z.read(x['path'])).hexdigest() == x['sha256'] for x in inputs)
save('inputs.json', {'recorded_utc':now(), 'source_commit':SHA, 'source_tree':git('rev-parse','HEAD^{tree}'), 'clean_tracked_source':False, 'owned_uncommitted_candidate':True, 'owned_changed_paths':sorted(OWNED), 'patch_sha256':digest(OUT/(PREFIX+'source.patch')), 'input_selection':'Every Git-tracked file except historical docs/receipts; exact worktree raw bytes including source, Cargo, fixture/assets, scripts and documentation', 'inputs':inputs, 'archive':archive.name, 'archive_sha256':digest(archive), 'rustc':subprocess.check_output(['rustc','+1.97.1','-Vv'],text=True), 'cargo':subprocess.check_output(['cargo','+1.97.1','-V'],text=True), 'environment':{k:env[k] for k in safe_keys if k in env}, 'priority':'BELOW_NORMAL_PRIORITY_CLASS', 'runtime_cache_marker_sha256':digest(RUNTIME/'CACHEDIR.TAG'), 'script_default_timeout_seconds':90, 'native_scope':'Standalone bounded uncommitted render-tick candidate on477. New maintained hidden-navigation Core mode makes23; Capture2 unchanged. Pixel oracle/fixture/tolerance/acquire count unchanged; explicit caller paint wait5s added.'})

kernel = ctypes.WinDLL('kernel32', use_last_error=True)
kernel.OpenProcess.argtypes = [ctypes.c_ulong, ctypes.c_bool, ctypes.c_ulong]
kernel.OpenProcess.restype = ctypes.c_void_p
kernel.GetExitCodeProcess.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
kernel.CloseHandle.argtypes = [ctypes.c_void_p]
results = []

def run(label, cmd, pixel=False, observe=False):
    actual_env = dict(env, WEBVIEW_READBACK_VALIDATE='1') if pixel else env
    result = {'label':label, 'command':cmd, 'cwd':str(REPO), 'source_commit':SHA, 'started_utc':now(), 'environment':{k:actual_env[k] for k in safe_keys if k in actual_env}, 'priority':'BelowNormal', 'default_per_mode_timeout_seconds':90 if label in ['core','capture'] else None}
    assert git('rev-parse','HEAD') == SHA and set(git('diff','--name-only').splitlines()) == OWNED
    start = time.monotonic(); native = {}; limitations = []
    with (OUT/(PREFIX+label+'.stdout.log')).open('xb') as stdout, (OUT/(PREFIX+label+'.stderr.log')).open('xb') as stderr:
        process = subprocess.Popen(cmd, cwd=REPO, env=actual_env, stdout=stdout, stderr=stderr, creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        result['owned_pid'] = process.pid
        print('START',label,process.pid,now(),flush=True)
        while process.poll() is None:
            if observe:
                try:
                    candidates = [psutil.Process(process.pid)] if pixel else psutil.Process(process.pid).children(recursive=True)
                    for child in candidates:
                        if child.name().lower() != 'demo-win.exe' or child.pid in native: continue
                        handle = kernel.OpenProcess(0x101000, False, child.pid)
                        native[child.pid] = {'pid':child.pid, 'command':child.cmdline(), 'observed_priority':int(child.nice()), 'observed_utc':now(), 'handle':handle}
                except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                    limitations.append({'observed_utc':now(), 'reason':type(e).__name__, 'detail':'Own process-tree observer exited/access race; native script result remains authoritative.'})
            if pixel and time.monotonic()-start >= 90:
                process.kill(); result['timed_out']=True; break
            time.sleep(0.1)
        result['actual_exit_code'] = process.wait()
    for record in native.values():
        handle = record.pop('handle')
        exit_code = ctypes.c_ulong(259)
        if handle and kernel.GetExitCodeProcess(handle, ctypes.byref(exit_code)):
            record['actual_exit_code'] = exit_code.value
        else: record['observer_limitation']='No readable own child handle at final observation'
        if handle: kernel.CloseHandle(handle)
    result.update(finished_utc=now(), elapsed_seconds=round(time.monotonic()-start,3), timed_out=result.get('timed_out',False), native_process_observations=list(native.values()), observer_limitations=limitations, final_source_commit=git('rev-parse','HEAD'), tracked_status=git('status','--porcelain','--untracked-files=no'), stdout_sha256=digest(OUT/(PREFIX+label+'.stdout.log')), stderr_sha256=digest(OUT/(PREFIX+label+'.stderr.log')))
    if observe: result['executable_sha256'] = digest(EXE)
    save(label+'.result.json',result); results.append(result)
    print('FINISH',label,result['actual_exit_code'],result['elapsed_seconds'],flush=True)
    assert result['final_source_commit'] == SHA and set(git('diff','--name-only').splitlines()) == OWNED
    return result

build = run('build',['cargo','+1.97.1','build','--locked','-p','demo-win','-j1'])
if build['actual_exit_code'] != 0: sys.exit(build['actual_exit_code'])
exe_hash = digest(EXE)
save('executable.json', {'recorded_utc':now(), 'source_commit':SHA, 'path':str(EXE), 'bytes':EXE.stat().st_size, 'sha256':exe_hash, 'actual_build_command':build['command']})
run('pixels',[str(EXE),'--probe-only'],pixel=True,observe=True)
for suite in ['Core','Capture']:
    run(suite.lower(),['pwsh','-NoLogo','-NoProfile','-File',str(REPO/'scripts/test-win.ps1'),'-Suite',suite,'-SkipBuild'],observe=True)
    assert digest(EXE) == exe_hash
tests = run('parser-tests',['cargo','+1.97.1','test','--locked','-p','scrying','--lib','webview2_composition_producer::navigation::tests','-j1'])
if tests['actual_exit_code'] != 0: sys.exit(tests['actual_exit_code'])
for row in ['28','29','30']:
    run('msrv-wgpu-'+row,['cargo','+1.92.0','check','--locked','-p','scrying','--lib','--no-default-features','--features','wgpu-'+row,'-j1'])
assert digest(EXE) == exe_hash
changed = [x['path'] for x in inputs if digest(REPO/x['path']) != x['sha256']]
save('source-after.json', {'recorded_utc':now(), 'source_commit':git('rev-parse','HEAD'), 'tracked_status':git('status','--porcelain'), 'input_count':len(inputs), 'changed_inputs':changed, 'executable_sha256':digest(EXE), 'all_command_exits_zero':all(x['actual_exit_code']==0 for x in results), 'results':[{'label':x['label'],'actual_exit_code':x['actual_exit_code'],'timed_out':x['timed_out']} for x in results], 'runtime_cache':str(RUNTIME), 'runtime_cache_retained_for_review':True})
sys.exit(0 if not changed and all(x['actual_exit_code']==0 and not x['timed_out'] for x in results) else 1)
