"""Repair only Rev11 candidate vertices in double precision; original source actors untouched."""
import bpy,numpy as np,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];d=json.loads((O/'evidence/authoring.json').read_text())
for group in d['crowdVariants']:
 for actor in group['actors']:
  foot=actor['anchorZ'];factor=actor['heightOnlyFactor'];T=np.eye(4);T[2,2]=factor;T[2,3]=foot*(1-factor)
  for old,new in zip(actor['sourceObjects'],actor['objects']):
   p,q=bpy.data.objects[old],bpy.data.objects[new];prev=q.data
   q.location=p.location.copy();q.rotation_mode=p.rotation_mode;q.rotation_euler=p.rotation_euler.copy();q.scale=p.scale.copy()
   q.delta_location=p.delta_location.copy();q.delta_rotation_euler=p.delta_rotation_euler.copy();q.delta_scale=p.delta_scale.copy()
   if factor==1:q.data=p.data
   else:
    q.data=p.data.copy();W=np.array(p.matrix_basis,dtype=np.float64);M=np.linalg.inv(W)@T@W
    for va,vb in zip(p.data.vertices,q.data.vertices):vb.co=(M@np.array([*va.co,1.0]))[:3]
    q.data.update()
   if prev.users==0:bpy.data.meshes.remove(prev)
s=next(s for s in bpy.data.scenes if s.get('variant')=='REV11');bpy.context.window.scene=s;s.frame_set(1);bpy.context.preferences.filepaths.save_version=0;dest=O/'source/Gullyverse-Rev11-Connected-Neighborhood.blend';bpy.ops.wm.save_as_mainfile(filepath=str(dest),compress=True)
d['masterSHA256']=hashlib.sha256(dest.read_bytes()).hexdigest();d['masterBytes']=dest.stat().st_size;d['heightImplementation']='Double-precision world-Z vertex transform, original object transform/XY/UV/topology fixed';(O/'evidence/authoring.json').write_text(json.dumps(d,indent=2));print('HEIGHT_PRECISION_REPAIR',d['masterSHA256'],flush=True)
