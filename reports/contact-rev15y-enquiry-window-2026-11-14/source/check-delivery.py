from pathlib import Path
import json,hashlib,struct
R=Path(__file__).resolve().parents[1];repo=R.parents[1];read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
old=read(repo/'reports/accommodation-rev15x1-clean-wall-2026-11-14/evidence/movement-recheck.json')
rows=[dict(path=r['path'],sha256=sha(repo/r['path']),unchanged=sha(repo/r['path'])==r['sha256'])for r in old['files']]
assert all(r['unchanged']for r in rows)
(R/'evidence/movement-recheck.json').write_text(json.dumps({'status':'UNCHANGED','files':rows,'integration':'No production application controller or world changes in this art phase'},indent=2)+'\n')
p=R/'delivery/Rev15Y-Enquiry-Window.glb';data=p.read_bytes();magic,version,size=struct.unpack('<III',data[:12]);assert magic==0x46546c67 and version==2 and size==len(data);length,kind=struct.unpack('<II',data[12:20]);assert kind==0x4e4f534a;g=json.loads(data[20:20+length]);lights=g['extensions']['KHR_lights_punctual']['lights'];nodes=g['nodes'];tags=[n.get('extras',{}).get('contactPart')for n in nodes]
assert tags.count('attendant')==1 and tags.count('message panel')==1 and tags.count('contact heading')==1 and len(lights)==3
assert all('uri'not in i for i in g.get('images',[]))
result={'status':'PASS','sha256':sha(p),'bytes':len(data),'meshes':len(g['meshes']),'images':len(g.get('images',[])),'lights':len(lights),'personLeftHeadingAndPanelPresent':True,'texturesEmbedded':True,'scope':'Contact component only; native Accommodation changes and source-window replacements require the manifest/full-world builder'};(R/'evidence/glb-structure.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
