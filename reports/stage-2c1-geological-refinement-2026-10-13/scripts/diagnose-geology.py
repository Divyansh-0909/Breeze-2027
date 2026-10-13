import bpy,json,math,numpy as np
from pathlib import Path
from mathutils.bvhtree import BVHTree
ROOT=Path.cwd();out=ROOT/'reports/stage-2c1-geological-refinement-2026-10-13/raw'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets-source/gullyverse/quarry-rollout/quarry-limestone.blend'))
rows=[]
for rid in [22,23]:
 for level in range(3):
  o=bpy.data.objects[f'Quarry_Rock_{rid:02d}_LOD{level}'];m=o.data;m.calc_loop_triangles();p=np.array([v.co[:]for v in m.vertices]);f=np.array([t.vertices[:]for t in m.loop_triangles]);tri=p[f];norm=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);area=np.linalg.norm(norm,axis=1);norm/=np.maximum(area[:,None],1e-20)
  cn=np.array([m.corner_normals[t.loops[0]].vector[:]for t in m.loop_triangles]);dots=np.sum(norm*cn,axis=1)
  bvh=BVHTree.FromPolygons([v.co for v in m.vertices],[t.vertices[:]for t in m.loop_triangles],all_triangles=True); pairs=bvh.overlap(bvh);bad=[]
  for a,b in pairs:
   if a>=b or set(f[a])&set(f[b]):continue
   if np.linalg.norm(tri[a].mean(0)-tri[b].mean(0))<.03:continue
   bad.append([a,b])
  ys=p[:,2];visible=f[(tri[:,:,2].mean(1)>2)&(tri[:,:,0].mean(1)>-66)]
  row={'rock':rid,'LOD':level,'triangles':len(f),'normalFaceDotMin':float(dots.min()),'cornerNormalsOpposedToFirstFace':int((dots<0).sum()),'nonAdjacentBVHOverlapPairs':len(bad),'overlapExamples':bad[:20],'heightM':[float(ys.min()),float(ys.max())],'shadowEnabled':False};rows.append(row)
print(rows,flush=True)
(out/'baseline-geometry-diagnosis.json').write_text(json.dumps({'status':'INSPECTED','method':'Blender BVH non-adjacent triangle candidates; counts require distinguishing shared-edge/near-coplanar contact from actual penetrations; no cast/receive shadows in authored runtime. First-loop normal dot is orientation diagnostic, not a smooth-normal error count.', 'rows':rows},indent=2))
