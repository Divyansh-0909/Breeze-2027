# Rev12 independent restore

This restores the private Blender neighborhood study, not a changed website. Do not run website installs/builds or Git commands to review it. Earlier checkpoints and the two website repositories stay protected.

1. Download every archive named in the final Drive index into a new empty local directory. Interim `Working-Source-Safety` ZIPs and the earlier non-v2 direct master are historical safety copies, not substitutes for the final archive set.
2. Check each archive byte size and SHA-256 against the external final index. Extract all ZIPs into one NEW empty restore directory. All paths are relative and there are no symlinks or credentials. Preserve the `source`, `baseline`, `inputs`, `evidence`, `references`, `renders` and `review` structure.
3. Run this per-file verification from that directory:

```python
import json, pathlib, hashlib
root = pathlib.Path('.')
manifest = json.loads((root / 'FILE-MANIFEST.json').read_text())['files']
for name, row in manifest.items():
    p = root / name
    assert p.stat().st_size == row['bytes'], name
    assert hashlib.sha256(p.read_bytes()).hexdigest() == row['sha256'], name
print('All payload hashes verified', len(manifest))
```

4. Open `source/Gullyverse-Rev12-Three-Plus-Storeys.blend` in Blender4.3.2. Final SHA256 is `101447553e9c487b860198465880fa21471908828b923da4e465c654d9ad51fc`, 24,389,347 bytes. Choose `REV12 / Three-to-Five Real Upper Storeys`. Its nineteen historical scenes, original A/B and H00/H06/H07/H09 controls remain available. The current +7% study directly shares old Rev11 actors; do not scale them again. All33 images are packed; fonts are builtin/packed as checked in the final restore receipt.
5. `GALLERY.html` opens locally. Phone/full/technical PDFs and the40s offline route MP4 live in `review/`. Full-resolution source PNGs and each camera/quality/hash record live in `renders/` and `evidence/`. Diagnostics are labelled separately. The recording plays80 actual Blender samples at2fps, not real-time game performance.
6. Optional independent Blender audits, without saving the model:

```sh
LP_NUM_THREADS=2 blender -b source/Gullyverse-Rev12-Three-Plus-Storeys.blend -t 2 --python-exit-code 9 --python source/validate_preservation.py
LP_NUM_THREADS=2 blender -b source/Gullyverse-Rev12-Three-Plus-Storeys.blend -t 2 --python-exit-code 9 --python source/validate_storeys.py
python source/run_checks.py
```

The script path discovers its root; no original `/workspace` path is needed for Blender audits. `verify_website.py` is a separate original-workspace preservation check requiring those repositories; it is not required to open the independent Blender checkpoint. Python3/Pillow/ReportLab rebuild review documents; Blender includes NumPy for authoring. FFmpeg assembles the offline recording. These tools are unnecessary merely to read existing PDFs/images.

7. To reproduce geometry ONLY in a separate copy, start from `inputs/Rev11-original.blend` and run `source/author_taller.py`. Authentic input SHA256 is `b149a04a56be0f6c7b7aa07c3d6f764e8b85b40b3423004d83689b27051b56cd`, 20,471,503 bytes. Do not resave that input. `make_author.py` is a HISTORICAL initial generator, not the authoritative edited author; do not use it to overwrite `author_taller.py`. `baseline/` and `source/prior-pilot/` include original audit/art-validator dependencies. New renders may have platform raster differences even with the same geometry; no pixel-identical regenerated-output guarantee is made.

All eleven houses pass the actual3+ upper-storey requirement. Floor/podium/hut exclusions, original 0.35m capsule/0.002m floor tolerances and the complete 960-frame path remain intact. Two inherited negative-Y scooter approaches and six nonpublic rear lightwell floor gaps remain unresolved. H00→H07 crowd-height grid differences remain historical; Rev11 H07→Rev12 H07 grid differences are zero. Exact steel rack/table source identity remains pending.

This package is for PRIVATE VISUAL REVIEW. No final A/B/hybrid or stature choice, public promotion, commit/push/merge/deployment or subsequent phase is authorized by opening it. No credentials, `.env` contents, installed dependencies or caches are included. Photo reference credits/limits are in `REFERENCE-ANALYSIS.md` and the provenance manifest; R2/R4 are private reference only with public redistribution rights unverified.

The externally verified archive/restore receipts are sidecars so they do not create circular archive hashes. The per-file manifest is protected by its containing source archive. Do not call a folder or local-only staging directory an independently verified backup.
