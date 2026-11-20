# Restore Rev15L

Download `INDEX.json`, `restore.py` and every numbered ZIP part from the complete checkpoint folder. Keep the filenames and parts together, then run:

```sh
python restore.py INDEX.json /path/to/downloads /path/to/empty/restore-folder
```

The script verifies part sizes and SHA-256, the complete concatenated archive hash, safe paths and every restored payload. It reads the parts as one seekable stream, so it does not need a second combined temporary ZIP. The destination must be empty.

Open `delivery/Gullyverse-Rev15L-Navigation-LED.blend` in Blender 4.3.2. The active scene is Rev15L and frame 1 shows the first logos. Play the timeline to see the repeating LED. The scene frame range is one exact strip period at 30 fps. All scene images are packed; no linked libraries are required. `REV15L / Team Carousel Controller` has `team_index` values 0–7 for the intact mural carousel.

Open `GALLERY.html` or the PDF and MP4 in `review/`. Serve the live preview with:

```sh
python -m http.server 8776 --directory viewer
```

Then open http://127.0.0.1:8776. The static preview needs no Node build or remote modules. Pause/play, close-up and sponsor selection are available. Schedule is a proposed label, not a live website destination.

The current delivery is self-contained. Re-running `source/build.py` requires the unchanged Rev15K master in its sibling report folder; its exact verified base is documented in `evidence/base-reference.json`. Install `source/requirements.txt` for sponsor preparation and PDF creation, use Blender 4.3.2 for the source scripts, and use the repository's Playwright plus Chromium and Playwright FFmpeg for browser checks and recording. Run preparation, `render-logo-strip.py`, `build.py`, `render.py`, `fresh-open.py`, the browser check, the demo recorder, then `create-review.py` in that order.

The build invokes the separate fresh-master exporter automatically. `source/export-viewer.py` can also refresh the GLB alone. `repository-files/` holds README and current-scene pointers; apply those deliberately rather than overwriting unrelated later user edits.
