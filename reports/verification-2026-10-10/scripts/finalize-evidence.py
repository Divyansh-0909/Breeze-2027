"""Verify report references and original source integrity; index actual artifacts."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone

repo = Path(__file__).resolve().parents[3]
output = Path(__file__).resolve().parents[1]

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + '\n')

before = json.loads((output / 'raw/source-hashes-before.json').read_text())
after = {name: digest(repo / name) if (repo / name).is_file() else None for name in before}
write_json(output / 'raw/source-hashes-after.json', after)
changed = [name for name in before if before[name] != after[name]]
integrity = json.loads((output / 'raw/source-integrity.json').read_text())
integrity.update(changedDuringAudit=changed, productionContentsUnchanged=not changed)
write_json(output / 'raw/source-integrity.json', integrity)
status = subprocess.check_output(['git', 'status', '--short', '--untracked-files=all'], cwd=repo, text=True)
(output / 'raw/git-status-after.txt').write_text(status)
assert not changed, 'Production source changed during verification: ' + ', '.join(changed)

# Ensure the manifest target exists before reference validation; it is populated below.
manifest_path = output / 'raw/artifact-manifest.json'
if not manifest_path.exists():
    write_json(manifest_path, {'status': 'being indexed'})
validation_path = output / 'raw/report-link-verification.json'
if not validation_path.exists():
    write_json(validation_path, {'status': 'references being checked'})
report = output / 'REPORT.md'
links = []
for match in re.finditer(r'!?\[[^\]]*\]\((<[^>]+>|[^)\s]+)(?:\s+"[^"]*")?\)', report.read_text()):
    target = match.group(1).strip('<>')
    if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'):
        continue
    path = (output / target.split('#', 1)[0]).resolve()
    links.append({'target': target, 'resolvedPath': str(path), 'exists': path.exists()})
missing = [link for link in links if not link['exists']]
write_json(output / 'raw/report-link-verification.json', {
    'report': 'REPORT.md', 'reportSHA256': digest(report),
    'relativeReferencesChecked': len(links), 'missing': missing,
    'allRelativeReferencesResolvable': not missing, 'references': links,
})
assert not missing, 'Unresolvable report references: ' + repr(missing)

artifacts = []
for path in sorted(output.rglob('*')):
    if not path.is_file() or path == manifest_path or '__pycache__' in path.parts:
        continue
    artifacts.append({'path': str(path.relative_to(output)), 'bytes': path.stat().st_size, 'sha256': digest(path)})
write_json(manifest_path, {
    'generatedAtUTC': datetime.now(timezone.utc).isoformat(),
    'directory': str(output),
    'manifestExcludesItselfAndPythonCache': True,
    'artifactCount': len(artifacts), 'totalIndexedBytes': sum(a['bytes'] for a in artifacts),
    'artifacts': artifacts,
})
print(json.dumps({'sourceFilesUnchanged': len(before), 'relativeReferencesResolvable': len(links), 'indexedArtifacts': len(artifacts), 'indexedBytes': sum(a['bytes'] for a in artifacts)}))
