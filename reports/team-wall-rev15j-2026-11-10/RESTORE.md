# Restore Rev15J

The complete checkpoint includes the packed Blender master, the standalone viewer with its vendor code and artwork, the user's wall reference, source scripts, evidence, laptop renders, gallery and review PDF. No credentials, dependencies or caches are included.

For a split ZIP backup, put `INDEX.json`, `restore.py` and all listed parts in one folder, then run:

    python restore.py INDEX.json /path/to/downloads /empty/restore

The script verifies every part and every extracted payload using byte size and SHA-256. An empty destination is required. It rejects unsafe archive paths.

Open `delivery/Gullyverse-Rev15J-OC-First.blend` with Blender 4.3.2. Select scene `REV15J / OC First / Reference Plaster Wall`, run the packed `team_wall_rev15j_controls.py` Text block, and use Sidebar / Team Wall. OC is slide 0; there are eight active teams. Historical versions are retained separately in the same master.

For the standalone viewer:

    python -m http.server 8772 --directory /path/to/restored/viewer

Open http://localhost:8772/ in a WebGL-capable browser. The viewer uses no CDN. The Blender PDF is the authoritative world-lighting review.

`source/render.py` and `source/fresh-open.py` operate directly on the delivered master. `source/build.py` regenerates from the authentic Rev15I1 source; set `TEAM_WALL_BASE` to that original master, which is preserved in the earlier verified Drive checkpoint documented in REPORT.md. The delivered Rev15J master is independently editable and does not require that older file to open, render or continue work.

The current website repository remains on `work-in-progress-2027`. These deliverables are an art candidate and local preview; publication is separate.
