# Restore Rev15N

Download `INDEX.json`, `restore.py` and every numbered ZIP part from this checkpoint folder, preserving filenames. Run:

```sh
python restore.py INDEX.json /path/to/downloads /path/to/empty/restore-folder
```

The standard-library script verifies part sizes and SHA-256, the concatenated archive hash, safe paths and every restored file. It streams across parts without a combined temporary ZIP.

Open `delivery/Gullyverse-Rev15N-Events-House-Wall.blend` in Blender 4.3.2. The active scene is Rev15N. Images are packed, with no linked libraries. All 43 previous scenes remain in addition to this scene. `REV15N / Team Carousel Controller` has `team_index` values 0–7. The LED retains its 10,676-frame period at 30 fps.

Review the gallery, PNGs in `renders/` and the PDF in `review/`. The current master is self-contained for editing. Source regeneration also needs the unchanged Rev15M report in the sibling `crowd-rev15m-aftermovie-models-2026-11-11` folder; exact master and verified checkpoint are listed in `evidence/base-reference.json`. Blender runs `source/build.py`, `source/fresh-open.py` and `source/render.py`. Original source inventories and facade/opening survey scripts are included. Python with Pillow, ReportLab and PyMuPDF creates the PDF.

Apply `repository-files/` pointers deliberately so later user edits survive. Earlier masters and Drive checkpoints are retained. Website integration remains separate.
