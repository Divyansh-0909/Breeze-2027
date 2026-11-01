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

old,oldscenes=snapshot(BASE/'source/Gullyverse-Lane-Rooftop-ABC.blend')
new,newscenes=snapshot(O/'source/Gullyverse-Lane-Rooftop-ABC-No-Reveal-Column.blend')
removed=set(old)-set(new)
assert len(removed)==9
assert all(new[n]==old[n]for n in new), 'Unexpected surviving geometry/camera/light change'
for name,s in newscenes.items():
    assert s['objects']==[n for n in oldscenes[name]['objects']if n not in removed]
    assert all(s[k]==oldscenes[name][k]for k in s if k!='objects')
assert all(i.packed_file for i in bpy.data.images if i.type=='IMAGE')
result={'status':'PASS','remainingObjectsCompared':len(new),'removed':sorted(removed),
        'survivingVertexTopologyUVDataUnchanged':True,'cameraAndLightingUnchanged':True,
        'sharedABCSceneObjectSetsCorrect':True,'allImagesPacked':True,
        'originalSHA256':hashlib.sha256((BASE/'source/Gullyverse-Lane-Rooftop-ABC.blend').read_bytes()).hexdigest(),
        'revisionSHA256':hashlib.sha256((O/'source/Gullyverse-Lane-Rooftop-ABC-No-Reveal-Column.blend').read_bytes()).hexdigest()}
(O/'evidence/master-comparison.json').write_text(json.dumps(result,indent=2)+'\n')
print('COMPARE_MASTERS_PASS',flush=True)
