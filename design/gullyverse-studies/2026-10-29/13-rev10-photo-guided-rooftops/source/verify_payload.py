from pathlib import Path
import hashlib,json
from html.parser import HTMLParser
O=Path(__file__).resolve().parents[1]
def verify(root=O):
 m=json.loads((root/'FILE-MANIFEST.json').read_text())
 for r in m['payloadFiles']:
  p=root/r['file'];assert p.is_file() and p.stat().st_size==r['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'],r['file']
 class Links(HTMLParser):
  def __init__(self):super().__init__();self.links=[]
  def handle_starttag(self,tag,attrs):
   for k,v in attrs:
    if k in ['src','href'] and v and not v.startswith(('http:','https:','#','data:')):self.links.append(v)
 l=Links();l.feed((root/'GALLERY.html').read_text());assert all((root/p).is_file() for p in l.links)
 return {'payloadFiles':len(m['payloadFiles']),'galleryLinks':len(l.links),'masterSHA256':m['masterSHA256']}
if __name__=='__main__':print(json.dumps(verify()))
