import os
"""Re-export the baked derivative independently; prune unused material bindings."""
import bpy,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];out=Path(os.environ.get('GULLYVERSE_OUT',str(ROOT/'public/models/gullyverse/locked-rev15z-v1')));src=out/'contact-frontage-baked.blend';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();guard=sha(src);bpy.ops.wm.read_factory_settings(use_empty=True)
with bpy.data.libraries.load(str(src))as(a,b):b.collections=['Runtime / contact-frontage']
c=b.collections[0];bpy.context.scene.collection.children.link(c);pruned=0;bindings=[]
for o in c.objects:
 if o.type!='MESH':continue
 me=o.data;materials=list(me.materials);used=sorted({p.material_index for p in me.polygons});mapping={old:i for i,old in enumerate(used)};oldFaces=[(tuple(me.vertices[v].co[:]for v in p.vertices),materials[p.material_index].name)for p in me.polygons];pruned+=len(materials)-len(used)
 oldIndices=[p.material_index for p in me.polygons]
 me.materials.clear()
 for i in used:me.materials.append(materials[i])
 for face,oldIndex in zip(me.polygons,oldIndices):face.material_index=mapping[oldIndex]
 assert oldFaces==[(tuple(me.vertices[v].co[:]for v in p.vertices),me.materials[p.material_index].name)for p in me.polygons]
 bindings.append({'node':o.name,'lightmapUV':o['runtimeLightmapChannel'],'uvLayers':[u.name for u in me.uv_layers]})
bpy.ops.export_scene.gltf(filepath=str(out/'contact-frontage.png.glb'),export_format='GLB',use_active_scene=True,export_apply=True,export_animations=False,export_extras=True,export_lights=False,export_normals=True,export_tangents=False)
assert sha(src)==guard
proof={'status':'PASS','sourceBakedDerivativeSHA256':guard,'outputSHA256':sha(out/'contact-frontage.png.glb'),'outputBytes':(out/'contact-frontage.png.glb').stat().st_size,'unusedBindingsRemoved':pruned,'geometryAndPerFaceMaterialNamesUnchanged':True,'bindings':bindings};(out/'reexport-verification.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps({k:v for k,v in proof.items()if k!='bindings'}))
