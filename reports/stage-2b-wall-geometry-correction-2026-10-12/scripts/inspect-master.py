import bpy,bmesh,json,numpy as np
from pathlib import Path
from mathutils.bvhtree import BVHTree
r=Path('reports/stage-2b-wall-geometry-correction-2026-10-12');bpy.ops.wm.open_mainfile(filepath=str(Path.cwd()/'assets-source/gullyverse/first-wall-corrected/first-wall-corrected.blend'));metadata=json.loads(Path('public/models/gullyverse/first-wall-corrected/manifest.json').read_text());anchor=np.array(metadata['anchor']);R=np.array([metadata['uAxis'],metadata['vAxis'],metadata['normal']]).T
host=(np.array(metadata['hostVerticesWorld'])-anchor)@R;rows=[]
for name in ['Wall_Master','Wall_LOD0','Wall_LOD1','Wall_LOD2','Wall_Collision']:
 o=bpy.data.objects[name];bm=bmesh.new();bm.from_mesh(o.data);non=sum(not e.is_manifold for e in bm.edges);volume=bm.calc_volume(signed=True);bm.free();assert non==0 and volume>0
 bvh=BVHTree.FromPolygons([v.co for v in o.data.vertices],[list(p.vertices)for p in o.data.polygons]);protected=[]
 for a,b in metadata['protectedOuterEdges']:
  for t in np.linspace(0,1,17):
   p=host[a]*(1-t)+host[b]*t;point=(p[0],-p[2],p[1]);nearest=bvh.find_nearest(point)
   if nearest[0]is not None:protected.append(nearest[3])
 rows.append({'name':name,'nonManifoldEdges':non,'signedVolumeM3':volume,'scale':list(o.scale),'rotation':list(o.rotation_euler),'UVs':[v.name for v in o.data.uv_layers],'protectedOuterEdgeMaxSurfaceDeviationM':max(protected),'triangles':sum(len(p.vertices)-2 for p in o.data.polygons)})
print([(r['name'],r['protectedOuterEdgeMaxSurfaceDeviationM'])for r in rows])
# Exact locked material, separately reusable without including the old geometric master.
mat=bpy.data.materials['Approved_Cool_Grey_Limestone_Family'];bpy.data.libraries.write(str(Path.cwd()/'assets-source/gullyverse/first-wall-corrected/approved-limestone-material.blend'),{mat},compress=True)
(r/'raw/master-inspection.json').write_text(json.dumps({'blender':bpy.app.version_string,'metreScale':bpy.context.scene.unit_settings.scale_length,'objects':rows,'images':[{'name':i.name,'packed':bool(i.packed_file),'size':list(i.size),'colorspace':i.colorspace_settings.name}for i in bpy.data.images if i.source=='FILE']},indent=2))
