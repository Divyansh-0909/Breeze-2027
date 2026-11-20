# Native lane and cypher gate

The walking adapter reads the grade and collision footprints exported from frozen Rev15Z. It shares the existing controller, input, player radius and 1.72 m eye height. Native Blender coordinates map to Three as `(x, y, z) → (x, z, -y)`.

The four road sections run from the lane at 6.0 m, up the 1:20 ramp, to the cypher at 7.2 m. The smooth floor follows the original road grade under the visible potholes. Collision uses separated wall wings and jambs, the open steel leaf, navigation supports, road-level lamp hardware and nearby characters. The lane edges keep visitors on the road in front of the shops. The cypher walk space currently ends at the forecourt, 22 m along the source Y axis.

Regenerate the collision data with Blender 4.3.2:

```sh
blender -b --python-exit-code 1 --python scripts/gullyverse/export-walk-space.py -- \
  /absolute/path/to/frozen-Rev15Z.blend \
  components/gullyverse-runtime/cypher-walk-space.json
npm run test:immersive
```

The tests drive the actual controller from the market lane through the gate and back. They cover grade joins, wall sliding and collision from either side of the gate. The centreline and player-radius samples also found native road geometry at all 1,248 points.

## Browser preview

Set `GULLYVERSE_RUNTIME_PREVIEW=1` on the local Next server and open `/runtime-preview/cypher`. The preview starts beyond the navigation stand and covers the open gate and forecourt. The geometry includes both connector houses and the adjoining asphalt faces, for 25 source objects and 15,196 triangles. It uses the existing asset pool, controller, input and shader preparation. The 1024 px, 128-sample diffuse lighting atlas has 11 denoised, linear-light mip levels. PBR remains a separate 2048 px bake, with a 1024 px mobile texture tier.

```sh
# Rebuild with the pinned toolchain from TEXTURE-ALPHA-FIX.md
bash scripts/gullyverse/build-cypher-gate.sh /absolute/path/to/frozen-Rev15Z.blend /writable/gate-build
CHROMIUM_BIN=/usr/bin/chromium node scripts/gullyverse/cypher-gate.browser.cjs /writable/review-folder
```

The browser test walks through and back with a keyboard, checks the same canvas remains mounted, walks through again using iPhone touch emulation, and verifies the WebGL fallback. The native source stays locked. The night preview around the gate is very dark. Full scene assembly and native-to-browser lighting comparison are pending. The market lane visual chunks, quarry handoff, outer cypher and the destination journeys remain future integration work.

## Contact database

The checked-in Contact migration reconciles the server's existing `ContactSubmission` model with the Prisma migration history. The disposable database test verifies creation with row-level security, form validation and persistence, and applying the migration again with a submission already present. The hosted login and admin inbox still need integration testing.
