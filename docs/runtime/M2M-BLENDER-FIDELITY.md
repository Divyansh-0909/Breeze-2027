# M2M Blender fidelity pass

The walkable gully and cypher are compared with the locked Rev15Z master from the same cameras. Blender 4.3 Eevee renders the saved look. The browser uses `?reviewCamera=` on the private preview route, which pins the camera to an exact Three.js pose and field of view. `scripts/gullyverse/fidelity-*.py` produce the data. The comparison found these gaps between the browser and Blender, and fixes them as follows.

## Causes and fixes

**Object-linked materials were dropped (596 slots, 73 material pairs).** Many objects share a mesh whose own material is a placeholder and override it per object. The exporter read only the mesh materials. This lost the three shutter murals (RITVIZ, CHAAR DIWARI, NEHA KAKKAR), the supporting pier and wall graffiti, shop paper and plywood backing, the mineral-concrete decks, glazing, and the crowd's varied skin and clothing. `export_locked.py` now copies object-linked slots onto the exported mesh before batching, procedural conversion and glTF export. All six walkable chunks are re-exported and re-baked.

**World-projected artwork is evaluated exactly at runtime.** The shutter murals and supporting graffiti are projected from world coordinates in Blender. Baking them into the shared atlas would blur them, so `fidelity.ts` evaluates each projection chain with the exact node constants. It only applies on the artwork's own surface (target object, world bounds, facing and, for atlas pieces, the source rectangle). Original images ship as KTX2 (desktop full size, mobile half). `fidelity-artspec.py` extracts the chains from the master.

**Road colour.** The export baked aggregate × RoadTint into a coarse atlas, about 10 cm per texel, which turned the fine asphalt into blotches. The source multiplies the 1.2 m aggregate tile (RoadDetailUV) by the RoadTint vertex colours. Both survive in the GLBs, so the runtime rebinds them. Shoulders use the source's flat mud mean colour.

**Reflections, metals and sky.** Three.js renders metals near-black without an environment. Seven Cycles panoramas render from the master at street level along the route (`fidelity-probes.py`, 1024 × 512 desktop, 512 × 256 mobile). The nearest probe drives `scene.environment`. Lightmapped surfaces keep their baked diffuse light and take only specular from the probe, so diffuse light is never counted twice. The probes load after the chunks and never delay the world. The background uses the master's constant world colour ("REV15P / Low cool night ambient"), because the panoramas also contain nearby geometry.

**Sponsor LED strip.** Logos with opaque white grounds, dark bands or baked checkerboards lit as solid blocks. `build-sponsor-strip.py` lights only each mark's ink. It works out the ground from the most common colour, treats pale neutral greys as background, and keeps very light fills off so the marks inside them read. The order, sizing and 10,676-cell loop are unchanged.

**Accommodation on the left house wall.** By request, the COMING / SOON graffiti, its shaded lamp and the lamp's light move from the forecourt cross wall onto the left house wall facing the plaza. This mirrors the Contact enquiry window on the right house. The exact mirror would cover a ground-floor window, so the artwork is centred on the clear limewash bay at y = 17.55 m. `scene_overrides.py` applies the move to the in-memory master in both export and bake, so the master stays byte-identical and every source-hash check holds. The walk-up and focused views use the plaza's open floor at about the Contact window's distances.

## Rebuild

Use Blender 4.3 (the `bpy` 4.3.0 module works through a `blender` shim), KTX-Software 4.4.2 and OIDN 2.5.1 as in [the runtime README](README.md).

```sh
python scripts/gullyverse/fidelity-artspec.py -- "$REV15Z_MASTER" artspecs.json
python scripts/gullyverse/fidelity-probes.py -- "$REV15Z_MASTER" "$PROBE_DIR" 1024 96 \
  market-south:0:-21:1.6 market-north:0:-6:1.6 approach:0:5:1.6 gate:0:13.5:1.6 \
  forecourt:0:19:1.6 plaza:0:27:1.6 screen:0:35:1.6
python scripts/gullyverse/build-fidelity-manifest.py artspecs.json "$PROBE_DIR/probes.json"
python scripts/gullyverse/build-sponsor-strip.py
```

Then rebuild the chunks with `build-cypher-gate.sh` (gate, approach) and `build-market-lane.sh` (south, north, plaza, audience). Publishing the approach chunk restores Blender's packed sponsor strip, so run `build-sponsor-strip.py` again afterwards.

Software-rendered Chromium comparisons check placement and colour, not device performance.
