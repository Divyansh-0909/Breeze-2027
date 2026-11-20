# Rev15T3 / Rebuilt potholes

13 November 2026. The user reported that the wet-grain road revision had ruined the potholes. This phase supersedes Rev15T2 for the visible ground defects.

Sixteen potholes have been rebuilt as cavities stitched into the existing visible floor meshes. They have irregular fractured asphalt rims, exposed aggregate along their sides, and smoother damp muddy beds. The old pyramid-shaped scatter and five small puddle discs are hidden in the new scene. 112 flattened irregular asphalt chips replace the pointed scatter. Four water surfaces follow the cavity contours 4.7–5.5 cm below the road; the sloped ramp defects use damp beds. Sixteen long side pools are retained.

The final refinement removes the first cavity study's faceted mud beds and rectangular material transition. Its two uploaded assets are explicitly named Superseded-First-Pass. Use the ordinary Rev15T3 filenames and current upload receipts.

The central walking strip, original navigation shell, ramp grade, flat unpainted cypher centre, all 189 original LOD0 crowd meshes, eight mural states, shops and signs remain. Existing lamps, world, exposure and T2 reflection settings are unchanged. No inspection lighting or post-capture brightening is used in the PDF.

The working master is `/dev/shm/Gullyverse-Rev15T3-Rebuilt-Potholes.blend` (216,317,316 bytes; SHA256 `09fa6d949d4b45c8a44dc5d465ba1ee1795ad695976ce1311de9375d711d416b`). It has 52 scenes, preserving 51 historical scenes, and 102 packed images. Native backup is incremental: the complete verified T2 master plus the packed T3 ground delta reconstruct the final active scene; see RESTORE.md. This restores equivalent scene content, rather than claiming byte-identical Blender serialization. The original T3 file's checksum remains recorded separately.

Validation passed: fresh-open checks of all 16 cavity depths, four recessed water contours, non-inverted fracture faces, 36 route-grade samples, 192 flat cypher samples and 1,040 edge-water vertices. The actual restore helper reconstructed the scene from the base and delta, matched geometry, UVs, vertex colours, material assignments, transforms, visibility and lights, then passed a separate fresh-open check. All eight original quarry movement/input/rendering file hashes are unchanged.

The separate runtime GLB is 12,937,412 bytes (SHA256 `2c7034022ab909a69c89d0845810f4acc3e6fa7a3c7a94e9ffb7930e40802889`), with 28 nodes and five embedded images. The isolated browser viewer loads three views without console or GL errors and verifies the road UV channels and eleven route ray samples. These checks do not measure full-world production performance. Public website integration remains pending. No commit, push or deployment occurred. No Firecrawl was used.

[Final review PDF](https://drive.google.com/file/d/1zFHlY9zRDnqO4CNiaWJSYJlluv9ZI1Mr/view); local copy: `review/Breeze-Rebuilt-Potholes-Review.pdf`.

[Versioned Drive phase](https://drive.google.com/drive/folders/1bQNlVv5ehwfFrRIQT6NlefT0lqTT5EcS). Current remote IDs and content verification are in evidence/*-upload.json and the final remote receipt. The source checkpoint also preserves the preceding T2 authoring scripts, textures and evidence. User-attached references are described in the evidence; the original attachment bytes were not available as a local file.
