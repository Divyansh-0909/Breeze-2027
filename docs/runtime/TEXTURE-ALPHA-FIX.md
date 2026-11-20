# Texture grain and transparent graffiti correction — 15 November 2026

Current private runtime version: `locked-rev15z-clean-v2`. The frozen Rev15Z master, original geometry, original PBR texture images and all earlier texture UVs remain exact. This correction changes the lighting export and sampling, rather than blurring or repainting the artwork.

The old lightmap split 2048 pixels into equal small object tiles, retained sampling noise, and forced transparent receiving planes opaque. The replacement uses an area-weighted shared `RuntimeIrradianceUV` set, explicit channels up to UV3, a combined bake-only receiver and OIDN 2.5.1's RTLightmap filter. A numerical guard rejects a silent denoising no-op. Only irradiance is filtered. The source art, colour, normal and roughness maps are unchanged.

The bake-only receiver is offset 1 mm along its source normals to avoid coplanar shadow intersections with the original shadow geometry. This bias is not applied to the exported visual meshes. Transparent graffiti casts no rectangular shadow. Both standalone headings — CONTACT US and COMING / SOON — retain their original PNG alpha, export as BLEND, use the shared `runtimeDecal` material policy and preserve their lettering, outlines, colours and positions. The exported catalogue is `transparent-graffiti.glb`; the original PNGs are in `graffiti/`.

Twelve lightmap levels average filtered linear HDR before RGBM packing. Numeric alpha stays lossless in KTX2/zstd. Browser sampling uses trilinear filtering, bounded anisotropy and MSAA; the remaining PBR images still use UASTC/Meshopt tiers. Source artwork grain, brick detail and asphalt material detail are preserved.

Use `quality-check.cjs` for actual desktop/phone imports, Canvas identity, GPU cleanup and transparent-texel probes. The phase's visual regression compares the same camera with the decal shown/hidden, plus before/after flat-surface variation and PNG/HDR versus compressed output. Geometry, earlier UVs and packed-image hashes are checked separately. Browser captures use SwiftShader and do not establish physical-device FPS.

The full-world journey, original-controller mounting, wet-road specular/color-management fidelity, real-device profiling and submission hardening remain later milestones. No production route, original controller, database or deployment is changed by this correction. The original master remains SHA-256 `89e765de6bb68a58a6a2d17d4d6d7ea6c696a6750402ede19306bdddc6a71041`.

## Rebuild tools

Install the repository's locked npm dependencies and the external glTF CLI lock in `scripts/gullyverse/toolchain`. `bootstrap-pinned.py` downloads and verifies the official Linux x64 KTX and OIDN releases; their licenses are included under `docs/runtime/licenses`.

```sh
npm ci --prefix scripts/gullyverse/toolchain
python scripts/gullyverse/bootstrap-pinned.py "$PWD/scripts/gullyverse/toolchain"
export GULLYVERSE_TOOLS="$PWD/scripts/gullyverse/toolchain"
export KTX_BIN="$GULLYVERSE_TOOLS/ktx/KTX-Software-4.4.2-Linux-x86_64/bin"
export GULLYVERSE_OIDN="$GULLYVERSE_TOOLS/oidn/oidn-2.5.1.x86_64.linux/bin/oidnDenoise"
node scripts/gullyverse/build-pilot.mjs /absolute/path/to/frozen-Rev15Z.blend
```

Use Blender 4.3.2. The supplied editable derivative and raw lighting PFM also allow filtering/re-export without repeating the whole initial procedural-map conversion. Set `GULLYVERSE_OUT` and `GULLYVERSE_PLAN` for explicit alternate paths. The standalone preview bundle needs only an HTTP server and no backend; its form sends no messages.

The original filesystem is full. This session's isolated worktree uses tmpfs; the environment refresh cleared it once, so the original source/master were restored with checksum verification and corrected-source safety copies were uploaded before rebuilding. The final Drive checkpoint, not an intermediate safety copy, is the restoration entry point.
