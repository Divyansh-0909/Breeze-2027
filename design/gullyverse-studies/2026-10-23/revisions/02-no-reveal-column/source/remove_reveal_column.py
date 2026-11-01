import bpy, hashlib, json
from pathlib import Path

O = Path(__file__).resolve().parents[1]
BASE = O.parents[1]
MASTER = BASE / 'source/Gullyverse-Lane-Rooftop-ABC.blend'
assert Path(bpy.data.filepath).resolve() == MASTER.resolve()

def snapshot():
    rows = {}
    for o in bpy.data.objects:
        rows[o.name] = {
            'type': o.type, 'matrix': [list(r) for r in o.matrix_world],
            'collections': sorted(c.name for c in o.users_collection),
            'data': o.data.name if o.data else None,
            'materialSlots': [s.material.name if s.material else None for s in o.material_slots],
        }
    return rows

before = snapshot()
prefixes = ('Roof service room / reveal occluder', 'Service roof cap',
            'Service black water tank', 'Tank reinforcing rib',
            'Street wayfinding paste-up')
removed = [o for o in bpy.data.objects if o.name.startswith(prefixes)]
names = sorted(o.name for o in removed)
assert 'Roof service room / reveal occluder' in names
for o in removed:
    bpy.data.objects.remove(o, do_unlink=True)
after = snapshot()
assert not set(before) - set(after) - set(names)
assert all(before[n] == after[n] for n in after), 'An unrelated object changed'
assert not any(o.name.startswith(prefixes) for o in bpy.data.objects)
assert len(bpy.data.scenes) == 3
bpy.context.preferences.filepaths.save_version = 0
destination = O / 'source/Gullyverse-Lane-Rooftop-ABC-No-Reveal-Column.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(destination), compress=True)
result = {
    'status': 'PASS', 'request': 'Remove the reveal column/block; no replacement occluder.',
    'originalMaster': str(MASTER),
    'originalSHA256': hashlib.sha256(MASTER.read_bytes()).hexdigest(),
    'newMaster': str(destination),
    'newSHA256': hashlib.sha256(destination.read_bytes()).hexdigest(),
    'removedObjects': names, 'allRemainingObjectSnapshotsIdentical': True,
    'remainingObjects': len(after), 'scenes': [s.name for s in bpy.data.scenes],
    'camerasRoutesLightsMaterialsUnchanged': True,
    'note': 'The old screen-hidden-from-landing condition is intentionally retired by this user request. All old evidence and master remain intact.',
}
(O / 'evidence/removal-verification.json').write_text(json.dumps(result, indent=2)+'\n')
print('REMOVAL_VERIFIED', json.dumps(result), flush=True)
