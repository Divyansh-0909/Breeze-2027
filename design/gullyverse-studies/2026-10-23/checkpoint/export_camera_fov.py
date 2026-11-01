import bpy,math,json
from pathlib import Path
out=Path(__file__).resolve().parent/'CAMERA-FOV-AND-POSES.json';rows=[]
for scene in sorted(bpy.data.scenes,key=lambda s:s.name):
 bpy.context.window.scene=scene;scene.frame_set(1);bpy.context.view_layer.update()
 for cam in bpy.data.collections['04_SHARED_CAMERA_RIG'].objects:
  if cam.name.startswith('13-'):continue
  mobile='mobile'in cam.name;scene.render.resolution_x=540 if mobile else 1200;scene.render.resolution_y=960 if mobile else 750
  frame=cam.data.view_frame(scene=scene)
  row={'variant':scene['variant'],'camera':cam.name,'position':list(cam.location),'rotationEuler':list(cam.rotation_euler),'matrix':[list(v)for v in cam.matrix_world],'width':scene.render.resolution_x,'height':scene.render.resolution_y,'lensMM':cam.data.lens,'sensorWidthMM':cam.data.sensor_width,'sensorHeightMM':cam.data.sensor_height,'sensorFit':cam.data.sensor_fit,'projection':cam.data.type}
  if cam.data.type=='PERSP':row['horizontalFOVDegrees']=math.degrees(max(math.atan2(v.x,-v.z)for v in frame)-min(math.atan2(v.x,-v.z)for v in frame));row['verticalFOVDegrees']=math.degrees(max(math.atan2(v.y,-v.z)for v in frame)-min(math.atan2(v.y,-v.z)for v in frame))
  else:row['orthoWidthM']=max(v.x for v in frame)-min(v.x for v in frame);row['orthoHeightM']=max(v.y for v in frame)-min(v.y for v in frame)
  rows.append(row)
for name in {r['camera']for r in rows}:
 group=[{k:v for k,v in r.items()if k!='variant'}for r in rows if r['camera']==name];assert group[0]==group[1]==group[2]
out.write_text(json.dumps({'status':'PASS_IDENTICAL_ACTUAL_BLENDER_VIEW_FRAMES','masterSHA256':'cc8c52a0a3a4106a2c94a36ec2364778ce5b2d8db6ef1ebabfbb553f38e66056','source':'Native Camera.view_frame(scene=scene), with each actual desktop/mobile output aspect. No scene file saved or render altered.','rows':rows},indent=2));print('CAMERA_FOV_EXPORTED',len(rows))
