"""Verify every baseline payload and retain only the two authorized source edits."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path.cwd()
OUT = ROOT / 'reports/recovery-phase2-c8-material-2026-10-19/raw'
rows = json.loads((OUT / 'starting-file-hashes.json').read_text())
allowed = {'components/immersive/ImmersiveShell.tsx', 'components/immersive/QuarryPerimeter.tsx'}
identical, changed, unexpected = 0, [], []
for row in rows:
    target = ROOT / row['path']
    if not target.is_file():
        unexpected.append({'path': row['path'], 'reason': 'missing'})
        continue
    with target.open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    if digest == row['sha256']:
        identical += 1
    else:
        result = {'path': row['path'], 'beforeSHA256': row['sha256'], 'afterSHA256': digest,
                  'beforeBytes': row['bytes'], 'afterBytes': target.stat().st_size}
        (changed if row['path'] in allowed else unexpected).append(result)
read_git = lambda *args: subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
result = {'status': 'FAIL' if unexpected else 'PASS', 'startingFiles': len(rows),
          'byteIdentical': identical, 'authorizedApplicationChanges': changed,
          'unexpectedChanges': unexpected, 'branch': read_git('branch', '--show-current'),
          'HEAD': read_git('rev-parse', 'HEAD'), 'gitStatus': read_git('status', '--short')}
assert result['branch'] == 'codex/navigation-board'
assert result['HEAD'] == '14f36da1a9b79a3b4926f7445bf0cde6c6c8f767'
(OUT / 'preservation.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({key: value for key, value in result.items() if key != 'gitStatus'}, indent=2))
raise SystemExit(bool(unexpected))
