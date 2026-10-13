"""Stage2C bounded full quarry rollout. Preserves approved maps/world/entry/stage.
Blender4.3.2, deterministic source-topology input. Writes only new rollout dirs.
"""
import bpy,bmesh,sys,json,math,hashlib,numpy as np
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from quarry_rollout_geometry import SOURCE,Geology,triangulate_rock,gate,reflect,distance_edges,PILOT_R,PILOT_ORIGIN
ROOT=Path(__file__).resolve().parents[2];SRC=ROOT/'assets-source/gullyverse/quarry-rollout';OUT=ROOT/'public/models/gullyverse/quarry-rollout';OUT.mkdir(exist_ok=True,parents=True)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
with bpy.data.libraries.load(str(ROOT/'assets-source/gullyverse/first-wall-corrected/first-wall-corrected.blend'),link=False)as(data,to):to.objects=['Wall_Master','Wall_LOD0','Wall_LOD1','Wall_LOD2']
pilotObjects={o.name:o for o in to.objects};mat=bpy.data.materials['Approved_Cool_Grey_Limestone_Family'];assert mat
scene=bpy.context.scene;scene.unit_settings.system='METRIC';scene.unit_settings.scale_length=1
masters=bpy.data.collections.new('EDITABLE_QUARRY_GEOLOGY');scene.collection.children.link(masters);refs=bpy.data.collections.new('APPROVED_PILOT_REFERENCE');scene.collection.children.link(refs);refs.hide_render=True
for o in pilotObjects.values():refs.objects.link(o);o.hide_set(True)
levels=[];levelCollections=[]
for i in range(3):
 collection=bpy.data.collections.new(f'RUNTIME_LOD{i}');scene.collection.children.link(collection);levelCollections.append(collection);parent=bpy.data.objects.new(f'Quarry_LOD{i}',None);collection.objects.link(parent);levels.append(parent)
proxyCollection=bpy.data.collections.new('ORIGINAL_COLLISION_REFERENCE');scene.collection.children.link(proxyCollection);objects=[[],[],[]];rows=[];parts=[]
def B(p):return np.stack([p[:,0],-p[:,2],p[:,1]],axis=1)
def G(p):return np.stack([p[:,0],p[:,2],-p[:,1]],axis=1)
def create(name,points,faces,uv0,uv1,collection):
 mesh=bpy.data.meshes.new(name+'_Mesh');mesh.from_pydata(B(np.array(points)).tolist(),[],np.asarray(faces).tolist());mesh.materials.append(mat);mesh.update();a=mesh.uv_layers.new(name='Metre_Scale_Unique_Face');b=mesh.uv_layers.new(name='Fine_Mineral_Metre');a.data.foreach_set('uv',np.asarray(uv0).reshape(-1));b.data.foreach_set('uv',np.asarray(uv1).reshape(-1));mesh.polygons.foreach_set('use_smooth',np.ones(len(mesh.polygons),dtype=bool));mesh.set_sharp_from_angle(angle=math.radians(65));mesh.uv_layers.active=a;ob=bpy.data.objects.new(name,mesh);collection.objects.link(ob);return ob

def pilot_body(name,source,collection):
 mesh=source.data;group=source.vertex_groups['SOURCE_SOLID_4'].index;ids={v.index for v in mesh.vertices if any(g.group==group and g.weight>.5 for g in v.groups)};polys=[p for p in mesh.polygons if all(i in ids for i in p.vertices)];used=sorted({i for p in polys for i in p.vertices});mapping={i:j for j,i in enumerate(used)};local=G(np.array([mesh.vertices[i].co[:]for i in used]));world=local@PILOT_R.T+PILOT_ORIGIN;faces=[[mapping[i]for i in p.vertices]for p in polys];a=[];b=[];norm=[];geo=Geology(next(r for r in SOURCE['rocks']if r['id']==4))
 for poly in polys:
  positions=np.array([world[mapping[i]]for i in poly.vertices]);fi=min(range(12),key=lambda f:abs(np.dot(geo.normals[f],positions.mean(axis=0)-geo.v[geo.faces[f][0]])))
  repairedA,repairedB=geo.uv(positions,fi)
  for j,l in enumerate(poly.loop_indices):
   # Retain all approved limestone body UVs/normals. Only former green faces
   # receive metric limestone coordinates, since they had no mapped material.
   a.append(mesh.uv_layers[0].data[l].uv[:]if poly.material_index==0 else repairedA[j]);b.append(mesh.uv_layers[1].data[l].uv[:]if poly.material_index==0 else repairedB[j]);n=np.array(mesh.corner_normals[l].vector);n=np.array([n[0],n[2],-n[1]])@PILOT_R.T;norm.append([n[0],-n[2],n[1]])
 ob=create(name,world,faces,a,b,collection);ob.data.normals_split_custom_set(norm);return ob

def stats(ob,closed=True):
 ob.data.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(ob.data);non=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free()
 if closed:assert non==0 and volume>0,(ob.name,non,volume)
 row={'name':ob.name,'triangles':len(ob.data.loop_triangles),'vertices':len(ob.data.vertices),'nonManifoldEdges':non,'signedVolumeM3':volume};rows.append(row);return row

def hull_project(ob,geo):
 p=G(np.array([v.co[:]for v in ob.data.vertices]));outside=0
 for f,n in zip(geo.faces,geo.normals):outside=max(outside,float(((p-geo.v[f[0]])@n).max()))
 for _ in range(6):
  for f,n in zip(geo.faces,geo.normals):p-=np.maximum(0,(p-geo.v[f[0]])@n)[:,None]*n
 for v,q in zip(ob.data.vertices,p):v.co=(q[0],-q[2],q[1])
 ob.data.update();return outside

def decimate(master,name,target,collection,geo=None):
 ob=master.copy();ob.data=master.data.copy();ob.name=name;ob.data.name=name+'_Mesh';collection.objects.link(ob);bpy.context.view_layer.objects.active=ob;mod=ob.modifiers.new('Feature_Weighted_LOD','DECIMATE');master.data.calc_loop_triangles();mod.ratio=target/len(master.data.loop_triangles);mod.use_collapse_triangulate=True;mod.vertex_group='SIMPLIFIABLE';mod.vertex_group_factor=1;bpy.ops.object.modifier_apply(modifier=mod.name)
 if geo:ob['hull_projection_max_m']=hull_project(ob,geo)
 ob.data.set_sharp_from_angle(angle=math.radians(65));return ob

for rock in SOURCE['rocks']:
 rid=rock['id'];geo=Geology(rock);baseName=f'Quarry_Rock_{rid:02d}'
 if rid==4:
  master=pilot_body(baseName+'_Master',pilotObjects['Wall_Master'],masters);stats(master)
  lods=[pilot_body(baseName+f'_LOD{i}',pilotObjects[f'Wall_LOD{i}'],levelCollections[i])for i in range(3)]
 else:
  points,faces,a,b,geo=triangulate_rock(rock,n=36 if rid in[3,5]else 32);master=create(baseName+'_Master',points,faces,a,b,masters);stats(master)
  # Pin original corners and sky/silhouette edges. Internal geological edges
  # are free to decimate; shared fitted-contact perimeter is protected.
  distance=np.min(np.linalg.norm(points[:,None]-geo.v[None,:],axis=2),axis=1);edge=distance_edges(points,geo.v,geo.protected+geo.join_edges);group=master.vertex_groups.new(name='SIMPLIFIABLE')
  radial=points-geo.c;radial/=np.linalg.norm(radial,axis=1)[:,None];facing=radial@geo.basis[:,2]
  allEdges=list({tuple(sorted((a,int(b))))for face in geo.faces for a,b in zip(face,np.roll(face,-1))})
  terrainContact=(points[:,1]>=0)&(points[:,1]<=2.8)&(distance_edges(points,geo.v,allEdges)<1e-5)
  free=(distance>1e-5)&(edge>1e-5)&~terrainContact
  # Budget geometry for the inward visitor-facing surfaces, not invisible
  # backs. The first browser inspection showed medium LOD over-simplification.
  for low,high,weight in[(-2,.05,1.0),(.05,.4,.6),(.4,2,.18)]:group.add(np.flatnonzero(free&(facing>=low)&(facing<high)).tolist(),weight,'REPLACE')
  lods=[decimate(master,baseName+f'_LOD{i}',t,levelCollections[i],geo)for i,t in enumerate([12000,5000,1200])]
 for i,ob in enumerate(lods):ob.parent=levels[i];objects[i].append(ob);stats(ob)
 points=np.array(rock['vertices']);lo=points.min(axis=0);hi=points.max(axis=0);lo[1]=max(0,lo[1]);center=(lo+hi)/2;radius=np.linalg.norm((hi-lo)/2);parts.append({'id':rid,'name':baseName,'center':center.tolist(),'radius':float(radius),'bounds':rock['bounds'],'sourceCorners':rock['vertices'],'seed':20261012+rid*977,'nodes':[o.name for o in lods]})
 master.hide_set(True);print('AUTHORED',rid,[len(o.data.polygons)for o in lods],flush=True)

# Quarry-facing collar and rear 40% of exterior roof; enclosed passage and
# landing portal are left in their original source/rendering system.
def surface_geometry(attrs,ranges,cap=False,n=10):
 vertices=np.array(attrs['position']).reshape(-1,3);triangles=[]
 for start,count in ranges:triangles.extend(vertices[start:start+count].reshape(-1,3,3))
 if not cap:
  # The existing exterior has section-local noise seams at the first rear
  # rings. Join logical section/ring corners; the exit rim already matches
  # exactly and stays fixed. This is a localized visible transition repair.
  samples={}
  for j,(start,count)in enumerate(ranges):
   for step in range(4):
    q=vertices[start+step*6:start+step*6+6]
    for key,p in [((j,step),q[0]),((j+1,step),q[1]),((j+1,step+1),q[2]),((j,step+1),q[5])]:samples.setdefault(key,[]).append(p)
  welded={k:np.unique(np.round(v,6),axis=0).mean(axis=0)for k,v in samples.items()};triangles=[]
  for j in range(7):
   for step in range(4):
    a,b,c,d=[welded[k]for k in[(j,step),(j+1,step),(j+1,step+1),(j,step+1)]];triangles.extend([np.array([a,b,c]),np.array([a,c,d])])
 # Derive actual open boundary edges. Refinement preserves all their points.
 edges={}
 for tri in triangles:
  for a,b in zip(tri,np.roll(tri,-1,axis=0)):
   key=tuple(sorted((tuple(np.round(a,5)),tuple(np.round(b,5)))));edges[key]=edges.get(key,0)+1
 boundary=[(np.array(a),np.array(b))for(a,b),count in edges.items()if count==1]
 points=[];faces=[];lookup={}
 def add(p):
  key=tuple(np.round(p,6))
  if key not in lookup:lookup[key]=len(points);points.append(p)
  return lookup[key]
 for tri in triangles:
  a,b,c=tri;grid={}
  for i in range(n+1):
   for j in range(n+1-i):grid[(i,j)]=add(a+(b-a)*i/n+(c-a)*j/n)
  for i in range(n):
   for j in range(n-i):
    faces.append([grid[(i,j)],grid[(i+1,j)],grid[(i,j+1)]] )
    if i+j<n-1:faces.append([grid[(i+1,j)],grid[(i+1,j+1)],grid[(i,j+1)]])
 original=np.array(points);distance=np.full(len(points),np.inf)
 for a,b in boundary:
  d=b-a;t=np.clip(((original-a)*d).sum(axis=1)/np.dot(d,d),0,1);distance=np.minimum(distance,np.linalg.norm(original-a-t[:,None]*d,axis=1))
 from corrected_wall_geometry import morphology
 q=original.copy();q[:,1]-=12;q[:,0]*=.6;q[:,2]=(original[:,2]+42)*.25;depth=morphology(q)*gate(distance,.8)*.65
 normals=np.zeros_like(original)
 for f in faces:
  a,b,c=original[f];nn=np.cross(b-a,c-a);nn/=np.linalg.norm(nn);normals[f]+=nn
 normals/=np.linalg.norm(normals,axis=1)[:,None]
 # Surface orientation of old double-sided geometry varies. Move into the
 # solid roof/collar and use an actual closed return, not a textured plane.
 if cap:
  if np.mean(normals[:,2])>0:faces=[f[::-1]for f in faces];normals=-normals
  moved=original.copy();moved[:,2]+=depth
 else:moved=original-normals*depth[:,None]
 # Rear closure lives inside the existing mass, away from the opening.
 back=original-normals*2.8
 if cap:
  # Keep the closed return inside the existing rock mass, outside the
  # actual curved passage. Extruding along its sloping normals intrudes
  # into the side walking corridor; a swept enlarged inner rim does not.
  back=original.copy();back[:,2]+=2.8;profile=np.array(SOURCE['tunnel']['profile']);innerDistance=np.full(len(original),np.inf)
  for a,b in zip(profile,np.roll(profile,-1,axis=0)):
   d=b-a;t=np.clip(((original[:,:2]-a)*d).sum(axis=1)/np.dot(d,d),0,1);innerDistance=np.minimum(innerDistance,np.linalg.norm(original[:,:2]-a-t[:,None]*d,axis=1))
  def center(z):
   path=SOURCE['tunnel']['centerline']
   for (x1,z1),(x2,z2)in zip(path,path[1:]):
    if z<=z1 and z>=z2:return x1+(x2-x1)*(z-z1)/(z2-z1)
   return path[-1][0]
  weight=gate(3.6-innerDistance,1.0);shift=np.array([center(min(0,z))-center(-42)for z in back[:,2]]);back[:,0]+=shift*weight;outward=original[:,:2]-[0,2.5];outward/=np.maximum(1e-9,np.linalg.norm(outward,axis=1))[:,None];back[:,:2]+=outward*(.10*weight)[:,None]
 count=len(original);faces2=faces+[[v+count for v in f[::-1]]for f in faces];edgecounts={}
 for f in faces:
  for a,b in zip(f,np.roll(f,-1)):key=tuple(sorted((a,int(b))));edgecounts[key]=edgecounts.get(key,0)+1
 for f in faces:
  for a,b in zip(f,np.roll(f,-1)):
   if edgecounts[tuple(sorted((a,int(b))))]==1:faces2.extend([[int(a),int(a)+count,int(b)+count],[int(a),int(b)+count,int(b)]])
 points=np.concatenate([moved,back]);fi=np.array(faces2);uvpos=points[fi.reshape(-1)];s,t=uvpos[:,0],uvpos[:,1]if cap else uvpos[:,2]+42;base=np.stack([reflect((s+7.36)/15.57,.08,.92),reflect((t+9.65)/19.89,.06,.94)],axis=1);fine=np.stack([(s+6)/12,(t+5)/10],axis=1)
 return points,fi,base,fine,distance,count,boundary

for name,attrs,ranges,cap in [('Quarry_Exit',SOURCE['exitAttributes'],[(0,len(SOURCE['exitAttributes']['position'])//3)],True),('Quarry_Crown',SOURCE['tunnelAttributes'],[(r['start'],r['count'])for r in SOURCE['tunnelRearRanges']],False)]:
 points,faces,a,b,distance,count,boundary=surface_geometry(attrs,ranges,cap,n=10);master=create(name+'_Master',points,faces,a,b,masters);stats(master);group=master.vertex_groups.new(name='SIMPLIFIABLE');group.add([i for i in range(len(points))if distance[i%count]>1e-5],1,'REPLACE');lods=[decimate(master,name+f'_LOD{i}',t,levelCollections[i])for i,t in enumerate([12000,4000,1400])]
 for i,ob in enumerate(lods):ob.parent=levels[i];objects[i].append(ob);stats(ob)
 lo=points.min(axis=0);hi=points.max(axis=0);parts.append({'id':name,'name':name,'center':((lo+hi)/2).tolist(),'radius':float(np.linalg.norm((hi-lo)/2)),'nodes':[o.name for o in lods],'boundary':[[a.tolist(),b.tolist()]for a,b in boundary]});master.hide_set(True)

# Separate closed proxy, preserving current collision registry rather than replacing it.
points=[];faces=[]
for r in SOURCE['rocks']:
 offset=len(points);points.extend(r['vertices']);faces.extend([[offset+f[0],offset+f[j],offset+f[j+1]]for f in r['faces']for j in range(1,4)])
proxy=create('Wall_Collision',points,faces,np.zeros((len(faces)*3,2)),np.zeros((len(faces)*3,2)),proxyCollection);proxy.data.materials.clear();proxy.display_type='WIRE';proxy.hide_set(True);stats(proxy)
def export(path,selected):
 bpy.ops.object.select_all(action='DESELECT')
 for o in selected:o.hide_set(False);o.select_set(True)
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_texcoords=True,export_normals=True,export_tangents=True,export_materials='EXPORT',export_extras=True,export_yup=True,export_animations=False)
export(OUT/'quarry-limestone.glb',[o for level in objects for o in level]+levels+[proxy])
for i in range(3):export(OUT/f'quarry-lod{i}.glb',objects[i]+[levels[i]])
export(OUT/'quarry-collision.glb',[proxy])
for i in range(2):levels[i].hide_set(True)
proxy.hide_set(True);masters.hide_render=True;bpy.ops.wm.save_as_mainfile(filepath=str(SRC/'quarry-limestone.blend'))
manifest={'version':1,'userApprovedBaseline':'Stage2B corrected limestone pilot approved 2026-10-12; no historic appearance restored','blender':bpy.app.version_string,'units':'metres','blenderUp':'Z','glTFUp':'Y','sourceQuarryBounds':SOURCE['quarryBounds'],'sourcePositionHash':hashlib.sha256(np.array(SOURCE['quarryAttributes']['position'],dtype='<f4').tobytes()).hexdigest(),'tunnelRearRanges':SOURCE['tunnelRearRanges'],'sourceTunnelVertexCount':len(SOURCE['tunnelAttributes']['position'])//3,'sourceExitVertexCount':len(SOURCE['exitAttributes']['position'])//3,'sourceRearPositions':[SOURCE['tunnelAttributes']['position'][i*3:i*3+3]for r in SOURCE['tunnelRearRanges']for i in range(r['start'],r['start']+r['count'])],'sourceExitPositions':np.array(SOURCE['exitAttributes']['position']).reshape(-1,3).tolist(),'parts':parts,'nodes':rows,'material':'Approved_Cool_Grey_Limestone_Family','materialLibrarySHA256':hashlib.sha256((ROOT/'assets-source/gullyverse/first-wall-corrected/approved-limestone-material.blend').read_bytes()).hexdigest(),'lockedTextureHashes':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()for p in(ROOT/'assets-source/gullyverse/first-wall-section/textures').iterdir()if p.is_file()},'policy':'one shared limestone map family; one visible LOD per part; all original world coordinates and movement polygons retained; original pilot body retained; original stage/ground/entry/passages untouched'}
for p in[SRC/'manifest.json',OUT/'manifest.json']:p.write_text(json.dumps(manifest,indent=2))
print('ROLLOUT_EXPORT',[(p.name,p.stat().st_size)for p in OUT.glob('*.glb')],flush=True)
