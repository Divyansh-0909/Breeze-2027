"""Remove ASCII85 overhead without changing any decoded image or page text."""
from pathlib import Path
import fitz,json,hashlib
R=Path('reports/recovery-stage3a-cave-tunnel-2026-10-20');rows=[]
def image_hashes(doc):
 out=[]
 for x in range(1,doc.xref_length()):
  if doc.xref_get_key(x,'Subtype')[1]!='/Image':continue
  keys=tuple(doc.xref_get_key(x,k)[1]for k in ['Width','Height','BitsPerComponent','ColorSpace'])
  out.append((keys,hashlib.sha256(doc.xref_stream(x)).hexdigest()))
 return sorted(out)
for p in sorted(R.glob('Gullyverse-Stage3A-*.pdf')):
 before=p.stat().st_size;doc=fitz.open(p);images=image_hashes(doc);text=[page.get_text()for page in doc];pages=len(doc);changed=0
 for x in range(1,doc.xref_length()):
  filt=doc.xref_get_key(x,'Filter')[1]
  if 'ASCII85Decode'in filt and'FlateDecode'in filt:
   doc.update_stream(x,doc.xref_stream(x),compress=True);changed+=1
 tmp=p.with_name(p.stem+'.optimized.pdf');doc.save(tmp,garbage=3,deflate=True);doc.close();new=fitz.open(tmp)
 assert image_hashes(new)==images and len(new)==pages and [page.get_text()for page in new]==text
 new.close();tmp.replace(p);rows.append({'file':p.name,'beforeBytes':before,'finalBytes':p.stat().st_size,'pages':pages,'ASCII85StreamsRemoved':changed,'allDecodedImageHashesIdentical':True,'pageTextIdentical':True})
(R/'raw/pdf-lossless-verification.json').write_text(json.dumps({'status':'PASS','rows':rows},indent=2)+'\n');print(json.dumps(rows,indent=2))
