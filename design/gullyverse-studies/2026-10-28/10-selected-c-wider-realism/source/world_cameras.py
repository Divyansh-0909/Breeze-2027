SPECS=[
('01-lane-entry',(0,-27,7.72),(0,18,9.3),28),
('02-whole-street',(0,-21,7.72),(0,10,10),25),
('03-shop-group-right',(0,-21,7.72),(4,-14,8),24),
('04-shop-group-left',(0,-9,7.77),(-4,.2,8.5),23),
('05-open-shop-eye',(-.3,-7,7.87),(-5.8,-7,7.8),22),
('06-doorway-inspection',(4.45,-15.2,7.72),(7.9,-16.8,7.7),21),
('07-chaar-context',(0,-25,7.72),(3.8,-25,7.45),23),
('08-ritviz-context',(0,-16,7.72),(-3.8,-16,7.45),23),
('09-neha-context',(0,2,8.32),(3.8,2,8.05),23),
('10-lane-roof-transition',(0,8,8.62),(0,35,10),24),
('11-rooftop-wide',(0,23,8.92),(0,44,10.8),22),
('12-screen-crowd',(0,36.5,8.92),(0,46,10.7),25),
('13-team',(8.8,26.2,8.92),(14.8,28.6,8.95),30),
('14-events',(-8.8,26.2,8.92),(-14.8,28.6,8.95),30),
('15-return-left',(-11,20.7,8.92),(-11.5,14.3,7.95),34),
('16-return-right',(11,20.7,8.92),(11.5,14.3,7.95),34),
('17-rooftop-reverse',(0,30,10.1),(0,14.3,8.3),20),
('18-mobile-lane',(0,-21,7.72),(0,18,9.3),19),
('19-mobile-rooftop',(0,22,8.92),(0,42,10.4),18),
('20-stock-counter',(0,-7,7.87),(-3.8,-7,6.95),30),
('21-upper-facades',(0,-19,10.1),(0,-1,13.1),24),
('22-roof-background',(0,36.5,10),(11,47,14.3),25)]
def add(scene):
 import bpy
 from mathutils import Vector
 for name,loc,target,lens in SPECS:
  key='WORLD REVIEW / '+name;d=bpy.data.cameras.get(key)or bpy.data.cameras.new(key);d.lens=lens;d.sensor_width=36;d.clip_start=.06;d.clip_end=250;o=bpy.data.objects.get(key)or bpy.data.objects.new(key,d)
  if o.name not in scene.objects:scene.collection.objects.link(o)
  o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
