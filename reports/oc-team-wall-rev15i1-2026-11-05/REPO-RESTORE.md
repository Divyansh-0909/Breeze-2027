# Rev15I1 wider OC names — Git WIP checkpoint

This folder contains the complete portable handoff for the wider OC mural names. The Blender master and historical baseline are in `delivery/` and `inputs/`; project authoring code is in `source/`; matched renders, PDF, captures and offline viewer files are preserved in their original relative paths.

The latest editable scene is `delivery/Gullyverse-Rev15I1-Wider-OC-Names.blend`. It includes 38 scenes (37 historical scenes plus REV15I1), packed image assets, and no linked libraries. Open `REV15I1`, then run packed `oc_wider_name_controls.py` and use Sidebar / Team Wall.

The four OC name widths are 90% of the portrait share (1.6767 m of 1.8630 m); image aspect ratio, portraits, roles, positions, face clearance, coordinator slide and other seven team slides are retained.

## New-workspace restore

1. Clone the `work-in-progress-2027` branch.
2. Run `git lfs install` and `git lfs pull` to fetch the two `.blend` masters and LFS review bundles.
3. Open the latest `.blend` directly in Blender 4.3.2. The screenshot gallery is `GALLERY.html`, the phone review is `review/Rev15I1-Wider-OC-Names.pdf`, and the portable viewer is packaged under `archive/` in the external Drive checkpoint. (The repo copy includes viewer source under `viewer/`.)
4. `FILE-MANIFEST.json` preserves per-file byte sizes and SHA-256 hashes for the delivery payload. `checkpoint/UPLOADED.json` records Drive component IDs; the independent Drive checkpoint is https://drive.google.com/drive/folders/1G468oe64ssXijPmwWxYQwG7pW6pjQYDU.

The candidate is a private art deliverable. It has not been wired into website defaults, committed at the time this README was created, or deployed.
