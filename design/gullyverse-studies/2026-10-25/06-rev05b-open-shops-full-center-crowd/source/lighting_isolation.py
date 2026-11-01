"""Same final geometry, camera and renderer; switch only authorized shop light energies."""
import bpy,json,hashlib,time,sys
from pathlib import Path
O=Path(__file__).resolve().parents[1];scene=next(s for s in bpy.data.scenes if s.name.startswith('C /'));bpy.context.window.scene=scene;scene.frame_set(1)
lights=[x for x in bpy.data.objects if x.name.startswith('Rev05B shop interior practical')];assert len(lights)==5
rows=[]
for name in ['21-shop-left-25','31-shop-inside-1']:
    scene.camera=bpy.data.objects[name];scene.render.engine='BLENDER_EEVEE_NEXT';scene.render.resolution_x=1200;scene.render.resolution_y=750;scene.render.resolution_percentage=100;scene.eevee.taa_render_samples=16
    for state,watts in [('off',0),('on',45)]:
        for l in lights:l.data.energy=watts
        target=O/'renders/lighting-inspection/C'/f'{name}-{state}.png';target.parent.mkdir(parents=True,exist_ok=True);scene.render.filepath=str(target);start=time.time();bpy.ops.render.render(write_still=True,scene=scene.name)
        rows.append({'file':str(target.relative_to(O)),'camera':name,'position':list(scene.camera.location),'rotation':list(scene.camera.rotation_euler),'lens':scene.camera.data.lens,'width':1200,'height':750,'samples':16,'exposure':scene.view_settings.exposure,'geometrySHA256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'interiorLightWattsEach':watts,'interiorLights':5,'originalStreetAndWorldLightsUnchanged':True,'softwareStillRenderSeconds':time.time()-start,'sha256':hashlib.sha256(target.read_bytes()).hexdigest()});print('LIGHTING_ISOLATION',name,state,flush=True)
(O/'evidence/lighting-isolation.json').write_text(json.dumps({'scope':'Offline EEVEE software still costs; two warm same-process comparisons, not interactive frame-time/GPU proof. No asset saved with diagnostic light state.','captures':rows},indent=2)+'\n')
