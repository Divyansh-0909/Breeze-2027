import bpy,json,math,re,hashlib
from pathlib import Path
from mathutils import Vector,Matrix
O=Path(__file__).resolve().parents[1]
OLD=Path(bpy.data.filepath)
assert OLD.is_file() and hashlib.sha256(OLD.read_bytes()).hexdigest()=='8d3d143a629f62aa49b70125c659090643a3046e17bff1e32910514b503943f8', 'Load the preserved revision-03 baseline before authoring.'
def floor(y):return 6+1.2*min(1,max(0,(y+10)/24))
groups={}
for o in bpy.data.objects:
    match=re.match(r'^(Audience \d{2}_\d{2}|Festival extra \d+|Balanced extra \d+) ',o.name)
    if match:groups.setdefault(match[1],[]).append(o)
assert len(groups)==60
formations=[]
def place(label,x,y,theta,role,radius):
    active=next(s for s in bpy.data.scenes if s.name.startswith(('B' if label.startswith('Festival extra ') else 'C')+' /'))
    bpy.context.window.scene=active;active.frame_set(1);bpy.context.view_layer.update()
    objects=groups[label];shirt=next(o for o in objects if o.name.endswith(' shirt'))
    old=Vector((shirt.location.x,shirt.location.y,7.2));new=Vector((x,y,7.2))
    transform=Matrix.Translation(new)@Matrix.Rotation(theta,4,'Z')@Matrix.Translation(-old)
    for o in objects:
        assert o.parent is None
        o.matrix_basis=transform@o.matrix_basis
        o.update_tag(refresh={'OBJECT'})
    formations.append({'label':label,'role':role,'oldFoot':list(old),'foot':list(new),'radiusM':radius,'angleDeg':math.degrees(theta),'forwardXY':[-math.sin(theta),math.cos(theta)],'targetScreenCenter':[0,45.8]})
for index,label in enumerate(sorted(k for k in groups if k.startswith('Audience '))):
    tier,slot=divmod(index,16);r=[7.8,10.2,12.6][tier]
    side=-1 if slot<8 else 1;j=slot%8
    gap=math.asin(2.0/r);angle=side*(gap+(math.radians(85)-gap)*j/7)
    place(label,r*math.sin(angle),45.8-r*math.cos(angle),angle,'shared semicircular tier '+str(tier+1),r)
for prefix,angles,r in [('Festival extra ',[-70,-52,-34,-16,16,34,52,70],14.0),('Balanced extra ',[-60,-26,26,60],11.4)]:
    for i,degrees in enumerate(angles):
        theta=math.radians(degrees);place(prefix+str(i),r*math.sin(theta),45.8-r*math.cos(theta),theta,'variant supplementary arc',r)
renames={'07-cutscene-begin':'07-crowd-approach','08-cutscene-mid':'08-crowd-middle','09-screen-reveal':'09-screen-front','13-CROWD-MOVE-20s':'13-CONTINUOUS-STRAIGHT-WALK'}
for previous,current in renames.items():
    obj=bpy.data.objects[previous];obj.name=current;obj.data.name=current
rig=bpy.data.collections['04_SHARED_CAMERA_RIG']
def forward_camera(name,y,lens=None):
    camera=bpy.data.objects[name];camera.location=(0,y,floor(y)+1.72)
    camera.rotation_euler=Vector((0,20,.6)).to_track_quat('-Z','Y').to_euler()
    if lens is not None:camera.data.lens=lens
for name,y in [('01-landing',-27),('02-lane-walk',-11),('03-opening',12),('04-hub',23),('07-crowd-approach',25.2),('08-crowd-middle',30.7),('09-screen-front',36.5),('12-mobile-landing',-27)]:
    forward_camera(name,y)
walk=bpy.data.objects['13-CONTINUOUS-STRAIGHT-WALK']
oldaction=walk.animation_data.action if walk.animation_data else None
walk.animation_data_clear()
if oldaction and oldaction.users==0:bpy.data.actions.remove(oldaction)
walk.data.lens=30;walk.rotation_euler=Vector((0,20,.6)).to_track_quat('-Z','Y').to_euler()
keys=[]
for y in [-27,-10,14,36.5]:
    frame=1+(y+27)/63.5*959;walk.location=(0,y,floor(y)+1.72)
    walk.keyframe_insert('location',frame=frame);walk.keyframe_insert('rotation_euler',frame=frame)
    keys.append({'frame':frame,'position':list(walk.location),'eyeHeightM':1.72})
walk.animation_data.action.name='Continuous straight walk / no reveal section'
for curve in walk.animation_data.action.fcurves:
    for point in curve.keyframe_points:point.interpolation='LINEAR'
for name,position,target,lens,ortho in [
    ('15-semicircle-high',(0,27,19.5),(0,39.5,7.9),24,None),
    ('16-rooftop-plan',(0,32,55),(0,32,0),35,48)]:
    data=bpy.data.cameras.new(name);data.lens=lens;data.clip_start=.08;data.clip_end=250
    cam=bpy.data.objects.new(name,data);rig.objects.link(cam);cam.location=position
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    if ortho:data.type='ORTHO';data.ortho_scale=ortho
for scene in bpy.data.scenes:
    scene.frame_start=1;scene.frame_end=960;scene.render.fps=24;scene.frame_set(1)
    scene.camera=walk
    bpy.context.window.scene=scene;bpy.context.view_layer.update()
bpy.context.view_layer.update()
guide=json.loads((O/'source/camera-guide.json').read_text())
guide['rig']=[{'id':o.name,'position':list(o.location),'rotationEuler':list(o.rotation_euler),'lensMM':o.data.lens,'sensorWidthMM':o.data.sensor_width,'type':o.data.type,'orthoScale':o.data.ortho_scale,'cameraToWorld':[list(r)for r in o.matrix_world]} for o in sorted(rig.objects,key=lambda o:o.name)]
guide.pop('crowdMove',None)
guide['straightWalk']={'camera':walk.name,'frames':[1,960],'fps':24,'durationSeconds':40,'keys':keys,'route':[[0,-27],[0,-10],[0,14],[0,22],[0,36.5]],'noLateralDetour':True,'noSeparateRevealSection':True,'eyeHeightM':1.72,'viewDirection':[0,20,.6],'pitchConstant':True,'note':'Only Z follows the existing gentle ramp. No screen-reveal lift, side turn, teleport or loading cut.'}
(O/'source/camera-guide.json').write_text(json.dumps(guide,indent=2)+'\n')
(O/'evidence/crowd-composition.json').write_text(json.dumps({'status':'AUTHORED','screenCenter':[0,45.8],'sharedPeople':48,'sharedRadiiM':[7.8,10.2,12.6],'arcHalfAngleDegrees':85,'centralFootCenterGapM':4.0,'semicircle':'Front semicircular fan, ends stop 5 degrees short of the screen plane for grazing-view clearance. No audience is placed behind the screen.','people':formations},indent=2)+'\n')
bpy.context.preferences.filepaths.save_version=0
master=O/'source/Gullyverse-Straight-Walk-Semicircular-Crowd.blend'
bpy.ops.wm.save_as_mainfile(filepath=str(master),compress=True)
(O/'evidence/authoring-change.json').write_text(json.dumps({'status':'AUTHORED','previousMaster':str(OLD),'previousMasterSHA256':hashlib.sha256(OLD.read_bytes()).hexdigest(),'masterSHA256':hashlib.sha256(master.read_bytes()).hexdigest(),'renamedCameras':renames,'peopleRepositioned':len(formations),'crowdGeometryReused':True,'noNewGeometryOrTextures':True,'centeredNavigationBoardRetained':True,'noRevealColumn':True,'originalLightsAndLayoutRetained':True},indent=2)+'\n')
print('STRAIGHT_WALK_AND_SEMICIRCLE_SAVED',len(formations),flush=True)
