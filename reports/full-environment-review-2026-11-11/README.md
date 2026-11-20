# Gullyverse full environment review — 11 November 2026

52 actual Blender captures of the current Rev15J1 environment, combined into a labelled PDF.

- `review/Gullyverse-Full-3D-Environment-2026-11-11.pdf`: combined review with contents, visual index, full-size images and capture notes.
- `review/gallery.html`: offline gallery; open after restoring this folder together with its `renders` folder.
- `renders/`: all 52 original PNG captures.
- `evidence/capture-plan.json`: all camera poses, labels and source notes.
- `evidence/captures.json`: completed captures and SHA-256 checksums.
- `evidence/inventory.json`: source object, material, camera and light inventory.
- `evidence/preservation.json`: source master and original scene/light preservation checks.
- `evidence/base-master-reference.json`: exact unchanged source master, prior verified Drive checkpoint and restoration proof.
- `source/`: capture, review assembly and checkpoint scripts.

## Scope and image labels

The existing environment contains five modelled open shop bays and three closed artist shutter fronts: Chaar Diwari, Ritviz and Neha Kakkar. Each open bay has a frontage and an interior capture. Each closed front has a frontal view and a grazing view of the slats and paint. Alternate opening/closing states are not authored in this review.

All eleven courtyard houses are covered: L1–L3, R1–R3, B1–B3 and F1–F2. Other views cover the lane and courtyard, crowd/screen, Organising Committee and events walls, plan/aerial layout, four exterior elevations, windows, timber shutters, balcony railings, doors, roofs, parapets, utilities, stair access, wall finishes, drainage, signs and conduit.

Six night views use the original lighting. Forty-six views use temporary inspection lighting. House/elevation/architectural views isolate the existing architectural meshes to expose walls and windows behind the crowd, screen and free artwork. Isolation is labelled on every affected page. House views include the lower podium levels that are normally below the raised courtyard.

The Organising Committee view is the unchanged existing 1600 × 900 PNG from the exact current master. New landscape views are 1280 × 720; house views are 1000 × 1400. The PDF uses JPEG encoding for smaller delivery size; the PNG originals are retained.

The master `.blend` is never saved by the capture scripts. Original scene memberships and source light energies are checked after rendering, and the master file SHA-256 is checked before and after. The source scene has 40 saved scenes and remains unchanged.

## Restore the review

Download `INDEX.json`, `restore.py`, and every numbered ZIP part from the review checkpoint folder. Keep all parts together. Run:

```sh
python restore.py INDEX.json /path/to/downloads /path/to/empty-review-folder
```

The restore script checks every ZIP part, the combined archive, safe archive paths, file sizes and every restored file checksum. The combined PDF, PNGs, offline gallery and provenance are self-contained in that review folder.

## Reproduce from the unchanged master

The complete editable master already exists in the verified Rev15J1 checkpoint linked in `evidence/base-master-reference.json`. Download its nine parts, index and restore script and restore them to a sibling folder named `team-wall-rev15j1-full-heading-2026-11-10`. Its `delivery/Gullyverse-Rev15J1-Full-Heading.blend` must have SHA-256 `8360e4894bcdaa3daffb72b9939a22ccabcc0375694064122ccfca3bb6b9ef3b`. That base also includes the unchanged mural PNG reused here.

With Blender 4.3.2 and Python with Pillow and ReportLab installed, run `source/plan.py`, then run Blender in background with `source/capture.py`, and run `source/create-review.py`. Completed entries in `evidence/captures.json` are skipped; to intentionally regenerate a view, remove only its corresponding entry before rendering. `source/inventory.py` can regenerate the source inventory from the master. Existing scene/model geometry is preserved; temporary review scenes are not saved.

Drive organization: a distinct full-environment review phase under Rev15, with a dated review checkpoint subfolder. Source master bytes are reused from the previously verified base rather than uploaded again. No commit, push or deployment is part of this capture task.
