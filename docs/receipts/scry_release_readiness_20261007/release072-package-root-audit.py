import hashlib
import json
import subprocess
import tarfile
import tomllib
from datetime import datetime, timezone
from pathlib import Path

repo = Path(r'C:\Users\mark_\Code\repos\wgpu-scry')
packet = repo / 'docs/receipts/scry_release_readiness_20261007'
archive = packet / 'release072-package-verify.crate'
commit = '4d8d1d3f8dd450b712960c90b74263a45b46e35b'
with tarfile.open(archive, 'r:gz') as tar:
    members = tar.getmembers()
    def read(name):
        return tar.extractfile('scrying-0.7.2/' + name).read()
    manifest = tomllib.loads(read('Cargo.toml').decode())
    vcs = json.loads(read('.cargo_vcs_info.json'))
    assert manifest['package']['version'] == '0.7.2'
    assert manifest['package']['rust-version'] == '1.92'
    assert vcs['git']['sha1'] == commit and not vcs['git'].get('dirty', False)
    assert manifest['dependencies']['grafting']['version'] == '0.6.0'
    assert 'serde_json' in manifest['target']['cfg(target_os = "windows")']['dependencies']
    rust = [m.name.split('/', 1)[1] for m in members if m.name.endswith('.rs')]
    for name in rust:
        blob = subprocess.check_output(['git', '-C', str(repo), 'show', f'{commit}:scrying/{name}'])
        assert read(name).replace(b'\r\n', b'\n') == blob.replace(b'\r\n', b'\n'), name
    assert 'src/latest_image_sample.rs' in rust
    assert len(members) == 93
same_archives = archive.read_bytes() == (packet / 'release072-package-dry-run.crate').read_bytes()
assert same_archives
result = {
    'recorded_utc': datetime.now(timezone.utc).isoformat(),
    'source_commit': commit, 'version': '0.7.2', 'member_count': len(members),
    'rust_members_match_committed_source': len(rust), 'msrv': '1.92',
    'published_grafting_dependency': '0.6.0', 'windows_json_dependency_present': True,
    'vcs_clean': True, 'package_and_dry_run_archives_identical': same_archives,
    'archive_bytes': archive.stat().st_size,
    'archive_sha256': hashlib.sha256(archive.read_bytes()).hexdigest(),
    'actual_publication_performed': False,
}
(packet / 'release072-package-root-audit.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
print(json.dumps(result))
