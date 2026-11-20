# M2D Market lane and quarry entry

Set `GULLYVERSE_RUNTIME_PREVIEW=1` before launching Next. Open `/runtime-preview/cypher?start=quarry` to enter through the original quarry and cave. The existing entrance sequence runs in the same canvas that renders the market. The curtain covers the switch between the original quarry coordinates and the Rev15Z market coordinates. The market then uses the original keyboard, touch and camera behavior on the existing walking adapter. Open `/runtime-preview/cypher` to start at the south end of the market, or use `?start=approach` to start by the navigation stand.

The `market-south` chunk owns the flat road and lower storefronts. The `market-north` chunk owns the next storefronts and the exact source ramp faces outside the existing navigation approach. The existing gate and forecourt complete the route. The source geometry includes the open and shuttered shops, road relief and water, overhead cables, and lamp poles. Small rigid opaque props with equivalent material and UV bindings share meshes within each section. The export manifests record the source objects in each group. Translucent surfaces, lighting hardware and the road keep their own bindings.

L01 and L04 are steady. L02 and L05 remain off. L03 and L06 use the authored timing for their visible lenses. Reduced motion keeps both flickering lenses steady. The road light pools are static irradiance bakes. The new chunks have 2048 px procedural maps and 1024 px denoised irradiance atlases. The authored image channels retain their existing UVs, with separate desktop, mobile and PNG fallback payloads.

## Rebuild and verify

Use Blender 4.3.2 and the KTX, OIDN and glTF tooling documented in [the runtime README](README.md). Provide the locked Rev15Z master when running the exporter. It verifies the source SHA-256 before creating writable derivatives. Use a build directory outside the repository.

```sh
bash scripts/gullyverse/build-market-lane.sh "$REV15Z_MASTER" "$MARKET_BUILD_DIR" south
bash scripts/gullyverse/build-market-lane.sh "$REV15Z_MASTER" "$MARKET_BUILD_DIR" north
blender -b --python-exit-code 1 --python scripts/gullyverse/verify-market-floor.py -- "$MARKET_BUILD_DIR/floor.json"
node node_modules/typescript/bin/tsc --noEmit --incremental false
npm run test:immersive
node scripts/gullyverse/market-route.browser.cjs "$MARKET_REVIEW_DIR"
node scripts/gullyverse/cypher-gate.browser.cjs "$GATE_REVIEW_DIR"
```

The screenshot directories must exist. The browser scripts default to `http://127.0.0.1:8898`. Set `BREEZE_PREVIEW_ORIGIN` and `CHROMIUM_BIN` when needed. The floor verifier found road geometry at all 5,719 sampled positions across the four published PNG fallback chunks. The maximum difference from the smooth walking grade was 7.7 cm. The two exports cover all 4,216 source ramp faces without overlap.

The quarry handoff is one way in this preview. The lane can be walked in both directions between its south end and the cypher forecourt. The full cypher, destination travel and return, a fixed-view lighting comparison, and physical device benchmarks remain pending.
