import bpy
from mathutils import Vector
def floor(y):return 6+1.2*min(1,max(0,(y+10)/24))
SHOP_SPECS=[('21-shop-left-25',-1,-25),('22-shop-left-7',-1,-7),('23-shop-left2',-1,2),('24-shop-right-16',1,-16),('25-shop-right-7',1,-7)]
POSES=['17-banner-frontal','18-banner-oblique','08-crowd-middle','16-rooftop-plan','19-hub-wide','01-landing','12-mobile-landing']+[r[0]for r in SHOP_SPECS]
def add_cameras():
    specs=[('17-banner-frontal',(0,-14,8.2),(0,-3,11.5),32),('18-banner-oblique',(-1.7,-12,7.72),(0,-3,11.5),30),('19-hub-wide',(0,12,11.5),(0,31,9.1),18)]
    for name,side,y in SHOP_SPECS:specs.append((name,(-side*.6,y-1.8,floor(y)+1.72),(side*5.7,y+.1,floor(y)+1.5),24))
    rig=bpy.data.collections['04_SHARED_CAMERA_RIG']
    for name,location,target,lens in specs:
        if name in bpy.data.objects:continue
        d=bpy.data.cameras.new(name);d.lens=lens;d.sensor_width=36;d.clip_start=.08;d.clip_end=250
        o=bpy.data.objects.new(name,d);rig.objects.link(o);o.location=location;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler()
    return specs
