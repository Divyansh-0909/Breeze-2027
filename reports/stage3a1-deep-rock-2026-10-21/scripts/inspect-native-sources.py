"""Read-only native-source inspection. Not browser acceptance evidence."""
from pathlib import Path
import bpy, json, numpy as np, math
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path.cwd();R=ROOT/'reports/stage3a1-deep-rock-2026-10-21/raw'
files=[('coastal_cliff_01',ROOT/'assets-source/gullyverse/quarry-scanned-composition/licensed-source/coastal_cliff_01/coastal_cliff_01_2k.blend'),('coastal_cliff_04',ROOT/'assets-source/gullyverse/quarry-fidelity-correction/licensed-source/coastal_cliff_04/coastal_cliff_04_1k.blend')]
rows=[]
for name,p in files:
 with bpy.data.libraries.load(str(p),link=False) as(a,b):b.objects=[name+'_LOD2']
 o=b.objects[0];v=np.array([list(o.matrix_world@x.co)for x in o.data.vertices]);f=[list(x.vertices)for x in o.data.polygons]
 bv=BVHTree.FromPolygons([Vector(x)for x in v],f,all_triangles=True)
 lo=v.min(0);hi=v.max(0);xs=np.linspace(lo[0]+.3,hi[0]-.3,1100);zs=np.linspace(.25,hi[2]-.3,180)
 image=np.zeros((len(zs),len(xs),4));depth=np.full((len(zs),len(xs)),np.nan);normals=np.zeros((len(zs),len(xs),3))
 light=Vector((-.4,-1,.8)).normalized()
 for j,z in enumerate(zs):
  for i,x in enumerate(xs):
   hit,n,_,_=bv.ray_cast(Vector((x,lo[1]-2,z)),Vector((0,1,0)),float(hi[1]-lo[1]+4))
   if hit is None:continue
   depth[j,i]=hit.y;normals[j,i]=n
   value=.22+.78*max(0,n.dot(light));image[j,i]=[value*.88,value*.90,value*.94,1]
 im=bpy.data.images.new(name+'_NATIVE_NEUTRAL_AUTHOR_INSPECTION',width=len(xs),height=len(zs));im.pixels.foreach_set(image.astype(np.float32).ravel());im.filepath_raw=str(R/(name+'-native-author-inspection.png'));im.file_format='PNG';im.save()
 np.savez_compressed(str(R/(name+'-native-surface-analysis.npz')),xs=xs,zs=zs,depth=depth,normals=normals)
 crops=[]
 for x in np.arange(math.ceil(lo[0]+2),hi[0]-10,4):
  for z in [1.,2.,3.]:
   m=(xs>=x)&(xs<=x+7);h=(zs>=z)&(zs<=z+3.2);d=depth[np.ix_(h,m)]
   if np.isfinite(d).mean()<.99:continue
   xx,zz=np.meshgrid(xs[m],zs[h]);A=np.c_[xx.ravel(),zz.ravel(),np.ones(d.size)];q=np.isfinite(d.ravel());coef=np.linalg.lstsq(A[q],d.ravel()[q],rcond=None)[0];res=d.ravel()[q]-A[q]@coef
   crops.append({'sourceX':[float(x),float(x+7)],'sourceZ':[z,z+3.2],'depthAfterRigidPlaneFitP01P50P99M':np.quantile(res,[.01,.5,.99]).tolist(),'depthRangeM':float(np.ptp(res)),'planeSlopes':coef.tolist()})
 crops.sort(key=lambda c:c['depthRangeM'],reverse=True)
 rows.append({'asset':name,'path':str(p.relative_to(ROOT)),'dimensionsM':(hi-lo).tolist(),'bounds':[lo.tolist(),hi.tolist()],'matrix':[[float(x)for x in row]for row in o.matrix_world],'triangles':len(f),'strongCrops':crops[:20]})
(R/'native-source-inspection.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows),flush=True)
