"""Reproducible Blender4.3 foundation, ONLY new stage2c5 asset paths.
python scripts/blender/foundation_materials.py
blender --background --python scripts/blender/author_quarry_foundation.py
"""
import bpy,bmesh,sys,json,hashlib
import numpy as np
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import foundation_geometry as geo

ROOT=Path(__file__).resolve().parents[2]
SRC=ROOT/'assets-source/gullyverse/quarry-foundation'
OUT=ROOT/'public/models/gullyverse/quarry-foundation'
RAW=ROOT/'reports/stage-2c5-photorealism-foundation-2026-10-13/raw'
for p in[SRC,OUT,RAW]:p.mkdir(parents=True,exist_ok=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1

def material(name,family):
    m=bpy.data.materials.new(name);m.use_nodes=True;m.use_backface_culling=True;m.diffuse_color=(.15,.145,.13,1)
    nodes=m.node_tree.nodes;links=m.node_tree.links;bs=nodes.get('Principled BSDF')
    bs.inputs['Metallic'].default_value=0;bs.inputs['Roughness'].default_value=.94
    def image(suffix,colour):
        n=nodes.new('ShaderNodeTexImage');n.image=bpy.data.images.load(str(SRC/'textures'/(family+suffix)))
        n.image.colorspace_settings.name='sRGB'if colour else'Non-Color';n.image.pack();return n
    base=image('-basecolor.jpg',True);normal=image('-normal.png',False);orm=image('-orm.png',False)
    links.new(base.outputs['Color'],bs.inputs['Base Color'])
    nm=nodes.new('ShaderNodeNormalMap');nm.inputs['Strength'].default_value=.7
    links.new(normal.outputs['Color'],nm.inputs['Color']);links.new(nm.outputs['Normal'],bs.inputs['Normal'])
    sep=nodes.new('ShaderNodeSeparateColor');links.new(orm.outputs['Color'],sep.inputs['Color'])
    links.new(sep.outputs['Green'],bs.inputs['Roughness']);links.new(sep.outputs['Blue'],bs.inputs['Metallic'])
    group=bpy.data.node_groups.get('glTF Material Output')or bpy.data.node_groups.new('glTF Material Output','ShaderNodeTree')
    if not group.interface.items_tree:group.interface.new_socket(name='Occlusion',in_out='INPUT',socket_type='NodeSocketFloat')
    ao=nodes.new('ShaderNodeGroup');ao.node_tree=group;links.new(sep.outputs['Red'],ao.inputs['Occlusion'])
    m['license']='CC0 photographic source, retained with provenance';m['colour_reference']='Original Stage2A dark rock'
    return m

rock=material('Foundation_Dark_Rock_PBR','dark-rock');terrainmat=material('Foundation_Dry_Terrain_PBR','dry-terrain')
def B(p):return np.stack([p[:,0],-p[:,2],p[:,1]],axis=1)
coll=bpy.data.collections.new('FOUNDATION_RUNTIME');scene.collection.children.link(coll)

def make(name,p,f,u,n,c,mat=rock):
    mesh=bpy.data.meshes.new(name+'_Mesh');mesh.from_pydata(B(p).tolist(),[],f.tolist());mesh.materials.append(mat);mesh.update()
    mesh.polygons.foreach_set('use_smooth',np.ones(len(mesh.polygons),dtype=bool))
    ids=np.array([l.vertex_index for l in mesh.loops]);uv=mesh.uv_layers.new(name='Unreflected_Metre_UV')
    uv.data.foreach_set('uv',u[ids].astype(np.float32).reshape(-1));mesh.normals_split_custom_set(B(n)[ids].tolist())
    colour=mesh.color_attributes.new(name='Geological_Variation',type='FLOAT_COLOR',domain='CORNER')
    colour.data.foreach_set('color',np.c_[c[ids],np.ones(len(ids))].astype(np.float32).reshape(-1))
    ob=bpy.data.objects.new(name,mesh);coll.objects.link(ob);ob['preview_only']=True
    ob['units']='metres';return ob

def stats(ob):
    ob.data.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(ob.data)
    row={'name':ob.name,'vertices':len(ob.data.vertices),'triangles':len(ob.data.loop_triangles),
         'zeroAreaFaces':sum(f.calc_area()<1e-10 for f in bm.faces),
         'boundaryEdges':sum(e.is_boundary for e in bm.edges),'nonManifoldInteriorEdges':sum(not e.is_manifold and not e.is_boundary for e in bm.edges)}
    bm.free();return row

def export(path,objects,materials=False):
    bpy.ops.object.select_all(action='DESELECT')
    for ob in objects:ob.hide_set(False);ob.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,
        export_texcoords=True,export_normals=True,export_tangents=True,
        export_materials='EXPORT'if materials else'NONE',export_extras=True,export_yup=True,
        export_animations=False,export_all_vertex_colors=True)

objects=[[],[],[]];parts=[];rows=[]
for level in range(3):
    for j in range(len(geo.old.BREAKS)-1):
        data=geo.sector(j,level);ob=make(f'Foundation_Wall_{j:02d}_LOD{level}',*data)
        objects[level].append(ob);row=stats(ob);rows.append(row);assert not row['zeroAreaFaces'],row
        if level==0:
            p=data[0];a,b=geo.old.BREAKS[j:j+2];s=(a+b)/2
            parts.append({'id':f'Wall_{j:02d}','center':geo.point(np.array([s]),np.array([.42]))[0].tolist(),
                'radius':float(np.hypot((b-a)/2,geo.old.rim_height(np.array(s))*.48)),
                'nodes':[f'Foundation_Wall_{j:02d}_LOD{i}'for i in range(3)],'arc':[float(a),float(b)],
                'material':'Foundation_Dark_Rock_PBR','refined':j in[13,14,15],
                'bounds':[p.min(0).tolist(),p.max(0).tolist()]})
    print('WALL_GEOMETRY',level,sum(r['triangles']for r in rows if r['name'].endswith(f'LOD{level}')),flush=True)

tiles,terrainstats=geo.terrain()
for id,p,f,u,n,c in tiles:
    first=None
    for level in range(3):
        if first is None:first=make('Foundation_'+id+'_LOD0',p,f,u,n,c,terrainmat);ob=first
        else:
            ob=first.copy();ob.data=first.data;ob.name='Foundation_'+id+f'_LOD{level}';coll.objects.link(ob)
        objects[level].append(ob);rows.append(stats(ob))
    lo,hi=p.min(0),p.max(0)
    parts.append({'id':id,'center':((lo+hi)/2).tolist(),'radius':float(np.linalg.norm(hi-lo)/2),
                  'nodes':['Foundation_'+id+f'_LOD{i}'for i in range(3)],'material':'Foundation_Dry_Terrain_PBR','bounds':[lo.tolist(),hi.tolist()]})
print('TERRAIN',terrainstats,flush=True)

# Modest fractured foot fragments are at the wall, outside circulation. No new
# collision registration; large sediment changes are deferred.
rng=np.random.default_rng(2026101305);vp=[];fp=[];up=[];np_=[];cp=[]
for s in np.linspace(geo.START+5,geo.END-5,44):
    foot,n,_=geo.old.frame(np.array([s]));center=np.array([foot[0,0],.02,foot[0,1]])-np.array([n[0,0],0,n[0,1]])*.45
    radius=rng.uniform(.16,.43);h=rng.uniform(.08,.23)
    ring=np.arange(7)*2*np.pi/7+rng.uniform(-.16,.16,7)
    bottom=np.c_[np.cos(ring)*radius,np.full(7,-.06),np.sin(ring)*radius*.7]+center
    top=np.c_[np.cos(ring)*radius*.48,np.full(7,h),np.sin(ring)*radius*.46]+center
    p=np.vstack([bottom,top]);faces=[]
    for j in range(7):k=(j+1)%7;faces.extend([[j,7+j,7+k],[j,7+k,k]])
    for j in range(1,6):faces.extend([[0,j+1,j],[7,7+j,7+j+1]])
    f=np.array(faces);normals=np.zeros_like(p)
    cross=np.cross(p[f[:,1]]-p[f[:,0]],p[f[:,2]]-p[f[:,0]])
    for j in range(3):np.add.at(normals,f[:,j],cross)
    normals/=np.maximum(1e-12,np.linalg.norm(normals,axis=1))[:,None]
    fp.extend(f+len(vp));vp.extend(p);np_.extend(normals);up.extend(p[:,[0,2]]/2);cp.extend(np.ones((len(p),3))*.93)
first=make('Foundation_Foot_Scree_LOD0',np.array(vp),np.array(fp),np.array(up),np.array(np_),np.array(cp))
for i in range(3):
    if i==0:ob=first
    else:ob=first.copy();ob.data=first.data;ob.name=f'Foundation_Foot_Scree_LOD{i}';coll.objects.link(ob)
    objects[i].append(ob);rows.append(stats(ob))
p=np.array(vp);lo,hi=p.min(0),p.max(0);parts.append({'id':'Foot_Scree','center':((lo+hi)/2).tolist(),
 'radius':float(np.linalg.norm(hi-lo)/2),'nodes':[f'Foundation_Foot_Scree_LOD{i}'for i in range(3)],'material':rock.name,'bounds':[lo.tolist(),hi.tolist()]})

for i in range(3):export(OUT/f'foundation-lod{i}.glb',objects[i])
export(OUT/'foundation-geometry.glb',[o for level in objects for o in level])
export(OUT/'foundation-collision-reference.glb',objects[2])
holders=[]
for j,mat in enumerate([rock,terrainmat]):
    p=np.array([[0,0,0],[.001,0,0],[0,.001,0]],float)
    holders.append(make('Foundation_Material_Holder_'+str(j),p,np.array([[0,1,2]]),p[:,:2],np.tile([0,0,1],(3,1)),np.ones((3,3)),mat))
export(OUT/'foundation-materials.glb',holders,True)
for ob in objects[1]+objects[2]+holders:ob.hide_set(True)
text=bpy.data.texts.new('FOUNDATION_AUTHORING_CONTRACT');text.write('Metres, Blender Z-up -> glTF Y-up. Two adjacent detailed regions only; original shell foot/rim/navigation unchanged. Shared source-derived CC0 micro-PBR maps. Cartesian outer land. Runtime exports are geometry-only with one material holder. Collision export is diagnostic, not active locomotion. Reproduce with scripts/blender/author_quarry_foundation.py.\n')
bpy.ops.wm.save_as_mainfile(filepath=str(SRC/'quarry-foundation.blend'))
manifest={'version':1,'blender':bpy.app.version_string,'units':'metres','previewOnly':True,'baseline':'f53168fd5b32e55984afa504b2f69d737f275aac',
 'worldRegistrySHA256':hashlib.sha256((ROOT/'public/models/gullyverse/blockout.layout.json').read_bytes()).hexdigest(),
 'runtime':'foundation-geometry.glb','materialRuntime':'foundation-materials.glb','parts':parts,'regions':geo.REGIONS,
 'trianglesByLOD':[sum(r['triangles']for r in rows if r['name'].endswith(f'LOD{i}'))for i in range(3)],
 'nodes':rows,'terrain':terrainstats,'boundaryPolicy':'Same fixed146-point sector sides and exact common rim at all LODs',
 'uvPolicy':'Unreflected wall arc/2 and height/2 metres; Cartesian terrain XZ/90; shared repeat microdetail',
 'collision':'Original world navigation polygons unchanged; exported low shell for diagnostic raycasts only',
 'materials':['Foundation_Dark_Rock_PBR','Foundation_Dry_Terrain_PBR'],
 'files':[{'file':p.name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}for p in sorted(OUT.glob('*.glb'))]}
(SRC/'manifest.json').write_text(json.dumps(manifest,indent=2));(OUT/'manifest.json').write_text(json.dumps(manifest,indent=2));(RAW/'blender-authoring.json').write_text(json.dumps(manifest,indent=2))
print('DONE',manifest['trianglesByLOD'],flush=True)
