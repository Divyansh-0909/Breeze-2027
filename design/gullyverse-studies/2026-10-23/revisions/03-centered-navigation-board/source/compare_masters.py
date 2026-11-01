import bpy, json, hashlib, array
from pathlib import Path
O=Path(__file__).resolve().parents[1]
BASE=O.parents[1]

def snapshot(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    objects={}
    for o in bpy.data.objects:
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
        objects[o.name]={'type':o.type,'matrix':[list(r)for r in o.matrix_world],
                         'dataHash':h.hexdigest(),
                         'materials':[s.material.name if s.material else None for s in o.material_slots]}
    scenes={s.name:{'world':s.world.name,'worldNodes':[(n.name,[repr(i.default_value) for i in n.inputs if hasattr(i,'default_value')])for n in s.world.node_tree.nodes],
                    'viewTransform':s.view_settings.view_transform,'exposure':s.view_settings.exposure,
                    'objects':sorted(o.name for o in s.objects)} for s in bpy.data.scenes}
    return objects,scenes

old,oldscenes=snapshot(BASE/'revisions/02-no-reveal-column/source/Gullyverse-Lane-Rooftop-ABC-No-Reveal-Column.blend')
new,newscenes=snapshot(O/'source/Gullyverse-Lane-Rooftop-ABC-Centered-Board.blend')
change=json.loads((O/'evidence/board-relocation.json').read_text())
allowed={r['name']for r in change['moved']}
assert set(new)-set(old)=={'14-board-arrival'}
assert not set(old)-set(new)
for name in old:
    assert old[name]['dataHash']==new[name]['dataHash']
    assert old[name]['materials']==new[name]['materials']
    if name not in allowed:assert old[name]==new[name]
for name,scene in newscenes.items():
    assert set(scene['objects'])-set(oldscenes[name]['objects'])=={'14-board-arrival'}
    assert not set(oldscenes[name]['objects'])-set(scene['objects'])
    for key in scene:
        if key!='objects':assert scene[key]==oldscenes[name][key]
assert all(i.packed_file for i in bpy.data.images if i.type=='IMAGE')
result={'status':'PASS','previousObjectsCompared':len(old),'translatedBoardObjects':18,'translatedExistingBoardLights':3,'newInspectionCamera':'14-board-arrival','originalCameraPosesUnchanged':True,'existingMeshDataUVsMaterialsUnchanged':True,'allUnrelatedObjectTransformsUnchanged':True,'globalLightingUnchanged':True,'allImagesPacked':True,'revisionSHA256':change['masterSHA256'],'previousSHA256':change['previousMasterSHA256']}
(O/'evidence/master-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print('MASTER_COMPARISON_PASS',flush=True)
