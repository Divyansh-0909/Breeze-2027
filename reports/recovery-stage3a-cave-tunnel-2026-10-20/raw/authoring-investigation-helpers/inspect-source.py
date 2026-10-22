import bpy,json,numpy as np
from pathlib import Path
root=Path('/workspace/Breeze-2027-navigation');rows=[]
for p in [root/'assets-source/gullyverse/quarry-fidelity-correction/licensed-source/coastal_cliff_04/coastal_cliff_04_1k.blend',root/'assets-source/gullyverse/quarry-scanned-composition/licensed-source/coastal_cliff_01/coastal_cliff_01_2k.blend']:
 bpy.ops.wm.open_mainfile(filepath=str(p))
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  xyz=np.array([o.matrix_world@v.co for v in o.data.vertices]);rows.append({'file':str(p.relative_to(root)),'name':o.name,'vertices':len(xyz),'polygons':len(o.data.polygons),'worldBounds':[xyz.min(0).tolist(),xyz.max(0).tolist()],'dimensions':np.ptp(xyz,axis=0).tolist(),'matrix':[list(r)for r in o.matrix_world]})
print('SOURCES',json.dumps(rows));(root/'reports/recovery-stage3a-cave-tunnel-2026-10-20/raw/source-inspection.json').write_text(json.dumps(rows,indent=2))
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(root/'public/models/gullyverse/quarry-foundation-refined/foundation-geometry.glb'))
rows=[]
for o in bpy.data.objects:
 if o.type=='MESH'and ('Terrain_2_2'in o.name or'Terrain_2_'in o.name):
  a=np.array([o.matrix_world@v.co for v in o.data.vertices]);a=a[:,[0,2,1]]*np.array([1,1,-1]);rows.append({'name':o.name,'vertices':len(a),'bounds':[a.min(0).tolist(),a.max(0).tolist()],'nearMouthVertices':int(((abs(a[:,0])<8)&(a[:,2]>-8)&(a[:,2]<8)).sum())})
print('TERRAIN',json.dumps(rows));(root/'reports/recovery-stage3a-cave-tunnel-2026-10-20/raw/terrain-inspection.json').write_text(json.dumps(rows,indent=2))
