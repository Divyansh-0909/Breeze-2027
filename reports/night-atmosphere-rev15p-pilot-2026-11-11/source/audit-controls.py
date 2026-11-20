import bpy,json
from pathlib import Path
R=Path(__file__).resolve().parents[1];P=R.parent/'house-railings-rev15o-ground-level-2026-11-11/delivery/Gullyverse-Rev15O-Clear-Ground-House-Fronts.blend';bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene
def val(x):
 if isinstance(x,(str,int,float,bool)):return x
 try:return [float(v) for v in x]
 except:return str(x)
def animation(data):
 a=getattr(data,'animation_data',None)
 if not a:return None
 return {'action':a.action.name if a.action else None,'drivers':[{'path':f.data_path,'index':f.array_index,'expression':f.driver.expression,'variables':[{'name':v.name,'type':v.type,'targets':[{'id':t.id.name if t.id else None,'path':t.data_path} for t in v.targets]} for v in f.driver.variables]} for f in a.drivers]}
def graph(tree):
 return {'nodes':[{'name':n.name,'type':n.bl_idname,'operation':getattr(n,'operation',None),'blendType':getattr(n,'blend_type',None),'uvMap':getattr(n,'uv_map',None),'extension':getattr(n,'extension',None),'interpolation':getattr(n,'interpolation',None),'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None,'inputs':[{'index':i,'name':x.name,'default':val(x.default_value) if hasattr(x,'default_value') else None} for i,x in enumerate(n.inputs)]} for n in tree.nodes],'links':[{'from':l.from_node.name,'fromSocket':l.from_socket.name,'to':l.to_node.name,'toSocket':l.to_socket.name} for l in tree.links],'animation':animation(tree)}
mats={slot.material for o in s.objects for slot in o.material_slots if slot.material}
out={'materials':{m.name:{'graph':graph(m.node_tree) if m.use_nodes else None,'animation':animation(m)} for m in mats},'shaderGroups':{g.name:graph(g) for g in bpy.data.node_groups},'world':graph(s.world.node_tree),'objectAnimation':{o.name:animation(o) for o in s.objects if o.animation_data},'instanceCounts':{v:sum(o.instance_type==v for o in s.objects) for v in ['NONE','VERTS','FACES','COLLECTION']},'packedFonts':[{'name':f.name,'packed':bool(f.packed_file),'filepath':f.filepath} for f in bpy.data.fonts]}
(R/'evidence/node-controls-and-animation.json').write_text(json.dumps(out,indent=2));print('FULL NODE CONTROL AUDIT',len(mats),flush=True)
