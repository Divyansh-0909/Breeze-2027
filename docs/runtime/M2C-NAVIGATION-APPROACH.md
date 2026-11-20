# Native navigation approach

The gated `/runtime-preview/cypher` opens on the upper ramp, with the navigation stand ahead. The existing controller walks up the ramp, below the signs, and through the steel gate into the forecourt on one canvas. The player can retrace the same route. The walk starts at source Y 2.2 m and uses the original smooth grade beneath the native asphalt. Collision includes the stand’s supports and the nearby lane figures.

The new chunk exports 46 locked Rev15Z objects, including the upper ramp, three figures, and the sign assembly with its original English lettering, arrows, and LED casing. Font curves and beveled pieces are evaluated before baking so the exported meshes sample the baked lighting at the same positions. The browser uses a uniform diffuse value on the white sign ink and borders so individual letters stay legible under the night lighting. The green panels use their baked shading. The adjoining gate asset provides the rest of the road and the connector houses.

The Past Sponsors display uses the frozen scene’s original strip of 62 logos with the original spacing. The 2048 × 384 texture rearranges the precise grayscale pixels into six banks and the shader looks up the original cells. It scrolls 30 cells per second and stops when reduced motion is enabled.

To rebuild the approach with the existing pinned Blender, KTX and OIDN toolchain:

```sh
bash scripts/gullyverse/build-cypher-gate.sh /absolute/path/to/frozen-Rev15Z.blend /writable/approach-build approach
blender -b --python-exit-code 1 --python scripts/gullyverse/export-walk-space.py -- \
  /absolute/path/to/frozen-Rev15Z.blend components/gullyverse-runtime/cypher-walk-space.json
```

With `GULLYVERSE_RUNTIME_PREVIEW=1` on the local Next server, run `CHROMIUM_BIN=/usr/bin/chromium node scripts/gullyverse/cypher-gate.browser.cjs /writable/review-folder`. The checks cover a keyboard round trip, an emulated phone touch crossing, the logo scroll, the reduced-motion preference, and the HTML fallback. Floor probes against the exported baseline GLBs cover the join between the upper ramp, apron, and cypher slab.

The lower market lane, connection to the quarry, and the full cypher and destination views remain in progress. The native master continues to be the source of record for the complete night scene.
