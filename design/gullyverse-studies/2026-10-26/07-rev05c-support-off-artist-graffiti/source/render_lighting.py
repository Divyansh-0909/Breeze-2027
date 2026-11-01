"""Matched Rev05B ON versus Rev05C OFF. No invented graffiti evidence."""
import bpy,json,time,hashlib,sys,shutil
from pathlib import Path
O=Path(__file__).resolve().parents[1]
OLD=Path('/workspace/gullyverse-world-concept/2026-10-25/06-rev05b-open-shops-full-center-crowd')
POSES=['21-shop-left-25','22-shop-left-7','23-shop-left2','24-shop-right-16','25-shop-right-7','31-shop-inside-1','01-landing','12-mobile-landing','19-hub-wide','08-crowd-middle']
source=json.loads((O/'source/baseline/rev05b-render-manifest.json').read_text())
rows=[]
for v in ['C','A','B']:
    scene=next(s for s in bpy.data.scenes if s.name.startswith(v+' /'))
    bpy.context.window.scene=scene;scene.frame_set(1);bpy.context.view_layer.update()
    assert all(o.data.energy==0 for o in scene.objects if o.type=='LIGHT' and o.name.startswith('Rev05B shop interior practical'))
    for name in POSES:
        before=next(r for r in source if r['edition']=='after' and r['variant']==v and r['camera']==name)
        assert before['masterSHA256']=='8fbfbfb1c69bd0daefb5690c935c8317ed3516ab0e1af07e8a9bd371747ec5ff'
        src=OLD/before['file']
        dest=O/f'renders/on/{v}/{name}.png';dest.parent.mkdir(parents=True,exist_ok=True)
        if src.exists():
            assert hashlib.sha256(src.read_bytes()).hexdigest()==before['sha256'];shutil.copyfile(src,dest)
        elif dest.exists():
            assert hashlib.sha256(dest.read_bytes()).hexdigest()==before['sha256']
        else:
            raise RuntimeError('Restore all image archives to reuse exact ON PNGs, or render the packed baseline using recorded camera/quality. Never substitute a different source.')
        record={**before,'edition':'on','file':str(dest.relative_to(O)),'provenance':'Exact existing Rev05B final PNG reused; source master/PNG hash verified.','optionalSupportWattsEach':45}
        rows.append(record)
        cam=bpy.data.objects[name];scene.camera=cam;mobile='mobile'in name
        scene.render.resolution_x=540 if mobile else 1200;scene.render.resolution_y=960 if mobile else 750;scene.render.resolution_percentage=100
        scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=16
        target=O/f'renders/off/{v}/{name}.png';target.parent.mkdir(parents=True,exist_ok=True);scene.render.filepath=str(target)
        start=time.monotonic();bpy.ops.render.render(write_still=True,scene=scene.name)
        after={'edition':'off','variant':v,'camera':name,'file':str(target.relative_to(O)),'position':list(cam.location),'rotationEuler':list(cam.rotation_euler),'lens':cam.data.lens,'sensorWidthMM':cam.data.sensor_width,'cameraType':cam.data.type,'orthoScale':cam.data.ortho_scale,'clipStart':cam.data.clip_start,'clipEnd':cam.data.clip_end,'width':scene.render.resolution_x,'height':scene.render.resolution_y,'samples':16,'engine':scene.render.engine,'viewTransform':scene.view_settings.view_transform,'look':scene.view_settings.look,'exposure':scene.view_settings.exposure,'seconds':time.monotonic()-start,'masterSHA256':hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'optionalSupportWattsEach':0,'provenance':'Fresh actual Blender EEVEE render. No generated image in evidence.'}
        for key in ['position','rotationEuler','lens','sensorWidthMM','cameraType','orthoScale','clipStart','clipEnd','width','height','samples','engine','viewTransform','look','exposure']:
            assert before[key]==after[key],(name,key,before[key],after[key])
        rows.append(after);(O/'evidence/render-manifest.json').write_text(json.dumps(rows,indent=2)+'\n')
        print('MATCHED_PAIR',v,name,round(after['seconds'],2),flush=True)
print('ALL_LIGHTING_COMPARISONS_COMPLETE',len(rows),flush=True)
