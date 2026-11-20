# Restore Rev15U2

Use Blender 4.3.2. Verify and extract this phase's source checkpoint ZIP. It includes every required T3, U1 and U2 recovery module under the original repository-relative paths, the private board viewer, reports, evidence and payload checksums. Native dependencies are reused verified Drive files listed in delivery/Dependency-Index.json and delivery/Base-Rev15T2-Native-Parts.json.

1. Download the thirteen complete T2 native parts, the final T3 ground delta and the U1 bilingual styling delta. Do not use an earlier English-only or first-pass component.
2. From the extracted repository root, run the following with your actual download and output paths:

```bash
python reports/ground-rev15t3-rebuilt-potholes-2026-11-13/source/restore-master.py /path/to/base-parts /path/to/T2.blend --index reports/navigation-board-rev15u2-english-centred-2026-11-14/delivery/Base-Rev15T2-Native-Parts.json
blender -b --python reports/ground-rev15t3-rebuilt-potholes-2026-11-13/source/restore-native.py -- --base /path/to/T2.blend --delta /path/to/Rev15T3-Rebuilt-Potholes-Additions.blend --output /path/to/T3.blend
blender -b --python reports/navigation-board-rev15u-highway-green-2026-11-13/source/restore-native.py -- --base /path/to/T3.blend --delta /path/to/Rev15U1-Bilingual-Highway-Sign-Styling.blend --output /path/to/U1.blend
blender -b --python reports/navigation-board-rev15u2-english-centred-2026-11-14/source/build.py -- --restore --base /path/to/U1.blend --output /path/to/U2.blend
```

The complete T2 base checksum is 33a2e589654ed8aaed1c5abee13111630118c24bff054331f2891160abee8fdb. The U2 source verifies the U1 scene fingerprint before making changes and checks the reconstructed U2 scene against its original fingerprint before saving. It refuses to overwrite an existing output. Actual reconstruction and a separate fresh opening passed, including all seven visible label centres, unchanged panel/arrow transforms, road attributes and unchanged digital sponsor display. See evidence/restore-check.json and evidence/restored-fresh-open.json. Whole-file serialization hashes may differ.

The packed Rev15U2-English-Centred-Labels.blend component contains the editable seven font objects and their packed English fonts. It is useful for authoring; the reconstruction command above uses the included deterministic source and the fonts already packed in U1. Hindi is removed only from the active navigation scene, preserving historical scenes and earlier verified backups.

For the private browser review, serve this report's viewer directory and open index.html. The GLB, original sponsor display assets and required Three.js files and license are included. This viewer uses diagnostic lighting; the PDF uses the native saved night lights. Full-world production website integration remains pending.
