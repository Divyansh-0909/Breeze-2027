"""Read-only audit: never saves or changes the source Blender data."""
import bpy, json, hashlib, time
from pathlib import Path
R=Path(__file__).resolve().parents[1]
P=R.parent/'house-railings-rev15o-ground-level-2026-11-11/delivery/Gullyverse-Rev15O-Clear-Ground-House-Fronts.blend'
EXPECTED='2c78b57e97a5a97683f946d60ad265b22a1eb88ae12abed6220ec268ce473657'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P)==EXPECTED
bpy.ops.wm.open_mainfile(filepath=str(P));s=bpy.context.scene
assert s.name=='REV15O / Clear Ground-Level House Fronts'
def vec(v): return [round(float(x),5) for x in v]
def graph(m):
 if not m.use_nodes:return []
 return [{'name':n.name,'type':n.bl_idname,'image':n.image.name if n.type=='TEX_IMAGE' and n.image else None,'group':n.node_tree.name if n.type=='GROUP' and n.node_tree else None,'inputs':{i.name:vec(i.default_value) if not isinstance(i.default_value,str) and hasattr(i.default_value,'__len__') else i.default_value for i in n.inputs if hasattr(i,'default_value') and isinstance(i.default_value,(int,float,str,bpy.types.bpy_prop_array))},'links':[(l.from_node.name,l.from_socket.name,l.to_socket.name) for l in m.node_tree.links if l.to_node==n]} for n in m.node_tree.nodes]
objects=[]
for o in s.objects:
 row={'name':o.name,'type':o.type,'parent':o.parent.name if o.parent else None,'collections':[c.name for c in o.users_collection],'location':vec(o.location),'dimensions':vec(o.dimensions),'hiddenRender':o.hide_render,'hideViewport':o.hide_viewport,'instanceType':o.instance_type,'instanceCollection':o.instance_collection.name if o.instance_collection else None,'data':o.data.name if o.data else None,'modifiers':[{'name':m.name,'type':m.type} for m in o.modifiers],'animated':bool(o.animation_data),'constraints':[c.type for c in o.constraints]}
 if o.type=='MESH':row.update(vertices=len(o.data.vertices),triangles=sum(len(p.vertices)-2 for p in o.data.polygons),materials=[slot.material.name if slot.material else None for slot in o.material_slots],uvLayers=[u.name for u in o.data.uv_layers])
 if o.type=='LIGHT':row.update(lightType=o.data.type,energy=o.data.energy,color=vec(o.data.color),shadow=o.data.use_shadow)
 if o.type=='CAMERA':row.update(lens=o.data.lens,rotation=vec(o.rotation_euler),matrix=[vec(v) for v in o.matrix_world],clip=[o.data.clip_start,o.data.clip_end])
 objects.append(row)
mats={m for o in s.objects if o.type=='MESH' for slot in o.material_slots for m in [slot.material] if m}
images=[]
for i in bpy.data.images:
 packed=list(i.packed_files)
 images.append({'name':i.name,'size':list(i.size),'channels':i.channels,'packedBytes':sum(p.packed_file.size for p in packed),'filepath':i.filepath,'source':i.source,'missing':i.source=='FILE' and not packed and not Path(bpy.path.abspath(i.filepath)).exists()})
groups=[{'name':g.name,'nodes':[n.bl_idname for n in g.nodes]} for g in bpy.data.node_groups]
summary={'scenes':len(bpy.data.scenes),'objects':len(objects),'meshObjects':sum(o.type=='MESH' for o in s.objects),'uniqueMeshes':len({o.data for o in s.objects if o.type=='MESH'}),'rawTrianglesAllMeshObjects':sum(x.get('triangles',0) for x in objects),'materials':len(mats),'imagesAllScenes':len(images),'packedImageBytesAllScenes':sum(i['packedBytes'] for i in images),'lights':sum(o.type=='LIGHT' for o in s.objects),'armatures':sum(o.type=='ARMATURE' for o in s.objects),'meshObjectsWithUV':sum(bool(o.data.uv_layers) for o in s.objects if o.type=='MESH'),'nativeRev13ACrowdMeshes':sum(o.type=='MESH' and o.data.name.startswith('REV13A shared') for o in s.objects)}
report={'source':str(P),'sourceBytes':P.stat().st_size,'sourceSHA256':EXPECTED,'blender':bpy.app.version_string,'scene':s.name,'summary':summary,'sceneMemberships':{x.name:[o.name for o in x.objects] for x in bpy.data.scenes},'sceneSettings':{'engine':s.render.engine,'viewTransform':s.view_settings.view_transform,'exposure':s.view_settings.exposure,'world':s.world.name if s.world else None,'frameStart':s.frame_start,'frameEnd':s.frame_end},'objects':objects,'materials':{m.name:graph(m) for m in sorted(mats,key=lambda m:m.name)},'shaderGroups':groups,'images':images,'linkedLibraries':[l.filepath for l in bpy.data.libraries],'actions':[{'name':a.name,'fcurves':len(a.fcurves),'range':vec(a.frame_range)} for a in bpy.data.actions]}
assert sha(P)==EXPECTED
(R/'evidence').mkdir(parents=True,exist_ok=True);(R/'evidence/inventory.json').write_text(json.dumps(report,indent=2,default=str));print('READ_ONLY_INVENTORY',json.dumps(summary),flush=True)
