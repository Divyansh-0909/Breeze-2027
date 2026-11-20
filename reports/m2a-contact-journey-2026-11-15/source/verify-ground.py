import bpy,json,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
R=Path('/dev/shm/m2a-contact-journey-2026-11-15');W=Path('/dev/shm/Breeze-2027-runtime');G=W/'public/models/gullyverse/locked-rev15z-m2a-contact-ground';master=Path('/dev/shm/Gullyverse-Rev15Z-Wide-Contact-Window-and-Restored-Graffiti.blend');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();m=json.loads((G/'manifest.json').read_text());assert sha(master)==m['source']['sha256'];name=m['objects'][0]['sourceObject']
with bpy.data.libraries.load(str(master))as(a,b):b.objects=[name]
original=b.objects[0]
with bpy.data.libraries.load(str(G/'contact-frontage-baked.blend'))as(a,b):b.collections=['Runtime / contact-frontage']
ground=next(o for o in b.collections[0].objects if o.get('runtimeOriginalSource')==name);row=m['objects'][0];indices=row['sourceFaces'];assert len(indices)==len(ground.data.polygons);assert tuple(map(tuple,original.matrix_world))==tuple(map(tuple,ground.matrix_world))
plan=json.loads((W/'scripts/gullyverse/contact-ground-plan.json').read_text());frame=plan['contact'];selection=plan['selection'];rawT=Vector(frame['tangent']);rawN=Vector(frame['normal'])
expected=[]
for face in original.data.polygons:
 centre=original.matrix_world@face.center
 if frame['frameBoundsU'][0]-1.2<=centre.dot(rawT)<=frame['frameBoundsU'][1]+1.2 and selection['depthBounds'][0]<=centre.dot(rawN)<=selection['depthBounds'][1] and selection['heightBounds'][0]<=centre.z<=selection['heightBounds'][1]:expected.append(face.index)
assert indices==expected,'Native face selection must include every original lower pothole face in the requested region'
for face,sourceIndex in zip(ground.data.polygons,indices):
 old=original.data.polygons[sourceIndex];assert [tuple(ground.data.vertices[i].co)for i in face.vertices]==[tuple(original.data.vertices[i].co)for i in old.vertices]
 for uv in row['originalUVLayers']:
  assert [tuple(ground.data.uv_layers[uv].data[i].uv)for i in face.loop_indices]==[tuple(original.data.uv_layers[uv].data[i].uv)for i in old.loop_indices]
vertices=[ground.matrix_world@v.co for v in ground.data.vertices];bvh=BVHTree.FromPolygons(vertices,[list(p.vertices)for p in ground.data.polygons]);config=json.loads((W/'components/gullyverse-runtime/contact-space.json').read_text());n=Vector(config['normal']).normalized();t=Vector(config['tangent']).normalized();radius=config['playerRadius'];samples=[]
print('BOUNDS',[(min(v[k] for v in vertices),max(v[k]for v in vertices))for k in range(3)],flush=True)
for dd in [-21,-20,-19,-18,-17,-16,-15]:
 print('COVERAGE',dd,[(uu,bvh.ray_cast(t*uu+n*dd+Vector((0,0,8.2)),Vector((0,0,-1)),2)[0]is not None)for uu in [-15,-14,-13,-12,-11,-10,-9]],flush=True)
for i in range(13):
 for j in range(13):
  u=config['walkU'][0]+radius+.01+(config['walkU'][1]-config['walkU'][0]-2*radius-.02)*i/12;d=config['walkDepth'][0]+radius+.01+(config['walkDepth'][1]-config['walkDepth'][0]-2*radius-.02)*j/12;p=t*u+n*d;p.z=config['floor']+1
  hit,normal,face,dist=bvh.ray_cast(p,Vector((0,0,-1)),2);assert hit is not None and normal.z>.5,(i,j,hit,normal);assert abs(hit.z-config['floor'])<.08;samples.append(hit.z)
clean=W/'public/models/gullyverse/locked-rev15z-clean-v2';cleanManifest=json.loads((clean/'manifest.json').read_text())
for item in cleanManifest['files']:assert sha(clean/item['file'])==item['sha256']
proof={'status':'PASS','sourceMasterSHA256':sha(master),'newSourceGroundFaces':len(indices),'allOriginalFacesInRegionIncludingLowerPotholeFacesPresent':True,'geometryTransformAndEveryOriginalUVExact':True,'floorCoverageSamples':len(samples),'allCapsuleInsetSamplesHaveNativeFloor':True,'floorHeightRange':[min(samples),max(samples)],'cleanContactShippingFilesUnchanged':len(cleanManifest['files']),'sourcePotholesAndAllOtherMasterObjectsUnmodified':True};(R/'evidence/ground-preservation.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))
