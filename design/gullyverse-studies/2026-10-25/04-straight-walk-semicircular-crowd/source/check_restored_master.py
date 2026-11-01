import bpy,json,sys,math
from pathlib import Path
args=sys.argv[sys.argv.index('--')+1:];out=Path(args[0]);O=Path(bpy.data.filepath).resolve().parents[1]
expected=json.loads((O/'evidence/scene-budget-final.json').read_text())['imageCount']
images=[i for i in bpy.data.images if i.type=='IMAGE']
assert len(bpy.data.scenes)==3 and len(images)==expected and all(i.packed_file for i in images)
assert not bpy.data.libraries
assert not any(o.name.startswith('Roof service room / reveal occluder')for o in bpy.data.objects)
assert '13-CROWD-MOVE-20s'not in bpy.data.objects and '09-screen-reveal'not in bpy.data.objects
cam=bpy.data.objects['13-CONTINUOUS-STRAIGHT-WALK'];scene=bpy.context.scene
def floor(y):return 6+1.2*min(1,max(0,(y+10)/24))
for frame in [1,300,620,960]:
    scene.frame_set(frame);bpy.context.view_layer.update();assert abs(cam.location.x)<1e-5 and abs(cam.location.z-floor(cam.location.y)-1.72)<.002
for person in json.loads((O/'evidence/crowd-composition.json').read_text())['people']:
    o=bpy.data.objects[person['label']+' shirt'];x,y,_=person['foot'];assert abs(o.location.x-x)<1e-4 and abs(o.location.y-y)<1e-4
scene.frame_set(1)
out.write_text(json.dumps({'status':'PASS','scenes':3,'packedImages':expected,'noLinkedBlendLibraries':True,'straightWalkAndEyeHeight':True,'semicircularActorPositions':True,'noRevealSectionOrColumn':True,'openedIndependentExtractedMaster':True},indent=2)+'\n')
print('RESTORED_MASTER_PASS',flush=True)
