from pathlib import Path
import datetime, hashlib, json, os, subprocess, time
import psutil
P=Path('C:/Users/mark_/Code/repos/wgpu-scry/docs/receipts/scry_release_readiness_20261007')
W=Path('C:/Users/mark_/Code/worktrees/wgpu-scry-release')
prefix='m4-unlocked-windows-'
frozen=json.loads((P/(prefix+'executable.json')).read_text(encoding='utf-8'))
inputs=json.loads((P/(prefix+'inputs.json')).read_text(encoding='utf-8'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def now(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
assert sha(Path(frozen['path']))==frozen['sha256']
assert all(sha(W/x['path'])==x['sha256'] for x in inputs['inputs'])
env=dict(os.environ,**inputs['environment']); env['WEBVIEW_READBACK_VALIDATE']='1'
cmd=[frozen['path'],'--probe-only']
record={'source_commit':frozen['source_commit'],'command':cmd,'cwd':str(W),'environment':dict(inputs['environment'],WEBVIEW_READBACK_VALIDATE='1'),'priority':'BelowNormal','timeout_seconds':90,'started_utc':now(),'fixture_selection':'--probe-only selects normal overflow:hidden probe HTML; retained --scripted negative selected scroll fixture and sent wheel/key inputs before fixed-corner readback.'}
start=time.monotonic()
with (P/(prefix+'probe-pixels.stdout.log')).open('xb') as stdout, (P/(prefix+'probe-pixels.stderr.log')).open('xb') as stderr:
    process=subprocess.Popen(cmd,cwd=W,env=env,stdout=stdout,stderr=stderr,creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
    record['owned_pid']=process.pid
    record['observed_priority']=int(psutil.Process(process.pid).nice())
    try: record['actual_exit_code']=process.wait(timeout=90); record['timed_out']=False
    except subprocess.TimeoutExpired:
        process.kill(); record['actual_exit_code']=process.wait(); record['timed_out']=True
record.update(finished_utc=now(),elapsed_seconds=round(time.monotonic()-start,3),executable_sha256=sha(Path(frozen['path'])),stdout_sha256=sha(P/(prefix+'probe-pixels.stdout.log')),stderr_sha256=sha(P/(prefix+'probe-pixels.stderr.log')),source_inputs_unchanged=all(sha(W/x['path'])==x['sha256'] for x in inputs['inputs']))
assert record['source_inputs_unchanged'] and record['executable_sha256']==frozen['sha256']
with (P/(prefix+'probe-pixels.result.json')).open('x',encoding='utf-8',newline='\n') as f: json.dump(record,f,indent=2); f.write('\n')
print(json.dumps(record,indent=2))
raise SystemExit(record['actual_exit_code'])
