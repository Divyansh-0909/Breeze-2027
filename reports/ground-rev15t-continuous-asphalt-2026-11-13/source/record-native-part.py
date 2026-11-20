from pathlib import Path
import json,sys
R=Path(__file__).resolve().parents[1];p=R/'delivery/Native-Master-Parts.json';d=json.loads(p.read_text());r=json.loads(sys.argv[1]);row=next(x for x in d['parts'] if x['file']==r['name'])
assert row['sha256']==r['sha256'] and row['bytes']==r['bytes'] and r['status']=='PASS'
row.update(id=r['id'],url=r['url'],parent=r['parent'],status='PASS')
d['status']='PASS' if all(x['status']=='PASS' for x in d['parts']) else 'IN_PROGRESS'
p.write_text(json.dumps(d,indent=2)+'\n')
print(json.dumps({'verifiedParts':sum(x['status']=='PASS' for x in d['parts']),'parts':len(d['parts'])}))
