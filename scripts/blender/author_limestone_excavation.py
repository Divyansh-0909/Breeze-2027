"""Blender4.3: continuous quarry macro + three geology areas, isolated new paths.
blender --background --python scripts/blender/author_limestone_excavation.py
python scripts/blender/pack_limestone_excavation.py
"""
import bpy,bmesh,sys,json,math,hashlib
import numpy as np
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import limestone_excavation_geometry as geo

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'assets-source/gullyverse/limestone-excavation'
OUT=ROOT/'public/models/gullyverse/limestone-excavation'
RAW=ROOT/'reports/stage-2c2-limestone-excavation-2026-10-13/raw'
for p in[SRC,OUT,RAW]:p.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
with bpy.data.libraries.load(str(ROOT/'assets-source/gullyverse/limestone-grey-pilot/quarry-grey-limestone-pilot.blend'),link=False)as(data,to):
    to.materials=['Quarry_Pilot_Grey_Limestone_PBR']
mat=to.materials[0];assert mat
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1

def B(p):return np.stack([p[:,0],-p[:,2],p[:,1]],axis=1)
def G(p):return np.stack([p[:,0],p[:,2],-p[:,1]],axis=1)
def make(name,points,faces,uv,normals,collection):
    mesh=bpy.data.meshes.new(name+'_Mesh');mesh.from_pydata(B(points).tolist(),[],faces.tolist());mesh.materials.append(mat);mesh.update()
    mesh.polygons.foreach_set('use_smooth',np.ones(len(mesh.polygons),dtype=bool))
    layer=mesh.uv_layers.new(name='Continuous_Metre_Limestone')
    ids=np.array([l.vertex_index for l in mesh.loops]);layer.data.foreach_set('uv',uv[ids].astype(np.float32).reshape(-1))
    mesh.normals_split_custom_set(B(normals)[ids].tolist())
    ob=bpy.data.objects.new(name,mesh);collection.objects.link(ob)
    ob['units']='metres';ob['source_field']='continuous perimeter, bedding and rim'
    ob['material_reference']='approved Grey limestone isolated LOD0 preview'
    ob['production_default_enabled']=False
    return ob

def stats(ob):
    mesh=ob.data;mesh.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(mesh)
    zero=sum(f.calc_area()<1e-11 for f in bm.faces)
    non=sum(not e.is_manifold for e in bm.edges);bm.free()
    p=G(np.array([v.co[:] for v in mesh.vertices]))
    return {'name':ob.name,'vertices':len(mesh.vertices),'triangles':len(mesh.loop_triangles),
            'zeroAreaFaces':zero,'boundaryOrNonManifoldEdgesBeforeWeld':non,
            'bounds':[p.min(axis=0).tolist(),p.max(axis=0).tolist()]}

def export(path,selected):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in selected:ob.hide_set(False);ob.select_set(True)
    bpy.context.view_layer.objects.active=selected[0]
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,
        export_texcoords=True,export_normals=True,export_tangents=True,
        export_materials='EXPORT',export_extras=True,export_yup=True,export_animations=False)

all_rows=[];variants={};master_collection=bpy.data.collections.new('EDITABLE_CONTINUOUS_MASTERS');scene.collection.children.link(master_collection)
for detailed,key in[(False,'macro'),(True,'detailed')]:
    levels=[];objects=[[],[],[]];parts=[];rows=[];source_arrays=[]
    for level in range(3):
        coll=bpy.data.collections.new(f'{key.upper()}_RUNTIME_LOD{level}');scene.collection.children.link(coll)
        parent=bpy.data.objects.new(f'Excavation_{key}_LOD{level}',None);coll.objects.link(parent);levels.append(parent)
        for j in range(len(geo.BREAKS)-1):
            points,faces,uv,normals=geo.surface_sector(j,level,detailed)
            ob=make(f'Excavation_{key.capitalize()}_Sector_{j:02d}_LOD{level}',points,faces,uv,normals,coll)
            ob.parent=parent;ob['lod_level']=level;ob['runtime_partition']=j
            row=stats(ob);assert row['zeroAreaFaces']==0,(key,row);rows.append(row);objects[level].append(ob)
            if level==0:
                lo,hi=points.min(axis=0),points.max(axis=0);center=(lo+hi)/2
                # LOD uses the exposed face, not the large outer terrain bounding sphere.
                s=(geo.BREAKS[j]+geo.BREAKS[j+1])/2
                wall=geo.wall_point(np.array([s]),np.array([.42]),detailed)[0]
                radius=float(np.hypot((geo.BREAKS[j+1]-geo.BREAKS[j])/2,geo.rim_height(np.array(s))*.48))
                parts.append({'id':f'Excavation_{j:02d}','center':wall.tolist(),'radius':radius,
                    'bounds':[lo.tolist(),hi.tolist()],
                    'nodes':[f'Excavation_{key.capitalize()}_Sector_{j:02d}_LOD{i}'for i in range(3)],
                    'arc':[float(geo.BREAKS[j]),float(geo.BREAKS[j+1])]})
                source_arrays.append((points,faces,uv,normals))
        print('GEOMETRY',key,level,sum(r['triangles']for r in rows if r['name'].endswith(f'LOD{level}')),flush=True)
    # Editable joined master makes the absence of independent rock panels explicit.
    vp=[];fp=[];up=[];np_=[];offset=0
    for p,f,u,n in source_arrays:vp.extend(p);fp.extend(f+offset);up.extend(u);np_.extend(n);offset+=len(p)
    master=make(f'Excavation_{key}_Master',np.array(vp),np.array(fp),np.array(up),np.array(np_),master_collection)
    bm=bmesh.new();bm.from_mesh(master.data);bmesh.ops.remove_doubles(bm,verts=list(bm.verts),dist=2e-5);bm.to_mesh(master.data);bm.free();master.data.update();master.hide_set(True)
    # Low shell is a separate export for diagnostic raycasting. Runtime walking
    # still uses the EXACT existing world-registry polygons, never this proxy.
    proxy_coll=bpy.data.collections.new(f'{key.upper()}_COLLISION_REFERENCE');scene.collection.children.link(proxy_coll)
    proxy_objects=[]
    for ob in objects[2]:
        proxy=ob.copy();proxy.data=ob.data;proxy.name=ob.name.replace('_LOD2','_Collision');proxy.parent=None
        proxy_coll.objects.link(proxy);proxy['collision_proxy']=True;proxy['active_walking_registration']=False;proxy_objects.append(proxy)
    for i in range(3):export(OUT/f'excavation-{key}-lod{i}.glb',objects[i]+[levels[i]])
    export(OUT/f'excavation-{key}.glb',[o for level in objects for o in level]+levels)
    export(OUT/f'excavation-{key}-collision.glb',proxy_objects)
    for ob in [o for level in objects for o in level]+proxy_objects+levels:ob.hide_set(True)
    variants[key]={'parts':parts,'nodes':rows,'runtime':f'excavation-{key}.glb',
                   'trianglesByLOD':[sum(r['triangles']for r in rows if r['name'].endswith(f'LOD{i}'))for i in range(3)],
                   'editableMaster':master.name}
    all_rows.extend(rows)
    bpy.ops.wm.save_as_mainfile(filepath=str(SRC/f'excavation-{key}.blend'))

readme=bpy.data.texts.new('AUTHORING_CONTRACT');readme.write('Original continuous limestone excavation. Metres. Blender Z-up -> glTF Y-up. A single perimeter field determines every partition and all LOD borders. Grey limestone material is imported unchanged from the user-approved isolated pilot. Navigation/lighting/world data are read, not changed. Regenerate only this new excavation directory.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(SRC/'excavation-detailed.blend'))
manifest={'version':1,'blender':bpy.app.version_string,'units':'metres','blenderUp':'Z','glTFUp':'Y',
          'previewOnly':True,'approvedReference':'reports/grey-limestone-pilot-2026-10-12/screenshots/02-grey-limestone-medium.png',
          'material':'Quarry_Pilot_Grey_Limestone_PBR','materialSource':'public/models/gullyverse/pilot-limestone-grey/quarry-grey-limestone-pilot.glb',
          'sourceMaterialSHA256':hashlib.sha256((ROOT/'public/models/gullyverse/pilot-limestone-grey/quarry-grey-limestone-pilot.glb').read_bytes()).hexdigest(),
          'worldRegistrySHA256':hashlib.sha256((ROOT/'public/models/gullyverse/blockout.layout.json').read_bytes()).hexdigest(),
          **geo.description(),'variants':variants,
          'topology':'One joined master; runtime surfaces intentionally open at the buried inner foot, distant outer terrain border beyond ordinary review framing, and original tunnel attachment. No independent exposed end caps.',
          'collision':'Existing authoritative walking and travel polygons unchanged. Separate low-shell raycast proxy, not registered as new movement.'}
(SRC/'manifest.json').write_text(json.dumps(manifest,indent=2));(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2))
(RAW/'blender-geometry.json').write_text(json.dumps({'variants':variants,'description':geo.description()},indent=2))
print('DONE',json.dumps({k:v['trianglesByLOD']for k,v in variants.items()}),flush=True)
