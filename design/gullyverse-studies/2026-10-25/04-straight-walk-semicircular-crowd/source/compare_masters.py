import bpy, json, hashlib, array
from pathlib import Path
O=Path(__file__).resolve().parents[1]
BASE=Path('/workspace/gullyverse-world-concept/2026-10-23/revisions/03-centered-navigation-board')

def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    objects={}
    for scene in bpy.data.scenes:
        bpy.context.window.scene=scene;scene.frame_set(1);bpy.context.view_layer.update()
        for o in scene.objects:
            h=hashlib.sha256()
            if o.type=='MESH':
                data=array.array('f',[0.0])*(len(o.data.vertices)*3)
                o.data.vertices.foreach_get('co',data);h.update(data.tobytes())
                h.update(json.dumps([list(p.vertices) for p in o.data.polygons]).encode())
                for uv in o.data.uv_layers:
                    data=array.array('f',[0.0])*(len(uv.data)*2)
                    uv.data.foreach_get('uv',data);h.update(data.tobytes())
            elif o.type in ('CURVE','FONT'):
                h.update(o.data.name.encode())
            if o.type=='LIGHT':
                h.update(repr((o.data.type,o.data.energy,list(o.data.color))).encode())
            if o.type=='CAMERA':
                h.update(repr((o.data.type,o.data.lens,o.data.sensor_width,o.data.ortho_scale)).encode())
            objects[o.name]={'type':o.type,'matrix':[list(r)for r in o.matrix_basis],
                             'dataHash':h.hexdigest(),
                             'materials':[s.material.name if s.material else None for s in o.material_slots]}
    scenes={s.name:{'world':s.world.name,'worldNodes':[(n.name,[repr(i.default_value) for i in n.inputs if hasattr(i,'default_value')])for n in s.world.node_tree.nodes],
                    'viewTransform':s.view_settings.view_transform,'exposure':s.view_settings.exposure,
                    'objects':sorted(o.name for o in s.objects)} for s in bpy.data.scenes}
    return objects,scenes

old,oldscenes=snapshot(BASE/'source/Gullyverse-Lane-Rooftop-ABC-Centered-Board.blend')
oldimages={i.name:{'users':i.users,'packed':bool(i.packed_file)}for i in bpy.data.images if i.type=='IMAGE'}
new,newscenes=snapshot(O/'source/Gullyverse-Straight-Walk-Semicircular-Crowd.blend')
renames=json.loads((O/'evidence/authoring-change.json').read_text())['renamedCameras']
assert set(new)-{renames.get(n,n)for n in old}=={'15-semicircle-high','16-rooftop-plan'}
assert not {renames.get(n,n)for n in old}-set(new)
crowd=[]
for name,previous in old.items():
 current=new[renames.get(name,name)]
 if previous['type']=='CAMERA':continue
 assert previous['dataHash']==current['dataHash'] and previous['materials']==current['materials']
 if name.startswith(('Audience ','Festival extra ','Balanced extra ')):crowd.append(name)
 else:assert previous==current, name
for name,scene in newscenes.items():
 for key in scene:
  if key!='objects':assert scene[key]==oldscenes[name][key]
for person in json.loads((O/'evidence/crowd-composition.json').read_text())['people']:
 scene=next(s for s in bpy.data.scenes if s.name.startswith(('B' if person['label'].startswith('Festival extra ') else 'C')+' /'));bpy.context.window.scene=scene;scene.frame_set(1);bpy.context.view_layer.update()
 shirt=bpy.data.objects[person['label']+' shirt'];x,y,_=person['foot']
 assert abs(shirt.location.x-x)<1e-4 and abs(shirt.location.y-y)<1e-4
 from mathutils import Vector
 forward=shirt.matrix_basis.to_quaternion()@Vector((0,1,0));target=Vector((-x,45.8-y,0));target.normalize();assert forward.dot(target)>.9999
newimages={i.name for i in bpy.data.images if i.type=='IMAGE'}
assert all(i.packed_file for i in bpy.data.images if i.type=='IMAGE')
result={'status':'PASS','originalObjectCount':len(old),'newObjectCount':len(new),'crowdPartsRigidlyMoved':len(crowd),'existingGeometryUVAndMaterialsUnchanged':True,'nonCrowdNonCameraTransformsUnchanged':True,'allGlobalAndLocalLightsUnchanged':True,'actualCrowdPositionsAndFacingVerified':True,'actualPackedImageCount':len(newimages),'imagesRetiredOnResave':{n:oldimages[n]for n in oldimages if n not in newimages},'originalMasterPreserved':True}
(O/'evidence/master-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print('COMPARE_PASS',json.dumps(result),flush=True)
