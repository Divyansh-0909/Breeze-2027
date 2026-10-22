"""Restore authoritative float32 interface normals after Blender export.

Blender encodes custom corner normals internally. Reimporting and assigning
them can accumulate quantization. Runtime shared-border data must instead
match the preserved C5.1 GLB. Positions, UVs and interior normals are untouched.
"""
from pathlib import Path
import json
import struct
import numpy as np


def read(path):
    data = Path(path).read_bytes()
    length = struct.unpack_from('<I', data, 12)[0]
    return json.loads(data[20:20 + length]), bytearray(data[28 + length:])


def array(document, payload, index):
    accessor = document['accessors'][index]
    view = document['bufferViews'][accessor['bufferView']]
    width = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}[accessor['type']]
    assert accessor['componentType'] == 5126, 'Expected float32 interface attributes'
    return np.ndarray((accessor['count'], width), dtype='<f4', buffer=payload,
                      offset=view.get('byteOffset', 0) + accessor.get('byteOffset', 0),
                      strides=(view.get('byteStride', width * 4), 4))


def restore_authoritative_border(root):
    root = Path(root)
    target = root / 'public/models/gullyverse/quarry-fidelity-correction/fidelity-region.glb'
    source = root / 'public/models/gullyverse/quarry-foundation-refined/foundation-geometry.glb'
    interfaces = json.loads((root / 'assets-source/gullyverse/quarry-fidelity-correction/protected-interfaces.json').read_text())
    baseline, original = read(source)
    document, payload = read(target)
    results = []
    for level in range(3):
        protected = {tuple(np.asarray(p, dtype=np.float32)) for p in interfaces[level]['vertices']}
        lookup = {}
        for node in baseline['nodes']:
            if node.get('name') not in [f'Foundation_Wall_{i}_LOD{level}' for i in [14, 15, 16]]:
                continue
            assert not any(key in node for key in ['matrix', 'translation', 'rotation', 'scale'])
            for primitive in baseline['meshes'][node['mesh']]['primitives']:
                attributes = primitive['attributes']
                for position, normal in zip(array(baseline, original, attributes['POSITION']),
                                            array(baseline, original, attributes['NORMAL'])):
                    key = tuple(position)
                    if key in protected:
                        lookup.setdefault(key, []).append(normal.copy())
        assert set(lookup) == protected, 'Missing authoritative raw border normals'
        node = next(node for node in document['nodes'] if node.get('name') == f'Fidelity_Wall_15_LOD{level}')
        restored = 0
        maximum_change = 0.
        for primitive in document['meshes'][node['mesh']]['primitives']:
            attributes = primitive['attributes']
            positions = array(document, payload, attributes['POSITION'])
            normals = array(document, payload, attributes['NORMAL'])
            tangents = array(document, payload, attributes['TANGENT'])
            for index, position in enumerate(positions):
                choices = lookup.get(tuple(position))
                if not choices:
                    continue
                old = normals[index].copy()
                normal = max(choices, key=lambda value: float(value @ old))
                maximum_change = max(maximum_change, float(np.linalg.norm(normal - old)))
                normals[index] = normal
                tangent = tangents[index, :3].astype(np.float64)
                tangent -= normal * float(tangent @ normal) / float(normal @ normal)
                length = np.linalg.norm(tangent)
                assert length > .9, 'Invalid original tangent derivative at protected border'
                tangents[index, :3] = tangent / length
                restored += 1
        assert restored >= len(protected)
        results.append({'LOD': level, 'exportCornersRestored': restored,
                        'maximumNormalVectorCorrection': maximum_change,
                        'positionAndUVChanged': False})
    encoded = json.dumps(document, separators=(',', ':')).encode()
    encoded += b' ' * (-len(encoded) % 4)
    target.write_bytes(struct.pack('<III', 0x46546c67, 2, 28 + len(encoded) + len(payload)) +
                       struct.pack('<II', len(encoded), 0x4e4f534a) + encoded +
                       struct.pack('<II', len(payload), 0x004e4942) + payload)
    return {'method': 'Original C5.1 raw float32 border normals; existing UV tangent re-orthogonalized.',
            'sourceFileUnchanged': True, 'levels': results}
