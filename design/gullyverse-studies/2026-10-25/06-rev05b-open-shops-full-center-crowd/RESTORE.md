# Restore Rev05B — genuine open shops and dense-center crowd

This is a Blender-only private concept checkpoint. It does not replace or patch the WIP website. A/B/C are preserved alternatives, not a selected final art direction.

1. Download every archive marked `required: true` in `ARCHIVE-INDEX.json` from this phase's new `02-Checkpoint` folder. Keep the index and `EXTERNAL-VERIFICATION.json`. Previous Rev05A and Rev04 backups remain separate and unchanged.
2. Verify each archive's byte size and SHA-256 against the index. Extract every complementary archive into the SAME new empty directory. Source, review and PNG paths are complementary; no existing repository should be overwritten.
3. From that directory run `sha256sum -c FILE-SHA256SUMS.txt`. `FILE-MANIFEST.json` records the member inventory. Manifest/index/verification receipts exclude themselves from their own hashes to avoid self-referential checksums.
4. Open `source/Gullyverse-Rev05B-Open-Shops-Full-Center-Crowd.blend` in Blender 4.3.2. It has all three A/B/C scenes, the unchanged 40-second camera action, 24 packed images, unchanged original cameras and 15 additional diagnostics. Fonts are builtin/packed. No previous workspace path or external linked image is needed simply to open/render it.
5. Open `GALLERY.html` for all 150 final full-resolution screenshots and the separately labelled light-only diagnostics. The concise phone review and full comparison PDF are under `review/`.

The exact starting master is included as `source/baseline/Rev05A.blend`, SHA-256 `b143dc873b9566217301119f97cf349a73db58d7fdc1591c451e2daf7000ee8c`. Its crowd input, original costs, protected website hash inventory and the newly approved prompt are included. It is independently openable and remains unmodified. The preceding full website backup chain stays in the protected historical checkpoints; this package is not falsely described as a new complete website snapshot.

To reproduce the authoring in a SEPARATE writable copy:

```sh
blender -b source/baseline/Rev05A.blend -t 1 --python-exit-code 1 --python source/author_rev05b.py -- --rev05b-authorized
blender -b source/Gullyverse-Rev05B-Open-Shops-Full-Center-Crowd.blend -t 1 --python-exit-code 1 --python source/validate_bodies_and_shops.py
blender -b source/Gullyverse-Rev05B-Open-Shops-Full-Center-Crowd.blend -t 1 --python-exit-code 1 --python source/validate_layout.py
blender -b -t 1 --python-exit-code 1 --python source/preservation_audit.py
```

The guarded authoring flag records the explicit Rev05B shop exception; it is not a request for new permission. Reproduction means deterministic actor/mesh composition and matching inputs. Blender save timestamps can alter container bytes; preserve the delivered verified master untouched.

`shop_recess.py` is a mesh helper, not a standalone mutation script. No Boolean union is used. Final cavities are 6.2m wide × 4.4m deep × 2.85m high; the first 3.8m proposal failed doorway clearance and is retained as diagnostic history. Five existing counters, their contents, closed shops and DJ furniture are exact. The negative-Y shop approaches at left Y+2 and right Y-7 still encounter fixed scooters; the other approaches pass. All failures remain in the technical logs.

The static crowd has no simulated crowd-parting feature. Its narrow protected body passage ends after the fixed walk endpoint; the screening center beyond it is populated. Do not infer a live-web collision implementation from these Blender concept checks.

Final diagnostic section cameras use a near-plane cut at local Z+2.7m to show the interior without deleting/hiding meshes. Inside-before views deliberately use a camera within the old solid block and are labelled diagnostics. Rejected camera crops and initial unlit/3.8m drafts are retained separately and excluded from the matched final gallery.

Materials and all 24 packed image bytes remain inherited. `source/provenance` contains original attribution/license inventories; those historical inventories may describe earlier authoring files not needed by this packed master. Poly Haven material rights are CC0. Project portraits, branding and the Aftermovie still retain project rights; do not call the whole asset pack CC0 or redistribute it as public stock. New people reuse neutral inherited proxy geometry, not a new third-party character kit.

Review generation uses Pillow, ReportLab, Matplotlib and NumPy; exact versions are in `source/review-tooling-versions.txt`. `build_density.py`, `build_review.py` and `build_report.py` reproduce the diagrams/reviews after the saved captures and validations exist. Two render jobs have separate manifests to avoid concurrent writes. The screenshot matrix uses 1200×750 desktop and 540×960 portrait at 16 EEVEE samples. PNGs are lossless originals; PDFs use compact JPEG embedding. No software-render duration is a physical-device FPS measurement.

Drive checkpoint folder: https://drive.google.com/drive/folders/1RBUH2fDcXWhGUn32txMNqo6ejWKwFz7p

No commit, push, merge, deploy, public/WIP promotion, automatic next look-dev phase or final A/B/C selection is authorized by restoration.
