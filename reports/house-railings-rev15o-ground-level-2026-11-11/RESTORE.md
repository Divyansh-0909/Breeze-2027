# Restore Rev15O

Download `INDEX.json`, `restore.py` and every numbered ZIP part from this checkpoint folder, preserving their names. Run:

```sh
python restore.py INDEX.json /path/to/downloads /path/to/empty/restore-folder
```

The standard-library script verifies every part and the concatenated archive SHA-256, safe extraction paths, file sizes and payload hashes. It streams across parts without a combined temporary ZIP.

Open `delivery/Gullyverse-Rev15O-Clear-Ground-House-Fronts.blend` in Blender 4.3.2. The active scene is Rev15O. All images are packed and no linked libraries are required. All 44 prior scenes remain. `REV15O / Team Carousel Controller` has `team_index` values 0–7. The LED plays its original 10,676-frame period at 30 fps.

Review `GALLERY.html`, the images in `renders/` and the PDF in `review/`. For source regeneration, restore the verified Rev15N report into the sibling `events-wall-rev15n-warm-brick-2026-11-11` folder; the exact master and checkpoint are in `evidence/base-reference.json`. Run the Blender build, fresh-open and render scripts. The original surveys and removal plan are included. Python with Pillow, ReportLab and PyMuPDF builds the PDF.

Apply `repository-files/` pointers deliberately to preserve later user edits. Previous masters and Drive backups remain. The website renderer has not been changed.
