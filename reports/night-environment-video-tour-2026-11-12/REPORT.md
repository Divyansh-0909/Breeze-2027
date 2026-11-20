# Full night-environment camera tour — 12 November 2026

The requested deliverable is a video tour of the environment after the approved night-lighting pass. This phase records the complete visible native night scene through a private browser capture viewer. The public website integration remains pending; no production route, movement controller or native master was changed.

The camera tour lasts 114 seconds across 13 chapters: lane arrival; warm shops; artist-painted shutters; an open-shop interior; damp paving and ramp; navigation and sponsor LED; courtyard entry; cypher and crowd; Events house wall; Organising Committee mural; Aftermovie screens and rear crowd; upper residential façades; and a complete elevated overview.

## Capture scene

The earlier three-camera browser asset omitted geometry outside its representative lane/cypher bounds. The capture export removes that bounds filter while retaining the current Organising Committee mural state. All 1,433 visible evaluated source mesh/font/curve objects and all 189 native crowd meshes are represented. The plain exported GLB has 702,088 triangles and 41 retained albedo images. Its compiled geometry/indices/UV0 and image bytes are checked against the full capture baseline; source fonts are evaluated and the glTF exporter may omit degenerate triangles. It is not an original-topology preservation claim.

The capture uses the Rev15P native night source and the Rev15P2 browser lighting contract: native diffuse lighting baked into vertex colour, an explicit UV1 floor atlas, native damp-ground roughness, cool distance fog, and the retained specular-only ground highlight. No exposure or native scene-light positions were changed. The moving LED uses the existing 62-logo atlas, spacing and 30 cells/second rate. Crowd poses and Aftermovie screen images remain static.

## Mural visibility correction in the capture

The first whole-scene camera audit showed a black mural because the four corner lighting samples were zero. The artwork image itself was intact. A separate UV0 diffuse-light texture was baked at the original mural surface, with the original lights and no saved source changes. The original carousel visibility driver had to be cleared on the unsaved source object during that bake so it would not re-enable a coplanar alpha-tested duplicate and shadow the new bake target.

A matching native night camera provides the reference. Mural lightmap factors of 0.5, 0.75, 1 and 1.5 were compared by mean absolute RGB error over the same mural area; 0.5 was closest in that descriptive check. The final light texture uses 64 samples. This binding is confined to the capture viewer; the prior pilot, original artwork and native files were preserved. Native/viewer material approximations remain documented rather than claimed identical.

## Recording and delivery

Frames are rendered deterministically at 1280×720 with an internal 0.85 render ratio. Each frame applies the scripted camera pose and sponsor-scroll time, renders the real capture geometry, and waits for GPU completion. Ten rendered frames per film second form the source video. The 24 FPS delivery version uses temporal frame interpolation with scene-cut detection. Neither frame rate certifies live website performance. The output is silent.

The PDF companion contains the 13 chapter midpoint views and a timestamp guide. Final video probing, full decode, source/website preservation checks and authenticated Drive download-back receipts are recorded in evidence and checkpoint files. Earlier verified backups and sharing permissions are retained. Camera-path geometry checks and visual inspection do not demonstrate interactive walking collision or a deployed website.

## Restoration

The supplied capture viewer, final GLB, runtime textures, exact Three.js runtime, sources, camera path and evidence are preserved in a versioned checkpoint. The separately verified packed native source is reused through the earlier Rev15P base backup. See RESTORE.md and the final delivery index. Rebuild intermediates and duplicate downloaded staging files were removed only after recording their checksums and confirming retained sources.
