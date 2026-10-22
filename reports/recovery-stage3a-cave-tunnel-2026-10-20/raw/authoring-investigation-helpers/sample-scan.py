import bpy,json,numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from pathlib import Path
R=Path('/workspace/Breeze-2027-navigation');src=R/'assets-source/gullyverse/quarry-scanned-composition/licensed-source/coastal_cliff_01/coastal_cliff_01_2k.blend';bpy.ops.wm.open_mainfile(filepath=str(src));o=bpy.data.objects['coastal_cliff_01_LOD2'];bv=BVHTree.FromObject(o,bpy.context.evaluated_depsgraph_get());x=np.linspace(-40,40,321);z=np.linspace(.1,8.7,87);a=[];missing=0
for h in z:
 row=[]
 for u in x:
  p,n,i,d=bv.ray_cast(Vector((u,-20,h)),Vector((0,1,0)),50)
  if p is None:row.append(None);missing+=1
  else:row.append(p.y)
 a.append(row)
Path('/workspace/recovery-stage3a/2026-10-20/scan-sample.json').write_text(json.dumps({'source':str(src),'x':x.tolist(),'z':z.tolist(),'depth':a}))
a=np.array(a,dtype=float);print('NATIVE_SCAN_DEPTH_QUANTILES',np.nanquantile(a,[0,.01,.1,.5,.9,.99,1]),'missing',missing,flush=True)
for lo,hi in [(-35,7),(-21,21),(-10,32),(-40,2)]:
 s=a[:,(x>=lo)&(x<=hi)];print('WINDOW',lo,hi,'missing',np.count_nonzero(np.isnan(s)),'range',np.nanmin(s),np.nanmax(s),'p',np.nanquantile(s,[.1,.5,.9]),flush=True)
