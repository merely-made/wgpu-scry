"""Integrate the qualified owned overlay and a version-only release change."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

primary = Path(r'C:\Users\mark_\Code\repos\wgpu-scry')
worktree = Path(r'C:\Users\mark_\Code\worktrees\wgpu-scry-release')
receipts = primary / 'docs/receipts/scry_release_readiness_20261007'

def sha(data):
    return hashlib.sha256(data).hexdigest()

def git(*args):
    return subprocess.check_output(['git', '-C', str(primary), *args])

guard = json.loads((receipts / 'm4-unlocked-windows-initial-guards.json').read_text(encoding='utf-8-sig'))
inputs = json.loads((receipts / 'm4-unlocked-windows-pixel-inputs.json').read_text(encoding='utf-8-sig'))
paths = inputs['owned_changed_paths']
assert len(paths) == 9, paths
assert git('rev-parse', 'HEAD').decode().strip() == inputs['source_commit']
for item in guard['dirty_docs_before']:
    data = (primary / item['path']).read_bytes()
    assert len(data) == item['bytes'] and sha(data) == item['sha256'], item['path']
assert set(git('diff', '--name-only').decode().splitlines()) == {x['path'] for x in guard['dirty_docs_before']}
record = []
input_map = {x['path']: x for x in inputs['inputs']}
for path in paths:
    data = (worktree / path).read_bytes()
    assert sha(data) == input_map[path]['sha256'], path
    before = (primary / path).read_bytes()
    (primary / path).write_bytes(data)
    record.append({'path': path, 'baseline_sha256': sha(before), 'qualified_sha256': sha(data)})

manifest = primary / 'scrying/Cargo.toml'
data = manifest.read_bytes()
assert data.count(b'version = "0.7.1"') == 1
manifest.write_bytes(data.replace(b'version = "0.7.1"', b'version = "0.7.2"', 1))
lock = primary / 'Cargo.lock'
data = lock.read_bytes()
needle = b'name = "scrying"\nversion = "0.7.1"'
assert data.count(needle) == 1
lock.write_bytes(data.replace(needle, b'name = "scrying"\nversion = "0.7.2"', 1))
for item in guard['dirty_docs_before']:
    assert sha((primary / item['path']).read_bytes()) == item['sha256']
result = {
    'recorded_utc': datetime.now(timezone.utc).isoformat(),
    'qualified_base_commit': inputs['source_commit'],
    'qualified_overlay': record,
    'version_only_delta': ['scrying/Cargo.toml', 'Cargo.lock'],
    'source_version': '0.7.2',
    'eight_preexisting_dirty_docs_unchanged': True,
    'publication_performed': False,
}
(receipts / 'release072-integration.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
print(json.dumps({'integrated_paths': paths, 'source_version': '0.7.2', 'dirty_docs_preserved': 8}))
