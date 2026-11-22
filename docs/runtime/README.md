Current integration covers [map navigation across the cypher route](M2K-CYPHER-MAP.md), the [Accommodation wall](M2J-CYPHER-ACCOMMODATION.md), the [cypher Aftermovie screen](M2I-CYPHER-AFTERMOVIE.md), the [Team mural carousel](M2H-CYPHER-TEAM.md), the [cypher Events wall](M2G-CYPHER-EVENTS.md), the [cypher enquiry window](M2F-CYPHER-CONTACT.md), the [walkable cypher plaza](M2E-CYPHER-PLAZA.md), the [market lane and quarry entry](M2D-MARKET-LANE.md), the [navigation approach and sponsor display](M2C-NAVIGATION-APPROACH.md), the [native lane and cypher gate](M2B-CYPHER-GATE.md), and the [native Contact journey](M2A-CONTACT-JOURNEY.md). Full-world integration is in progress.

# Current rendering correction

See [TEXTURE-ALPHA-FIX.md](TEXTURE-ALPHA-FIX.md) for the current clean-v2 rendering pipeline and its verified checkpoint. The original M0/M1 notes below describe the initial prototype and remain as history.

# Private locked-world runtime pilot

The exact Rev15Z native is immutable. This branch adds an actual source-derived Contact frontage as the first export experiment. It does not mount the whole level, replace live routes, or provide a finished movement journey. See `M0-AUDIT.md` for the website backlog.

## Run the supplied standalone preview

Serve the restored `public/models/gullyverse/locked-rev15z-v1` directory over HTTP:

```sh
python -m http.server 8893 --bind 127.0.0.1 --directory public/models/gullyverse/locked-rev15z-v1
```

Open `http://127.0.0.1:8893/`. The bundled viewer needs no running Next server or backend. It uses real GLB geometry/PBR maps, an explicitly bound lightmap, KTX2 device transcoding and Meshopt decoding. The form intentionally sends nothing. A phone viewport gets the 1024-pixel texture tier and an accessible form sheet. The same Canvas remains mounted during asset switches.

## Rebuild

Restore the exact frozen native from the separate Frozen Rev15Z Source Seal. Verify its complete SHA-256 against `ART-LOCK.json`. Restore this source overlay onto repository commit `0e1e23dd2f5181df202d862d147067249bc55a41` and install the repository's locked npm dependencies. Use Blender 4.3.2, including its NumPy module.

```sh
npm ci
npm ci --prefix scripts/gullyverse/toolchain
```

Install the official KTX-Software 4.4.2 Linux build from the URL in `TOOLCHAIN.json`; verify the listed SHA-256 before extraction. Set `KTX_BIN` to its `bin` directory. The external toolchain directory contains the locked glTF Transform CLI; it is not a production dependency.

```sh
export GULLYVERSE_TOOLS="$PWD/scripts/gullyverse/toolchain"
export KTX_BIN=/absolute/path/to/KTX-Software-4.4.2-Linux-x86_64/bin
node scripts/gullyverse/build-pilot.mjs /absolute/path/to/Gullyverse-Rev15Z-Wide-Contact-Window-and-Restored-Graffiti.blend
```

Output is versioned by `export-plan.json`. Hash mismatches stop the build. `BLENDER` can override the executable. `TMPDIR` should point to a writable directory with enough free space. This session used tmpfs because the original workspace filesystem was full; no valid Git objects or user assets were removed.

## Export contract

- Original packed source images/UVs survive where glTF supports their channels; unsupported procedural colour, normal and roughness channels are converted to maps. The original Generated-coordinate frame is preserved when clipping a house mesh. No portrait/sign/poster artwork is redrawn.
- Eighteen source meshes produce 5,745 triangles and 29 material bindings. Only a bounded part of the Contact house/frontage is included; the complete source inventory accounts for everything else as bake context, future chunks or explicit exclusions. Native form illustrations become accessible HTML.
- Disjoint object tiles hold `RuntimeLightmapUV`, bound explicitly per material to channel 0, 1 or 2. The source may already use two UV sets; assuming every lightmap is UV1 would be wrong. The UV round-trip validator verifies all 29 bindings against Blender.
- Static diffuse irradiance is separate from source colour. The full source provides shadows/bounce context. Fog volumes are excluded from the bake. Practical-light range selection and decorative emission conversion are documented in the manifest; exact Eevee falloff/color-management matching is still an open quality task.
- Baseline uses linear Radiance HDR. Compressed lightmaps use linear RGBM RGBA8, where alpha is independent numeric data. The PNG writer bypasses Blender's float-image unpremultiplication; numerical round-trip error is asserted. PBR maps use Basis/KTX2 mipmaps. The alpha-as-data lightmap uses lossless RGBA8 KTX2/zstd because lossy alpha clipped dark shadows; linear base-level filtering matches the HDR baseline while atlas mip filtering remains under review. Fog and final view treatment remain runtime work.
- Collision GLB and trigger JSON are separate conservative pilot proxies. They are not a validated full-level collision map. Blender-to-Three mapping is `(x,y,z) -> (x,z,-y)`, source floor 7.2 and eye height 1.7; the old quarry registry needs an adapter.
- Compression deduplicates data, applies UASTC level 2/zstd18 and Meshopt without decimation. Normalized lightmap UVs/positions are quantized; repeating source UVs outside `[0,1]` retain floats. Desktop preserves source image dimensions; mobile limits PBR images to 1024. Native master is never saved.
- Two independent exports from the same baked derivative matched byte-for-byte. Full bake and cross-platform byte determinism are not asserted. Runtime inputs/outputs have hashes and fixed seeds; wall-clock bake timings are informational.

## Validation and limits

`browser-check.cjs` checks actual imports, desktop/mobile layouts, Canvas identity, cleanup, failure fallback, reload and local-only form behavior. `validate-output.py` checks GLB structure, preserved source images and complete inventory accounting. `verify-uv.py` runs inside Blender. Browser diagnostics use SwiftShader; their slow frame times and phone emulation are not device-performance evidence.

The first browser lightmap remains visibly different from the saved Blender night render. The visual acceptance gate is open; do not promote these assets into production until the comparison passes. Whole-world journeys, original-controller integration, live content/admin integration, device profiling and submission hardening remain M2–M5. The full Next build passed against the user-selected disposable local PostgreSQL fixture backend and anonymous auth placeholder. Actual Contact POST validation/persistence and catalog reads passed; hosted authentication/admin integration remains open.

The Drive checkpoint includes the standalone viewer, editable baked component, source scripts, manifests, evidence and review PDF. It references the exact frozen source seal and original repository commit; it excludes dependencies, caches, credentials and unrelated original website assets. The browser bundle is self-contained once served over HTTP. Whole-website recovery also requires the original repository/LFS assets or prior verified website checkpoint.
