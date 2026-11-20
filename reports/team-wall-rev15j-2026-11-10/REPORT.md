# Rev15J — OC first, reference plaster wall

10 November 2026. Continuation of the user's request to remove the Coordinators slide and retain the wall shown in the attached OC reference.

The active carousel now contains eight teams, in this order: Organising Committee, Content, Design, Marketing, Public Relations, Sponsorship, Videography, Web Development. OC is the default. Coordinator artwork is excluded from the new scene and its viewer; it remains available in the 38 historical scenes.

The editable master is `delivery/Gullyverse-Rev15J-OC-First.blend`. Select scene **REV15J / OC First / Reference Plaster Wall**, run the packed `team_wall_rev15j_controls.py` Text block, and use Sidebar / Team Wall. There are 39 scenes in total. All file images are packed and there are no linked libraries.

## Where previous work stopped

Authenticated Drive inspection found the shared Recovery Control document last updated on 5 November, recording Rev15I complete and stopped for visual review. It explicitly retained Coordinators first and OC second. The newer Rev15I1 checkpoint is under the Rev15I phase and contains the wider OC names; its review folder is empty and the shared document has no Rev15I1 entry. All six master parts exist in Drive, even though the repository's upload receipt only lists its first three parts. The restored master is 141,815,521 bytes and matches SHA-256 `07650da781f0ec7ff4e91b6725a9e45de8a55ae4fee8175e539b45bb2cb203b7`.

No completed Coordinator-removal checkpoint was found in the inspected Drive history or Git snapshot. This describes saved evidence; it cannot establish whether an earlier session had unsaved edits.

- Shared control document: https://docs.google.com/document/d/1ynihhc-k0aSRGVY6oJttLY8MD1AhKPahCcqheL-g56k
- Rev15I1 phase: https://drive.google.com/drive/folders/1xJ6Mf7VwZ94uq0NDAkHaCPkAtcIgksc5
- Rev15I1 master parts: https://drive.google.com/drive/folders/1G468oe64ssXijPmwWxYQwG7pW6pjQYDU
- Source evidence: `evidence/prior-work-drive.json`.

## Wall appearance

The attached JPEG is the earlier OC Blender render resized to 1280 × 720, with compression differences (mean absolute RGB differences approximately 2.12 / 1.50 / 2.32 out of 255). It is preserved under `inputs/`.

The authentic Blender wall, its material owners, world lighting and colour management are retained exactly. The previous browser GLB exposed raw texture images without Blender's colour mixing or UV scale nodes, producing the dark, strongly repeated surface visible in the earlier PDF. `viewer/wall-materials.js` now reconstructs the original MixRGB values and texture scales from recorded Blender material data. The viewer also uses AgX tone mapping and the source exposure. Its simplified lights still differ from the Blender world; the eight main laptop renders and PDF use the actual Blender scene and original lighting.

## Validation

- Original 38 scene memberships preserved; all non-art owners, wall geometry/materials, world, floor and navigation owners shared exactly.
- Eight exclusive slides; no Coordinators in active scene; OC default; remaining art meshes/materials unchanged.
- Fresh master open: 39 scenes, packed file images, zero linked libraries, eight visibility checks pass.
- Browser: all eight next-button transitions, keyboard wrap to OC, previous-button wrap to Web, selection reload, repeated allocations and 390px layout pass. No script/console errors or failed requests. This uses software WebGL, not physical-device performance testing.
- Eight new actual Blender renders at 1600 × 900. `review/Team-Mural-OC-First-Laptop-Review.pdf` contains one per page.

No application source, public website defaults, commits, pushes or deployments are included in this art checkpoint. The website's older `/team` board remains a separate future integration task.

## Current handoff

Review the OC-first carousel and wall using `GALLERY.html` or the updated PDF. This candidate is **Rev15J**, superseding the nine-slide Rev15I1 review for current work. Historical deliverables remain intact. Backup receipts are stored under `checkpoint/` after verified upload; the Drive phase is https://drive.google.com/drive/folders/17vCXMlCsQ7YiWYb264nM-K7lMBgToPW6.
