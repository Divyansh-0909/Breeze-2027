# Restore the Rev05A partial correction

This is an independently openable Blender concept, not a website patch. Banner and audience are implemented; shop interiors and shelf relocation are NOT implemented. Do not mistake guarded proposal scripts or diagrams for approved candidate geometry.

1. Download `Rev05A-Source-and-Reports.zip` and all three image archives `Rev05A-Images-A.zip`, `Rev05A-Images-B.zip`, `Rev05A-Images-C.zip` from the new checkpoint folder. Download the archive index and external verification receipt too. Earlier checkpoints need not be overwritten.
2. Verify each archive against `ARCHIVE-INDEX.json` SHA-256 and byte size. Extract all four into the SAME new empty directory. They contain complementary relative paths without a repository root.
3. Verify `FILE-SHA256SUMS.txt` with `sha256sum -c FILE-SHA256SUMS.txt` from that directory. No credentials, `.env`, node_modules, website working copies, Blender toolchain or temporary caches are included.
4. Open `source/Gullyverse-Rev05A-Banner-Crowd-Shelves-Pending.blend` in Blender 4.3.2. It contains three A/B/C scenes, the unchanged 40-second action, 24 packed images and the diagnostic cameras. No linked assets or external fonts are needed merely to open/render it.
5. Open `GALLERY.html` locally to review all 58 original PNGs; the PDF and side-by-side JPGs are in `review`. Diagnostics and exact camera/hash metadata are in `evidence`.

The original Rev04 baseline is included unchanged in `source/baseline/source/Gullyverse-Straight-Walk-Semicircular-Crowd.blend`, SHA-256 `6041c26ac21fd990f14e2dae0fbe2cad15c21739f045d8cf56b7b8439a9e239a`. Its `evidence/crowd-composition.json` is included as deterministic authoring input. Original provenance lives in `source/provenance`; project portraits, branding and the Aftermovie still retain project rights and are not CC0. Existing Poly Haven provenance is preserved separately. New people reuse inherited simple proxy meshes; no new external mesh kit is downloaded.

To reproduce banner/crowd authoring, create a separate writable copy first, then run from the extracted root:

```sh
blender -b source/baseline/source/Gullyverse-Straight-Walk-Semicircular-Crowd.blend -t 1 --python source/author_crowd_banner.py
blender -b source/Gullyverse-Organic-Crowd-No-Banner-Intermediate.blend -t 1 --python source/export_review_master.py
blender -b source/Gullyverse-Rev05A-Banner-Crowd-Shelves-Pending.blend -t 1 --python source/validate_crowd.py
blender -b source/Gullyverse-Rev05A-Banner-Crowd-Shelves-Pending.blend -t 1 --python source/validate_layout.py
blender -b -t 1 --python source/preservation_audit.py
```

Reproducibility means deterministic composition/geometry and input hashes; Blender save timestamps may change the `.blend` container bytes. Keep the delivered verified master untouched.

**Do not run `prepare_shop_interior.py --allow-interior-recesses` without the user's explicit narrow architecture exception.** That source is a prepared proposal. Its unlinked-copy math test does not prove complete shelf integration. A new authorized revision would require new master, full mesh/stock/counter validation and all fifteen shop after views under the existing lights.

Previous baseline/checkpoint dependency, for history and original motion proof only: Rev04 task folder https://drive.google.com/drive/folders/1nCeYtoSNp8C-77jZrSR49SO-6qBDWboD ; master https://drive.google.com/file/d/1i7pmAssGNAt6qYWsVwJEjh_ozAmrRE7i/view . No history is deleted by this checkpoint. This source is not a complete website backup; the protected WIP remains at e638140b37045a805b23b4d406d387a8870f8486 in the earlier checkpoints.
