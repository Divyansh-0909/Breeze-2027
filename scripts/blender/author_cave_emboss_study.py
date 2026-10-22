"""One9m pilot: native scan + closed rock body, volumetric high-poly union.

No Boolean modifier, source chart fitting or rejected experiment mesh is used.
Runtime cages conform to a genuine closed3D author mesh, retaining their exact
original boundary vertices and independently frozen walking envelope.
"""
from pathlib import Path
import bpy,bmesh,numpy as np,json,math,hashlib,sys,subprocess,collections
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];S=ROOT/'assets-source/gullyverse/cave-material-study';O=ROOT/'public/models/gullyverse/cave-material-study';R=ROOT/'reports/cave-material-study-2026-10-22/raw'
for p in [S,O,R]:p.mkdir(parents=True,exist_ok=True)
master=ROOT/'assets-source/gullyverse/c9-cave-recovery/cave-entrance-working.blend'
original=ROOT/'public/models/gullyverse/c9-cave-recovery/cave-entrance.glb'
source=S/'licensed-source/namaqualand_cliff_01/namaqualand_cliff_01_1k.blend'
frozen={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in [master,original,source]}
bpy.ops.wm.open_mainfile(filepath=str(master))
base=bpy.data.objects['Cave_Passage2_Authored_High']
# Keep exact historic geometry as a hidden, unmodified authoring reference.
for o in bpy.data.objects:o.hide_render=True;o.hide_set(True);o.select_set(False)
body=bpy.data.objects.new('Pilot_Closed_Rock_Body',base.data.copy());bpy.context.scene.collection.objects.link(body);body.hide_set(False);body.select_set(True);bpy.context.view_layer.objects.active=body
body.data.materials.clear()
solid=body.modifiers.new('Actual_Rock_Body_Thickness_Not_A_Sheet','SOLIDIFY');solid.thickness=3.8;solid.offset=-1;solid.use_even_offset=True
bpy.ops.object.modifier_apply(modifier=solid.name)
with bpy.data.libraries.load(str(source),link=False)as(a,b):b.objects=['namaqualand_cliff_01_LOD0']
scan=b.objects[0];bpy.context.scene.collection.objects.link(scan);scan.name='Pilot_Native_Weathered_Cliff_085'
native_bounds=[[min(v.co[k]for v in scan.data.vertices),max(v.co[k]for v in scan.data.vertices)]for k in range(3)]
# Rigid quarter-turn plus uniform0.85; native8.28m width becomes7.04m,
# entirely inside the old9m Passage2. No width/depth anisotropy.
for v in scan.data.vertices:
    x,y,z=v.co;v.co=(-9.12-.85*y,19.5+.85*x,.10+.85*z)
scan.data.materials.clear();bm=bmesh.new();bm.from_mesh(scan.data)
open_edges=[e for e in bm.edges if e.is_boundary]
bmesh.ops.holes_fill(bm,edges=open_edges,sides=0);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(scan.data);bm.free()
scan.hide_set(False);scan.select_set(True);body.select_set(True);bpy.context.view_layer.objects.active=body
bpy.ops.object.join();body.name='Pilot_Volumetric_High_Continuous_Rock'
remesh=body.modifiers.new('Closed_Volume_Composition_Not_Boolean','REMESH');remesh.mode='VOXEL';remesh.voxel_size=.065;remesh.use_smooth_shade=True
bpy.ops.object.modifier_apply(modifier=remesh.name)
bm=bmesh.new();bm.from_mesh(body.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(body.data);bm.free();body.data.update()
target=BVHTree.FromPolygons([v.co for v in body.data.vertices],[list(f.vertices)for f in body.data.polygons],all_triangles=False)
print('CLOSED_HIGH',len(body.data.vertices),len(body.data.polygons),flush=True)
body.hide_render=True;body.hide_set(True)
for o in bpy.data.objects:
    if o.name.startswith('Cave_') and '_LOD' in o.name:o.name='Historical_Reference_'+o.name
existing=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(original));imported=[o for o in bpy.data.objects if o not in existing]
runtime=[];metrics=[]
def smooth(t):t=max(0,min(1,t));return t*t*(3-2*t)
for level in range(3):
    o=next(o for o in imported if o.name==f'Cave_Passage2_LOD{level}')
    o.hide_set(False);m=o.data;old=[v.co.copy()for v in m.vertices]
    # Position-welded boundary detection respects split tangent vertices.
    keys=[tuple(round(float(x),6)for x in v.co)for v in m.vertices];edges=collections.Counter(tuple(sorted((keys[a],keys[b])))for f in m.polygons for a,b in zip(f.vertices,list(f.vertices)[1:]+[f.vertices[0]]))
    boundary={v for e,c in edges.items()if c==1 for v in e};pinned={i for i,k in enumerate(keys)if k in boundary}
    groups={}
    for i,key in enumerate(keys):groups.setdefault(key,[]).append(i)
    old_normals=[n.vector.copy()for n in m.corner_normals];moved=0;maxmove=0;bad=0
    for v in m.vertices:
        p=v.co.copy();rel=p.x+6
        if v.index in pinned or rel>=-1.5:continue
        weight=smooth((p.y-15.4)/.9)*smooth((23.6-p.y)/.9)*smooth((p.z-.20)/.55)*smooth((5.1-p.z)/.65)*smooth((-rel-1.5)/.7)
        if weight<=0:continue
        q,n,face,d=target.find_nearest(p,2.0)
        if q is None:continue
        candidate=p.lerp(q,weight)
        # Never alter movement/collision; reject offending projected samples.
        if .1<candidate.z<2.5 and abs(candidate.x+6)<2.38:
            bad+=1;continue
        v.co=candidate;delta=(candidate-p).length;moved+=delta>1e-6;maxmove=max(maxmove,delta)
    # Nearest-surface retopology may collapse two cage samples onto the same
    # scanned crease. Repair those exact local folds before export, rather
    # than flipping normals or accepting zero-area/non-manifold triangles.
    repairs=0
    for iteration in range(12):
        rejected=set()
        for face in m.polygons:
            a,b,c=list(face.vertices)[:3]
            old_cross=(old[b]-old[a]).cross(old[c]-old[a])
            cross=(m.vertices[b].co-m.vertices[a].co).cross(m.vertices[c].co-m.vertices[a].co)
            if cross.length<old_cross.length*.10 or cross.normalized().dot(old_cross.normalized())<.25:
                rejected.update(i for i in [a,b,c]if i not in pinned)
        if not rejected:break
        rejected={i for j in rejected for i in groups[keys[j]]}
        for key in {keys[i]for i in rejected}:
            group=groups[key];i=group[0];point=old[i].lerp(m.vertices[i].co,.60)
            for j in group:m.vertices[j].co=point
        repairs+=len(rejected)
    m.normals_split_custom_set([(0.0,0.0,0.0)]*len(m.loops));m.update()
    normals=[n.vector.copy()for n in m.corner_normals]
    for i,loop in enumerate(m.loops):
        if loop.vertex_index in pinned:normals[i]=old_normals[i]
    m.normals_split_custom_set(normals);m.update()
    material=bpy.data.materials.new('Cave_Study_Geometry_Placeholder_LOD'+str(level));material.use_nodes=True
    material.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=1
    m.materials.clear();m.materials.append(material)
    metrics.append({'LOD':level,'triangles':len(m.polygons),'boundaryVerticesPinned':len(pinned),'maximumMovementM':maxmove,'movedVertices':int(moved),'clearanceProjectionsRejected':bad,'specificFoldVertexRepairs':repairs})
    runtime.append(o)
for o in bpy.context.selected_objects:o.select_set(False)
for o in runtime:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=runtime[0]
path=O/'emboss-pilot.glb'
bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=True,export_vertex_color='ACTIVE',export_materials='EXPORT',export_animations=False)
# Retain the existing canonical frame at protected partition rings.
frames=ROOT/'assets-source/gullyverse/c9-cave-recovery/shared-boundary-normals.json'
subprocess.run(['node',str(ROOT/'scripts/blender/cave_mikktspace.mjs'),str(path),'--shared-normals',str(frames)],cwd=ROOT,check=True)
for o in runtime:o.hide_render=True;o.hide_set(True)
body.hide_render=False;body.hide_set(False);body.select_set(True);bpy.context.view_layer.objects.active=body
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=str(S/'cave-emboss-study.blend'),compress=True)
manifest={'privateOnly':True,'productionApproved':False,'status':'DIAGNOSTIC_PENDING_STRICT_VALIDATION','region':'Passage2','regionLengthM':9,'stationsBlenderM':[15,24],'replaceNodes':[o.name for o in runtime],'runtime':path.name,'runtimeBytes':path.stat().st_size,'runtimeSHA256':hashlib.sha256(path.read_bytes()).hexdigest(),'source':{'asset':'namaqualand_cliff_01','page':'https://polyhaven.com/a/namaqualand_cliff_01','license':'CC0 1.0','nativeBoundsM':native_bounds,'uniformScaleXYZ':[.85]*3,'rotation':'Rigid quarter-turn aboutZ','translationBlenderM':[-9.12,19.5,.10]},'authorHigh':{'vertices':len(body.data.vertices),'polygons':len(body.data.polygons),'voxelSizeM':.065,'rockBodyThicknessM':3.8,'booleanModifiers':0},'runtimeCages':metrics,'limitations':'Nearest-surface retopology can lose deep hidden undercuts; evaluate actual neutral geometry before adoption. Not a scan of a cave.','frozenInputs':frozen,'newTextureImages':0,'collisionChanged':False}
for p,h in frozen.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h
(O/'pilot-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(R/'pilot-authoring.json').write_text(json.dumps(manifest,indent=2)+'\n');print('PILOT_EXPORTED',path.stat().st_size,metrics,flush=True)
