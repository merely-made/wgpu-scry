import hashlib
import json
import os
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

repo = Path(r'C:\Users\mark_\Code\repos\wgpu-scry')
worktree = Path(r'C:\Users\mark_\Code\worktrees\wgpu-scry-release')
packet = repo / 'docs/receipts/scry_release_readiness_20261007'
commit = '4d8d1d3f8dd450b712960c90b74263a45b46e35b'
assert subprocess.check_output(['git', '-C', str(worktree), 'rev-parse', 'HEAD']).decode().strip() == commit
assert not subprocess.check_output(['git', '-C', str(worktree), 'status', '--porcelain'])
audit = json.loads((packet / 'release072-package-root-audit.json').read_text())
assert audit['source_commit'] == commit and audit['version'] == '0.7.2'
msrv = json.loads((packet / 'release072-msrv-result.json').read_text(encoding='utf-8-sig'))
assert msrv['head_sha'] == commit and msrv['required_jobs_passed'] == 12
assert msrv['run_conclusion'] == 'success'
env = os.environ.copy()
env['CARGO_TARGET_DIR'] = r'C:\t\cargo-targets\wgpu-scry'
env['CARGO_BUILD_JOBS'] = '1'
env['CARGO_NET_GIT_FETCH_WITH_CLI'] = 'true'
command = ['cargo', '+1.92.0', 'publish', '--locked', '-p', 'scrying', '-j1']
started = datetime.now(timezone.utc).isoformat()
t = time.monotonic()
with (packet / 'release072-publish.stdout.log').open('wb') as stdout, (packet / 'release072-publish.stderr.log').open('wb') as stderr:
    process = subprocess.Popen(command, cwd=worktree, env=env, stdout=stdout, stderr=stderr,
        creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS | subprocess.CREATE_NO_WINDOW)
    code = process.wait()
result = {
    'recorded_utc': datetime.now(timezone.utc).isoformat(), 'started_utc': started,
    'command': command, 'source_commit': commit, 'version': '0.7.2',
    'actual_exit_code': code, 'elapsed_seconds': round(time.monotonic() - t, 3),
    'source_status_after': subprocess.check_output(['git', '-C', str(worktree), 'status', '--porcelain']).decode(),
    'qualified_archive_sha256': audit['archive_sha256'],
    'generated_archive_sha256_after': hashlib.sha256(Path(r'C:\t\cargo-targets\wgpu-scry\package\scrying-0.7.2.crate').read_bytes()).hexdigest(),
    'priority': 'BelowNormal', 'jobs': 1,
}
(packet / 'release072-publish-result.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result))
raise SystemExit(code)
