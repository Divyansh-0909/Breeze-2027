"""Private natural cave composition, real-source cropping and boundary retopology.

No change to C9 or movement registry; no Boolean, folded-plane cliff or random
rock displacement. Source geometry is uniformly transformed, cut around the
protected bent corridor and retained in the editable master. All runtime maps
are borrowed from the existing approved C8 3x owner.
"""
from pathlib import Path
import bpy,bmesh,numpy as np,json,math,hashlib,sys,subprocess
sys.path.insert(0,str(Path(__file__).resolve().parent))
from cave_scan_surface import passage
from cave_shared_frames import shared_frames
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
S=ROOT/'assets-source/gullyverse/c9-cave-recovery';O=ROOT/'public/models/gullyverse/c9-cave-recovery';R=ROOT/'reports/recovery-stage3a-cave-tunnel-2026-10-20/raw'
for p in [S,O,R]:p.mkdir(parents=True,exist_ok=True)
W=json.loads((ROOT/'public/models/gullyverse/blockout.layout.json').read_text())
# Blender Z up, site WebGL Y up; site travel -Z maps to Blender +Y.
def B(p):return (float(p[0]),-float(p[2]),float(p[1]))
def G(p):return (float(p[0]),float(p[2]),-float(p[1]))
def center(y):return float(np.interp(np.clip(y,0,42),[-p[1]for p in W['tunnel']['centerline']],[p[0]for p in W['tunnel']['centerline']]))
def mesh(name,xyz,faces):
 m=bpy.data.meshes.new(name);m.from_pydata(xyz,[],faces);m.update();o=bpy.data.objects.new(name,m);bpy.context.scene.collection.objects.link(o);return o

def decimate(o,target,protect=True):
 bpy.context.view_layer.objects.active=o;o.select_set(True)
 group=o.vertex_groups.new(name='Protected_Shared_Interfaces')
 if protect:
  bm=bmesh.new();bm.from_mesh(o.data);bm.verts.ensure_lookup_table();boundary=[v.index for v in bm.verts if v.is_boundary];bm.free()
  if boundary:group.add(boundary,1.0,'REPLACE')
 m=o.modifiers.new('Source_Form_Retopology','DECIMATE');m.ratio=min(1,target/len(o.data.polygons));m.use_collapse_triangulate=True
 if protect:m.vertex_group=group.name;m.invert_vertex_group=True;m.vertex_group_factor=1000
 bpy.ops.object.modifier_apply(modifier=m.name);o.select_set(False)
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free();o.data.update()
 return o

def chains(edges):
 adjacency={}
 for a,b in edges:
  adjacency.setdefault(a,[]).append(b);adjacency.setdefault(b,[]).append(a)
 assert all(len(v)<=2 for v in adjacency.values()),('Branched cut',[(k,len(v))for k,v in adjacency.items()if len(v)>2][:10])
 paths=[]
 while adjacency:
  start=next((k for k,v in adjacency.items()if len(v)==1),next(iter(adjacency)))
  path=[];previous=None;current=start
  while current in adjacency:
   path.append(current);neighbors=adjacency.pop(current);n=next((j for j in neighbors if j!=previous and j in adjacency),None)
   if n is None:break
   previous,current=current,n
  paths.append(path)
 return paths

# Actual scanned three-dimensional source. Keep original geometry editable.
src=ROOT/'assets-source/gullyverse/quarry-fidelity-correction/licensed-source/coastal_cliff_04/coastal_cliff_04_1k.blend'
bpy.ops.wm.open_mainfile(filepath=str(src));native=bpy.data.objects['coastal_cliff_04_LOD2'];native_mesh=native.data.copy();native_world=native.matrix_world.copy()
for original_object in list(bpy.data.objects):
 bpy.data.objects.remove(original_object,do_unlink=True)
reference=bpy.data.objects.new('CC0_Coastal04_Original_Native_Reference',native_mesh);bpy.context.scene.collection.objects.link(reference);reference.matrix_world=native_world
reference.hide_render=True;reference.hide_set(True)
working=bpy.data.objects.new('Cave_Entrance_Authored_High',native_mesh.copy());bpy.context.scene.collection.objects.link(working)
# 1.7 uniformly in XYZ: original ~11m vertical capture becomes ~18.7m;
# no directional expansion. The 58m original entrance width is cropped, not fitted.
scale=1.7
for v in working.data.vertices:
 p=native_world@v.co;v.co=(p.x*scale,p.y*scale+3.0,p.z*scale-.3)
working.data.materials.clear();decimate(working,85000,False)
# Temporarily express X relative to the existing bent path for the cut only.
# Restore every surviving source vertex to its original rigid-transformed X.
bm=bmesh.new();bm.from_mesh(working.data)
for v in bm.verts:v.co.x-=center(v.co.y)
for point,normal in [((-29,0,0),(1,0,0)),((30,0,0),(-1,0,0)),((0,0,-.38),(0,0,1)),((0,-4,0),(0,1,0))]:
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=point,plane_no=normal,clear_inner=True)
# Deliberately asymmetric mouth, constrained outside the 2.38m protected route.
profile=np.array([[-4.15,-.5],[-4.0,1.8],[-3.65,3.6],[-2.7,5.0],[-1.35,5.85],[.65,6.25],[2.1,5.65],[3.4,4.3],[3.95,2.3],[4.15,-.5]])
planes=[]
for a,b in zip(profile[:-1],profile[1:]):
 tangent=b-a;n=np.array([tangent[1],-tangent[0]]);n/=np.linalg.norm(n);planes.append((a,n))
 bmesh.ops.bisect_plane(bm,geom=list(bm.verts)+list(bm.edges)+list(bm.faces),dist=1e-7,plane_co=(a[0],0,a[1]),plane_no=(n[0],0,n[1]))
inside=lambda x,z: all(np.dot(np.array([x,z])-a,n)>=-1e-6 for a,n in planes)
remove=[f for f in bm.faces if inside(f.calc_center_median().x,f.calc_center_median().z)]
bmesh.ops.delete(bm,geom=remove,context='FACES')
bmesh.ops.delete(bm,geom=[v for v in bm.verts if not v.link_faces],context='VERTS')
bmesh.ops.remove_doubles(bm,verts=[v for v in bm.verts if v.is_boundary],dist=1e-6)
# The true scan cut edge is shared by the authored throat. No overlaid rocks.
bm.verts.ensure_lookup_table();cut=[]
for e in bm.edges:
 if not e.is_boundary:continue
 a,b=e.verts
 if min(a.co.z,b.co.z)<-.35:continue
 if all(min(abs(np.dot(np.array([v.co.x,v.co.z])-p,n))for p,n in planes)<2e-4 for v in [a,b]):cut.append((a.index,b.index))
paths=chains(cut);paths.sort(key=len,reverse=True)
print('MOUTH_PATHS',[(len(p),float(max(bm.verts[i].co.z for i in p)),[list(bm.verts[p[0]].co),list(bm.verts[p[-1]].co)])for p in paths],flush=True)
arches=[p for p in paths if max(bm.verts[i].co.z for i in p)>4]
assert len(arches)==1,'The selected source does not produce one safe raised mouth; do not hide capture defects.'
path=arches[0]
for v in bm.verts:v.co.x+=center(v.co.y)
# A specific thin captured forecourt fin read as a floating blade in the
# browser. Sculpt its lower 1.2m into the buried foot, preserving the mouth and
# 2.38m navigation envelope. No whole-cliff smoothing or random displacement.
foot_brush={'centerBlenderM':[-4.1,-2.0,.65],'maximumDropM':0,'vertices':0}
for v in bm.verts:
 x,y,z=v.co
 if not(-5.9<x<-2.5 and -4<=y<-.2 and -.2<z<2.1):continue
 w=math.exp(-((x+4.1)/1.1)**2-((y+2)/1.6)**2)*(max(0,1-z/2.1))
 drop=min(max(0,z+.32),1.2*w);v.co.z-=drop
 if drop>1e-6:foot_brush['vertices']+=1;foot_brush['maximumDropM']=max(foot_brush['maximumDropM'],float(drop))
bmesh.ops.triangulate(bm,faces=list(bm.faces));bm.to_mesh(working.data);bm.free();working.data.update()
# Save the genuine edge before any further authoring, to diagnose source suitability.
cut_points=[list(working.data.vertices[i].co)for i in path]
(R/'mouth-native-cut.json').write_text(json.dumps({'source':str(src.relative_to(ROOT)),'uniformScaleXYZ':[scale]*3,'profile':profile.tolist(),'points':cut_points,'triangles':len(working.data.polygons)},indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(S/'cave-entrance-source-trial.blend'),compress=True)
print('ENTRANCE_TRIAL_READY',len(working.data.polygons),flush=True)

# The latest user continuation is implemented as the approved natural rock
# vault, with no artificial ceiling panel or visible/hanging light fixtures.
if cut_points[0][0]>cut_points[-1][0]:path=list(reversed(path));cut_points=list(reversed(cut_points))
throat,passage_highs,passage_source=passage(ROOT,W,center,mesh,cut_points,working,path)

material_spec=json.loads((ROOT/'assets-source/gullyverse/recovered-c8-material/material-manifest.json').read_text())
# The shared texture already includes its 1x repeat and the approved /3 scale.
# Geometry therefore supplies the established metre/2 host UVs, not a second
# copy of the material repeat. Projection-island offsets are exact tile periods.
uv_per_metre=1/material_spec['hostUVUnitMetres']
island_period=8/material_spec['approvedUVRepeat']
mat=bpy.data.materials.new('Cave_Borrowed_C8_3x_PBR');mat.use_nodes=True;shader=mat.node_tree.nodes.get('Principled BSDF');shader.inputs['Base Color'].default_value=(.2,.18,.16,1);shader.inputs['Roughness'].default_value=.94

def finish(o):
 m=o.data
 if not m.uv_layers:m.uv_layers.new(name='UVMap')
 uv=m.uv_layers[0].data
 for face in m.polygons:
  n=np.abs(face.normal);axis=int(np.argmax(n))
  axes=([1,2]if axis==0 else[0,2]if axis==1 else[0,1])
  for li in face.loop_indices if 'Entrance'in o.name else []:
   v=m.vertices[m.loops[li].vertex_index].co
   # Explicit authored projection islands, offset by exact texture periods.
   # Identical numeric UVs at different projection orientations must not share
   # a tangent average. The offset changes no approved 3x visible sample.
   uv[li].uv=(v[axes[0]]*uv_per_metre+axis*island_period,v[axes[1]]*uv_per_metre)
  face.use_smooth=True
 col=m.color_attributes.get('Color')or m.color_attributes.new(name='Color',type='FLOAT_COLOR',domain='POINT')
 if 'Floor'not in o.name:
  for i,v in enumerate(m.vertices):col.data[i].color=(1,1,1,1)
 m.materials.clear();m.materials.append(mat);m.update()

runtime=[];parts=[]
for name,high,targets in [('Entrance',working,[18000,9000,4200]),('Throat',throat,[4400,2500,1600])]+passage_highs:
 nodes=[];counts=[]
 for level,target in enumerate(targets):
  o=bpy.data.objects.new(f'Cave_{name}_LOD{level}',high.data.copy());bpy.context.scene.collection.objects.link(o)
  decimate(o,target,True);finish(o);runtime.append(o);nodes.append(o.name);counts.append(len(o.data.polygons))
 high.hide_render=True;high.hide_set(True)
 xyz=np.array([G(v.co)for v in high.data.vertices]);lo=xyz.min(0);hi=xyz.max(0);c=(lo+hi)/2
 parts.append({'id':name,'nodes':nodes,'triangles':counts,'materialRole':'floor'if name=='Floor'else'rock','center':c.tolist(),'radius':float(np.linalg.norm(hi-lo)/2),'bounds':[lo.tolist(),hi.tolist()]})
# Corrected throat side orientation is inspected from the protected centerline.
for o in runtime:
 bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
 if 'Throat'in o.name or 'Passage'in o.name:
  score=0
  for f in bm.faces:
   c=f.calc_center_median();to=Vector((center(c.y)-c.x,0,2.2-c.z));score+=f.normal.dot(to)*f.calc_area()
  if score<0:bmesh.ops.reverse_faces(bm,faces=list(bm.faces))
 bm.to_mesh(o.data);bm.free();o.data.update()
 # Captured fracture corners cannot average opposite surface normals/tangent
 # derivatives. Split shading at real >55-degree edges; position is unchanged.
 bpy.context.view_layer.objects.active=o;o.select_set(True)
 split=o.modifiers.new('Physical_Fracture_Shading_Boundaries','EDGE_SPLIT')
 split.split_angle=math.radians(55);split.use_edge_angle=True;split.use_edge_sharp=False
 bpy.ops.object.modifier_apply(modifier=split.name);o.select_set(False);finish(o)
# Independently decimated parts share positions but otherwise calculate
# different one-sided normals. Match their artificial partition rings before
# export; genuine fractured shading away from the rings remains untouched.
shared_frame_result=shared_frames(runtime)
# Blender's loop-space custom-normal compression rounds differently on either
# side of a partition. Carry the common vectors into the float32 GLB before
# genuine MikkTSpace generation, rather than widening frame tolerances.
frame_file=S/'shared-boundary-normals.json'
frame_file.write_text(json.dumps(shared_frame_result.pop('canonicalWebGLFrames'),indent=2)+'\n')
shared_frame_result['canonicalFrameFile']=str(frame_file.relative_to(ROOT))
shared_frame_result['runtimeFloat32CanonicalOverride']=True
# Authoring source remains a separate hidden collection, excluded from runtime.
for o in bpy.context.selected_objects:o.select_set(False)
for o in runtime:o.hide_set(False);o.select_set(True)
bpy.context.view_layer.objects.active=runtime[0]
filepath=O/'cave-entrance.glb'
bpy.ops.export_scene.gltf(filepath=str(filepath),export_format='GLB',use_selection=True,export_yup=True,export_texcoords=True,export_normals=True,export_tangents=True,export_vertex_color='ACTIVE',export_materials='EXPORT',export_animations=False,export_extras=True)
subprocess.run(['node',str(ROOT/'scripts/blender/cave_mikktspace.mjs'),str(filepath),'--shared-normals',str(frame_file)],cwd=ROOT,check=True)
manifest={'version':'stage3a-natural-cave-candidate','privateOnly':True,'completeStage3A':False,'interiorStatus':'42m source-derived rock-vault candidate, validation and visual review pending. No artificial ceiling panels or visible fixtures. Exact artist artwork unavailable.','runtime':filepath.name,'runtimeBytes':filepath.stat().st_size,'runtimeSHA256':hashlib.file_digest(filepath.open('rb'),'sha256').hexdigest(),'parts':parts,'source':{'asset':'coastal_cliff_04','license':'CC0 1.0','page':'https://polyhaven.com/a/coastal_cliff_04','sourceFile':str(src.relative_to(ROOT)),'uniformScaleXYZ':[scale]*3,'croppedNotFit':True},'passageSource':passage_source,'originalTunnelInterfaceMetres':42,'approvedTextureScale':3,'newPBRImages':0,'C9Changed':False,'collisionRegistryChanged':False,'visibleFixtures':0,'suppliedArtistArt':'PENDING; generic historical artwork omitted'}
manifest.update(candidateImplemented=True,productionApproved=False,
 sharedFrameCorrection=shared_frame_result,
 interiorStatus='42m source-derived rock vault implemented privately. Awaiting visual approval; exact artist PNGs remain pending.',
 textureMapping={'geometryUVMetresPerUnit':material_spec['hostUVUnitMetres'],'sharedTextureRepeatAtApprovedScale':material_spec['approvedUVRepeat'],'effectiveAtlasPeriodAt3xM':material_spec['hostUVUnitMetres']/material_spec['approvedUVRepeat'],'UV1QuarryBakeChanged':False},
 lighting={'newLights':0,'visibleFixtures':0,'globalLightingChanged':False,'interiorOnly':'Analytical opening/overburden response; not baked GI. Exterior material unfiltered.'},
 entranceFootSculpt=foot_brush)
(O/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
(R/'entrance-working-runtime.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Source master displays the SAME material with metre/2 UVs and approved 3x
# mapping. Runtime export above deliberately contains placeholders only.
author=bpy.data.materials.new('Cave_Authoring_Approved_C8_3x');author.use_nodes=True
nodes=author.node_tree.nodes;links=author.node_tree.links;bsdf=nodes.get('Principled BSDF');bsdf.inputs['Metallic'].default_value=0
coord=nodes.new('ShaderNodeTexCoord');mapping=nodes.new('ShaderNodeMapping');mapping.name='APPROVED_3X_NOT_EXTRA_UV_SCALING'
mapping.inputs['Scale'].default_value=(material_spec['approvedUVRepeat'],material_spec['approvedUVRepeat'],1)
mapping.inputs['Location'].default_value.y=material_spec['baseUVRepeat']-material_spec['approvedUVRepeat']
links.new(coord.outputs['UV'],mapping.inputs['Vector'])
textures={}
for suffix,colour in [('basecolor.jpg',True),('normal.png',False),('orm.png',False)]:
 t=nodes.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(ROOT/'assets-source/gullyverse/recovered-c8-material/textures'/('scanned-multi-'+suffix)))
 t.image.colorspace_settings.name='sRGB'if colour else'Non-Color';links.new(mapping.outputs['Vector'],t.inputs['Vector']);textures[suffix]=t
links.new(textures['basecolor.jpg'].outputs['Color'],bsdf.inputs['Base Color']);normal=nodes.new('ShaderNodeNormalMap');normal.inputs['Strength'].default_value=.7
links.new(textures['normal.png'].outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],bsdf.inputs['Normal'])
separate=nodes.new('ShaderNodeSeparateColor');links.new(textures['orm.png'].outputs['Color'],separate.inputs['Color']);links.new(separate.outputs['Green'],bsdf.inputs['Roughness'])
for o in [working,throat]+[high for _,high,_ in passage_highs]+runtime:
 if 'Floor'not in o.name:o.data.materials.clear();o.data.materials.append(author)
contract=bpy.data.texts.get('CAVE_RECOVERY_CONTRACT')or bpy.data.texts.new('CAVE_RECOVERY_CONTRACT');contract.clear();contract.write(json.dumps(manifest,indent=2))
bpy.ops.file.pack_all()
bpy.ops.file.make_paths_relative()
bpy.ops.wm.save_as_mainfile(filepath=str(S/'cave-entrance-working.blend'),compress=True)
print('PRIVATE_ENTRANCE_RUNTIME',json.dumps(manifest),flush=True)
