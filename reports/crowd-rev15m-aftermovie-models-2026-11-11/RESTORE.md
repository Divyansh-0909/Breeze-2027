# Restore Rev15M

Download `INDEX.json`, `restore.py` and all numbered ZIP parts from the complete checkpoint folder, preserving filenames. Run:

```sh
python restore.py INDEX.json /path/to/downloads /path/to/empty/restore-folder
```

The standard-library script checks every part and concatenated archive hash, safe extraction paths and every restored file. It streams across parts without an intermediate combined ZIP.

Open `delivery/Gullyverse-Rev15M-Consistent-Crowd.blend` in Blender 4.3.2. The active scene is Rev15M. All images are packed; there are no linked libraries. All 42 previous scenes remain in addition to the new scene. `REV15M / Team Carousel Controller` has `team_index` values 0–7. The LED plays its original 10,676-frame period at 30 fps.

Review `GALLERY.html`, the PNGs in `renders/` and the PDF in `review/`. The master is self-contained for further editing. For source regeneration, restore the unchanged verified Rev15L1 report into the sibling `navigation-board-rev15l1-logo-spacing-2026-11-11` folder; exact hash and checkpoint are in `evidence/base-reference.json`. Blender runs the included inspection/build/fresh-open/render scripts. Python with Pillow, ReportLab and PyMuPDF builds the review PDF.

Apply `repository-files/` pointers deliberately, preserving any later user edits. Previous original/edited masters and Drive backups remain intact. The website renderer has not been changed.
