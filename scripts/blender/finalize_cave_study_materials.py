"""Normalize scalar channels, preserve source aspect, seal comparison manifest."""
from pathlib import Path
import json,hashlib
from PIL import Image
import numpy as np
from research_cave_materials import ROOT,S,O,digest
d=json.loads((O/'materials.json').read_text());d['materials'].append(json.loads((S/'ambientcg-material.json').read_text()))
for material in d['materials']:
    rough=next(r for r in material['sourceMaps']if r['slot']=='roughness')
    p=ROOT/rough['file'];im=Image.open(p);a=np.asarray(im)
    if a.ndim==3:a=a[:,:,0]
    denominator=65535 if a.max()>255 else 255
    linear=np.clip(a.astype(np.float32)/denominator,0,1)
    byte=np.rint(linear*255).astype(np.uint8)
    orm=np.stack([np.full_like(byte,255),byte,np.zeros_like(byte)],axis=2)
    Image.fromarray(orm).save(O/material['id']/'orm.png',optimize=False,compress_level=3)
    material['scalarSource']={'mode':im.mode,'denominator':denominator,'roughnessRange':[float(linear.min()),float(linear.max())]}
    material['aspect']=material.get('aspect',1)
    material['runtimeMaps']=[]
    for file in ['basecolor.jpg','normal.png','orm.png']:
        p=O/material['id']/file;size=Image.open(p).size
        material['runtimeMaps'].append({'file':str(p.relative_to(ROOT/'public')),'bytes':p.stat().st_size,'sha256':digest(p),'pixels':list(size)})
    material['runtimeBytes']=sum(r['bytes']for r in material['runtimeMaps'])
    material['decodedRGBA8MipBytes']=sum(r['pixels'][0]*r['pixels'][1]*4*4/3 for r in material['runtimeMaps'])
    material['comparisonUV']={'metresPerHostUVUnit':2,'tileWidthMAt1x':5.395311,'tileHeightMAt1x':5.395311/material['aspect'],'normalStrength':.7,'albedoGain':1,'AOApplied':False,'runtimeDisplacement':False,'sameHostGeometry':True}
    print(material['id'],material['scalarSource'],material['runtimeBytes'],flush=True)
d['materials']=list({r['id']:r for r in d['materials']}.values())
text=json.dumps(d,indent=2)+'\n';(O/'materials.json').write_text(text);(S/'provenance-manifest.json').write_text(text)
(S/'PROVENANCE-SHA256.txt').write_text(digest(S/'provenance-manifest.json')+'  provenance-manifest.json\n')
