# Rev10 independent source and review restoration

PRIVATE BLENDER ONLY. Both A and B await USER CHOICE. No website integration or production promotion. The exact original C180 crowd, screen, floor, route, art and lighting remain locked. Existing Rev09/earlier checkpoints are untouched.

Use the final Drive review/restore index to download ALL numbered final ZIPs. Check archive SHA-256 and byte size against that index, then extract every ZIP into the SAME NEW EMPTY directory, preserving paths. These are complementary independently valid ZIPs, not binary fragments. The final index identifies every required archive. Ignore the clearly labelled INTERIM source-safety snapshot.

Open `source/Gullyverse-Rev10-Photo-Guided-Alternatives.blend` in Blender4.3.2 or a compatible newer version. The packed master contains15 scenes: all13 untouched Rev09 archives plus `REV10 A / Connected Working Rooftops` and `REV10 B / Layered Residential Galleries`. Default A is only a proposal, not user approval. All33 existing image owners and fonts are packed. Reference photographs are separate PRIVATE research files; none is a scene texture.

The checkpoint contains REAL `.blend` payloads, not LFS pointers: new Rev10, original Rev09 and original corrugated-artist master needed for validation. Shared maps are packed in the masters; no website checkout, node_modules, build output, credentials or Google token is needed to open the scene. Source reference credits/licences and restrictions are in `source/REFERENCE-PROVENANCE.json`. R2/R4 public redistribution rights remain unverified; do not put those images into the website or public asset textures.

Before local diagnostics, run:

```sh
python source/verify_payload.py
```

This verifies every delivered file byte/hash and relative gallery link. FILE-MANIFEST.json excludes its own hash; the separate verified Drive index lists archive hashes. `GALLERY.html` works offline after ALL numbered archives are extracted together. PDFs contain efficient embedded images for phones; PNG originals remain full resolution.

To reopen or test without resaving the master:

```sh
blender -b source/Gullyverse-Rev10-Photo-Guided-Alternatives.blend -t 2 --python-exit-code 9 --python source/verify_reopen.py
blender -b source/Gullyverse-Rev10-Photo-Guided-Alternatives.blend -t 2 --python-exit-code 9 --python source/validate_architecture.py
```

The second command compares every original object/material/image/world and all13 archived scene memberships/settings against the included `source/Rev09-Original.blend`. Validation writes JSON evidence, so verify payloads BEFORE running diagnostics in your working copy. The sealed master is never resaved by validators/render scripts. Original `.blend` hashes remain unchanged after opening.

To reproduce a chosen actual offline still, use the render script with `-- A 03-aerial`, `-- B 03-aerial` or `-- before 03-aerial`. All camera overrides are explicit in `source/rooftop_cameras.py` and in per-image JSON metadata. Do not alter original historical camera objects. `render_walk.py -- A` or `-- B` samples the existing original1–960 action into80 actual frames. Movies encode those frames at2fps for40seconds; this is not gameplay FPS or real-device performance certification.

Recipe reproducibility is supplied by `source/author_rooftops.py`. Run ONLY on the included original Rev09 master in a SEPARATE WORKING COPY. It constructs both studies and writes a new master/evidence, so do not run over this sealed backup. A regenerated Blender binary is not expected to have a byte-identical hash. Set REV10_AUTHOR_OUTPUT to an explicit destination if needed. Public-photo downloads are optional for repeat inspection; original downloaded files are already included and hash-verified.

`source/verify_website.py` is OPTIONAL and only applies when the exact original website checkout exists at its documented path. The website itself was not edited and is not duplicated into this private art checkpoint. Its protected hash inventory/current Git state are included as preservation evidence, not a claim this model is already integrated.

The final receipt records authenticated full download-back verification plus a fresh extraction/reopen of all numbered ZIPs. The final handoff and Doc-preservation proof are separate post-delivery sidecars to avoid circular self-hash claims. Stop for user choice between A/B; do not automatically proceed or deploy.
