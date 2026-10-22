from pathlib import Path
import bpy,bmesh,json,hashlib
ROOT=Path.cwd();S=ROOT/'assets-source/gullyverse/c9-cave-deep-relief';rows=[]
for name in ['cave-deep-pilot-authoring.blend','cave-deep-pilot.blend']:
 p=S/name;bpy.ops.wm.open_mainfile(filepath=str(p));meshes=[]
 for o in bpy.data.objects:
  if o.type!='MESH':continue
  bm=bmesh.new();bm.from_mesh(o.data)
  meshes.append({'name':o.name,'vertices':len(bm.verts),'faces':len(bm.faces),'nonManifoldInteriorEdges':sum(len(e.link_faces)>2 for e in bm.edges),'zeroAreaFaces':sum(f.calc_area()<1e-12 for f in bm.faces),'dimensions':list(o.dimensions),'scale':list(o.scale)});bm.free()
 missing=[];images=[]
 for image in bpy.data.images:
  if image.source not in ['FILE','TILED']:continue
  packed=bool(image.packed_file);resolved=Path(bpy.path.abspath(image.filepath));images.append({'name':image.name,'packed':packed,'exists':resolved.is_file(),'size':list(image.size)})
  if not packed and not resolved.is_file():missing.append(image.name)
 rows.append({'path':str(p.relative_to(ROOT)),'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest(),'bytes':p.stat().st_size,'opens':True,'missingLinkedImages':missing,'images':images,'meshes':meshes})
result={'status':'PASS'if not any(r['missingLinkedImages']for r in rows)else'FAIL_MISSING_LINKED_IMAGES','validationScope':'Editable source accessibility only. Does not override the failed runtime first-hit/visual gate. Unmodified native reference meshes can have captured open edges.','files':rows}
(ROOT/'reports/stage3a1-deep-rock-2026-10-21/raw/master-accessibility.json').write_text(json.dumps(result,indent=2)+'\n');print(result['status'],[len(r['meshes'])for r in rows],flush=True)
