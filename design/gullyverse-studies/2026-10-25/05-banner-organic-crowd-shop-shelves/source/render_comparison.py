import bpy,json,sys,time,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];master_sha=hashlib.sha256(Path(bpy.data.filepath).read_bytes()).hexdigest();sys.path.insert(0,str(O/'source'))
from diagnostic_cameras import add_cameras,POSES
args=sys.argv[sys.argv.index('--')+1:];edition=args[0]
assert edition in ['before','after','preview']
main_only='--main-only'in args
add_cameras()
jobs=[('C','15-semicircle-high')]if edition=='preview'else[(v,n)for v in ['C','A','B']for n in POSES]
if main_only:jobs=[(v,n)for v,n in jobs if n not in [r[0]for r in __import__('diagnostic_cameras').SHOP_SPECS]]
manifest=O/'evidence/render-manifest.json';rows=json.loads(manifest.read_text())if manifest.exists()else[]
for variant,name in jobs:
    target=O/'renders'/edition/variant/(name+'.png');target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists():continue
    scene=next(s for s in bpy.data.scenes if s.name.startswith(variant+' /'));bpy.context.window.scene=scene;scene.frame_set(1);scene.camera=bpy.data.objects[name]
    scene.render.engine='BLENDER_EEVEE_NEXT';scene.render.resolution_percentage=100
    mobile='mobile'in name;scene.render.resolution_x=540 if mobile else 1200;scene.render.resolution_y=960 if mobile else 750
    scene.eevee.taa_render_samples=16;scene.render.filepath=str(target);start=time.time()
    bpy.ops.render.render(write_still=True,scene=scene.name)
    row={'edition':edition,'variant':variant,'camera':name,'file':str(target.relative_to(O)),'position':list(scene.camera.location),'rotationEuler':list(scene.camera.rotation_euler),'lens':scene.camera.data.lens,'sensorWidthMM':scene.camera.data.sensor_width,'cameraType':scene.camera.data.type,'width':scene.render.resolution_x,'height':scene.render.resolution_y,'samples':16,'engine':scene.render.engine,'exposure':scene.view_settings.exposure,'seconds':time.time()-start,'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'masterSHA256':master_sha,'shelfStatus':'pending_user_exception'if'Intermediate'in bpy.data.filepath else'candidate','scope':'Actual Blender software-rendered concept evidence, not browser/device performance.'}
    rows.append(row);manifest.write_text(json.dumps(rows,indent=2)+'\n');print('SAVED',edition,variant,name,flush=True)
print('CAPTURES_COMPLETE',edition,len(jobs),flush=True)
