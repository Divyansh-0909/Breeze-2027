# Restore Rev15J1

Put INDEX.json, restore.py and every listed ZIP part in a single download folder. Restore into an empty directory:

    python restore.py INDEX.json /downloads /empty/restore

The restorer verifies all part and payload sizes and SHA-256 hashes. The checkpoint contains the complete packed 40-scene Blender master, full viewer and vendor assets, new heading image and reference, source code, evidence, gallery, eight laptop views and updated PDF. It needs no earlier checkpoint to open, edit, render or preview.

Open `delivery/Gullyverse-Rev15J1-Full-Heading.blend` with Blender 4.3.2. Select **REV15J1 / Organising Committee Full Heading**, run packed `team_wall_rev15j1_controls.py` and use Sidebar / Team Wall. Organising Committee is first; Coordinators is excluded from the eight active teams.

For the viewer:

    python -m http.server 8773 --directory /restored/viewer

Open http://localhost:8773/ in a WebGL-capable browser. The main PDF and laptop renders show the actual Blender world lighting; the browser's simpler lights remain an approximation.

`source/build.py` reproduces the update from the prior Rev15J master, available in its verified Drive checkpoint. Set `TEAM_WALL_BASE` to that file when regenerating. The delivered master is already independently editable. `source/render.py` updates the changed first view; the other seven views are unchanged and included. `source/fresh-open.py` validates the saved master without external assets.
