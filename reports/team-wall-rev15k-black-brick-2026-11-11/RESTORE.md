# Restore Rev15K

Download `INDEX.json`, `restore.py` and every numbered ZIP part from the complete checkpoint folder. Keep the parts together, then run:

```sh
python restore.py INDEX.json /path/to/downloads /path/to/empty/restore-folder
```

The script checks each part's bytes and SHA-256, the assembled archive hash, safe paths and every restored payload. Open `delivery/Gullyverse-Rev15K-Black-Brick-Murals.blend` in Blender 4.3.2. The active scene is Rev15K. Change `team_index` on `REV15K / Team Carousel Controller` from 0 through 7 to switch teams. The master contains the original history and packed images, with no linked libraries.

Open `GALLERY.html` or the PDF under `review/`. To run the interactive viewer without Node dependencies, serve the `viewer` directory with `python -m http.server 8775 --directory viewer` and open http://127.0.0.1:8775. All viewer modules and art are included.

The complete current delivery is self-contained. Re-running `source/build.py` from the exact baseline additionally requires the unchanged Rev15J1 master as a sibling report folder, documented in `evidence/base-reference.json`. That original is reused from its earlier fully verified checkpoint. `repository-files/` contains the task's README and current-mural pointer snapshots; apply those deliberately in the project rather than overwriting unrelated current user work.

`source/render.py` renders all eight teams without saving the master. `source/render-details.py` produces the material views. `source/create-review.py` builds the PDF (Pillow, ReportLab and PyMuPDF). `source/fresh-open.py` checks the packed master. The source browser check requires Playwright/Chromium in the repository development environment; it is not needed to run the static preview.
