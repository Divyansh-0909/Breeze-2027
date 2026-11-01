ARTISTS=[{'key':'chaar-diwari','label':'CHAAR DIWARI','side':1,'cy':-25,'z':7.43,'host':'Closed rolling shutter.001'}, {'key':'ritviz','label':'RITVIZ','side':-1,'cy':-16,'z':7.43,'host':'Closed rolling shutter'}, {'key':'neha-kakkar','label':'NEHA KAKKAR','side':1,'cy':2,'z':8.03,'host':'Closed rolling shutter.002'}]
def add_cameras():
 import bpy
 from mathutils import Vector
 rig=bpy.data.collections['04_SHARED_CAMERA_RIG'];spec=[]
 for a in ARTISTS:
  k,side,cy,z=a['key'],a['side'],a['cy'],a['z'];eye=z+.29
  spec.extend([(f'ART-{k}-front',(0,cy,eye),(side*3.73,cy,z),18),(f'ART-{k}-grazing',(side*1.55,cy-2.7,z+.25),(side*3.73,cy,z),32),(f'ART-{k}-context',(0,max(-27,cy-5),eye),(side*3.73,cy,z+.3),22),(f'ART-{k}-detail',(side*1.8,cy-.9,z+.4),(side*3.73,cy+.15,z+.25),50),(f'ART-{k}-mobile',(0,cy,eye),(side*3.73,cy,z),12)])
 spec.extend([('ART-wall-pier-left',(0,-24.1,7.72),(-4,-21.15,7.5),36),('ART-wall-pier-right',(0,-14.5,7.72),(4,-12.15,7.5),36),('ART-wall-return-left',(-11,21.3,8.92),(-11.5,14.3,7.75),40),('ART-wall-return-right',(11,21.3,8.92),(11.5,14.3,7.75),40),('ART-rooftop-back-context',(0,25,10.1),(0,14.3,8.0),20),('ART-lane-left-context',(0,-27,8.2),(-3,-20.8,8.3),23),('ART-lane-right-context',(0,-21.5,8.2),(3,-13.5,8.1),23)])
 for name,loc,target,lens in spec:
  if name in bpy.data.objects:continue
  d=bpy.data.cameras.new(name);d.lens=lens;d.sensor_width=36;d.clip_start=.08;d.clip_end=250
  ob=bpy.data.objects.new(name,d);rig.objects.link(ob);ob.location=loc;ob.rotation_euler=(Vector(target)-ob.location).to_track_quat('-Z','Y').to_euler()
 return [s[0]for s in spec]
