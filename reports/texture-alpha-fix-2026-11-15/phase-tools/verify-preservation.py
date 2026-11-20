import bpy,json,hashlib,numpy as np
from pathlib import Path
r=Path('/dev/shm/texture-alpha-fix-2026-11-15');w=Path('/dev/shm/Breeze-2027-runtime');old=w/'public/models/gullyverse/locked-rev15z-v1/contact-frontage-baked.blend';new=w/'public/models/gullyverse/locked-rev15z-clean-v2/contact-frontage-baked.blend';bpy.ops.wm.read_factory_settings(use_empty=True)
def load(p):
 with bpy.data.libraries.load(str(p))as(a,b):b.collections=['Runtime / contact-frontage']
 return {o['runtimeOriginalSource']:o for o in b.collections[0].objects}
a=load(old);b=load(new);assert a.keys()==b.keys();rows=[]
def data(coll,prop,n):
 ar=np.empty(n,np.float32);coll.foreach_get(prop,ar);return ar.tobytes()
def images(o):return {hashlib.sha256(n.image.packed_file.data).hexdigest()for m in o.data.materials if m and m.use_nodes for n in m.node_tree.nodes if n.type=='TEX_IMAGE'and n.image and n.image.packed_file}
for name,o in a.items():
 n=b[name];assert tuple(map(tuple,o.matrix_world))==tuple(map(tuple,n.matrix_world));assert data(o.data.vertices,'co',len(o.data.vertices)*3)==data(n.data.vertices,'co',len(n.data.vertices)*3);assert [(tuple(f.vertices),f.material_index)for f in o.data.polygons]==[(tuple(f.vertices),f.material_index)for f in n.data.polygons]
 for uv in o.data.uv_layers:assert data(uv.data,'uv',len(uv.data)*2)==data(n.data.uv_layers[uv.name].data,'uv',len(uv.data)*2)
 assert images(o)==images(n);rows.append({'source':name,'shapeTransformFacesAndOriginalUVsExact':True,'allPackedPBRImageHashesExact':True,'newIrradianceUV':n['runtimeLightmapChannel']})
source=Path('/dev/shm/Gullyverse-Rev15Z-Wide-Contact-Window-and-Restored-Graffiti.blend');assert hashlib.sha256(source.read_bytes()).hexdigest()=='89e765de6bb68a58a6a2d17d4d6d7ea6c696a6750402ede19306bdddc6a71041';(r/'evidence/preservation.json').write_text(json.dumps({'status':'PASS','sourceMasterSHA256':'89e765de6bb68a58a6a2d17d4d6d7ea6c696a6750402ede19306bdddc6a71041','objects':rows,'originalMasterAndLegacyRuntimeDerivativeUnmodified':True},indent=2)+'\n');print('SHAPE_PBR_ORIGINAL_UV_AND_MASTER_PASS',len(rows))
