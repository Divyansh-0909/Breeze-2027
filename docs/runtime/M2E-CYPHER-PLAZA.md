# M2E Walkable cypher plaza

Run the gated Next preview with `GULLYVERSE_RUNTIME_PREVIEW=1`. The market route continues through the steel gate onto the plaza and connects to the same way back. Use `/runtime-preview/cypher?start=plaza` to start inside the gate. The market, navigation approach and quarry entry links described in [M2D](M2D-MARKET-LANE.md) are also available.

The plaza export includes the rest of the rooftop slab, the native perimeter houses, the screen with its existing still, and the destination frontages that face the plaza. It keeps the visible Team mural state, the eight Events placeholders, the Accommodation lettering and the Contact façade. The audience export uses the locked positions, scales, outfits and poses of all 180 actors with their authored LOD1 meshes. The six plaza characters outside the audience keep their authored meshes. Lighting uses separate denoised irradiance atlases. The compressed audience payloads join opaque primitives that share a material while retaining their baked UVs. The PNG fallback records the original actor IDs. The gated scene prepares the six chunks before revealing the walkable route.

The walking adapter follows the taper of the original slab and uses the original smooth 7.2 m deck height. The player radius and movement controller carry over from earlier stages. The footprint survey sampled 40,232 positions and found six cells without upper surface support. The adapter excludes those cells and protects the edge, the nine screen supports and casing bounds, and the audience and plaza figures. The collision tests walk both sides of the plaza and back to the entrance.

## Rebuild

Use the verified Rev15Z master, Blender 4.3.2 and the KTX, OIDN and glTF tools from the [runtime README](README.md). Create a build and a review directory outside the repository.

```sh
bash scripts/gullyverse/build-market-lane.sh "$REV15Z_MASTER" "$PLAZA_BUILD_DIR" plaza
bash scripts/gullyverse/build-market-lane.sh "$REV15Z_MASTER" "$PLAZA_BUILD_DIR" audience
blender -b --python-exit-code 1 --python scripts/gullyverse/plan-plaza-walk.py -- "$REV15Z_MASTER" components/gullyverse-runtime/plaza-walk-space.json
blender -b --python-exit-code 1 --python scripts/gullyverse/verify-plaza.py -- "$PLAZA_BUILD_DIR/verification.json"
node node_modules/typescript/bin/tsc --noEmit --incremental false
npm run test:immersive
node scripts/gullyverse/cypher-plaza.browser.cjs "$PLAZA_REVIEW_DIR"
```

The browser test starts by the navigation stand and uses actual keyboard and touch input through the gate. It checks the loaded desktop and mobile payloads, the return on the same canvas, and asset and shader errors. Chromium's software renderer and phone emulation are used for functional checks.

Destination interactions have their own remaining integration work, including live poster data, the other Team carousel states, the enquiry form, and screen playback. Visual matching and physical-device performance checks are still open.
