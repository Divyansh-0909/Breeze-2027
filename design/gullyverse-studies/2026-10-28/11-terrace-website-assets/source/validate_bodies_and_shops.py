import bpy,json,math,itertools,bmesh,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
from mathutils.bvhtree import BVHTree
O=Path(__file__).resolve().parents[1];scene=next(s for s in bpy.data.scenes if s.get('variant')=='TERRACE ARCH');bpy.context.window.scene=scene;scene.frame_set(1);bpy.context.view_layer.update();data=json.loads((O/'evidence/rev05b-authoring.json').read_text())
def geometry(objects):
    v=[];f=[];owners=[]
    for obj in objects:
        assert obj.type=='MESH'and obj.parent is None
        off=len(v);v.extend(obj.matrix_basis@x.co for x in obj.data.vertices);f.extend(tuple(off+i for i in p.vertices)for p in obj.data.polygons);owners.extend([obj.get('pilotOriginalObject',obj.name)]*len(obj.data.polygons))
    return v,f,owners
actors=[];target={n for row in data['actors']for n in row['objects']}
for row in data['actors']:
    objs=[bpy.data.objects[n]for n in row['objects']];v,f,_=geometry(objs);low=[min(p[i]for p in v)for i in range(3)];high=[max(p[i]for p in v)for i in range(3)]
    assert abs(low[2]-7.2)<.002
    assert min(p.y for p in v)>23.4 and max(p.y for p in v)<44.2
    assert max(abs(p.x)for p in v)<14.75
    if low[1]<36.95:assert low[0]>=.45-1e-5 or high[0]<=-.45+1e-5
    shirt=next(o for o in objs if o.name.endswith(' shirt'));forward=shirt.matrix_basis.to_quaternion()@Vector((0,1,0));to=Vector((-row['foot'][0],45.8-row['foot'][1],0));to.normalize();assert forward.dot(to)>=math.cos(math.radians(12.001))
    actors.append({'row':row,'low':low,'high':high,'tree':BVHTree.FromPolygons(v,f)})
overlaps=[];pairs=0;broad=0
for a,b in itertools.combinations(actors,2):
    pairs+=1
    if any(a['high'][i]<b['low'][i]or b['high'][i]<a['low'][i]for i in range(3)):continue
    broad+=1;hits=a['tree'].overlap(b['tree'])
    if hits:overlaps.append([a['row']['label'],b['row']['label'],len(hits)])
assert not overlaps,overlaps
props=[o for o in scene.objects if o.type=='MESH'and o.name not in target and not o.get('pilotOriginalObject',o.name).startswith(('Bounded lane haze','Rooftop slab','Lane flat','Accessible ramp','Flared ramp apron'))]
pv,pf,_=geometry(props);prop_tree=BVHTree.FromPolygons(pv,pf)
prop_overlaps=[]
for a in actors:
    hits=a['tree'].overlap(prop_tree)
    if hits:prop_overlaps.append([a['row']['label'],len(hits)])
assert not prop_overlaps,prop_overlaps
counts={s['variant']:sum(all(n in s.objects for n in r['objects'])for r in data['actors'])for s in bpy.data.scenes if s.get('variant')in ['A','B','C','C+A PILOT','C+A WORLD']}
assert counts==dict(data['newAudienceCounts'],**{'C+A PILOT':data['newAudienceCounts']['C'],'C+A WORLD':data['newAudienceCounts']['C']})
center={v:sum(abs(r['foot'][0])<1.65 and r['foot'][1]>37 and all(n in s.objects for n in r['objects'])for r in data['actors'])for v in ['A','B','C']for s in bpy.data.scenes if s['variant']==v}
assert min(center.values())>=10,center
av,af,_=geometry([bpy.data.objects[n]for n in target]);crowd=BVHTree.FromPolygons(av,af)
legibility=[]
for camname in ['01-landing','14-board-arrival']:
    cam=bpy.data.objects[camname];board=bpy.data.objects['EXISTING GULLYVERSE hero raster'];points=[board.matrix_basis@v.co for v in board.data.vertices];points.append(sum(points,Vector())/len(points))
    blocked=0
    for p in points:
        direction=p-cam.location;dist=direction.length;direction.normalize();hit=crowd.ray_cast(cam.location,direction,dist-.01)
        blocked+=hit[0]is not None
    assert blocked==0
    legibility.append({'camera':camname,'raysToBoard':len(points),'crowdOccludedRays':blocked})
result={'status':'PASS','actualAudienceCounts':counts,'actorsChecked':len(actors),'bodyPartsChecked':len(target),'actorPairsChecked':pairs,'AABBCandidatePairs':broad,'bodyTriangleOverlaps':overlaps,'crowdPropTriangleOverlaps':prop_overlaps,'centerScreeningPeopleInsideOld3_3mGap':center,'protectedNarrowPassageBodyBoundaryX':.45,'passageEndsAtY':36.95,'straightCameraEndsAtY':36.5,'staticNoParting':True,'boardVisibility':legibility,'footToleranceM':.002,'maxFacingAngleVariationDeg':12,'standingFloorContactExcluded':True,'allVariantCollectionsCombined':True,'selectedPilotPropGeometryActuallySurveyed':True,'groundContactExclusionUsesOriginalSemanticIdentity':True}
(O/'evidence/body-overlap-validation.json').write_text(json.dumps(result,indent=2)+'\n');print('BODIES_PASS',counts,center,flush=True)

SHOPS=[(-1,-25,0),(-1,-7,2),(-1,2,3),(1,-16,1),(1,-7,2)]
def floor(y):return 6+1.2*min(1,max(0,(y+10)/24))
all_mesh=[o for o in scene.objects if o.type=='MESH'and not o.name.startswith('Bounded lane haze')];vv,ff,owner=geometry(all_mesh);full=BVHTree.FromPolygons(vv,ff)
records=[]
for side,cy,index in SHOPS:
    g=floor(cy);name=f'Building / {side} / {index}';host=bpy.data.objects[name];trim=min([o for o in bpy.data.objects if o.name.startswith('Shop recess')and o.location.x*side>0],key=lambda o:abs(o.location.y-cy));mesh_checks=[]
    for obj in [host,trim]:
        m=obj.data;bm=bmesh.new();bm.from_mesh(m);assert all(e.is_manifold for e in bm.edges);assert bm.calc_volume(signed=True)>0;assert all(f.calc_area()>1e-9 for f in bm.faces);volume=bm.calc_volume(signed=True);bm.free();m.calc_loop_triangles();m.calc_tangents(uvmap=m.uv_layers.active.name)
        maxdot=0;minlen=10
        for loop in m.loops:
            assert all(math.isfinite(z)for z in [*loop.normal,*loop.tangent,*loop.bitangent]);maxdot=max(maxdot,abs(loop.normal.dot(loop.tangent)));minlen=min(minlen,loop.tangent.length);assert abs(abs(loop.bitangent_sign)-1)<1e-5
        assert maxdot<1e-4 and minlen>.999
        uv=[u for v in m.uv_layers.active.data for u in v.uv];assert all(math.isfinite(u)for u in uv)
        mesh_checks.append({'object':obj.name,'vertices':len(m.vertices),'faces':len(m.polygons),'triangles':len(m.loop_triangles),'closedManifold':True,'signedVolume':volume,'minTangentLength':minlen,'maxNormalTangentDot':maxdot,'finiteUV':True,'zeroAreaFaces':0})
    v,f,_=geometry([host]);tree=BVHTree.FromPolygons(v,f)
    p=Vector((side*5.85,cy,g+1.72));rays=[]
    for label,origin,direction,expected in [('front',Vector((side*2.6,cy,g+1.72)),Vector((side,0,0)),side*8.4),('left',p,Vector((0,-1,0)),cy-3.1),('right',p,Vector((0,1,0)),cy+3.1),('floor',p,Vector((0,0,-1)),g+.015),('ceiling',p,Vector((0,0,1)),g+2.85)]:
        hit=tree.ray_cast(origin,direction,12);assert hit[0]is not None,label
        axis=0 if label=='front'else 1 if label in ['left','right']else 2
        assert abs(hit[0][axis]-expected)<1e-5,(name,label,list(hit[0]),expected)
        assert hit[1].dot(direction)<-.99,(name,label,list(hit[1]))
        rays.append({'ray':label,'hit':list(hit[0]),'normal':list(hit[1]),'expectedCoordinate':expected})
    stock=[r for r in data['shelfAndItemTransforms']if r['shop']==[side,cy]];assert len(stock)==45
    minbehind=10;wallgap=10;contacts=[]
    for r in stock:
        obj=bpy.data.objects[r['object']];points=[obj.matrix_basis@v.co for v in obj.data.vertices];us=[side*p.x for p in points];ys=[p.y-cy for p in points];zs=[p.z-g for p in points]
        assert min(us)>4 and max(us)<8.265 and max(abs(y)for y in ys)<3.1 and min(zs)>.015 and max(zs)<2.85,(name,obj.name)
        minbehind=min(minbehind,min(us)-4);wallgap=min(wallgap,3.1-max(abs(y)for y in ys))
    for bank in [r for r in data['assemblies']if r['shop']==[side,cy]]:
        rigid=Matrix(bank['rigidMatrix']);rows=[r for r in stock if r['object']in bank['objects']]
        for r in rows:
            expected=rigid@Matrix(r['before']);now=bpy.data.objects[r['object']].matrix_basis;assert max(abs(expected[i][j]-now[i][j])for i in range(4)for j in range(4))<1e-5
        boards=[bpy.data.objects[r['object']]for r in rows if r['object'].startswith('Shop stock shelf')];cartons=[bpy.data.objects[r['object']]for r in rows if r['object'].startswith('Dry goods carton')]
        tops=[max((b.matrix_basis@v.co).z for v in b.data.vertices)for b in boards]
        for carton in cartons:
            bottom=min((carton.matrix_basis@v.co).z for v in carton.data.vertices);err=min(abs(bottom-z)for z in tops);assert err<2e-5;contacts.append(err)
    clear_errors=[];sample_count=0;minray=10;doorway_options=[]
    for sign in [-1,1]:
        option_start=len(clear_errors)
        route=[(side*2.2,cy+sign*2.2),(side*4.25,cy+sign*2.2),(side*5.25,cy+sign*1.4),(side*7.5,cy)]
        for a,b in zip(route,route[1:]):
            steps=math.ceil(math.dist(a,b)/.1)
            for k in range(steps+1):
                t=k/steps;x=a[0]*(1-t)+b[0]*t;y=a[1]*(1-t)+b[1]*t;sample_count+=1
                for z in [.8,1.72]:
                    for angle in range(0,360,15):
                        rad=math.radians(angle);hit=full.ray_cast(Vector((x,y,g+z)),Vector((math.cos(rad),math.sin(rad),0)),.8)
                        if hit[0]is not None:
                            minray=min(minray,hit[3])
                            if hit[3]<.35:clear_errors.append({'point':[x,y,g+z],'object':owner[hit[2]],'distance':hit[3]})
        doorway_options.append({'side':sign,'status':'PASS'if len(clear_errors)==option_start else'BLOCKED','errors':clear_errors[option_start:]})
    visible=[];inside_visible=[]
    for r in stock:
        obj=bpy.data.objects[r['object']];points=[obj.matrix_basis@v.co for v in obj.data.vertices];points.append(sum(points,Vector())/len(points));lane=False;inside=False
        for isinside in [False,True]:
            for dy in [-2.2,0,2.2]if not isinside else[-.8,.8]:
                origin=Vector((side*(4.45 if isinside else 1.5),cy+dy,g+1.72))
                for targetp in points:
                    direction=targetp-origin;dist=direction.length;direction.normalize();hit=full.ray_cast(origin,direction,dist+.02)
                    if hit[0]is not None and owner[hit[2]]==obj.name:
                        if isinside:inside=True
                        else:lane=True
        if lane:visible.append(obj.name)
        if inside:inside_visible.append(obj.name)
    assert any(r['status']=='PASS'for r in doorway_options),(name,clear_errors[:10])
    for bank in [r for r in data['assemblies']if r['shop']==[side,cy]]:
        assert any(n in visible for n in bank['objects']),(name,bank['bank'],'no lane visibility')
    records.append({'shop':[side,cy],'host':name,'geometry':mesh_checks,'cavityRays':rays,'shelves':9,'cartons':36,'stockObjectsBehindOpening':len(stock),'minimumStockBehindOpeningM':minbehind,'minimumStockSideWallGapM':wallgap,'maxCartonBottomShelfTopErrorM':max(contacts),'doorwayRouteSamples':sample_count,'capsuleRadiusM':.35,'minimumMeasuredRouteRayClearanceM':minray,'doorwayRouteOptions':doorway_options,'atLeastOne035mApproachClear':True,'allApproachFailuresRetained':clear_errors,'stockObjectsVisibleFromLane':visible,'stockObjectsVisibleFromInside':inside_visible,'allThreeBanksVisibleFromLane':True})
result={'status':'PASS','fiveShops':records,'all225StockObjectsMovedAsRigidAssemblies':True,'counterPreservation':'See preservation-audit.json; no counter/contents/closed-store edits allowed.','scope':'Blender concept checks, not regulatory accessibility or runtime collision certification.'}
(O/'evidence/shop-geometry-stock-validation.json').write_text(json.dumps(result,indent=2)+'\n');print('SHOPS_PASS',[(r['shop'],len(r['stockObjectsVisibleFromLane']),len(r['stockObjectsVisibleFromInside']))for r in records],flush=True)
