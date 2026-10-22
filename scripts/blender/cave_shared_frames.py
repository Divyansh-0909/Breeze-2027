"""Match shading at artificial passage partitions without moving geology.

Use the actual adjacent LOD0 face angles to define one common boundary normal.
Copy that same frame to each independently selected LOD. Real fracture edges
away from those partition rings retain their authored split normals.
"""
import math
from mathutils import Vector

JOINS = [('Throat', 'Passage1', 6), ('Passage1', 'Passage2', 15),
         ('Passage2', 'Passage3', 24), ('Passage3', 'Passage4', 33)]


def shared_frames(runtime):
    by_name = {o.name: o for o in runtime}
    canonical = {}
    key = lambda v: tuple(round(float(x), 5) for x in v)
    for a, b, station in JOINS:
        accumulated = {}
        for name in [a, b]:
            m = by_name[f'Cave_{name}_LOD0'].data
            for f in m.polygons:
                ids = list(f.vertices)
                for j, vi in enumerate(ids):
                    p = m.vertices[vi].co
                    if abs(p.y - station) > 1e-5:
                        continue
                    u = m.vertices[ids[j-1]].co - p
                    v = m.vertices[ids[(j+1) % len(ids)]].co - p
                    if u.length < 1e-8 or v.length < 1e-8:
                        continue
                    angle = math.acos(max(-1, min(1, u.normalized().dot(v.normalized()))))
                    k = key(p)
                    accumulated[k] = accumulated.get(k, Vector()) + f.normal * angle
        assert accumulated and all(v.length > 1e-6 for v in accumulated.values())
        canonical.update({k: v.normalized() for k, v in accumulated.items()})
    changed = {}
    for o in runtime:
        if not any(x in o.name for x in ['Throat', 'Passage']):
            continue
        m = o.data
        normals = [n.vector.copy() for n in m.corner_normals]
        count = 0
        for i, loop in enumerate(m.loops):
            k = key(m.vertices[loop.vertex_index].co)
            if k in canonical:
                normals[i] = canonical[k]
                count += 1
        m.normals_split_custom_set(normals)
        m.update()
        changed[o.name] = count
    return {'method': 'Shared angle-weighted adjacent LOD0 face normals at artificial partition rings; identical canonical normals across LODs. Positions and UVs unchanged. MikkTSpace regenerated after export.',
            'protectedStationsBlenderYMetres': [j[2] for j in JOINS],
            'canonicalPositions': len(canonical), 'updatedCornerNormals': changed,
            'canonicalWebGLFrames': [{'position': [p[0], p[2], -p[1]], 'normal': [n.x, n.z, -n.y]} for p, n in canonical.items()]}
