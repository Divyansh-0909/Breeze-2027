# Restore Rev15L1

Download `INDEX.json`, `restore.py` and all numbered ZIP parts from this checkpoint folder. Keep their names together, then run:

```sh
python restore.py INDEX.json /path/to/downloads /path/to/empty/restore
```

The standard-library script verifies part sizes and hashes, the concatenated archive SHA-256, safe paths and each restored file. It streams across parts without a combined temporary ZIP.

Open `delivery/Gullyverse-Rev15L1-Wider-Logo-Gaps.blend` in Blender 4.3.2. All images are packed and no linked libraries are required. Play the timeline for the LED. The mural controller is still `REV15L / Team Carousel Controller`, with `team_index` values 0–7. The active scene is Rev15L1.

Serve the self-contained static preview with `python -m http.server 8777 --directory viewer`, then open http://127.0.0.1:8777. No Node build or remote modules are required.

For source regeneration, also restore the verified Rev15L base into the sibling report folder `navigation-board-rev15l-led-sponsors-2026-11-11`. Its exact master and checkpoint are identified in `evidence/base-reference.json`. Run `source/prepare-spacing.py`, then Blender with `source/render-logo-strip.py`, `source/apply-spacing.py` and `source/fresh-open.py`. Python with Pillow and NumPy runs `source/check-spacing.py`. Browser checks use the repository Playwright and Chromium; the recorder also uses FFmpeg. The included render and review scripts reproduce the evidence.

`repository-files/` preserves current README and documentation pointers. Apply deliberately to retain later user edits. Earlier masters and Drive backups remain intact.
