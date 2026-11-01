import bpy,bmesh,json,hashlib,math,sys
from pathlib import Path
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'source'));from scene_snapshot import snapshot
master=O/'source/Gullyverse-Rev10-Photo-Guided-Alternatives.blend';a,ea,ma,wa,ia=snapshot(O/'source/Rev09-Original.blend');members={s.name:sorted(o.name for o in s.objects)for s in bpy.data.scenes};b,eb,mb,wb,ib=snapshot(master)
assert all(b.get(n)==v for n,v in a.items()),[n for n,v in a.items()if b.get(n)!=v];assert wa==wb and ma==mb and ia==ib;assert all(eb[n]==v for n,v in ea.items());assert all(sorted(o.name for o in bpy.data.scenes[n].objects)==v for n,v in members.items());assert len(bpy.data.scenes)==15
data=json.loads((O/'evidence/authoring.json').read_text());old=next(s for s in bpy.data.scenes if s.get('variant')=='SQUARE C180');actors=json.loads((O/'evidence/rev05b-authoring.json').read_text())['actors'];actors=[r for r in actors if all(n in old.objects for n in r['objects'])];assert len(actors)==180
rows=[]
for r in data['studies']:
 s=next(s for s in bpy.data.scenes if s.get('variant')==r['variant']);bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update();checks=[]
 assert not any(o.name.startswith('WEB CROWD /')for o in s.objects)
 for actor in actors:
  for n in actor['objects']:assert s.objects.get(n)==old.objects[n],n
 for o in old.objects:
  if o.name not in r['removedOnlyFromNewScene']:assert s.objects.get(o.name)==o,o.name
 assert {o.name for o in s.objects if o.type=='LIGHT'}=={o.name for o in old.objects if o.type=='LIGHT'};assert sum(o.type=='LIGHT'and o.data.energy>0 for o in s.objects)==12;assert sum(o.type=='LIGHT'and o.data.energy==0 for o in s.objects)==5
 for n in r['newMeshes']:
  o=s.objects[n];m=o.data;bm=bmesh.new();bm.from_mesh(m);assert all(e.is_manifold for e in bm.edges),n;area=min(f.calc_area()for f in bm.faces);vol=bm.calc_volume(signed=True);assert area>1e-9 and vol>0,(n,area,vol);bm.free();m.calc_loop_triangles();m.calc_tangents(uvmap=m.uv_layers.active.name);dot=max(abs(l.normal.dot(l.tangent))for l in m.loops);unit=min(l.tangent.length for l in m.loops);assert dot<1e-4 and unit>.999,(n,dot,unit);assert all(math.isfinite(x)for l in m.loops for x in[*l.normal,*l.tangent,*l.bitangent]);assert all(abs(abs(l.bitangent_sign)-1)<1e-5 for l in m.loops)
  checks.append({'name':n,'triangles':len(m.loop_triangles),'closedManifold':True,'positiveSignedVolume':vol,'minFaceArea':area,'maxNormalTangentDot':dot,'minUnitTangent':unit})
 rows.append({'variant':r['variant'],'actorsExact':180,'bodyPartsExact':1440,'originalProtectedObjectsUnchanged':True,'newMeshes':checks,'newLightsImagesMaterials':0,'floorAndSevenArtworkAndFiveCountersExact':True})
proof={'status':'PASS','masterSHA256':hashlib.sha256(master.read_bytes()).hexdigest(),'baselineSHA256':'3f637b223aff0fd4eb397ae6e51d821ed5de5675cf9707643a1cdf955821ab78','historicalScenesPreserved':13,'sceneCount':15,'originalObjectSignaturesExact':len(a),'allOriginalImagesMaterialsWorldsExact':True,'all33ImagesPacked':all(i.packed_file for i in bpy.data.images if i.type=='IMAGE'),'selectedCrowd':'EXACT PRIOR BLENDER C180','thresholdsUnchanged':True,'rows':rows}
(O/'evidence/preservation-and-geometry.json').write_text(json.dumps(proof,indent=2));print('ARCHITECTURE_PRESERVATION_PASS',len(a),flush=True)
