from pathlib import Path
import json,hashlib,zipfile
O=Path(__file__).resolve().parent.parent;W=O/'checkpoint';prefix='Gullyverse-Lane-Rooftop-Concept/';families=[('Gullyverse-Concept-Source-and-Assets.zip',[p for d in ['source','assets']for p in (O/d).rglob('*')if p.is_file()and'__pycache__'not in p.parts and p.suffix!='.pyc']+[O/'RESTORE.md',O/'GULLYVERSE-LANE-ROOFTOP-CONCEPT-REPORT.md']),('Gullyverse-Concept-Review-and-Evidence.zip',[p for d in ['renders','review','evidence']for p in (O/d).rglob('*')if p.is_file()and'__pycache__'not in p.parts and p.suffix!='.pyc'])];specs=[];allrows=[]
for name,files in families:
 out=W/name;rows=[]
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,6)as z:
  for p in sorted(set(files)):
   rel=p.relative_to(O).as_posix();data=p.read_bytes();rows.append({'file':rel,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'archive':name});z.writestr(prefix+rel,data)
 with zipfile.ZipFile(out)as z:
  for row in rows:assert hashlib.sha256(z.read(prefix+row['file'])).hexdigest()==row['sha256']
 spec={'archive':name,'bytes':out.stat().st_size,'sha256':hashlib.file_digest(out.open('rb'),'sha256').hexdigest(),'members':len(rows),'parts':[]}
 if out.stat().st_size>50*1024*1024:
  with out.open('rb')as f:
   i=0
   while data:=f.read(50*1024*1024):
    i+=1;p=W/(name+f'.part{i:03}');p.write_bytes(data);spec['parts'].append({'name':p.name,'path':str(p),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
  out.unlink()
 else:spec['path']=str(out)
 specs.append(spec);allrows.extend(rows);print(json.dumps(spec),flush=True)
(W/'archives.json').write_text(json.dumps(specs,indent=2));(W/'files-manifest.json').write_text(json.dumps(allrows,indent=2));(W/'FILE-SHA256SUMS.txt').write_text(''.join(r['sha256']+'  '+prefix+r['file']+'\n'for r in allrows));print('PACKAGED',len(allrows),'files')
