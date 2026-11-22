"""Extract the master's light objects for runtime specular highlights.

Usage: python fidelity-lights.py -- MASTER.blend OUT.json
Lights are invisible to camera rays, so the reflection probes never contain them; the runtime adds
their specular highlights over the baked diffuse light. Scene overrides (scene_overrides.py) apply.
"""
import bpy, sys, json, math
from pathlib import Path
from mathutils import Vector
argv = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.open_mainfile(filepath=argv[0]); scene = bpy.context.scene; bpy.context.view_layer.update()
sys.path.insert(0, str(Path(__file__).resolve().parent)); import scene_overrides
scene_overrides.apply(scene, {})
vl = bpy.context.view_layer; rows = []
for o in scene.objects:
    if o.type != 'LIGHT' or o.hide_render or not o.visible_get(view_layer=vl): continue
    d = o.data; m = o.matrix_world; p = m.translation; aim = (m.to_3x3() @ Vector((0, 0, -1))).normalized()
    if d.energy <= 0 or not any(d.color): continue
    # Blender power P (W) -> radiant intensity: point/spot P/(4*pi); one-sided area P/pi along its normal.
    intensity = d.energy / math.pi if d.type == 'AREA' else d.energy / (4 * math.pi)
    angle = d.spot_size / 2 if d.type == 'SPOT' else (math.pi / 2 if d.type == 'AREA' else math.pi / 2)
    rows.append({"name": o.name, "type": d.type, "position": [round(p.x, 3), round(p.z, 3), round(-p.y, 3)],
                 "direction": [round(aim.x, 4), round(aim.z, 4), round(-aim.y, 4)],
                 "color": [round(c, 4) for c in d.color], "intensity": round(intensity * d.specular_factor, 4),
                 "angle": round(angle, 4), "penumbra": round(d.spot_blend if d.type == 'SPOT' else 0.5, 3),
                 "omni": d.type in ('POINT', 'SUN') and False})
json.dump(rows, open(argv[1], "w"), indent=1)
print("LIGHTS", len(rows)); [print("LIGHT", r["type"], r["name"][:50], r["intensity"], r["position"]) for r in rows]
import os; os._exit(0)
