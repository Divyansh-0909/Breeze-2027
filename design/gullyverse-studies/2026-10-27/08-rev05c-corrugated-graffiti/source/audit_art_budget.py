import bpy,json,hashlib
from pathlib import Path
O=Path(__file__).resolve().parents[1]
exec(compile((O/'source/audit_scene.py').read_text(),str(O/'source/audit_scene.py'),'exec'))
p=O/'evidence/scene-budget-final.json';r=json.loads(p.read_text());d=json.loads((O/'evidence/art-authoring.json').read_text())
r['materialDatablocksTotal']=len(bpy.data.materials)
r['newImageBytesPNG']=sum((O/'source/derived'/f'{k}-paint-rgba.png').stat().st_size for k in ['chaar-diwari','ritviz','neha-kakkar'])+(O/'source/generated/supporting-wall-atlas.png').stat().st_size
r['newPackedUniqueImageCount']=4
r['paintedMaterials']=[{'name':m.name,'nodes':len(m.node_tree.nodes),'imageTextureNodes':sum(n.type=='TEX_IMAGE'for n in m.node_tree.nodes),'sourceImages':sorted({n.image.name for n in m.node_tree.nodes if n.type=='TEX_IMAGE'and n.image}),'emissionStrength':next(n.inputs['Emission Strength'].default_value for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED')}for m in bpy.data.materials if m.name.startswith('ART /')]
r['newMeshObjects']=0;r['modifiedShutterMeshDatablocks']=57;r['profileMeshTriangles']=sum(len(bpy.data.objects[x['object']].data.loop_triangles)for x in d['profiles'])
r['lightsPerScene']=[{'variant':s['variant'],'stored':sum(o.type=='LIGHT'for o in s.objects),'optionalOff':sum(o.type=='LIGHT'and o.name.startswith('Rev05B shop interior practical')and o.data.energy==0 for o in s.objects)}for s in bpy.data.scenes]
r['runtimeCaveat']='Authoring-only scene audit. No website asset export/loading, R3F draw-call query, hardware frame-time or physical-device certification in this milestone.'
p.write_text(json.dumps(r,indent=2)+'\n');print('ART_BUDGET',[(x['variant'],x['evaluatedMeshAndCurveTriangles'])for x in r['scenes']],r['imageCount'],r['estimatedUniqueImageRGBA8MipMiB'],r['newImageBytesPNG'])
