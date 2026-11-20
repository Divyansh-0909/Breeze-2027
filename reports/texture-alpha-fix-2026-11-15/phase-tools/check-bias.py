import bpy,json,numpy as np
from pathlib import Path
r=Path('/dev/shm/texture-alpha-fix-2026-11-15');rows=[]
for folder in [Path('/dev/shm/Breeze-2027-runtime/public/models/gullyverse/locked-rev15z-clean-v2'),r/'scratch/bias-check']:
 with (folder/'irradiance.raw.pfm').open('rb')as f:
  f.readline();w,h=map(int,f.readline().split());f.readline();a=np.frombuffer(f.read(),dtype='<f4').reshape(h,w,3)
 with bpy.data.libraries.load(str(folder/'contact-frontage-baked.blend'))as(x,y):y.collections=['Runtime / contact-frontage']
 samples=[]
 for o in y.collections[0].objects:
  if 'Rooftop slab'not in o['runtimeOriginalSource']:continue
  for p in o.data.polygons:
   if p.normal.z<.5:continue
   uv=np.mean([o.data.uv_layers['RuntimeIrradianceUV'].data[i].uv[:]for i in p.loop_indices],axis=0);samples.append({'normalZ':p.normal.z,'area':p.area,'rgb':a[min(int(uv[1]*h),h-1),min(int(uv[0]*w),w-1)].tolist()})
 weight=np.array([x['area']for x in samples]);vals=np.array([x['rgb']for x in samples]);mean=(vals*weight[:,None]).sum(0)/weight.sum();rows.append({'folder':str(folder),'topFloorFaces':len(samples),'meanIrradiance':mean.tolist()})
(r/'evidence/bias-diagnostic.json').write_text(json.dumps(rows,indent=2)+'\n');print(json.dumps(rows))
