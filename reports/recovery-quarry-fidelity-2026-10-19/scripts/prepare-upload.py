"""Build a non-secret upload ledger only after archives and restoration pass."""
from pathlib import Path
import json, hashlib, mimetypes, datetime

ROOT = Path.cwd()
R = ROOT / 'reports/recovery-quarry-fidelity-2026-10-19'
W = Path('/workspace/recovery-fidelity/2026-10-19/checkpoint')
folders = json.loads((W.parent / 'drive-folders.json').read_text())
assert json.loads((W / 'restore-verification.json').read_text())['status'] == 'PASS'
index = json.loads((W / 'checkpoint-index.json').read_text())
manifest = W / 'upload-manifest.json'
assert not manifest.exists(), 'Never reset an existing upload/verification ledger'
files = []

def add(path, role):
    assert path.is_file()
    with path.open('rb') as stream: digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    assert not any(r['name'] == path.name for r in files)
    files.append({'name': path.name, 'path': str(path), 'bytes': path.stat().st_size, 'sha256': digest,
                  'parent_id': folders[role], 'role': role,
                  'mime_type': mimetypes.guess_type(path.name)[0] or 'application/octet-stream', 'status': 'pending'})

for row in index['archives']:
    role = 'review' if row['group'] == 'C' else 'verification' if row['group'] == 'D' else 'checkpoint'
    add(W / row['name'], role)
for name in ['fidelity-file-manifest.json', 'DEPENDENCIES.json', 'checkpoint-index.json', 'SHA256SUMS.txt', 'restore-verification.json', 'restored-master-read.log']:
    add(W / name, 'verification')
for name in ['RESTORE-FIDELITY.md', 'apply-fidelity.py', 'REVIEW-START.html']:
    add(W / name, 'checkpoint')
for name in ['Gullyverse-Quarry-Fidelity-Phone-Review.pdf', 'Gullyverse-Quarry-Fidelity-Full-Screenshots.pdf', 'Gullyverse-Quarry-Fidelity-Technical-Report.pdf']:
    add(R / name, 'review')
add(ROOT / 'docs/gullyverse-recovery-quarry-fidelity-correction.md', 'review')
for name in ['visitor-journey.mp4', 'automatic-lod-inspection.mp4']: add(R / 'videos' / name, 'review')
for name in ['stage-fidelity-matrix.csv', 'matched-pose-verification.json', 'review-package.json']: add(R / name, 'review')
for name in ['pdf-review-verification.json', 'browser-final-assessment.json', 'source-validation-summary.json', 'survey-accounting.json']:
    add(R / 'raw' / name, 'verification')
manifest.write_text(json.dumps({'version': 'quarry-fidelity-correction', 'createdUTC': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                                'folder': folders['parent'], 'sealed': False, 'verificationStatus': 'pending', 'files': files}, indent=2) + '\n')
print(json.dumps({'files': len(files), 'bytes': sum(r['bytes'] for r in files), 'allPendingFullDownloadBack': True}))
