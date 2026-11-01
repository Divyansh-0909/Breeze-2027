import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];stats=[]
for scene in sorted(bpy.data.scenes,key=lambda s:s.name):
 bpy.context.window.scene=scene;scene.frame_set(1);bpy.context.view_layer.update();deps=bpy.context.evaluated_depsgraph_get();tri=0;vertex=0;materials=set();meshObjects=0
 for o in scene.objects:
  if o.type not in ['MESH','CURVE','FONT']:continue
  if o.name.startswith('Bounded lane haze'):continue
  ev=o.evaluated_get(deps);m=ev.to_mesh()
  if m:
   m.calc_loop_triangles();tri+=len(m.loop_triangles);vertex+=len(m.vertices);meshObjects+=1;materials.update(mat.name for mat in m.materials if mat)
  ev.to_mesh_clear()
 stats.append({'variant':scene['variant'],'scene':scene.name,'evaluatedMeshAndCurveTriangles':tri,'evaluatedVertices':vertex,'meshAndConvertedCurveObjects':meshObjects,'materialDatablocks':len(materials),'localLights':sum(o.type=='LIGHT'for o in scene.objects),'hazeVolumes':1,'crowd':'Neutral low-poly stand-ins; shared base plus variant secondary extras.','renderEngine':scene.render.engine,'previewSamples':scene.eevee.taa_render_samples})
images=[{'name':i.name,'width':i.size[0],'height':i.size[1],'packed':bool(i.packed_file),'decodedRGBA8Bytes':i.size[0]*i.size[1]*4,'mipRGBA8Estimate':i.size[0]*i.size[1]*4*4/3}for i in bpy.data.images if i.type=='IMAGE']
assert all(i['packed']for i in images)
master=O/'source/Gullyverse-Straight-Walk-Semicircular-Crowd.blend';result={'scenes':stats,'uniqueImages':images,'imageCount':len(images),'estimatedUniqueImageRGBA8MipMiB':sum(i['mipRGBA8Estimate']for i in images)/2**20,'masterBytes':master.stat().st_size,'masterSHA256':hashlib.file_digest(master.open('rb'),'sha256').hexdigest(),'allImagesPacked':True,'noExternalFontDatablock':all(f.filepath=='<builtin>'or f.packed_file for f in bpy.data.fonts),'scope':'Offline authoring scene counts, not runtime draw calls or physical-device FPS. No web GLB export in this concept phase.'};(O/'evidence/scene-budget-final.json').write_text(json.dumps(result,indent=2));print('SCENE_AUDIT',len(stats),len(images),[(s['variant'],s['evaluatedMeshAndCurveTriangles'],s['localLights'])for s in stats],flush=True)
