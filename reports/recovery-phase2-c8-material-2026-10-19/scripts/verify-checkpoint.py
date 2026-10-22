#!/usr/bin/env python3
"""Extract and independently restore all Phase 2 archives on a NEW Phase 1 copy."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def link_or_copy(source, target):
    try:
        os.link(source, target)
        return target
    except OSError:
        return shutil.copyfile(source, target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase1', type=Path, required=True, help='Previously verified Phase 1 project directory')
    parser.add_argument('--checkpoint', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True, help='NEW nonexistent directory')
    args = parser.parse_args()
    checkpoint, source, destination = args.checkpoint.resolve(), args.phase1.resolve(), args.out.resolve()
    if destination.exists():
        raise ValueError('Never overwrite a prior restoration test')
    destination.mkdir(parents=True)
    overlay = destination / 'overlay'
    overlay.mkdir()
    index = json.loads((checkpoint / 'checkpoint-index.json').read_text())
    members, archives = set(), []
    for row in index['archives']:
        path = checkpoint / row['name']
        assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256']
        with zipfile.ZipFile(path) as archive:
            assert archive.testzip() is None
            for item in archive.infolist():
                name = Path(item.filename)
                assert not name.is_absolute() and '..' not in name.parts
                assert item.filename not in members, 'Overlapping archive member'
                members.add(item.filename)
            archive.extractall(overlay)
        archives.append({**row, 'CRC': 'PASS', 'extraction': 'PASS'})
    manifest = json.loads((overlay / 'recovery-phase2/phase2-file-manifest.json').read_text())
    restored = destination / 'project'
    # Atomic replacements in apply-phase2 preserve all hard-linked references.
    shutil.copytree(source, restored, copy_function=link_or_copy)
    command = [sys.executable, str(overlay / 'apply-phase2.py'), '--base', str(restored)]
    first = subprocess.run(command, cwd=overlay, text=True, capture_output=True, check=True)
    second = subprocess.run(command, cwd=overlay, text=True, capture_output=True, check=True)
    for row in manifest['files']:
        path = restored / row['path']
        assert path.stat().st_size == row['bytes'] and sha(path) == row['sha256']
        if row['beforeSHA256'] and (source / row['path']).is_file():
            assert sha(source / row['path']) == row['beforeSHA256'], 'Phase 1 source was altered'
    # Prove the full preflight refuses unrelated edits before writing new files.
    conflict = destination / 'conflict-test'
    for row in manifest['requiredBaselineFiles']:
        target = conflict / row['path']; target.parent.mkdir(parents=True, exist_ok=True)
        link_or_copy(source / row['path'], target)
    conflicting_file = conflict / 'components/immersive/ImmersiveShell.tsx'
    conflicting_file.parent.mkdir(parents=True, exist_ok=True)
    conflicting_file.write_text('// Independent unrelated user edit — must be preserved.\n')
    previous = {str(path.relative_to(conflict)): sha(path) for path in conflict.rglob('*') if path.is_file()}
    rejected = subprocess.run([sys.executable, str(overlay / 'apply-phase2.py'), '--base', str(conflict)],
                              cwd=overlay, text=True, capture_output=True)
    assert rejected.returncode != 0 and 'Refusing to overwrite unrelated user changes' in rejected.stderr
    assert previous == {str(path.relative_to(conflict)): sha(path) for path in conflict.rglob('*') if path.is_file()}
    result = {'status': 'PASS', 'archives': archives, 'uniqueArchiveMembers': len(members),
              'phase2ProjectFilesSHA256Verified': len(manifest['files']),
              'firstApply': json.loads(first.stdout), 'idempotentApply': json.loads(second.stdout),
              'unrelatedChangeRejectedWithoutWrites': True, 'phase1SourceUnchanged': True,
              'restoredProject': str(restored), 'externalBackup': 'Established separately by Drive download-back receipt'}
    (checkpoint / 'checkpoint-restoration-verification.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
