from pathlib import Path
import bpy,json,hashlib,collections
root=Path.cwd();p=root/'assets-source/gullyverse/cave-material-study/licensed-source/namaqualand_cliff_01/namaqualand_cliff_01_1k.blend'
before=hashlib.sha256(p.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(p));rows=[]
for o in bpy.data.objects:
    if o.type!='MESH':continue
    a=[o.matrix_world@v.co for v in o.data.vertices];lo=[min(v[k]for v in a)for k in range(3)];hi=[max(v[k]for v in a)for k in range(3)];edges=collections.Counter(tuple(sorted((int(a),int(b))))for f in o.data.polygons for a,b in zip(f.vertices,list(f.vertices)[1:]+[f.vertices[0]]))
    rows.append({'name':o.name,'vertices':len(o.data.vertices),'polygons':len(o.data.polygons),'dimensionsM':[hi[k]-lo[k]for k in range(3)],'bounds':[lo,hi],'openEdges':sum(n==1 for n in edges.values()),'nonManifoldEdges':sum(n>2 for n in edges.values()),'UVs':list(o.data.uv_layers.keys()),'scale':list(o.scale)})
assert hashlib.sha256(p.read_bytes()).hexdigest()==before
out={'sourceFile':str(p.relative_to(root)),'sha256':before,'objects':rows,'nativeSourceUnmodified':True}
(root/'reports/cave-material-study-2026-10-22/raw/native-source-inspection.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out),flush=True)
