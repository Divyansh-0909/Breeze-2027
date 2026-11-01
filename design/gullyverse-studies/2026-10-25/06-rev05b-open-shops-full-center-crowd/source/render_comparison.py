import bpy,json,sys,time,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'source'))
from diagnostic_cameras import add_cameras,POSES
add_cameras();args=sys.argv[sys.argv.index('--')+1:];edition=args[0];assert edition in ['before','after','preview']
variants=['C']if edition=='preview'else['C','A','B']
poses=['21-shop-left-25','31-shop-inside-1','41-shop-section-1','16-rooftop-plan','08-crowd-middle','48-board-foreground']if edition=='preview'else POSES
if '--shops-only'in args:poses=[p for p in poses if 'shop'in p]
if '--crowd-only'in args:poses=[p for p in poses if 'shop'not in p]
mode='shops'if'--shops-only'in args else'crowd'if'--crowd-only'in args else'all'
manifest=O/f'evidence/render-manifest-{edition}-{mode}.json';rows=json.loads(manifest.read_text())if manifest.exists()else[];master=Path(bpy.data.filepath);sha=hashlib.sha256(master.read_bytes()).hexdigest()
for v in variants:
    scene=next(s for s in bpy.data.scenes if s.name.startswith(v+' /'));bpy.context.window.scene=scene;scene.frame_set(1);bpy.context.view_layer.update()
    for name in poses:
        target=O/'renders'/edition/v/(name+'.png');target.parent.mkdir(parents=True,exist_ok=True)
        if target.exists():continue
        cam=bpy.data.objects[name];scene.camera=cam;mobile='mobile'in name;scene.render.resolution_x=540 if mobile else 1200;scene.render.resolution_y=960 if mobile else 750;scene.render.resolution_percentage=100
        scene.render.engine='BLENDER_EEVEE_NEXT';scene.eevee.taa_render_samples=16;scene.render.filepath=str(target);start=time.time();bpy.ops.render.render(write_still=True,scene=scene.name)
        row={'edition':edition,'variant':v,'camera':name,'file':str(target.relative_to(O)),'position':list(cam.location),'rotationEuler':list(cam.rotation_euler),'lens':cam.data.lens,'sensorWidthMM':cam.data.sensor_width,'cameraType':cam.data.type,'orthoScale':cam.data.ortho_scale,'clipStart':cam.data.clip_start,'clipEnd':cam.data.clip_end,'width':scene.render.resolution_x,'height':scene.render.resolution_y,'samples':16,'engine':scene.render.engine,'viewTransform':scene.view_settings.view_transform,'look':scene.view_settings.look,'exposure':scene.view_settings.exposure,'seconds':time.time()-start,'masterSHA256':sha,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'diagnostic':'Camera near-plane cutaway at local +2.7m, same before/after; no mesh hidden.'if'section'in name else'Inside inspection camera, outside public lane.'if'inside'in name else'Elevated diagnostic camera.'if name in ['16-rooftop-plan','19-hub-wide','46-left-spillover','47-right-spillover']else'Actual Blender concept camera.','scope':'Blender EEVEE software-rendered concept, not browser/device performance.'};rows.append(row);manifest.write_text(json.dumps(rows,indent=2)+'\n');print('SAVED',edition,v,name,flush=True)
print('CAPTURES_COMPLETE',edition,len(variants)*len(poses),flush=True)
