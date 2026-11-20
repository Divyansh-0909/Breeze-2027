# Night environment camera-tour recovery

This phase records the current approved night environment. It adds a capture-only full-scene export and recording harness. It does not integrate the scene into a production website route or change the original quarry controller. The interactive integration remains pending.

## Open the deliverables

The final video is `video/Breeze-Night-Environment-Full-Tour-2026-11-12.mp4`. It is a silent, 1 minute 54 second camera tour. `review/Breeze-Night-Environment-Tour-Companion.pdf` contains key views and chapter times.

The capture source ZIP is independently sufficient to open the exported scene: extract its paths under a repository root, run `python reports/night-environment-video-tour-2026-11-12/source/serve.py`, then open `http://127.0.0.1:8771/`. Python 3.9+ and a WebGL2 browser are sufficient. The exact Three.js 0.169 runtime and loader are included. The exported scene initially opens at the far lane camera; the recording script supplies the tour path. No account or Google Drive connection is required for local viewing.

Verify all payloads against the checkpoint index. The source video and final video are stored as separate verified outputs if excluded from a source archive; consult the final delivery index for exact locations and hashes. Earlier verified source checkpoints and masters were preserved.

## Rebuild from the packed native master

Rebuilding requires the complete earlier Rev15P base checkpoint. Download its 11 parts and the recovery index/script from the dated backup; the packed native master is included there. Native/base folder: https://drive.google.com/drive/folders/19lLbeomN6cqhASBobc3T2SvmUHoz8wKG

Earlier combined recovery index and script: https://drive.google.com/drive/folders/1vIEijMklnKneib70t0xEnHo9mKaZQ7dh

Native dependency: `reports/night-atmosphere-rev15p-pilot-2026-11-11/delivery/Gullyverse-Rev15P-Night-Atmosphere-Pilot.blend`, 171,729,972 bytes, SHA-256 `f539f05e9fe2e82d2909a79f326f6b53485d3e00832707a51ab073c269d95682`. It retains all 45 earlier scenes plus the isolated night scene, all 69 packed images and all eight mural states.

Use Blender 4.3.2, Python with NumPy/Pillow, Node 24 with the checkout's Sharp/Playwright dependencies, Chromium, FFmpeg with libx264/framerate, and ReportLab/pypdf/DejaVu fonts for the PDF. Source scripts retain the execution workspace paths; adjust those explicit paths when restoring elsewhere. Installed dependencies and credentials are deliberately excluded from backups.

1. From the checkout root, run `blender -b -t 2 --python reports/night-environment-video-tour-2026-11-12/source/export-full.py`.
2. Run `python reports/night-environment-video-tour-2026-11-12/source/rebuild-full.py`. This regenerates paint projection, texture conversion, diffuse illumination, ground maps, the unlit GLB and the mural lightmap. None saves a native Blender file.
3. Start `source/serve.py`, then run `node reports/night-environment-video-tour-2026-11-12/source/record-tour.mjs` to render the deterministic 10 FPS source camera sequence into an MP4.
4. Run `source/encode-delivery.py` to make and strictly validate the 24 FPS delivery copy. This offline temporal frame interpolation is a video presentation step, not a measurement of live website performance.
5. Run `source/create-companion.py` after key frames and `evidence/video-upload.json` exist to regenerate the PDF. The saved upload receipt supplies the clickable video URL.

The exact original 10 FPS recording is backed up as four verified binary parts. Download the part names in `checkpoint/source-video-parts-index.json` into a directory and run `python source/restore-source-video.py DOWNLOAD_DIRECTORY NEW_OUTPUT.mp4` from this phase directory. The helper verifies each part and the combined SHA-256 before installing the output. The source archive intentionally excludes video bytes; the final delivery index links the playable MP4 and the source parts.

## Material and coverage contract

The full export retains every visible native mesh/font/curve in the current Organising Committee state, without the earlier lane/cypher subset bounds. It contains 1,433 evaluated source objects, all 189 source crowd meshes, and 702,088 exported triangles. Crowd poses and the Aftermovie screen images are static. The 62-logo LED advances at the source 30 cells/second using film time. This tour does not cycle the other seven mural states; they remain in the packed native source.

The GLB uses vertex lighting with `nativeLightfieldScale=32`. The supplied viewer applies the scale and binds the ground lightmap/roughness atlas on UV1. The mural receives a separate UV0 lightmap because four corner samples incorrectly blackened the whole mural in the first capture export. During its unsaved texture bake, the original coplanar artwork visibility driver is cleared in memory to prevent self-shadowing. The viewer uses the best tested mural multiplier from the native-camera comparison, without editing the original artwork, source geometry or lighting master. The supplied viewer is the material reference; arbitrary GLB viewers may display different brightness.

The video is a camera inspection of the private environment. It does not demonstrate walking collision, public-site deployment or physical-device FPS. It preserves the native source and all eight recorded website movement/rendering hashes. The rejected Schedule navigation label remains an unresolved placeholder in the source scene.
