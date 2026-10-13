import json,numpy as np
from pathlib import Path
r=Path('reports/stage-2b-wall-geometry-correction-2026-10-12');data=json.loads((r/'raw/host-topology.json').read_text());allpos=np.array(data['sourceAttributes']['position']).reshape(-1,3);allcol=np.array(data['sourceAttributes']['color']).reshape(-1,3);joins=[]
for rock,faces in [(3,[2,3]),(5,[3,6])]:
 start=(rock-2)*108;p=allpos[start:start+108];v=[];idx={}
 def key(x):
  k=tuple(np.round(x,5))
  if k not in idx:idx[k]=len(v);v.append(x.tolist())
  return idx[k]
 loops=[]
 for i in range(12):
  tri=[[key(x)for x in p[i*9+j:i*9+j+3]]for j in [0,3,6]];edges=[(a,t[(j+1)%3])for t in tri for j,a in enumerate(t)];boundary=[e for e in edges if (e[1],e[0])not in edges];loop=[boundary[0][0]]
  while len(loop)<5:loop.append(next(b for a,b in boundary if a==loop[-1]))
  loops.append(loop)
 shared=list(set(loops[faces[0]])&set(loops[faces[1]]));assert len(shared)==2
 ranges=[{'start':start+i*9,'count':9}for i in faces];joins.append({'rock':rock,'vertices':v,'faces':loops,'selectedFaces':faces,'sharedEdge':shared,'sourceRanges':ranges,'color':allcol[start].tolist(),'deformation':'localized0..20m high, within2.5m of the existing contact edge; original boundaries/corners fixed'})
Path('assets-source/gullyverse/first-wall-corrected/joins.json').write_text(json.dumps(joins,indent=2));print([(j['rock'],j['sourceRanges'])for j in joins])
