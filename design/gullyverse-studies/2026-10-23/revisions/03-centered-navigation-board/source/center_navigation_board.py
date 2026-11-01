import bpy,json,hashlib,array
from pathlib import Path
from mathutils import Vector
O=Path(__file__).resolve().parents[1];BASE=O.parent/'02-no-reveal-column'
OLD=BASE/'source/Gullyverse-Lane-Rooftop-ABC-No-Reveal-Column.blend'
assert Path(bpy.data.filepath).resolve()==OLD.resolve()
delta=Vector((-5.6,-4.0,0))
coll=bpy.data.collections['02_SHARED_NAVIGATION_LANDMARK']
board=list(coll.objects)
lamps=[o for o in bpy.data.objects if o.type=='LIGHT' and o.name.startswith('Signboard practical')]
assert len(lamps)==3
moved=[]
before={o.name:[list(r)for r in o.matrix_world]for o in bpy.data.objects}
for o in board+lamps:
    original=list(o.location);o.location+=delta
    moved.append({'name':o.name,'from':original,'to':list(o.location),'kind':'landmark'if o in board else'board-local light'})
camdata=bpy.data.objects['03-opening'].data.copy();camdata.name='14-board-arrival';camdata.lens=24
cam=bpy.data.objects.new('14-board-arrival',camdata)
bpy.data.collections['04_SHARED_CAMERA_RIG'].objects.link(cam)
cam.location=(0,13,8.87);cam.rotation_euler=(Vector((0,22,10.3))-cam.location).to_track_quat('-Z','Y').to_euler()
bpy.context.view_layer.update()
for o in bpy.data.objects:
    if o.name in before and o not in board+lamps:assert [list(r)for r in o.matrix_world]==before[o.name]
assert not any(o.name.startswith('Roof service room / reveal occluder')for o in bpy.data.objects)
guide=json.loads((O/'source/camera-guide.json').read_text());guide['proposedNavigation']['signboardCenter']=[0,21,7.2]
guide['rig'].append({'id':cam.name,'position':list(cam.location),'target':[0,22,10.3],'lensMM':24,'cameraToWorld':[list(r)for r in cam.matrix_world],'rotationEuler':list(cam.rotation_euler),'note':'New concept inspection camera; original named camera poses retained unchanged.'})
(O/'source/camera-guide.json').write_text(json.dumps(guide,indent=2)+'\n')
bpy.context.preferences.filepaths.save_version=0
master=O/'source/Gullyverse-Lane-Rooftop-ABC-Centered-Board.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(master),compress=True)
result={'status':'PASS','request':'Place navigation board in the rooftop-cypher approach, rather than off to the right.',
 'previousCenter':[5.6,25,7.2],'newCenter':[0,21,7.2],
 'translation':list(delta),'moved':moved,'newCamera':cam.name,
 'unrelatedTransformsUnchanged':True,'originalCamerasUnchanged':True,
 'geometryMaterialsScaleAndBrandingUnchanged':True,'globalLightingUnchanged':True,
 'localLightAdjustment':'Only the existing board practical follows the board in each variant; no light added.',
 'previousMasterSHA256':hashlib.sha256(OLD.read_bytes()).hexdigest(),
 'masterSHA256':hashlib.sha256(master.read_bytes()).hexdigest()}
(O/'evidence/board-relocation.json').write_text(json.dumps(result,indent=2)+'\n')
print('BOARD_CENTERED',json.dumps({'objects':len(board),'lamps':len(lamps),'center':result['newCenter']}),flush=True)
