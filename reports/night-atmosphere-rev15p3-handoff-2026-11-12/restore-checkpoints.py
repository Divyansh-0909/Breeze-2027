#!/usr/bin/env python3
"""Restore verified Rev15P + Rev15P2 output checkpoints from Drive parts."""
import argparse, hashlib, json, shutil, zipfile
from pathlib import Path

def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        while data := f.read(1024 * 1024):
            h.update(data)
    return h.hexdigest()

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('downloads', type=Path, help='Folder containing all downloaded .partNNN files')
    p.add_argument('destination', type=Path, help='New, empty restoration directory')
    p.add_argument('--manifest', type=Path, default=Path(__file__).with_name('SOURCE-CHECKPOINT-INDEX.json'))
    args = p.parse_args()
    manifest = json.loads(args.manifest.read_text())
    if args.destination.exists() and any(args.destination.iterdir()):
        raise SystemExit('Use a new, empty restoration directory to preserve existing work.')
    args.destination.mkdir(parents=True, exist_ok=True)
    for archive in manifest['archives']:
        parts = []
        for part in sorted(archive['parts'], key=lambda x: x['index']):
            hits = list(args.downloads.rglob(part['name']))
            if len(hits) != 1:
                raise SystemExit(f"Expected one copy of {part['name']}; found {len(hits)}")
            src = hits[0]
            if src.stat().st_size != part['bytes'] or digest(src) != part['sha256']:
                raise SystemExit(f'Part checksum failed: {src.name}')
            parts.append(src)
        joined = args.destination / archive['name']
        with joined.open('wb') as out:
            for src in parts:
                with src.open('rb') as f:
                    shutil.copyfileobj(f, out, 1024 * 1024)
        if joined.stat().st_size != archive['bytes'] or digest(joined) != archive['sha256']:
            raise SystemExit(f'Archive checksum failed: {joined.name}')
        with zipfile.ZipFile(joined) as z:
            if sorted(z.namelist()) != sorted(row['path'] for row in archive['payloads']):
                raise SystemExit('Archive payload list differs from manifest')
            for row in archive['payloads']:
                target = (args.destination / row['path']).resolve()
                if not target.is_relative_to(args.destination.resolve()):
                    raise SystemExit('Unsafe archive path')
                target.parent.mkdir(parents=True, exist_ok=True)
                h, size = hashlib.sha256(), 0
                with z.open(row['path']) as src, target.open('wb') as out:
                    while data := src.read(1024 * 1024):
                        out.write(data); h.update(data); size += len(data)
                if size != row['bytes'] or h.hexdigest() != row['sha256']:
                    raise SystemExit(f"Payload checksum failed: {row['path']}")
        print(f"PASS: {archive['name']}, {len(archive['payloads'])} payloads")
    print('Restored. Read RESTORE-AND-CURRENT-STATUS.md for the native scene and private viewer.')

if __name__ == '__main__':
    main()
