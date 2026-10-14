"""Blender BVH survey of actual exports; joins and protected visitor clearances.
blender --background --python <this file>. No application or asset mutations.
"""
import bpy,json,math,sys
import numpy as np
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path.cwd();RAW=ROOT/'reports/stage-2c5-photorealism-foundation-2026-10-13/raw'
sys.path.insert(0,str(ROOT/'scripts/blender'))
import foundation_geometry as foundation
geo=foundation.old

def B(p):return Vector((p[0],-p[2],p[1]))
def G(p):return [p[0],p[2],-p[1]]
def tree(objects):
    vertices=[];faces=[]
    for ob in objects:
        if ob.type!='MESH':continue
        offset=len(vertices);vertices.extend(ob.matrix_world@v.co for v in ob.data.vertices)
        faces.extend([[offset+i for i in p.vertices]for p in ob.data.polygons])
    return BVHTree.FromPolygons(vertices,faces,all_triangles=False,epsilon=1e-6)
def imported(path):
    prior=set(bpy.data.objects);bpy.ops.import_scene.gltf(filepath=str(path))
    return [o for o in bpy.data.objects if o not in prior and o.type=='MESH']

bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
levels=[];objects=[];topology=[]
shell_face_counts=[]
source=json.loads((ROOT/'assets-source/gullyverse/quarry-rollout/source-topology.json').read_text())
tunnel=np.array(source['tunnelAttributes']['position']).reshape(-1,3)
keep=np.ones(len(tunnel),dtype=bool)
for r in source['tunnelRearRanges']:keep[r['start']:r['start']+r['count']]=False
retained=tunnel[keep]
mesh=bpy.data.meshes.new('Unchanged_Passage_Occlusion_Mesh')
mesh.from_pydata([B(p)for p in retained],[],np.arange(len(retained)).reshape(-1,3).tolist())
unchanged_tube=bpy.data.objects.new('Unchanged_Passage_Occlusion',mesh)
for i in range(3):
    obs=imported(ROOT/f'public/models/gullyverse/quarry-foundation/foundation-lod{i}.glb')
    levels.append(tree(obs+[unchanged_tube]));objects.append(obs)
    shell_face_counts.append(sum(len(o.data.polygons)for o in obs))
    tri=0;zero=0;normals=0
    for ob in obs:
        ob.data.calc_loop_triangles();tri+=len(ob.data.loop_triangles)
        for face in ob.data.loop_triangles:
            if face.area<1e-10:zero+=1
        coords=np.array([v.co[:]for v in ob.data.vertices]);assert np.isfinite(coords).all()
        assert ob.data.uv_layers
        uvs=np.array([uv.uv[:]for uv in ob.data.uv_layers[0].data]);assert np.isfinite(uvs).all()
        normals+=sum(np.linalg.norm(n.vector[:])<.99 for n in ob.data.corner_normals)
    topology.append({'LOD':i,'triangles':int(tri),'zeroAreaTriangles':int(zero),'shortNormals':int(normals),'finitePositionsAndUVs':True})
    assert zero==0 and normals==0

# Shared borders, including every cross-LOD adjacent pairing, use the exact
# same field positions and normals. Check exports' float32 positions directly.
manifest=json.loads((ROOT/'public/models/gullyverse/quarry-foundation/manifest.json').read_text())
mesh_by_level=[]
for obs in objects:mesh_by_level.append({o.name.split('.')[0]:o for o in obs})
seams=[]
for j in range(len(geo.BREAKS)-1):
    nxt=(j+1)%(len(geo.BREAKS)-1);s=geo.BREAKS[j+1]%geo.LENGTH
    expected=foundation.point(np.full_like(geo.COMMON_V,s),geo.COMMON_V)
    maximum=0
    for level in range(3):
        for part in[j,nxt]:
            ob=mesh_by_level[level][f'Foundation_Wall_{part:02d}_LOD{level}']
            actual=np.array([G(ob.matrix_world@v.co)for v in ob.data.vertices])
            # Chunked nearest landmark checks without a scipy dependency inside Blender.
            for chunk in np.array_split(expected,8):
                err=np.sqrt(((chunk[:,None]-actual[None,:])**2).sum(axis=2)).min(axis=1)
                maximum=max(maximum,float(err.max()))
    seams.append({'joinAfterPart':j,'maximumSharedBorderErrorM':maximum})
    assert maximum<2e-5,(j,maximum)

eyes=[[0,1.72,-51],[0,1.72,-96],[-10.5,1.72,-110.8],[-18,1.72,-72.55],[17.4,1.72,-72.55]]
rays=[];horizontalGaps=[];lodDifferences=[];invertedHits=[]
for eye in eyes:
    for pitch in[0,10,20,30,40]:
        for yaw in range(0,360,3):
            a,b=math.radians(pitch),math.radians(yaw)
            direction=B([math.cos(a)*math.sin(b),math.sin(a),-math.cos(a)*math.cos(b)])
            casts=[t.ray_cast(B(eye),direction,650)for t in levels];hits=[c[3]for c in casts]
            row={'eye':eye,'pitch':pitch,'yaw':yaw,'hitsM':hits};rays.append(row)
            if pitch==0 and any(h is None for h in hits):
                # Exactly the open original passage is permitted, not a wall gap.
                point=Vector(B(eye))+direction*max(h for h in hits if h is not None) if any(h is not None for h in hits)else None
                angle=math.atan2(0-eye[0],-(-42-eye[2]));diff=abs(math.atan2(math.sin(b-angle),math.cos(b-angle)))
                allowance=math.atan2(3.3,math.hypot(eye[0],-42-eye[2]))+.008
                if diff>allowance:horizontalGaps.append(row)
            if any(h is None for h in hits)and any(h is not None for h in hits):lodDifferences.append(row)
            for level,c in enumerate(casts):
                if c[3] is not None and c[2]<shell_face_counts[level] and c[1].dot(direction)>.03:invertedHits.append({**row,'LOD':level,'normalDotRay':c[1].dot(direction)})

# The sampled low shell must never add a rock surface inside the preserved
# playable quarry. The tunnel attachment is intentionally at its existing rim.
clearances=[];boundary=np.array(geo.WORLD['quarry']['boundary'])
for j in range(len(geo.BREAKS)-1):
    s=np.linspace(geo.BREAKS[j],geo.BREAKS[j+1],35)
    ss,vv=np.meshgrid(s,np.linspace(0,1,15));points=foundation.point(ss.ravel(),vv.ravel())
    inside=np.ones(len(points),dtype=bool)
    for a,b in zip(boundary,np.roll(boundary,-1,axis=0)):
        d=b-a;n=np.array([d[1],-d[0]])/np.linalg.norm(d)
        inside&=((points[:,[0,2]]-a)@n)>0.0
    violations=points[inside&(points[:,1]>.25)&(np.abs(points[:,0])>3.3)]
    clearances.append({'part':j,'insidePlayableBoundaryVertices':len(violations)})
    assert len(violations)==0,(j,violations.tolist())

result={'status':'PASS'if not horizontalGaps and not invertedHits else'FAIL',
 'method':'Blender imports actual final runtime GLBs; finite attributes, all cross-LOD fixed borders, BVH full-perimeter/upward rays from five visitor locations and wall clearance survey. Open tunnel is separately allowed. Exact Stage2C skyline is revoked by Stage2C2.',
 'topology':topology,'seams':seams,'horizontalUnexpectedGaps':horizontalGaps,
 'crossLODHitDifferences':lodDifferences,'invertedVisibleHits':invertedHits,
 'wallClearances':clearances,'samples':rays,
 'limitations':'Sampling is not an exhaustive self-intersection or pixel-visibility proof. Buried inner foot, distant outer terrain border and original tunnel attachment are intentionally open surfaces. Original double-sided passage is retained as an occluder, not judged as newly authored geometry.'}
(RAW/'excavation-geometry-validation.json').write_text(json.dumps(result,indent=2))
print(result['status'],'gaps',len(horizontalGaps),'inverted',len(invertedHits),'LOD skyline differences',len(lodDifferences),flush=True)
assert not horizontalGaps and not invertedHits
