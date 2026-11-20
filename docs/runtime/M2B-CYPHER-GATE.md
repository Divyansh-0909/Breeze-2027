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

The tests drive the actual controller from the market lane through the gate and back. They cover grade joins, wall sliding and collision from either side of the gate. The renderer and other destination journeys are separate from this collision data.
