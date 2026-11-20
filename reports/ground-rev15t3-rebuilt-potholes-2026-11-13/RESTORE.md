# Restore Rev15T3

Use Blender 4.3.2. Download this phase's checkpoint parts and Checkpoint-Index.json, download the standalone restore-checkpoint.py helper, then run `python restore-checkpoint.py /path/to/checkpoint-parts /path/to/checkpoint.zip --index /path/to/Checkpoint-Index.json` and extract the verified ZIP. Every payload has a checksum in PAYLOAD-SHA256.json. The current packed delta and runtime GLB are separate Drive files; their verified IDs and checksums are included in the source evidence.

The complete T2 native master is reused as the base. `delivery/Base-Rev15T2-Native-Parts.json` records all thirteen verified Drive part IDs, sizes and SHA256 hashes. Download those parts into one directory, then run from this report directory:

```bash
python source/restore-master.py /path/to/base-parts /path/to/Gullyverse-Rev15T2.blend --index delivery/Base-Rev15T2-Native-Parts.json
blender -b --python source/restore-native.py -- --base /path/to/Gullyverse-Rev15T2.blend --delta /path/to/Rev15T3-Rebuilt-Potholes-Additions.blend --output /path/to/Gullyverse-Rev15T3.blend
```

The base master must be exactly 214,265,912 bytes, SHA256 `33a2e589654ed8aaed1c5abee13111630118c24bff054331f2891160abee8fdb`. The restore helper preserves the complete 51-scene base, creates the final 52nd scene, appends the packed ground delta, hides the old scatter/discs, and verifies the active scene against the original final T3 fingerprint before saving. It refuses to overwrite existing output. This process was actually tested, then the reconstructed file was reopened in a separate Blender process and passed all geometry, route, water, crowd, mural and image checks. See evidence/restore-check.json and evidence/restored-fresh-open.json. Blender serialization can produce a different whole-file hash while the checked scene content is identical.

For authoring reproducibility, `source/build.py` can rebuild the cavities from the exact T2 master using the included road-layout configuration. It needs no external textures because the base and delta pack their image data. `source/render.py -- --source /path/to/master.blend --expected-sha256 ACTUAL_SHA256` renders the saved lighting; its default source paths refer to the session working files. `source/create-review.py` rebuilds the PDF from the included, hash-verified captures. Its before views are included in the preceding T2 report folder inside the checkpoint.

For the isolated browser asset review, place the downloaded GLB in this report's delivery directory, serve the extracted repository root with a local HTTP server, and open this report's viewer/index.html. The checkpoint includes the four required Three.js vendor files and license. The automated Playwright check requires Playwright and Chromium at /usr/bin/chromium. Runtime viewer lighting is diagnostic; the PDF uses the actual native night lights.

The ordinary Rev15T3 asset names are final. Files prefixed Superseded-First-Pass retain an earlier cavity study and should not be used for restoration. Original quarry website movement code is unchanged; full-world production integration remains pending.
