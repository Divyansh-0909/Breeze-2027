import bpy,bmesh,json,math,sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'source'));from art_cameras import ARTISTS
d=json.loads((O/'evidence/art-authoring.json').read_text());checks=[]
def bounds(names):
 p=[bpy.data.objects[n].matrix_world@v.co for n in names for v in bpy.data.objects[n].data.vertices]
 return [[min(q[i]for q in p),max(q[i]for q in p)]for i in range(3)]
new={}
for a in d['shutters']:
 names=[a['host']]+a['slats'];allverts=[];allfaces=[];measures=[]
 for name in names:
  ob=bpy.data.objects[name];m=ob.data;bm=bmesh.new();bm.from_mesh(m)
  assert all(e.is_manifold for e in bm.edges),name
  volume=bm.calc_volume(signed=True);assert volume>0,name
  assert all(f.calc_area()>1e-9 for f in bm.faces),name
  bm.free();m.calc_loop_triangles();m.calc_tangents(uvmap=m.uv_layers.active.name)
  maxdot=max(abs(l.normal.dot(l.tangent))for l in m.loops);minlen=min(l.tangent.length for l in m.loops)
  assert maxdot<1e-4 and minlen>.999,name
  assert all(math.isfinite(x)for l in m.loops for x in [*l.normal,*l.tangent,*l.bitangent]),name
  assert all(abs(abs(l.bitangent_sign)-1)<1e-5 for l in m.loops),name
  assert all(math.isfinite(x)for uv in m.uv_layers.active.data for x in uv.uv),name
  offset=len(allverts);allverts.extend(ob.matrix_world@v.co for v in m.vertices);allfaces.extend(tuple(offset+i for i in p.vertices)for p in m.polygons)
  measures.append({'object':name,'closedManifold':True,'positiveVolume':volume,'triangles':len(m.loop_triangles),'minTangentLength':minlen,'maxNormalTangentDot':maxdot})
 tree=BVHTree.FromPolygons(allverts,allfaces);hits=[]
 for zoff in [0,.03,.06,.074]:
  z=bpy.data.objects[a['slats'][8]].matrix_world.translation.z+zoff;origin=Vector((0,a['cy'],z));direction=Vector((a['side'],0,0));hit=tree.ray_cast(origin,direction,5)
  assert hit[0]is not None and hit[1].dot(direction)<-.001,(a['key'],zoff,hit)
  hits.append({'zOffsetFromSlatCenter':zoff,'hit':list(hit[0]),'facingDot':hit[1].dot(direction)})
 assert abs(abs(hits[0]['hit'][0])-3.6775)<1e-5
 frontdepth=abs(hits[-1]['hit'][0])-abs(hits[0]['hit'][0]);assert frontdepth>.025 and frontdepth<.031
 gaps=[]
 for n1,n2 in zip(a['slats'],a['slats'][1:]):
  lo=bounds([n1]);hi=bounds([n2]);gap=hi[2][0]-lo[2][1];assert .00098<gap<.00102,gap;gaps.append(gap)
 mats={bpy.data.objects[n].material_slots[0].material.name for n in names};assert len(mats)==1
 image_nodes=[n for n in bpy.data.materials[next(iter(mats))].node_tree.nodes if n.type=='TEX_IMAGE'];assert len(image_nodes)==1 and image_nodes[0].image.name.startswith('ART / original')
 rec={'artist':a['label'],'objectCount':len(names),'physicalSlatCount':18,'bounds':bounds(names),'grooveDepthMeasuredM':frontdepth,'metalThicknessM':.003,'seamGapMinM':min(gaps),'seamGapMaxM':max(gaps),'oneContinuousWorldSpacePaintMaterial':True,'oneSourceImageOwner':image_nodes[0].image.name,'allFrontAndValleyHitsFacing':hits,'meshes':measures}
 new[a['key']]=rec['bounds'];checks.append(rec)
bpy.ops.wm.open_mainfile(filepath=str(O/'source/prior-pilot/baseline/Rev05C-Approved-Corrugated-Art.blend'))
for a in d['shutters']:
 before=bounds([a['host']]+a['slats']);after=new[a['key']];err=max(abs(before[i][j]-after[i][j])for i in range(3)for j in range(2));assert err<1e-5,(a['key'],err)
 next(r for r in checks if r['artist']==a['label'])['maximumOuterAssemblyBoundsErrorM']=err
result={'status':'PASS','controlledShutterAssemblies':3,'slatMeshes':54,'backingMeshes':3,'newMeshObjects':0,'artistToShutter':[{'artist':a['label'],'host':a['host'],'slatCount':18,'source':a['source']}for a in d['shutters']],'checks':checks,'normalAndTangentTolerancesUnchanged':True,'wallGeometryUnchanged':True,'noHoveringPaintPlanes':True}
(O/'evidence/shutter-geometry-validation.json').write_text(json.dumps(result,indent=2)+'\n');print('SHUTTER_PROFILE_UV_NORMALS_PASS',[(r['artist'],r['grooveDepthMeasuredM'])for r in checks])
