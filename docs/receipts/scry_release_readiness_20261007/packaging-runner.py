from pathlib import Path
import datetime, hashlib, json, os, subprocess, sys, time

repo = Path('C:/Users/mark_/Code/worktrees/wgpu-scry-release')
out = Path('C:/Users/mark_/Code/repos/wgpu-scry/docs/receipts/scry_release_readiness_20261007')
target = Path('C:/t/cargo-targets/wgpu-scry')
sha = '2c3ebd24118851cf6125cfb193f55aab20e3ad67'
def stamp(): return datetime.datetime.now(datetime.timezone.utc).isoformat()
def git(*args): return subprocess.check_output(['git', *args], cwd=repo, text=True).strip()
def save(name, value):
    path = out / name
    assert not path.exists(), name
    path.write_bytes((json.dumps(value, indent=2) + '\n').encode())
assert git('rev-parse', 'HEAD') == sha and not git('status', '--porcelain')
target.mkdir(exist_ok=True)
marker = target / 'CACHEDIR.TAG'
assert not marker.exists()
marker.write_bytes(b'Signature: 8a477f597d28d172789f06886806bc55\n# Reusable wgpu-scry Cargo target, owned release-readiness gate 2026-10-07.\n')
inventory = [{'path': p, 'sha256': hashlib.sha256((repo / p).read_bytes()).hexdigest()} for p in git('ls-files').splitlines()]
env = dict(os.environ, CARGO_TARGET_DIR=str(target), CARGO_BUILD_JOBS='1')
safe_env = {k: env[k] for k in ['CARGO_TARGET_DIR', 'CARGO_BUILD_JOBS', 'RUSTFLAGS', 'CARGO_ENCODED_RUSTFLAGS', 'RUSTUP_TOOLCHAIN'] if k in env}
save('packaging-inputs.json', {'recorded_utc': stamp(), 'source_sha': sha, 'source_tree': git('rev-parse', 'HEAD^{tree}'), 'tracked_clean': True, 'tracked_inputs': inventory, 'environment': safe_env, 'toolchain': subprocess.check_output(['rustc', '+1.92.0', '-Vv'], text=True), 'priority': 'BELOW_NORMAL_PRIORITY_CLASS', 'target': str(target), 'target_marker_sha256': hashlib.sha256(marker.read_bytes()).hexdigest(), 'scope': 'Windows MSRV library rows and reversible exact-source package verification; no version bump or publication.'})
gates = [('list', ['cargo', '+1.92.0', 'package', '--locked', '-p', 'scrying', '--list']), ('package', ['cargo', '+1.92.0', 'package', '--locked', '-p', 'scrying', '-j1'])]
gates += [('wgpu-' + row, ['cargo', '+1.92.0', 'check', '--locked', '-p', 'scrying', '--lib', '--no-default-features', '--features', 'wgpu-' + row, '-j1']) for row in ['28', '29', '30']]
results = []
for name, cmd in gates:
    prefix = 'packaging-' + name
    result = {'command': cmd, 'cwd': str(repo), 'source_sha': sha, 'started_utc': stamp(), 'environment': safe_env, 'priority': 'BelowNormal'}
    start = time.monotonic()
    with (out / (prefix + '.stdout.log')).open('xb') as stdout, (out / (prefix + '.stderr.log')).open('xb') as stderr:
        process = subprocess.Popen(cmd, cwd=repo, env=env, stdout=stdout, stderr=stderr, creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        print('START', name, 'PID', process.pid, result['started_utc'], flush=True)
        result['owned_pid'] = process.pid
        result['actual_exit_code'] = process.wait()
    result.update(finished_utc=stamp(), elapsed_seconds=round(time.monotonic()-start, 3), final_source_sha=git('rev-parse', 'HEAD'), tracked_status=git('status', '--porcelain', '--untracked-files=no'), stdout_sha256=hashlib.sha256((out/(prefix+'.stdout.log')).read_bytes()).hexdigest(), stderr_sha256=hashlib.sha256((out/(prefix+'.stderr.log')).read_bytes()).hexdigest())
    save(prefix+'.result.json', result)
    results.append(result)
    print('FINISH', name, result['actual_exit_code'], result['elapsed_seconds'], flush=True)
    # Keep independent checks after a package failure; preserve every actual exit.
    assert result['final_source_sha'] == sha and not result['tracked_status']
changes = [p['path'] for p in inventory if hashlib.sha256((repo/p['path']).read_bytes()).hexdigest() != p['sha256']]
save('packaging-local-summary.json', {'recorded_utc': stamp(), 'source_sha': sha, 'gates': results, 'all_exit_zero': all(x['actual_exit_code'] == 0 for x in results), 'tracked_input_changes': changes, 'final_tracked_status': git('status','--porcelain','--untracked-files=no')})
sys.exit(0 if all(x['actual_exit_code']==0 for x in results) and not changes else 1)
