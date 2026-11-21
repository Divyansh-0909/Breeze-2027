"""Pack light UVs in independent tiles for large courtyard geometry and people."""
import math

import bpy
import numpy as np


def pack_light_tiles(targets, uv_name, size):
    deck = next((obj for obj in targets if obj.get("groundSurface")), None)
    shell = next((obj for obj in targets if "Existing Events house shell" in obj.name), None)
    large = [obj for obj in (deck, shell) if obj is not None]
    small = [obj for obj in targets if obj not in large]
    tiles = {}
    if large:
        for index, obj in enumerate(large):
            tiles[obj] = (index / len(large), 0, (index + 1) / len(large), 0.64)
    start = 0.64 if large else 0
    columns = math.ceil(math.sqrt(len(small) / (1 - start))) if small else 1
    rows = math.ceil(len(small) / columns) if small else 1
    for index, obj in enumerate(small):
        x, y = index % columns, index // columns
        h = (1 - start) / rows
        tiles[obj] = (x / columns, start + h * y, (x + 1) / columns, start + h * (y + 1))

    bpy.ops.object.select_all(action="DESELECT")
    layer = bpy.context.view_layer
    margin = 2 / size
    for obj in targets:
        obj.select_set(True)
        layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.002,
                                 area_weight=0.35, correct_aspect=False, scale_to_bounds=True)
        bpy.ops.object.mode_set(mode="OBJECT")
        obj.select_set(False)
        data = obj.data.uv_layers[uv_name].data
        uv = np.empty(len(data) * 2, dtype=np.float32)
        data.foreach_get("uv", uv)
        uv = uv.reshape(-1, 2)
        assert np.isfinite(uv).all(), obj.name
        lower = uv.min(axis=0)
        uv -= lower
        uv /= np.maximum(uv.max(axis=0), 1e-8)

        if obj is deck:
            # Keep the entire road top in a single planar light chart. The
            # underside and edge faces occupy a narrow strip below it.
            uv[:, 1] *= 0.14
            mesh = obj.data
            points = [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
            top = [face for face in mesh.polygons if face.normal.z > 0.1
                   and all(points[index].z > 6.95 for index in face.vertices)]
            top_points = [points[index] for face in top for index in face.vertices]
            assert top_points, obj.name
            min_x, max_x = min(v.x for v in top_points), max(v.x for v in top_points)
            min_y, max_y = min(v.y for v in top_points), max(v.y for v in top_points)
            for face in top:
                for loop, vertex in zip(face.loop_indices, face.vertices):
                    point = points[vertex]
                    uv[loop] = ((point.x - min_x) / (max_x - min_x),
                                0.16 + 0.84 * (point.y - min_y) / (max_y - min_y))

        x0, y0, x1, y1 = tiles[obj]
        uv *= (x1 - x0 - 2 * margin, y1 - y0 - 2 * margin)
        uv += (x0 + margin, y0 + margin)
        assert ((uv >= 0) & (uv <= 1)).all(), obj.name
        data.foreach_set("uv", uv.ravel())
    print("ISOLATED_IRRADIANCE_TILES", len(large), len(small), flush=True)
