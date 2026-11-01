"""Optional material-only floor patch proposal. NEVER saved into selected Blender master."""
import bpy,json,sys,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1];sys.path.insert(0,str(O/'source'));from rooftop_cameras import add
base=next(s for s in bpy.data.scenes if s.get('variant')=='REV11');s=base.copy();s.name='OPTIONAL ONLY / restrained floor patina'
for c in list(s.collection.children):s.collection.children.unlink(c)
for o in list(s.collection.objects):s.collection.objects.unlink(o)
floor=next(o for o in base.objects if o.name=='WORLD / PILOT / Rooftop slab / 32m x 40m')
for o in base.objects:
 if o!=floor:s.collection.objects.link(o)
q=floor.copy();q.data=floor.data.copy();s.collection.objects.link(q)
for slot in q.material_slots:
 if not slot.material:continue
 mat=slot.material.copy();slot.material=mat;mat.name='OPTIONAL DIAGNOSTIC / original floor with subtle mineral patina';nt=mat.node_tree;bs=next(n for n in nt.nodes if n.type=='BSDF_PRINCIPLED');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=.55;noise.inputs['Detail'].default_value=2.0;tex=nt.nodes.new('ShaderNodeTexCoord');nt.links.new(tex.outputs['Object'],noise.inputs['Vector']);ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(.70,.70,.70,1);ramp.color_ramp.elements[1].color=(1,1,1,1);nt.links.new(noise.outputs['Fac'],ramp.inputs[0]);mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.22
 if bs.inputs['Base Color'].is_linked:nt.links.new(bs.inputs['Base Color'].links[0].from_socket,mix.inputs[1])
 else:mix.inputs[1].default_value=bs.inputs['Base Color'].default_value
 nt.links.new(ramp.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],bs.inputs['Base Color'])
bpy.context.window.scene=s;s.frame_set(1);add(s);s.render.engine='BLENDER_EEVEE_NEXT';s.eevee.taa_render_samples=16;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG'
rows=[]
for pose in['03-aerial','15-mobile']:
 s.camera=bpy.data.objects['REV10 CAMERA / '+pose];s.render.resolution_x=576 if 'mobile'in pose else 1280;s.render.resolution_y=1024 if 'mobile'in pose else 720;f=O/'review'/('OPTIONAL-floor-'+pose+'.png');s.render.filepath=str(f);bpy.ops.render.render(write_still=True);rows.append({'pose':pose,'file':str(f.relative_to(O)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(O/'evidence/optional-floor-proposal.json').write_text(json.dumps({'proposalOnlyNotSelected':True,'masterWasNotSaved':True,'originalFloorMeshMaterialUVUnchanged':True,'noImagesAdded':True,'oneClonedFloorMaterialWrapperOnlyInTemporaryProcess':True,'maxDarkeningPercent':6.6,'cameraLightingIdentical':True,'rows':rows},indent=2))
