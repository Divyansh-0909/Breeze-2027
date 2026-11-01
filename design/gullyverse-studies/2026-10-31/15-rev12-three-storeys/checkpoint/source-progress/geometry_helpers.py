from mathutils import Vector
import math
def uvmetre(o):
    m = o.data
    uv = m.uv_layers.get('PILOT_world_metres') or m.uv_layers.new(name='PILOT_world_metres')
    for p in m.polygons:
        n = (o.matrix_world.to_3x3().inverted().transposed() @ p.normal).normalized()
        a = max(range(3), key=lambda i: abs(n[i]))
        sgn = 1 if n[a] > 0 else -1
        for li in p.loop_indices:
            v = o.matrix_world @ m.vertices[m.loops[li].vertex_index].co
            uv.data[li].uv = (v.y * sgn, v.z) if a == 0 else (-v.x * sgn, v.z) if a == 1 else (v.x * sgn, v.y)
    m.uv_layers.active = uv
    uv.active_render = True
def piece(name, v, f, mat, zone, metadata):
    bucket = buckets.setdefault((zone, mat.name), {'v': [], 'f': []})
    off = len(bucket['v'])
    bucket['v'].extend(v)
    bucket['f'].extend((tuple((off + j for j in p)) for p in f))
    parts.append({'name': name, 'zone': zone, 'material': mat.name, **metadata})
def box(name, loc, dims, mat, zone):
    x, y, z = loc
    a, b, c = [d / 2 for d in dims]
    v = [(x + sx * a, y + sy * b, z + sz * c) for sx, sy, sz in [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]]
    piece(name, v, [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)], mat, zone, {'location': loc, 'dimensions': dims})
def rod(name, a, b, r, mat, zone, n=6):
    a, b = (Vector(a), Vector(b))
    d = (b - a).normalized()
    u = d.cross(Vector((0, 0, 1)) if abs(d.z) < 0.9 else Vector((1, 0, 0))).normalized()
    w = d.cross(u)
    v = [list(p + r * (math.cos(2 * math.pi * j / n) * u + math.sin(2 * math.pi * j / n) * w)) for p in [a, b] for j in range(n)]
    f = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))] + [(j, (j + 1) % n, (j + 1) % n + n, j + n) for j in range(n)]
    piece(name, v, f, mat, zone, {'ends': [list(a), list(b)], 'radiusM': r})
