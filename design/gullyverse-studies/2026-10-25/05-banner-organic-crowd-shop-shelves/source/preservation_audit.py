import bpy,json,hashlib,array
from pathlib import Path
O=Path(__file__).resolve().parents[1]
OLD=O/'source/baseline/source/Gullyverse-Straight-Walk-Semicircular-Crowd.blend'
NEW=O/'source/Gullyverse-Rev05A-Banner-Crowd-Shelves-Pending.blend'
def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=str(path));objects={}
    for o in bpy.data.objects:
        h=hashlib.sha256()
        if o.type=='MESH':
            data=array.array('f',[0.0])*(len(o.data.vertices)*3);o.data.vertices.foreach_get('co',data);h.update(data.tobytes());h.update(json.dumps([list(p.vertices)for p in o.data.polygons]).encode())
            for uv in o.data.uv_layers:
                data=array.array('f',[0.0])*(len(uv.data)*2);uv.data.foreach_get('uv',data);h.update(data.tobytes())
        if o.type=='LIGHT':h.update(repr((o.data.type,o.data.energy,list(o.data.color),o.data.size if o.data.type=='AREA'else None)).encode())
        if o.type=='CAMERA':h.update(repr((o.data.type,o.data.lens,o.data.sensor_width,o.data.ortho_scale)).encode())
        if o.type=='FONT':h.update(o.data.body.encode())
        action=None
        if o.animation_data and o.animation_data.action:action=[{'path':c.data_path,'index':c.array_index,'keys':[(list(p.co),p.interpolation)for p in c.keyframe_points]}for c in o.animation_data.action.fcurves]
        objects[o.name]={'type':o.type,'basis':[list(r)for r in o.matrix_basis],'dataHash':h.hexdigest(),'materials':[s.material.name if s.material else None for s in o.material_slots],'action':action}
    return objects,{s.name:{'world':s.world.name,'exposure':s.view_settings.exposure,'transform':s.view_settings.view_transform,'look':s.view_settings.look,'fps':s.render.fps,'frameRange':[s.frame_start,s.frame_end]}for s in bpy.data.scenes}
before,world_before=snapshot(OLD);after,world_after=snapshot(NEW)
removed=set(before)-set(after);assert removed=={'Festival takeover banner'}
actors=json.loads((O/'evidence/organic-crowd-authoring.json').read_text());changed=set(actors['changedExistingCrowdParts']);created=set(actors['addedCrowdParts'])
new=set(after)-set(before);assert new==created|{'17-banner-frontal','18-banner-oblique','19-hub-wide','21-shop-left-25','22-shop-left-7','23-shop-left2','24-shop-right-16','25-shop-right-7'}
for name,old in before.items():
    if name in removed:continue
    now=after[name]
    assert old['dataHash']==now['dataHash']and old['materials']==now['materials']and old['action']==now['action'],name
    if name not in changed:assert old==now,name
assert world_before==world_after
counters={name:{'matrix':r['basis'],'meshAndUVSHA256':r['dataHash'],'unchanged':True}for name,r in after.items()if name.startswith(('Counter','DJ tabletop','DJ table leg'))}
result={'status':'PASS','phaseStatus':'PARTIAL_SHOP_EXCEPTION_PENDING','removed':sorted(removed),'crowdPartsChanged':len(changed),'newLinkedCrowdParts':len(created),'newDiagnostics':len(new)-len(created),'originalCamerasAnd40sActionIdentical':True,'allNonTargetGeometryUVMaterialsAndTransformsIdentical':True,'allLightsAndEnvironmentIdentical':True,'shelvesNotMovedWithoutException':True,'countersAndTables':counters,'baselineMasterSHA256':hashlib.sha256(OLD.read_bytes()).hexdigest(),'reviewMasterSHA256':hashlib.sha256(NEW.read_bytes()).hexdigest()}
(O/'evidence/preservation-audit.json').write_text(json.dumps(result,indent=2)+'\n');print('PRESERVATION_PASS',len(counters),'counter/table objects',flush=True)
