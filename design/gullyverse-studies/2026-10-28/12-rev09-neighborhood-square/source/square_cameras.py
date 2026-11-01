SPECS=[
('01-plan',(0,31,90),(0,31,0),34,'ORTHO',91),
('02-entry-square',(0,14.4,8.92),(0,43,12.0),20,'PERSP',0),
('03-aerial',(35,-3,37),(0,32,9),25,'PERSP',0),
('04-front',(0,24,8.92),(0,46,12),22,'PERSP',0),
('05-back',(0,42.5,10.1),(0,16,11),18,'PERSP',0),
('06-left-diagonal',(-12,22.8,8.92),(7,40,12),20,'PERSP',0),
('07-right-diagonal',(12,22.8,8.92),(-7,40,12),20,'PERSP',0),
('08-left-house',(-8,34.8,10.2),(-17,36,12.6),24,'PERSP',0),
('09-right-house',(8,37,10.5),(17,38.3,15),23,'PERSP',0),
('10-team',(10.8,26,8.92),(15,29,10),24,'PERSP',0),
('11-events',(-10.8,26,8.92),(-15,29,10),24,'PERSP',0),
('12-elevation',(-50,31,13),(0,31,10),30,'ORTHO',67),
('13-return-left',(-11,20.7,8.92),(-11.5,14.3,7.95),34,'PERSP',0),
('14-return-right',(11,20.7,8.92),(11.5,14.3,7.95),34,'PERSP',0),
('15-mobile',(0,17,8.92),(0,43,12),15,'PERSP',0),
('16-mobile-lateral',(9,27,8.92),(-12,39,12),17,'PERSP',0),
('17-chaar',(0,-25,7.72),(3.8,-25,7.45),23,'PERSP',0),
('18-ritviz',(0,-16,7.72),(-3.8,-16,7.45),23,'PERSP',0),
('19-neha',(0,2,8.32),(3.8,2,8.05),23,'PERSP',0)]
def add(s):
 import bpy
 from mathutils import Vector
 for name,loc,target,lens,kind,ortho in SPECS:
  key='REV09 CAMERA / '+name;d=bpy.data.cameras.get(key)or bpy.data.cameras.new(key);d.lens=lens;d.sensor_width=36;d.clip_start=.06;d.clip_end=300;d.type=kind
  if kind=='ORTHO':d.ortho_scale=ortho
  o=bpy.data.objects.get(key)or bpy.data.objects.new(key,d)
  if o.name not in s.objects:s.collection.objects.link(o)
  o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
