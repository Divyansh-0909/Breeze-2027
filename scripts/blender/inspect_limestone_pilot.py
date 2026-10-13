"""Read-only inspection of the authored master; writes diagnostic JSON only."""
import bpy,bmesh,json,numpy as np
from pathlib import Path
root=Path(__file__).resolve().parents[2]
bpy.ops.wm.open_mainfile(filepath=str(root/'assets-source/gullyverse/limestone-pilot/quarry-limestone-pilot.blend'))
rows=[];lo=bpy.data.objects['Rock_Collision'];mins=np.array([min(v.co[i] for v in lo.data.vertices) for i in range(3)]);maxs=np.array([max(v.co[i] for v in lo.data.vertices) for i in range(3)])
for o in bpy.data.objects:
 if o.type!='MESH':continue
 bm=bmesh.new();bm.from_mesh(o.data);volume=bm.calc_volume(signed=True);bm.free();verts=np.array([list(v.co) for v in o.data.vertices])
 rows.append({'name':o.name,'signedVolumeM3':volume,'UVLayers':len(o.data.uv_layers),'objectScale':list(o.scale),'objectRotation':list(o.rotation_euler),'proxyEnclosesRuntimeVertices':bool(np.all(verts>=mins-1e-6) and np.all(verts<=maxs+1e-6)) if o.name.startswith('Rock_LOD') else None})
# Bilinear deviation to the source sculpt in shared front UV domain, no caps/back included.
master=np.array([list(v.co) for v in bpy.data.objects['Rock_Master_Sculpt'].data.vertices])[:257*193].reshape(193,257,3);u,v=np.meshgrid(np.linspace(0,1,257),np.linspace(0,1,193));deviation=[]
for name,nx,nz in [('Rock_LOD0',144,108),('Rock_LOD1',80,60),('Rock_LOD2',40,30)]:
 grid=np.array([list(v.co) for v in bpy.data.objects[name].data.vertices])[:(nx+1)*(nz+1)].reshape(nz+1,nx+1,3);xx=u*nx;yy=v*nz;ix=np.minimum(np.floor(xx).astype(int),nx-1);iy=np.minimum(np.floor(yy).astype(int),nz-1);fx=(xx-ix)[...,None];fy=(yy-iy)[...,None];approx=(grid[iy,ix]*(1-fx)+grid[iy,ix+1]*fx)*(1-fy)+(grid[iy+1,ix]*(1-fx)+grid[iy+1,ix+1]*fx)*fy;error=np.linalg.norm(approx-master,axis=-1);deviation.append({'LOD':name,'UVBilinearRMSErrorM':float(np.sqrt(np.mean(error**2))),'p95ErrorM':float(np.quantile(error,.95)),'maxErrorM':float(error.max()),'method':'Shared front UV bilinear reconstruction versus master, not Hausdorff distance or screen-space error'})
result={'Blender':bpy.app.version_string,'metricScale':bpy.context.scene.unit_settings.scale_length,'objects':rows,'LODError':deviation,'images':[{'name':i.name,'packed':bool(i.packed_file),'size':list(i.size),'colorSpace':i.colorspace_settings.name} for i in bpy.data.images if i.source=='FILE']}
(root/'reports/limestone-rock-pilot-2026-10-12/raw/master-inspection.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))
