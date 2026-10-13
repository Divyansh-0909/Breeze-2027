# Limestone rock pilot — October 12, 2026

The user approved the first rock pilot and requested a limestone variant. This is a **separate asset and isolated preview**. Neither the original pilot nor the approved production environment is changed. No commit, push or deployment. Starting branch `codex/navigation-board`, HEAD `e3dbbc233f1f12f5e4d96333db3b797e75da4760`, empty tracked staged/unstaged diff; prior untracked assets/review evidence remain preserved. [Starting record](raw/starting-state.json), [hash preservation](raw/preservation.json).

## Visual comparison

[Open the browsable gallery](gallery.html). Ten actual Chromium PNGs at original resolution; desktop1366×900 and portrait390×844, effectiveDPR1, FOV58. [Camera/quaternion/lighting metadata](raw/captures.json). Portrait screens are aspect checks, not physical phone benchmarks.

The pale warm-gray/ivory calcite albedo, muted mineral staining, finer chalky normal response, matte roughness and shallow solution pockets distinguish this from the darker first pilot. It retains the first pilot's layered quarry form and anchor. Macro geometric bedding remains the same style; this is a variant, not a new overall quarry silhouette. No external reference-image texels or third-party material images were used. Some long bedding/slab regularity and cap mapping still need any future final-art refinement; this is not a claim of complete photographic realism.

Lighting is the unchanged Hub global configuration: background/fog#737d87 at205–520m; hemi#a9bfd4/#8a8274 intensity1.35; direction[-70,37,-145] #efd0a4 intensity1.35; practical[0,9.75,-67.4] #ffc681 intensity42, range21, decay2. ACES exposure1, sRGB output, shadows disabled. No special light or exposure was introduced for the limestone. The slightly darker/cooler cracks are the material and actual geometry under those lights. The stage-specific global mode was not substituted/tested on this segment.

Fixed medium inspection camera[31,5.6,-98] looking at[46,5,-104], close[41.1,5.4,-103.4] at[45.9,5.4,-104], long[3,7,-87] at[46,5,-104]. Development anchor[47.4,0,-104], yaw−π/2, scale1; the procedural wall stays intact behind the opt-in patch. Existing production cameras/coordinates/bounds/map are untouched.

## Asset files and export

[Editable Blender master](../../assets-source/gullyverse/limestone-pilot/quarry-limestone-pilot.blend), **9,760,728 bytes**; [combined runtime GLB](../../public/models/gullyverse/pilot-limestone/quarry-limestone-pilot.glb), **3,748,024 bytes**. [Asset instructions](../../assets-source/gullyverse/limestone-pilot/README.md), [LOD/anchor manifest](../../assets-source/gullyverse/limestone-pilot/asset-manifest.json), [asset inventory, hashes and texture specifications](raw/asset-inventory.json).

Blender4.3.2, original metre-scale closed surface, editable100,992-triangle master; runtimeLOD0 **32,616**, LOD1 **10,440**, LOD2 **2,820** triangles; proxy12. BlenderZ-up/front−Y→glTFY-up/front+Z. Approx12.075m wide×10.017m tall×4.106m deep. Unique frontUVs, lower-density caps, exported normals/tangents. Three explicit LODs share one visual PBR material/three maps in the combined GLB. Source maps2048px, runtime1024px baseJPEG/normalPNG/packedORMPNG. Estimated decoded RGBA8+mips **16MiB** per limestone material set, not driver VRAM measured. No compression decoder/runtime dependency was added. The old2MB experimental transfer target is still not met; file size is smaller than the first pilot4,127,092B, but this does not establish faster physical rendering.

The editable source and separateLOD/proxy GLBs are provided. Hide all but one LOD and the proxy explicitly; visibility is not encoded by glTF. Shared-cache ownership is preserved with the original unchanged `BlenderAsset` infrastructure; no production cache management changes.

## Verification

- Fresh Blender master reopened; all runtime vertices lie inside the proxy, signed volume positive, correct units/object scale, UVs and eight packed maps present. [Inspection](raw/master-inspection.json).
- All five GLBs pass Khronos validation with **zero errors/warnings**. [Validator results](raw/glTF-validator.json). A missing earlier temporary validator was reinstalled in `/tmp` only; project dependencies were not modified.
- Real isolated raycast succeeds. Shader preparation and six covered warm draws precede reveal. Browser captures showed no broken materials/UVs; this is settled-frame evidence, not a certified physical first-render hitch test.
- Ten alternating limestone mount/unmount cycles after warming both comparison assets plateau at **7 geometries / 7 textures / 3 programs**. Two URL parses total, one original and one limestone. Both caches deliberately retain their warmedLOD geometries/textures between mounts.
- Retirement occurs only after all preview consumers unmount: disposes8 owned geometries incl. proxies,4 materials incl. proxy defaults,6 textures and closes6ImageBitmaps, clears only these two isolated preview URLs. Counters return to ground-only **1geometry / 1texture / 1program**. Original production caches are not involved. [Resource and browser evidence](raw/preview-verification.json).
- Preserved hashes:664 original production source/config/assets; earlier pilot/report/master/exports/ZIP and original authoring tools. No original production source modification, no new navigation/state-machine work. Full production regression/build suites were not rerun for this isolated asset-only variant; preceding Stage2A results remain intact, and this variant received its own export/loader/geometry/lifecycle checks.

## Software-renderer diagnostics

Chromium151.0.7922.173, Debian13 cloudVM with ANGLE Vulkan SwiftShader (renderer string in raw evidence). Desktop1366×900, fixedDPR0.5, no CPU/network throttle; two sequential8-second samples after readiness. Same medium camera/light/render settings; screenshot collection is in separate DPR1 pages. No physical laptop, iPhone or AndroidGPU is available. Physical benchmarks remain pending and do not block this variant.

| Variant | FPS | p50 / p95 / p99 / max ms | Calls | Triangles |
|---|---:|---|---:|---:|
| original-stone-medium | 7.62 | 127.6 / 167.0 / 174.6 / 179.0 | 2 | 43,880 |
| limestone-medium | 9.01 | 110.9 / 147.5 / 152.9 / 153.3 | 2 | 43,880 |


These short software measurements vary with VM scheduling; the FPS difference does **not** certify a limestone performance improvement. Both renders include the same11,264-triangle common ground plus selected32,616-triangleLOD0. No sustained60FPS or driverVRAM leak-free claim. Resource plateau reflects bounded preview caches, not proof about driver memory. The asset remains opt-in and contributes zero default production transfer/geometry.

## Portable review package

`gullyverse-limestone-pilot-review.zip` contains this note, gallery/allPNG/metadata/raw checks, Blender master/maps, five limestoneGLBs, the original GLB for comparison, unchanged shared authoring field, new authoring scripts, bundled local viewer and font. Extract and run `python reports/limestone-rock-pilot-2026-10-12/preview/serve-preview.py`; open localhost:3002. The normal website and original pilot remain unchanged.

New files only: `scripts/blender/limestone_pilot_surface.py`, `limestone_pilot_materials.py`, `author_limestone_pilot.py`, `inspect_limestone_pilot.py`; dedicated `assets-source/gullyverse/limestone-pilot/`, `public/models/gullyverse/pilot-limestone/`, this report directory and review ZIP. No full quarry, tunnel, stage or other destination was replaced. This variant stops at review; no permanent production substitution is made.
