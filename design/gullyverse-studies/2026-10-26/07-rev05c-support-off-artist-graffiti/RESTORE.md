# Rev05C partial lighting checkpoint

This is the separately authorized PRIVATE Blender correction. It does not change the website. The combined artist-graffiti task is NOT complete.

1. Download every complementary ZIP listed in `checkpoint/ARCHIVE-INDEX.json`, plus the archive index, per-file manifest and final external verification receipt. Check each archive's exact byte size and SHA-256 before extraction. Extract all ZIPs into the SAME new empty directory. They are ordinary complementary ZIPs, not binary split parts.
2. Verify all entries in `FILE-MANIFEST.json`. Open `source/Gullyverse-Rev05C-Interior-Support-Off.blend` using Blender4.3.2. It contains three A/B/C scenes,39cameras, all24packed images and builtin/packed fonts. It does not require the old cloud paths to view or edit. Five optional interior supports are0W. Original twelve lights, all architecture, crowd and40second walk are preserved.
3. Baseline `source/baseline/Rev05B.blend` is the exact packed original with SHA2568fbfbfb1c69bd0daefb5690c935c8317ed3516ab0e1af07e8a9bd371747ec5ff. It is included for independent comparison. Original provenance is under`source/provenance`.
4. Reproduce the light correction using:

   `blender -b source/baseline/Rev05B.blend -t 2 --python-exit-code 1 --python source/author_rev05c.py`

   Run `source/validate_layout.py`, `source/validate_bodies_and_shops.py`, `source/audit_scene.py` on the new master. `source/verify_restored_master.py` checks packed dependencies and disabled supports. Blender serialization may vary between versions; restore the supplied exact master for byte-identical retrieval.
5. Open`GALLERY.html` locally after all image ZIPs are extracted. Every full-resolution PNG is linked relatively. The ON images are exact hash-verified prior Rev05B renders; OFF images are freshly rendered at identical camera/global-light settings. `source/render_lighting.py` can rerender OFF and reuse the restored exact ON files without needing historical directories.
6. Use `python source/build_review.py` and`python source/build_report.py` to regenerate evidence after restored renders are available. Python dependencies: Pillow,ReportLab,PyMuPDF. The report/checkpoint contain no credentials or private environment files.

## Blocking source-art requirement

Provide the actual original Chaar Diwari,Ritviz,Neha Kakkar graffiti image files through accessible Drive IDs or links. Metadata/hash/license fields remain unresolved in the placement plan. The three measured shutter assignments are not completed artworks. `image_gen.imagegen` is available but was not used without those requested style references. No substitute artist-name art, code-drawn generated-art imitation or invented rights assertion is supplied.

Continue the existing combined Rev05C after source inspection. Do not restart shop/crowd modelling or the light correction. Do not choose A/B/C or change the website automatically.

## Preservation and limitations

This archive is self-contained for the partial Blender study, not a full website backup. Protected Rev05B checkpoint: https://drive.google.com/drive/folders/1RBUH2fDcXWhGUn32txMNqo6ejWKwFz7p . WIP site remains atwork-in-progress-2027/e638140b37045a805b23b4d406d387a8870f8486with its prior dirty state untouched.

Two inherited negative-Y approaches remain blocked by scooter steering at leftY+2and rightY-7; tested positive-Y alternatives pass. Geometry/route checks do not certify accessibility or physical-device performance. No commit,push,merge,deploy or production promotion occurred.
