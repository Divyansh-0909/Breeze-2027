# Restore Rev15U1

Use Blender 4.3.2. Download the verified source checkpoint ZIP and Checkpoint-Index.json from this phase, verify its SHA256, and extract it. The ZIP records every payload in PAYLOAD-SHA256.json and includes a self-contained private browser viewer. It also contains the minimal T3 recovery modules under their original report path. The required native assets are separate verified Drive files; delivery/Dependency-Index.json lists their IDs, URLs, sizes and hashes.

1. Download the thirteen T2 native parts in delivery/Base-Rev15T2-Native-Parts.json. The complete base must be exactly 214,265,912 bytes, SHA256 33a2e589654ed8aaed1c5abee13111630118c24bff054331f2891160abee8fdb.
2. Download the final T3 packed native ground delta named Rev15T3-Rebuilt-Potholes-Additions.blend from the previousNativeDelta entry in Dependency-Index.json. Do not use its Superseded-First-Pass counterpart.
3. Download this phase's Rev15U1-Bilingual-Highway-Sign-Styling.blend.
4. From the extracted repository root, run the following with your actual download paths:

```bash
python reports/ground-rev15t3-rebuilt-potholes-2026-11-13/source/restore-master.py /path/to/base-parts /path/to/T2.blend --index reports/navigation-board-rev15u-highway-green-2026-11-13/delivery/Base-Rev15T2-Native-Parts.json
blender -b --python reports/ground-rev15t3-rebuilt-potholes-2026-11-13/source/restore-native.py -- --base /path/to/T2.blend --delta /path/to/Rev15T3-Rebuilt-Potholes-Additions.blend --output /path/to/T3.blend
blender -b --python reports/navigation-board-rev15u-highway-green-2026-11-13/source/restore-native.py -- --base /path/to/T3.blend --delta /path/to/Rev15U1-Bilingual-Highway-Sign-Styling.blend --output /path/to/U.blend
```

The helpers refuse to overwrite an existing output. T3 and U1 restoration validate the active scene content, including geometry, UVs, vertex colours, material assignments, visibility, transforms and lighting; U1 also checks the font data. The U1 helper preserves all 52 historical scenes and adds the 53rd. It restores the original local transform channels, then creates the fresh view layer after linking the style delta. This prevents a matrix decomposition from changing the saved Euler rotations. The actual reconstructed file is then reopened independently to verify the original panel transforms and unchanged digital display. See evidence/restore-check.json and evidence/restored-fresh-open.json. File serialization checksums can differ; the checked scene content must match.

The fonts and styling source are included. To rebuild the styling through its authoring script, use source/build.py with --base pointing to a restored T3 file and --expected-sha256 set to that file's actual checksum. This authoring command writes a new master and delta, so choose a separate output. It is not necessary for the primary native restore path above.

For browser review, serve the extracted viewer directory with any local HTTP server and open index.html. Its board.glb, vendor files and original sponsor atlas/manifest are included. The separate runtime GLB uploaded to Drive is byte-identical to viewer/board.glb. The Playwright browser check requires the project's Playwright dependency and /usr/bin/chromium. Browser lighting is diagnostic; the PDF uses the saved native night lighting. Full-world production website integration remains pending.

The final scene uses Hindi and English, taller 0.68 m destination panels and Accommodation in place of Schedule. The earlier English-only U draft is preserved in history/english-only, with its source build, fonts, packed component and verification records.
