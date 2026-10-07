"""Archive completed registry jobs and audit their resolved consumer graphs."""
import hashlib
import io
import json
from pathlib import Path
import subprocess
import zipfile

packet = Path(__file__).resolve().parent
listing = json.loads((packet / "release072-registry-corrected-artifacts.json").read_text(encoding="utf-8-sig"))
expected = {"grafting": "0.6.0", "scrying": "0.7.2", "welding": "0.14.1"}
facts = []
for artifact in listing["artifacts"]:
    name = artifact["name"]
    assert name in {"registry-triplet-metal-intel", "registry-triplet-metal-m4", "registry-triplet-radv"}, name
    assert artifact["workflow_run"]["head_sha"] == "e8ffee2d6b680154cae645d54a340116f08acb5d"
    raw = subprocess.check_output(["gh", "api", f"repos/merely-made/wgpu-graft/actions/artifacts/{artifact['id']}/zip"])
    archive = packet / f"release072-registry-corrected-{name}.zip"
    archive.write_bytes(raw)
    row = {"artifact_id": artifact["id"], "artifact_name": name,
           "archive": archive.name, "bytes": len(raw),
           "sha256": hashlib.sha256(raw).hexdigest(), "consumers": []}
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        assert z.testzip() is None
        members = z.namelist()
        for kind in ("graft", "scry", "weld"):
            matches = [p for p in members if p.endswith(f"receipts/{kind}/metadata.json")]
            assert len(matches) == 1, (name, kind, matches)
            metadata = json.loads(z.read(matches[0]))
            packages = metadata["packages"]
            selected = []
            for crate, version in expected.items():
                matching = [p for p in packages if p["name"] == crate]
                assert len(matching) == 1, (name, kind, crate)
                p = matching[0]
                assert p["version"] == version and p["source"].startswith("registry+"), p
                selected.append({"name": crate, "version": version, "source": p["source"]})
            gpu = [p for p in packages if p["name"] == "wgpu"]
            assert len(gpu) == 1
            assert gpu[0]["version"] == ("29.0.4" if kind == "graft" else "30.0.1")
            external = [p for p in packages if p.get("source") and not p["source"].startswith("registry+")]
            if kind != "graft":
                assert not external, (name, kind, external)
            else:
                assert len(external) == 57
                assert all(p["source"].startswith("git+https://github.com/servo/servo?") or
                           p["source"].startswith("git+https://github.com/jamienicol/glslopt-rs?") for p in external)
            row["consumers"].append({"kind": kind, "selected_registry_packages": selected,
                                     "one_wgpu": gpu[0]["version"],
                                     "external_non_registry_count": len(external),
                                     "metadata_member": matches[0],
                                     "metadata_sha256": hashlib.sha256(z.read(matches[0])).hexdigest()})
    facts.append(row)
assert len(facts) == 3
(packet / "release072-registry-corrected-audit.json").write_text(json.dumps(facts, indent=2) + "\n", encoding="utf-8")
print("Archived and independently verified all nine consumer graphs from three completed registry jobs.")
