from pathlib import Path
import json,hashlib,math
from PIL import Image
ROOT=Path.cwd();REPORT=ROOT/'reports/recovery-phase3-c9-2026-10-19';RAW=REPORT/'raw'
groups={label:json.loads((RAW/f'{label}-captures.json').read_text())for label in ['c51','c8-3x','c9']}
assert all(g['status']=='PASS'for g in groups.values())
build=(ROOT/'.next/BUILD_ID').read_text().strip();assert all(g['build']==build for g in groups.values())
by={label:{Path(c['file']).name:c for c in g['captures']}for label,g in groups.items()}
assert all(set(g)==set(by['c51'])for g in by.values());rows=[]
for name,base in by['c51'].items():
 pair=[]
 for label,g in by.items():
  c=g[name];file=REPORT/c['file'];im=Image.open(file);assert im.size==(c['data']['viewport']['width'],c['data']['viewport']['height'])
  assert c['canvas']['effectiveDpr']==1 and c['data']['snapshot']['quality']==0
  for field in ['x','y','z','yaw','pitch','fov']:assert abs(c['data']['camera'][field]-base['data']['camera'][field])<1e-9,(name,label,field)
  assert c['lighting']==base['lighting'] and c['data']['lighting']==base['data']['lighting'],(name,label,'lights differ')
  assert c['canvas']==base['canvas']
  if label!='c51':assert c['scanned']['enabled']and c['scanned']['scale']==3
  if label=='c9':assert c['composition']['enabled']and c['composition']['ready']and c['composition']['sourceUniformScale']==.9
  pair.append({'mode':label,'file':c['file'],'width':im.width,'height':im.height,'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'camera':c['data']['camera'],'lighting':c['lighting'],'DPR':1,'quality':0})
 rows.append({'name':name,'title':base['title'],'note':base['note'],'matched':True,'versions':pair})
result={'status':'PASS','build':build,'images':sum(len(g['captures'])for g in groups.values()),'matchedViewpoints':len(rows),'comparisons':rows,'historicalReferenceCaveat':'Original C8 PDF records rounded poses for approved3x. The C9 PDF lacks full raw pose metadata; historical panels are reference-aligned, not asserted pixel-identical. Historical PDF image compression is preserved and identified.'}
(REPORT/'matched-pose-verification.json').write_text(json.dumps(result,indent=2)+'\n');print('MATCHED_REVIEW PASS',result['images'],'images',len(rows),'poses')
