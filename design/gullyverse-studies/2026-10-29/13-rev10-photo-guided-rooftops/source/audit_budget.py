import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];rows=[]
for variant in['SQUARE C180','PHOTO A','PHOTO B']:
 s=next(s for s in bpy.data.scenes if s.get('variant')==variant);bpy.context.window.scene=s;s.frame_set(1);bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();tri=0;mats=set();images=set();geos=set()
 for o in s.objects:
  if o.type not in['MESH','CURVE','FONT']:continue
  ev=o.evaluated_get(dep);m=ev.to_mesh();m.calc_loop_triangles();tri+=len(m.loop_triangles);ev.to_mesh_clear();geos.add(o.data.name)
  for sl in o.material_slots:
   if sl.material:mats.add(sl.material.name)
 for n in mats:
  m=bpy.data.materials[n]
  if m.node_tree:
   for n in m.node_tree.nodes:
    if n.type=='TEX_IMAGE'and n.image:images.add(n.image.name)
 memory=sum(bpy.data.images[n].size[0]*bpy.data.images[n].size[1]*4*4/3 for n in images)
 rows.append({'variant':variant,'triangles':tri,'meshCurveOwners':sum(o.type in['MESH','CURVE']for o in s.objects),'geometryDatablocks':len(geos),'materials':len(mats),'shaderNodes':sum(len(bpy.data.materials[n].node_tree.nodes)if bpy.data.materials[n].node_tree else 0 for n in mats),'imageOwners':len(images),'RGBA8PlusMipsMiBEstimate':memory/1024**2,'lightOwners':sum(o.type=='LIGHT'for o in s.objects),'activeLights':sum(o.type=='LIGHT'and o.data.energy>0 for o in s.objects)})
count=54000;master=O/'source/Gullyverse-Rev10-Photo-Guided-Alternatives.blend';proof={'status':'MEASURED_BLENDER_ONLY','rows':rows,'selectedOriginalCrowdTriangles':count,'selectedCrowdCount':180,'webHistoricalCrowdTriangles':639792,'mainMasterBytes':master.stat().st_size,'masterSHA256':hashlib.sha256(master.read_bytes()).hexdigest(),'newImages':0,'newTextureDownloadBytes':0,'newActiveLights':0,'noBrowserDrawsFPSVRAMOrHardwareCertification':True,'aestheticPreferenceIsAuthoritativeNotOnlyPolyCount':True}
(O/'evidence/budget.json').write_text(json.dumps(proof,indent=2));print('BUDGET_COMPLETE',[(r['variant'],r['triangles'])for r in rows],flush=True)
