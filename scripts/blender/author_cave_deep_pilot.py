"""Stage3A.1 short native-triangle pilot only. Never overwrite Stage3A."""
from pathlib import Path
import bpy,bmesh,numpy as np,sys,json,hashlib,subprocess,math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(Path(__file__).parent))
from cave_native_graft import graft
from cave_shared_frames import shared_frames
S=ROOT/'assets-source/gullyverse/c9-cave-deep-relief';O=ROOT/'public/models/gullyverse/c9-cave-deep-relief';R=ROOT/'reports/stage3a1-deep-rock-2026-10-21/raw'
for p in [S,O,R]:p.mkdir(parents=True,exist_ok=True)
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets-source/gullyverse/c9-cave-recovery/cave-entrance-working.blend'))
manifest=json.loads((ROOT/'public/models/gullyverse/c9-cave-recovery/manifest.json').read_text());body=bpy.data.objects['Cave_Passage1_Authored_High']
new,info=graft(body,ROOT,source_x=-27.,source_z=4.6,station=11.2,side=-1,width=6.2,height=3.2,depth_offset=2.85)
print('NATIVE_GRAFT',json.dumps(info),flush=True)
bm=bmesh.new();bm.from_mesh(new.data)
print('PILOT_HIGH_TOPOLOGY',{'vertices':len(bm.verts),'faces':len(bm.faces),'nonManifold':sum(len(e.link_faces)>2 for e in bm.edges),'degenerateFaces':sum(f.calc_area()<1e-12 for f in bm.faces),'looseVertices':sum(not v.link_faces for v in bm.verts)},flush=True);bm.free()
# Unwrap the actual new continuous surface ONCE before LOD construction.
# Pin all established perimeter UVs. This avoids cube-projection seams and the
# invalid giant UV jump that the first trial made at its protected end rings.
oldpositions=[v.co.copy()for v in body.data.vertices];oldfaces=[list(f.vertices)for f in body.data.polygons]
oldtree=BVHTree.FromPolygons(oldpositions,oldfaces,all_triangles=True)
print('UV_OLD_TREE_READY',flush=True)
bm=bmesh.new();bm.from_mesh(new.data);bm.verts.ensure_lookup_table();boundary_indices={v.index for v in bm.verts if v.is_boundary};bm.free()
uv=new.data.uv_layers.new(name='UVMap')
print('UV_LAYER_READY',len(new.data.loops),flush=True)
for loop in new.data.loops:
 vertex=new.data.vertices[loop.vertex_index];point,normal,index,distance=oldtree.find_nearest(vertex.co)
 f=body.data.polygons[index];ids=list(f.vertices);oldcoords=[Vector((*body.data.uv_layers[0].data[li].uv,0))for li in f.loop_indices]
 value=barycentric_transform(point,*[oldpositions[i]for i in ids],*oldcoords)
 uv.data[loop.index].uv=(value.x,value.y);uv.data[loop.index].pin_uv=loop.vertex_index in boundary_indices
print('UV_SEED_AND_PINS_READY',flush=True)
# Re-open the edited datablocks before entering edit mode; retain an editable
# diagnostic master even if the runtime validation rejects this experiment.
bpy.ops.wm.save_as_mainfile(filepath=str(S/'cave-deep-pilot-authoring.blend'),compress=True)
bpy.ops.wm.open_mainfile(filepath=str(S/'cave-deep-pilot-authoring.blend'))
new=bpy.data.objects['Cave_Passage1_Deep_Authored_High'];body=bpy.data.objects['Cave_Passage1_Authored_High']
for o in bpy.context.selected_objects:o.select_set(False)
new.hide_set(False);new.select_set(True);bpy.context.view_layer.objects.active=new
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');print('UNWRAP_BEGIN',flush=True);bpy.ops.uv.unwrap(method='ANGLE_BASED',margin=.001);print('UNWRAP_END',flush=True);bpy.ops.object.mode_set(mode='OBJECT');new.select_set(False)
info['UVMethod']='Single angle-based unwrap of actual high surface with every established perimeter UV pinned; UV interpolation retained through all LODs. No independent per-LOD unwrap.'
# Store real native crops and the original high body, both editable.
body.hide_render=True;body.hide_set(True)
uvsource={tuple(round(float(x),5)for x in v.co):tuple(body.data.uv_layers[0].data[next(l.index for l in body.data.loops if l.vertex_index==v.index)].uv)for v in body.data.vertices if abs(v.co.y-6)<1e-5 or abs(v.co.y-15)<1e-5}
placeholder=bpy.data.materials.new('Deep_Cave_Borrowed_C8_Placeholder');placeholder.use_nodes=True;bs=placeholder.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(.2,.18,.16,1);bs.inputs['Roughness'].default_value=.94
repeat=.5;island_period=8/.061782042468605296
def finish(o,new_uv=False):
 m=o.data
 if new_uv and not m.uv_layers:
  uv=m.uv_layers.new(name='UVMap')if not m.uv_layers else m.uv_layers[0]
  for f in m.polygons:
   axis=int(np.argmax(np.abs(f.normal)));axes=([1,2]if axis==0 else[0,2]if axis==1 else[0,1])
   for li in f.loop_indices:
    v=m.vertices[m.loops[li].vertex_index].co;k=tuple(round(float(x),5)for x in v)
    uv.data[li].uv=uvsource[k]if k in uvsource else(v[axes[0]]*repeat+axis*island_period,v[axes[1]]*repeat)
 col=m.color_attributes.get('Color')or m.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='POINT')
 if new_uv:
  for c in col.data:c.color=(1,1,1,1)
 for f in m.polygons:f.use_smooth=True
 m.materials.clear();m.materials.append(placeholder);m.update()
runtime=[]
for part in manifest['parts']:
 for level,node in enumerate(part['nodes']):
  old=bpy.data.objects[node]
  if part['id']=='Passage1':
   bpy.data.objects.remove(old,do_unlink=True);o=bpy.data.objects.new(node,new.data.copy());bpy.context.scene.collection.objects.link(o)
   # Boundary preservation is mandatory, including every old shared ring.
   bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();boundary=[v.index for v in bm.verts if v.is_boundary or v.co.z < .15];bm.free()
   g=o.vertex_groups.new(name='Protected_Actual_Cave_Interfaces');g.add(boundary,1,'REPLACE')
   bpy.context.view_layer.objects.active=o;o.hide_set(False);o.select_set(True)
   d=o.modifiers.new('Selective_Runtime_Retopology','DECIMATE');d.ratio=min(1,[12000,6000,3000][level]/len(o.data.polygons));d.use_collapse_triangulate=True;d.vertex_group=g.name;d.invert_vertex_group=True;d.vertex_group_factor=1000
   bpy.ops.object.modifier_apply(modifier=d.name)
   bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
   split=o.modifiers.new('True_Fracture_Split','EDGE_SPLIT');split.split_angle=math.radians(55);split.use_edge_angle=True;split.use_edge_sharp=False;bpy.ops.object.modifier_apply(modifier=split.name)
   o.select_set(False);finish(o,True)
  else:o=old;finish(o,False)
  o.hide_render=False;o.hide_set(False);runtime.append(o)
 part['triangles']=[len(bpy.data.objects[n].data.polygons)for n in part['nodes']]
 p=np.array([[v.co.x,v.co.z,-v.co.y]for v in bpy.data.objects[part['nodes'][0]].data.vertices]);lo=p.min(0);hi=p.max(0);part.update(center=((lo+hi)/2).tolist(),radius=float(np.linalg.norm(hi-lo)/2),bounds=[lo.tolist(),hi.tolist()])
new.hide_set(True);new.hide_render=True
frame=shared_frames(runtime);framefile=S/'shared-boundary-normals.json';framefile.write_text(json.dumps(frame.pop('canonicalWebGLFrames'),indent=2)+'\n')
for o in bpy.context.selected_objects:o.select_set(False)
for o in runtime:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=runtime[0];file=O/'cave-deep-pilot.glb'
bpy.ops.export_scene.gltf(filepath=str(file),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=True,export_vertex_color='ACTIVE',export_materials='EXPORT',export_animations=False,export_extras=True)
subprocess.run(['node',str(ROOT/'scripts/blender/cave_mikktspace.mjs'),str(file),'--shared-normals',str(framefile)],cwd=ROOT,check=True)
manifest.update(version='stage3a1-native-triangle-pilot',runtime=file.name,runtimeBytes=file.stat().st_size,runtimeSHA256=hashlib.file_digest(file.open('rb'),'sha256').hexdigest(),candidateImplemented=True,completeStage3A=False,productionApproved=False,pilotOnly=True,pilotStationsM=[6,15],newNativeGraft=info,tunnelTextureFeatureScale=2,quarryTextureScale=3,sharedFrameCorrection=frame,interiorStatus='Short true-native-geometry pilot; neutral/browser gate pending. No automatic full-route rollout.',newPBRImages=0)
(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');(R/'pilot-authoring.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Editable source has the authentic original scan, original body and new mesh.
contract=bpy.data.texts.get('STAGE3A1_PILOT_CONTRACT')or bpy.data.texts.new('STAGE3A1_PILOT_CONTRACT');contract.write(json.dumps(manifest,indent=2))
bpy.ops.file.pack_all();bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(S/'cave-deep-pilot.blend'),compress=True)
print('PILOT_EXPORTED',json.dumps({'bytes':file.stat().st_size,'parts':manifest['parts']}),flush=True)
