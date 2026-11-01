import math
SHOPS=[(-1,-25),(-1,-7),(-1,2),(1,-16),(1,-7)]
SHOP_NAMES=['21-shop-left-25','22-shop-left-7','23-shop-left2','24-shop-right-16','25-shop-right-7']
SHOP_POSES=[]
def floor(y):return 6+1.2*min(1,max(0,(y+10)/24))
for i,n in enumerate(SHOP_NAMES):SHOP_POSES.extend([n,f'{31+i}-shop-inside-{i+1}',f'{41+i}-shop-section-{i+1}'])
CROWD_POSES=['08-crowd-middle','16-rooftop-plan','19-hub-wide','46-left-spillover','47-right-spillover','48-board-foreground','49-center-filled','50-mobile-crowd','01-landing','12-mobile-landing']
POSES=SHOP_POSES+CROWD_POSES
def add_cameras():
    import bpy
    from mathutils import Vector
    rig=bpy.data.collections['04_SHARED_CAMERA_RIG'];specs=[]
    for i,(side,y)in enumerate(SHOPS):
        g=floor(y);specs.append((f'{31+i}-shop-inside-{i+1}',(side*4.45,y-.8,g+1.9),(side*6.6,y+.2,g+1.35),18,'PERSP',None))
        specs.append((f'{41+i}-shop-section-{i+1}',(side*5.6,y,g+12),(side*5.6,y,g),26,'ORTHO',9.6))
    specs.extend([
        ('46-left-spillover',(-10,28.6,9.7),(-10.5,38.3,8.5),30,'PERSP',None),
        ('47-right-spillover',(10,28.6,9.7),(10.5,38.3,8.5),30,'PERSP',None),
        ('48-board-foreground',(0,21.8,9.05),(0,32,8.5),23,'PERSP',None),
        ('49-center-filled',(0,35.2,8.92),(0,43.5,9.9),26,'PERSP',None),
        ('50-mobile-crowd',(0,30,8.92),(0,44,10.5),20,'PERSP',None)])
    for name,loc,target,lens,kind,scale in specs:
        if name in bpy.data.objects:continue
        data=bpy.data.cameras.new(name);data.lens=lens;data.sensor_width=36;data.clip_start=9.3 if 'section'in name else .08;data.clip_end=250;data.type=kind
        if scale:data.ortho_scale=scale
        obj=bpy.data.objects.new(name,data);rig.objects.link(obj);obj.location=loc;obj.rotation_euler=(Vector(target)-obj.location).to_track_quat('-Z','Y').to_euler()
        if 'section'in name:
            i=int(name[:2])-41;obj.rotation_euler.z=-SHOPS[i][0]*math.pi/2
    return [s[0]for s in specs]
