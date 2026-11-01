SPECS=[
('01-approach',(0,9,8.67),(0,40,10),23),
('02-screen-wide',(0,23,8.92),(0,44,10.8),22),
('03-crowd-eye',(0,36.5,8.92),(0,46,10.7),25),
('04-left-diagonal',(-12,23.5,8.92),(6,43,10.0),22),
('05-right-diagonal',(12,23.5,8.92),(-6,43,10.0),22),
('06-reverse',(0,42.5,10.5),(0,17,9.2),18),
('07-team',(8.8,26.2,8.92),(14.8,28.6,8.95),24),
('08-events',(-8.8,26.2,8.92),(-14.8,28.6,8.95),24),
('09-perimeter',(-13,44.5,8.92),(15,37,9.8),21),
('10-roof-elevated',(32,-4,31),(0,31,6.9),27),
('11-top-plan',(0,31,75),(0,31,0),34),
('12-cross-section',(-45,31,11.5),(0,31,5.8),33),
('13-rear-terrace',(1.5,44.5,8.92),(12,49,10.2),24),
('14-return-art',(-11,20.7,8.92),(-11.5,14.3,7.95),34),
('15-mobile-approach',(0,12,8.82),(0,42,10.4),16),
('16-mobile-crowd',(0,24.7,8.92),(0,43.5,10.3),18),
('17-furniture-A',(8.8,40.5,10.5),(10.2,46.2,7.7),25),
('18-furniture-B',(-8.8,40.5,10.5),(-10.2,46.2,7.7),25),
('19-lane-lock',(0,-21,7.72),(0,10,10),25)]
def add(sc):
 import bpy
 from mathutils import Vector
 for name,loc,target,lens in SPECS:
  key='TERRACE CAMERA / '+name;d=bpy.data.cameras.get(key)or bpy.data.cameras.new(key);d.lens=lens;d.sensor_width=36;d.clip_start=.06;d.clip_end=300
  if 'top-plan'in name:d.type='ORTHO';d.ortho_scale=56
  if 'cross-section'in name:d.type='ORTHO';d.ortho_scale=49
  o=bpy.data.objects.get(key)or bpy.data.objects.new(key,d)
  if o.name not in sc.objects:sc.collection.objects.link(o)
  o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
