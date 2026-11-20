import bpy,json,time,hashlib,numpy as np
from pathlib import Path
R=Path(__file__).resolve().parents[1]
master=R.parent/'night-atmosphere-rev15p-pilot-2026-11-11/delivery/Gullyverse-Rev15P-Night-Atmosphere-Pilot.blend'
before=hashlib.sha256(master.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(master));s=bpy.context.scene;s.frame_set(1);bpy.context.view_layer.update()
source=next(o for o in s.objects if o.get('artKind') and o.get('carouselSlide')==0)
ob=source.copy();ob.data=source.data.copy();ob.animation_data_clear();ob.name='CAPTURE / mural illumination only';s.collection.objects.link(ob)
# The original carousel visibility driver otherwise re-enables a coplanar
# alpha-tested duplicate during baking, producing a black portrait silhouette.
# This is an unsaved in-memory capture scene only.
source.animation_data_clear();source.hide_render=True;ob.hide_render=False
m=bpy.data.materials.new('CAPTURE / neutral diffuse');m.use_nodes=True;m.node_tree.nodes['Principled BSDF'].inputs['Base Color'].default_value=(.5,.5,.5,1);m.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value=1;ob.data.materials.clear();ob.data.materials.append(m)
image=bpy.data.images.new('CAPTURE / mural direct indirect',width=1024,height=512,alpha=False);image.colorspace_settings.name='Non-Color';n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=image;m.node_tree.nodes.active=n
s.render.engine='CYCLES';s.cycles.samples=64;s.cycles.max_bounces=3;s.cycles.diffuse_bounces=2;s.render.bake.target='IMAGE_TEXTURES';s.render.bake.use_pass_color=False;s.render.bake.use_pass_direct=True;s.render.bake.use_pass_indirect=True;s.render.bake.margin=4
for o in s.objects:o.select_set(False)
ob.select_set(True);bpy.context.view_layer.objects.active=ob
t=time.monotonic();print('MURAL',source.name,[list(p.normal) for p in ob.data.polygons],ob.data.uv_layers.active.name,flush=True);bpy.ops.object.bake(type='DIFFUSE')
image.filepath_raw=str(R/'viewer/textures/mural-lightmap.png');image.file_format='PNG';image.save();pixels=np.empty(len(image.pixels),dtype=np.float32);image.pixels.foreach_get(pixels);rgb=pixels.reshape(-1,4)[:,:3]
assert hashlib.sha256(master.read_bytes()).hexdigest()==before
proof={'source':source.name,'nativeMasterUnchanged':True,'sourceSHA256':before,'method':'Neutral diffuse direct/indirect UV0 texture bake on original native mural surface; no geometry or artwork changes saved','seconds':time.monotonic()-t,'size':[1024,512],'range':[float(rgb.min()),float(rgb.max())],'percentiles':{str(v):float(np.percentile(rgb,v)) for v in [1,50,90,99]},'normals':[list(p.normal) for p in ob.data.polygons]}
(R/'evidence/mural-lightmap.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof),flush=True)
