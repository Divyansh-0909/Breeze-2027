import json,struct,numpy as np,bpy
from pathlib import Path
from mathutils.bvhtree import BVHTree
from mathutils import Vector
r=Path('reports/stage-2b-wall-geometry-correction-2026-10-12');data=json.loads((r/'raw/host-topology.json').read_text());allpos=np.array(data['sourceAttributes']['position']).reshape(-1,3);m=json.loads(Path('public/models/gullyverse/first-wall-corrected/manifest.json').read_text());R=np.array([m['uAxis'],m['vAxis'],m['normal']]).T;origin=np.array(m['anchor'])
def glb(path):
 b=Path(path).read_bytes();n=struct.unpack_from('<I',b,12)[0];doc=json.loads(b[20:20+n]);binary=b[28+n:]
 def array(i):
  a=doc['accessors'][i];v=doc['bufferViews'][a['bufferView']];count={'SCALAR':1,'VEC3':3}[a['type']];dtype={5126:'<f4',5123:'<u2',5125:'<u4'}[a['componentType']];return np.frombuffer(binary,dtype=dtype,count=a['count']*count,offset=v.get('byteOffset',0)+a.get('byteOffset',0)).reshape(a['count'],count)
 node=next(n for n in doc['nodes']if n.get('name')=='Wall_LOD0');points=[];faces=[]
 for p in doc['meshes'][node['mesh']]['primitives']:
  xyz=array(p['attributes']['POSITION'])@R.T+origin;idx=array(p['indices']).reshape(-1,3);offset=len(points);points.extend(xyz.tolist());faces.extend((idx+offset).tolist())
 return points,faces

def scene(ranges,path):
 mask=np.ones(len(allpos),dtype=bool)
 for start,count in ranges:mask[start:start+count]=False
 base=allpos[mask];points=base.tolist();faces=np.arange(len(base)).reshape(-1,3).tolist();p,f=glb(path);offset=len(points);points+=p;faces+=[[v+offset for v in face]for face in f];return BVHTree.FromPolygons(points,faces)
old=scene([(243,9)],'public/models/gullyverse/first-wall-section/first-wall-section.glb');ranges=[(m['hostRange']['start'],m['hostRange']['count'])]+[(p['start'],p['count'])for p in m['joinRanges']];new=scene(ranges,'public/models/gullyverse/first-wall-corrected/first-wall-corrected.glb');rows=[]
for name,pos in [('frontal',[29,5,-60]),('hub',[18,1.72,-52]),('long',[0,1.72,-51]),('stage',[-10.5,1.72,-110.8])]:
 position=np.array(pos);forward=np.array([42.1893,6.5,-63.6718])-position;forward/=np.linalg.norm(forward);right=np.cross(forward,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,forward);lost=0;beforehit=0;tested=0;examples=[]
 for x in np.linspace(-1,1,50):
  for y in np.linspace(-1,1,36):
   d=forward+right*x*np.tan(29*np.pi/180)*(1366/900)+up*y*np.tan(29*np.pi/180);d/=np.linalg.norm(d);a=old.ray_cast(Vector(pos),Vector(d),700);b=new.ray_cast(Vector(pos),Vector(d),700);tested+=1
   if a[0]is not None:
    beforehit+=1
    if b[0]is None:lost+=1;examples.append([float(x),float(y)])
 rows.append({'view':name,'rays':tested,'beforeWallHits':beforehit,'newNoSurfaceWhereOldHit':lost,'examples':examples})
# Contact perimeter vertices are fixed in the master; measure sampled retained-face boundaries on LODs.
bpy.ops.wm.open_mainfile(filepath=str(Path.cwd()/'assets-source/gullyverse/first-wall-corrected/first-wall-corrected.blend'));joins=[]
for i in range(3):
 ob=bpy.data.objects[f'Wall_LOD{i}'];bvh=BVHTree.FromPolygons([v.co for v in ob.data.vertices],[list(p.vertices)for p in ob.data.polygons]);errors=[]
 for j in m['joiningContacts']:
  verts=(np.array(j['vertices'])-origin)@R;edges={tuple(sorted((int(a),int(b))))for f in j['selectedFaces']for a,b in zip(j['faces'][f],np.roll(j['faces'][f],-1))};edges.remove(tuple(sorted(j['sharedEdge'])))
  for a,b in edges:
   for t in np.linspace(0,1,17):
    p=verts[a]*(1-t)+verts[b]*t;near=bvh.find_nearest((p[0],-p[2],p[1]));errors.append(near[3])
 joins.append({'LOD':i,'contactPerimeterMaxDeviationM':max(errors)})
result={'method':'Actual old/new scene geometry BVH,50x36 rays at same58-degree FOV in4views; no lighting/texture simulation. Checks newly uncovered holes,not rendered photorealism. Original rock overlaps retained; no coplanar duplicate faces after source-cut.', 'rays':rows,'contactPerimeters':joins};(r/'raw/scene-seam-validation.json').write_text(json.dumps(result,indent=2));print(rows);print(joins)
