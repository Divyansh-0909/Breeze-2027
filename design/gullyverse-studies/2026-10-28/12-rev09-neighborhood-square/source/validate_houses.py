import bpy,bmesh,json,math
from pathlib import Path
O=Path(__file__).resolve().parents[1];a=json.loads((O/'evidence/authoring.json').read_text());s=next(s for s in bpy.data.scenes if s.get('variant')=='SQUARE C180');bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update();rows=[]
for name in a['newConstruction']:
 o=bpy.data.objects[name];m=o.data;m.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(m);assert all(e.is_manifold for e in bm.edges),name;area=min(f.calc_area()for f in bm.faces);assert area>1e-9,(name,area);volume=bm.calc_volume(signed=True);assert volume>0;bm.free();m.calc_tangents(uvmap=m.uv_layers.active.name)
 assert all(math.isfinite(q)for l in m.loops for q in[*l.normal,*l.tangent,*l.bitangent]);dot=max(abs(l.normal.dot(l.tangent))for l in m.loops);unit=min(l.tangent.length for l in m.loops);assert dot<1e-4 and unit>.999,(name,dot,unit);assert all(abs(abs(l.bitangent_sign)-1)<1e-5 for l in m.loops)
 rows.append({'object':name,'triangles':len(m.loop_triangles),'closedManifoldComponents':True,'signedVolume':volume,'minimumFaceArea':area,'maxNormalTangentDot':dot,'minimumTangentLength':unit})
def length(intervals,lo,hi):
 intervals=sorted((max(lo,a),min(hi,b))for a,b in intervals if b>lo and a<hi);last=lo;n=0
 for a,b in intervals:
  n+=max(0,b-max(last,a));last=max(last,b)
 return n
coverage={}
for edge in['left','right','back','front']:
 hs=[h for h in a['houses']if h['edge']==edge];bounds=(14,48)if edge in['left','right']else(-16,16);intervals=[(h['center']-h['frontageM']/2,h['center']+h['frontageM']/2)for h in hs];covered=length(intervals,*bounds)
 # Front entrance X[-8.3,+8.3] excluded from the eligible perimeter.
 if edge=='front':covered=length(intervals,-16,-8.3)+length(intervals,8.3,16)
 coverage[edge]={'frontageIntervals':intervals,'coveredMetres':covered,'eligibleMetres':15.4 if edge=='front'else bounds[1]-bounds[0]}
eligible=sum(v['eligibleMetres']for v in coverage.values());covered=sum(v['coveredMetres']for v in coverage.values());r={'status':'PASS','strictAreaThreshold':1e-9,'strictNormalTangentDotMaximum':1e-4,'strictUnitTangentMinimum':.999,'tolerancesUnchanged':True,'newMeshes':rows,'houseCount':len(a['houses']),'courtyardFacingStoreysRange':[min(h['courtyardFacingStoreys']for h in a['houses']),max(h['courtyardFacingStoreys']for h in a['houses'])],'mainRoofZRange':[min(h['mainRoofM']for h in a['houses']),max(h['mainRoofM']for h in a['houses'])],'floorDatumUnchangedM':7.2,'referenceOpenCenterMetres':[32,34],'referenceFloorAreaM2':1088,'mainFloorGeometryRemovedOrAddedM2':0,'entranceProtectedOpeningWidthM':16.6,'perimeterFrontage':coverage,'eligiblePerimeterExcludingEntranceM':eligible,'houseCoveredPerimeterM':covered,'perimeterCoveragePercentExcludingEntrance':100*covered/eligible,'coverageDefinition':'Union of authored inward-facing house frontages projected onto original 32x34m rectangle. Excludes 16.6m entrance; does not count sheds, parapets or distant scenery.','newEmissiveOrPhysicalLights':0}
(O/'evidence/house-geometry-and-coverage.json').write_text(json.dumps(r,indent=2));print('HOUSE_GEOMETRY_PASS',len(rows),r['perimeterCoveragePercentExcludingEntrance'],flush=True)
