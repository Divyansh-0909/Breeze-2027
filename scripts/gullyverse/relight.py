import os
"""Higher-sample Eevee-compatible static irradiance; reuse verified baked PBR UVs.

Eevee's distance-limited practicals and decorative emissive surfaces must not
become unrelated, unlimited Cycles emitters. Source geometry stays immutable.
"""
import bpy,bmesh,json,hashlib,numpy as np,math
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];out=Path(os.environ.get('GULLYVERSE_OUT',str(ROOT/'public/models/gullyverse/locked-rev15z-v1')));plan=json.loads(Path(os.environ.get('GULLYVERSE_PLAN',str(Path(__file__).with_name('export-plan.json')))).read_text());manifest=json.loads((out/'manifest.json').read_text());source=Path(plan['source']['path']);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();assert sha(source)==plan['source']['sha256'];bpy.ops.wm.open_mainfile(filepath=str(source));native=bpy.context.scene;native.frame_set(1);bpy.context.view_layer.update()
with bpy.data.libraries.load(str(out/'contact-frontage-baked.blend'))as(a,b):b.collections=['Runtime / contact-frontage']
targetCollection=b.collections[0];targets=list(targetCollection.objects);targetNames={o['runtimeOriginalSource']for o in targets};faces={r['sourceObject']:r['sourceFaces']for r in manifest['objects']};scene=bpy.data.scenes.new('RUNTIME / higher-sample irradiance');scene.world=native.world.copy();scene.collection.children.link(targetCollection);bpy.context.window.scene=scene;contextMaterials={};lightRows=[]
def neutral_emission(mat):
 if mat.as_pointer()in contextMaterials:return contextMaterials[mat.as_pointer()]
 c=mat.copy();contextMaterials[mat.as_pointer()]=c
 if not c.use_nodes:return c
 for n in c.node_tree.nodes:
  if n.type=='BSDF_PRINCIPLED':
   for l in list(n.inputs['Emission Strength'].links):c.node_tree.links.remove(l)
   n.inputs['Emission Strength'].default_value=0
  elif n.type=='EMISSION':
   for l in list(n.inputs['Strength'].links):c.node_tree.links.remove(l)
   n.inputs['Strength'].default_value=0
 return c
bb=[o.matrix_world@Vector(p)for o in targets for p in o.bound_box];lo=Vector(tuple(min(p[i]for p in bb)for i in range(3)));hi=Vector(tuple(max(p[i]for p in bb)for i in range(3)))
volumeExclusions=[]
for old in native.objects:
 if old.type=='VOLUME' or (old.type=='MESH'and any(mat and mat.use_nodes and any(n.type in ['PRINCIPLED_VOLUME','VOLUME_ABSORPTION','VOLUME_SCATTER']for n in mat.node_tree.nodes)for mat in old.data.materials)):
  volumeExclusions.append(old.name);continue
 if old.hide_render or old.get('contactPart')in['native form label','native form illustration']:continue
 if old.type=='LIGHT':
  p=old.matrix_world.translation;distance=math.sqrt(sum(max(lo[i]-p[i],0,p[i]-hi[i])**2 for i in range(3)));include=old.data.energy>0 and(not old.data.use_custom_distance or distance<old.data.cutoff_distance);lightRows.append({'name':old.name,'energy':old.data.energy,'included':include,'distanceToChunk':distance,'nativeCutoff':old.data.cutoff_distance if old.data.use_custom_distance else None})
  if include:scene.collection.objects.link(old)
  continue
 if old.name in targetNames and faces[old.name]=='ALL':continue
 c=old.copy();c.name='Irradiance context / '+old.name;scene.collection.objects.link(c)
 if old.name in faces:
  c.data=old.data.copy();bm=bmesh.new();bm.from_mesh(c.data);bm.faces.ensure_lookup_table();bmesh.ops.delete(bm,geom=[bm.faces[i]for i in faces[old.name]],context='FACES');bm.to_mesh(c.data);bm.free()
 if old.type=='MESH':
  for i,slot in enumerate(c.material_slots):
   if slot.material:
    original=slot.material;slot.link='OBJECT';slot.material=neutral_emission(original)
size=plan['bake']['resolution'];image=bpy.data.images.new('Runtime clean irradiance',width=size,height=size,alpha=False,float_buffer=True,is_data=True);image.colorspace_settings.name='Non-Color';restore=[]
for ob in targets:
 for mat in ob.data.materials:
  if not mat:continue
  nodes=mat.node_tree.nodes;links=mat.node_tree.links;p=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
  for link in list(p.inputs['Normal'].links):
   restore.append((mat,p.inputs['Normal'],None,[(link.from_socket,link.to_socket)]));links.remove(link)
  for key,value in [('Metallic',0),('Roughness',1),('Alpha',1),('Emission Strength',0)]:
   socket=p.inputs[key];old=[(l.from_socket,l.to_socket)for l in socket.links];restore.append((mat,socket,socket.default_value,old))
   for l in list(socket.links):links.remove(l)
   socket.default_value=value
  tex=nodes.new('ShaderNodeTexImage');tex.image=image;nodes.active=tex
for o in scene.objects:o.select_set(o in targets)
bpy.context.view_layer.objects.active=targets[0];scene.render.engine='CYCLES';scene.cycles.samples=128;scene.cycles.seed=plan['bake']['seed'];scene.cycles.use_light_tree=True;scene.cycles.max_bounces=3;scene.cycles.diffuse_bounces=2;scene.render.threads_mode='FIXED';scene.render.threads=4;scene.render.bake.use_clear=False;scene.render.bake.use_selected_to_active=False;scene.render.bake.margin=6;scene.render.bake.use_pass_color=False;scene.render.bake.use_pass_direct=True;scene.render.bake.use_pass_indirect=True;print('RELIGHT_START',sum(r['included']for r in lightRows),flush=True);bpy.ops.object.bake(type='DIFFUSE',uv_layer='RuntimeLightmapUV');image.filepath_raw=str(out/'lightmap.hdr');image.file_format='HDR';image.save()
for mat,socket,value,old in restore:
 if value is not None:socket.default_value=value
 for f,t in old:mat.node_tree.links.new(f,t)
manifest['bake'].update(samples=128,lightTree=True,method='Cycles direct+indirect irradiance; lamps selected by bounding-box range only, exact Eevee per-texel cutoff and view treatment remain open; decorative surface emission is visual',lightSelection=lightRows,rawHDRSHA256=sha(out/'lightmap.hdr'),volumeExclusions=volumeExclusions,fogBaked=False,receivingNormal='Macro geometry; source normal maps preserved separately in runtime PBR');(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');assert sha(source)==plan['source']['sha256'];print('RELIGHT_PASS',sha(out/'lightmap.hdr'),flush=True)
