"""Build-time scene overrides applied to the in-memory locked master (never saved).

The Rev15Z master stays byte-identical, so every runtime source-hash check still holds. Export and
lighting bake both apply the same overrides right after opening the master, so the baked light,
shadows and exported geometry agree.

accommodation-left-wall (user request, 22 November 2026): move the COMING / SOON graffiti, its shaded
wall lamp and the lamp's light from the forecourt cross wall (left corner, y = 14.0) onto the left
house wall facing the plaza, mirroring the Contact enquiry window on the right house. The exact mirror
(centre y = 18.6) would cover the ground-floor window at y = 19.0-20.0, so the artwork is centred on
the clear limewash bay at y = 17.55, at the Contact window's height band.
"""
import math

from mathutils import Matrix, Vector

ACCOMMODATION = (
    "REV15Z / COMING above SOON graffiti",
    "REV15Z / Accommodation shaded wall-lamp fixture",
    "REV15Z / Accommodation local wall illumination",
)
TARGET_Y, TARGET_Z = 17.55, 8.97
PAINT_OFFSET = 0.012  # metres in front of the plaster, as on the original wall


def _bbox_centre(obj):
    points = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    return sum(points, Vector()) / len(points)


def accommodation_left_wall(scene, depsgraph):
    graffiti = scene.objects[ACCOMMODATION[0]]
    old_centre = _bbox_centre(graffiti)
    old_normal = Vector((0.0, 1.0, 0.0))  # faces the plaza from the cross wall at y = 14.0
    hidden = {name: scene.objects[name].hide_get() for name in ACCOMMODATION}
    for name in ACCOMMODATION:
        scene.objects[name].hide_set(True)
    hit, point, normal, *_ = scene.ray_cast(depsgraph, Vector((-8.0, TARGET_Y, TARGET_Z)), Vector((-1.0, 0.0, 0.0)))
    for name, state in hidden.items():
        scene.objects[name].hide_set(state)
    assert hit and normal.x > 0.5, "left house wall not found"
    facing = Vector((normal.x, normal.y, 0.0)).normalized()
    new_centre = Vector((point.x, point.y, TARGET_Z)) + facing * PAINT_OFFSET
    angle = math.atan2(facing.y, facing.x) - math.atan2(old_normal.y, old_normal.x)
    transform = Matrix.Translation(new_centre) @ Matrix.Rotation(angle, 4, "Z") @ Matrix.Translation(-old_centre)
    for name in ACCOMMODATION:
        obj = scene.objects[name]
        obj.matrix_world = transform @ obj.matrix_world
    return {"id": "accommodation-left-wall", "objects": list(ACCOMMODATION),
            "from": [round(v, 3) for v in old_centre], "to": [round(v, 3) for v in new_centre],
            "facing": [round(v, 4) for v in facing], "rotationDegrees": round(math.degrees(angle), 2)}


OVERRIDES = {"accommodation-left-wall": accommodation_left_wall}


def apply(scene, plan):
    """Apply the overrides named in plan['sceneOverrides'] (all of them by default)."""
    import bpy
    names = plan.get("sceneOverrides", list(OVERRIDES))
    records = []
    for name in names:
        depsgraph = bpy.context.evaluated_depsgraph_get()
        records.append(OVERRIDES[name](scene, depsgraph))
        bpy.context.view_layer.update()
    plan["sceneOverrideRecords"] = records
    print("SCENE_OVERRIDES", records, flush=True)
    return records
