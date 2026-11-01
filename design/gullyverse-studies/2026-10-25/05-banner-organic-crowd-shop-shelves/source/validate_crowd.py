import bpy,json,math,itertools
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parents[1]
data=json.loads((O/'evidence/organic-crowd-authoring.json').read_text())
actors=[]
for row in data['actors']:
    vertices=[];faces=[]
    for name in row['objects']:
        obj=bpy.data.objects[name];assert obj.parent is None
        base=len(vertices);vertices.extend(obj.matrix_basis@v.co for v in obj.data.vertices)
        faces.extend(tuple(base+i for i in p.vertices)for p in obj.data.polygons)
    low=[min(v[i]for v in vertices)for i in range(3)];high=[max(v[i]for v in vertices)for i in range(3)]
    assert abs(low[2]-7.2)<.002, (row['label'],'ground contact',low[2])
    assert (low[0]>=1.65-1e-5 or high[0]<=-1.65+1e-5)
    assert low[1]>=30.5-1e-5 and high[1]<=45.1+1e-5
    assert low[0]>=-14.75-1e-5 and high[0]<=14.75+1e-5
    shirt=next(bpy.data.objects[n]for n in row['objects']if n.endswith(' shirt'))
    forward=shirt.matrix_basis.to_quaternion()@Vector((0,1,0));target=Vector((-row['foot'][0],45.8-row['foot'][1],0));target.normalize()
    facing=forward.dot(target);assert facing>=math.cos(math.radians(11.001))
    actors.append({'label':row['label'],'low':low,'high':high,'tree':BVHTree.FromPolygons(vertices,faces),'forwardDot':facing,'parts':len(row['objects'])})
collisions=[];broad=0;pairs=0
for a,b in itertools.combinations(actors,2):
    pairs+=1
    if any(a['high'][i]<b['low'][i]or b['high'][i]<a['low'][i]for i in range(3)):continue
    broad+=1;hits=a['tree'].overlap(b['tree'])
    if hits:collisions.append({'a':a['label'],'b':b['label'],'triangleHits':len(hits)})
assert not collisions
counts={v:sum(all(n in scene.objects for n in row['objects'])for row in data['actors'])for v in ['A','B','C']for scene in bpy.data.scenes if scene.name.startswith(v+' /')}
assert counts==data['newAudienceCounts']
assert bpy.data.objects.get('Festival takeover banner')is None
for name in ['Existing Aftermovie / center','Existing Aftermovie / left','Existing Aftermovie / right','EXISTING GULLYVERSE hero raster','Small festival lane poster']:assert name in bpy.data.objects
actor_names={n for row in data['actors']for n in row['objects']}
prop_vertices=[];prop_faces=[]
for obj in bpy.data.objects:
    if obj.type!='MESH'or obj.name in actor_names or obj.name.startswith(('Bounded lane haze','Rooftop slab','Lane flat','Accessible ramp','Flared ramp apron')):continue
    assert obj.parent is None
    base=len(prop_vertices);prop_vertices.extend(obj.matrix_basis@v.co for v in obj.data.vertices)
    prop_faces.extend(tuple(base+i for i in p.vertices)for p in obj.data.polygons)
props=BVHTree.FromPolygons(prop_vertices,prop_faces);prop_collisions=[]
for actor in actors:
    hits=actor['tree'].overlap(props)
    if hits:prop_collisions.append({'actor':actor['label'],'triangleHits':len(hits)})
assert not prop_collisions,prop_collisions
result={'status':'PASS','actualAudienceCounts':counts,'actualActorsChecked':len(actors),'actualBodyPartsChecked':sum(a['parts']for a in actors),'actorPairsChecked':pairs,'AABBCandidatePairs':broad,'actualTriangleOverlapPairs':collisions,'crowdPropTriangleOverlaps':prop_collisions,'standingFloorContactExcludedFromPropOverlap':True,'bodyFootprintsAvoidCentralAisle':True,'centralClearHalfWidthM':1.65,'actualFeetWithin002mOfFloor':True,'maximumViewingAngleVariationDeg':11,'noPeopleBehindScreen':True,'screenAndNavigationPreserved':True,'counterState':'Checked separately without modifying it.','scope':'Conservative whole-body footprints during authoring plus actual triangle BVHs here; does not rely on foot centers alone. BVHs checked across all variants combined, which is stricter than visibility of one variant.'}
(O/'evidence/body-overlap-validation.json').write_text(json.dumps(result,indent=2)+'\n');print('BODY_VALIDATION_PASS',counts,'pairs',pairs,flush=True)
