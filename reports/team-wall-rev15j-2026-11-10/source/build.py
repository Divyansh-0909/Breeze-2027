import bpy
import copy
import hashlib
import json
import os
from pathlib import Path

O = Path(__file__).resolve().parents[1]
SOURCE = Path(os.environ.get('TEAM_WALL_BASE', '/workspace/scratch/team-mural-recovery/Rev15I1-source.blend'))
BASE_SHA = '07650da781f0ec7ff4e91b6725a9e45de8a55ae4fee8175e539b45bb2cb203b7'
assert hashlib.sha256(SOURCE.read_bytes()).hexdigest() == BASE_SHA
bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
base = next(s for s in bpy.data.scenes if s.get('variant') == 'REV15I1')
historical = {s.name: tuple(s.objects) for s in bpy.data.scenes}
before_count = len(bpy.data.scenes)
s = bpy.data.scenes.new('REV15J / OC First / Reference Plaster Wall')
s['variant'] = 'REV15J'
s.world = base.world
for prop in ['view_transform', 'look', 'exposure', 'gamma']:
    setattr(s.view_settings, prop, getattr(base.view_settings, prop))
s.frame_start, s.frame_end = base.frame_start, base.frame_end
s.render.fps = base.render.fps
s.camera = base.camera
bpy.context.window.scene = s
s.frame_set(1)
controller = bpy.data.objects.new('REV15J / Team Carousel Controller', None)
s.collection.objects.link(controller)
controller['team_index'] = 0
controller.id_properties_ui('team_index').update(min=0, max=7)
previous = json.loads((O.parent/'oc-team-wall-rev15i1-2026-11-05/evidence/carousel-manifest.json').read_text())
manifest = copy.deepcopy(previous)
manifest.update(version='REV15J', coreSource=BASE_SHA, defaultTeam=0)
manifest['slides'] = manifest['slides'][1:]
manifest['order'] = manifest['order'][1:]
manifest['removedTeam'] = 'Coordinators'
lookup = {}
for index, slide in enumerate(manifest['slides']):
    slide['index'] = index
    for art in slide['art']:
        lookup[art['object']] = art
removed = []
for obj in base.objects:
    if obj.name == 'REV15I1 / Team Carousel Controller':
        continue
    if not obj.get('artKind'):
        s.collection.objects.link(obj)
        continue
    if obj['carouselSlide'] == 0:
        removed.append(obj.name)
        continue
    new = obj.copy()
    new.name = obj.name.replace('REV15I1 /', 'REV15J /', 1)
    s.collection.objects.link(new)
    new.animation_data_clear()
    new['carouselSlide'] = int(obj['carouselSlide']) - 1
    for prop in ['hide_render', 'hide_viewport']:
        driver = new.driver_add(prop).driver
        variable = driver.variables.new()
        variable.name = 'index'
        variable.type = 'SINGLE_PROP'
        variable.targets[0].id = controller
        variable.targets[0].data_path = '["team_index"]'
        driver.expression = f'index != {new["carouselSlide"]}'
    lookup[obj.name]['object'] = new.name
s['carouselOrder'] = json.dumps(manifest['order'])
s['initialTeam'] = 'Organising Committee'
s['authorizedChange'] = 'Remove Coordinators from active carousel; OC first. Retain exact reference Blender wall and world.'
s['userVisualApproval'] = 'PENDING'
s['websiteUnmodified'] = True
s['wallReference'] = 'inputs/user-wall-reference.jpg'
controller.update_tag()
bpy.context.view_layer.update()
(O/'evidence/carousel-manifest.json').write_text(json.dumps(manifest, indent=2))
web = copy.deepcopy(manifest)
for slide in web['slides']:
    for art in slide['art']:
        art['image'] = 'art/' + Path(art['image']).name
(O/'viewer/carousel.json').write_text(json.dumps(web, indent=2))
checks = {
    'all38HistoricalSceneMembershipsExact': all(tuple(bpy.data.scenes[name].objects) == objects for name, objects in historical.items()),
    'allNonArtOwnersSharedExactly': all(s.objects.get(o.name) == o for o in base.objects if not o.get('artKind') and o.name != 'REV15I1 / Team Carousel Controller'),
    'exactReferenceWorldAndWallMaterials': s.world == base.world and all(s.objects.get(o.name) == o for o in base.objects if 'house shell' in o.name),
    'eightSlidesOCFirst': len(manifest['slides']) == 8 and manifest['order'][0] == 'Organising Committee' and 'Coordinators' not in manifest['order'],
    'noCoordinatorArtInActiveScene': len(removed) == 6 and not any('Coordinators' in o.name for o in s.objects),
    'remainingArtMeshesAndMaterialsExact': all(o.data == base.objects[o.name.replace('REV15J /', 'REV15I1 /', 1)].data for o in s.objects if o.get('artKind')),
}
visibility = []
art_objects = [o for o in s.objects if o.get('artKind')]
for index, slide in enumerate(manifest['slides']):
    controller['team_index'] = index
    controller.update_tag()
    bpy.context.view_layer.update()
    active = [o for o in art_objects if not o.hide_render]
    visibility.append({'index': index, 'team': slide['team'], 'visibleArt': len(active), 'pass': len(active) == len(slide['art']) and all(o['carouselSlide'] == index for o in active)})
checks['eightExclusiveSlides'] = all(row['pass'] for row in visibility)
assert all(checks.values()), checks
controller['team_index'] = 0
controller.update_tag()
bpy.context.view_layer.update()
text = bpy.data.texts.load(str(O/'source/carousel_controls.py'))
text.name = 'team_wall_rev15j_controls.py'
s.render.engine = 'BLENDER_EEVEE_NEXT'
s.eevee.taa_render_samples = 8
bpy.ops.file.pack_all()
bpy.context.preferences.filepaths.save_version = 0
master = O/'delivery/Gullyverse-Rev15J-OC-First.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(master), compress=True)
result = {'status': 'PASS', 'checks': checks, 'visibility': visibility, 'removedArtOwners': removed, 'baseSHA256': BASE_SHA, 'masterSHA256': hashlib.sha256(master.read_bytes()).hexdigest(), 'masterBytes': master.stat().st_size, 'historicalSceneCount': before_count, 'newSceneCount': len(bpy.data.scenes)}
(O/'evidence/blender-validation.json').write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2), flush=True)
