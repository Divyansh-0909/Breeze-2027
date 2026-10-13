"""Localized underlying contact-face carving. No new boulders or texture maps."""
import json,numpy as np
from pathlib import Path
from corrected_wall_geometry import R,ORIGIN,gate
ROOT=Path(__file__).resolve().parents[2]
JOINS=json.loads((ROOT/'assets-source/gullyverse/first-wall-corrected/joins.json').read_text())
def build_join(join,n=36):
 world=np.array(join['vertices']);polyverts=(world-ORIGIN)@R;center=polyverts.mean(axis=0);coords=[];faces=[];index={}
 def add(p):
  key=tuple(np.round(p,6))
  if key not in index:index[key]=len(coords);coords.append(p)
  return index[key]
 for fi in join['selectedFaces']:
  poly=polyverts[join['faces'][fi]];centroid=poly.mean(axis=0)
  for a,b in zip(poly,np.roll(poly,-1,axis=0)):
   grid={}
   for i in range(n+1):
    for j in range(n+1-i):grid[(i,j)]=add(centroid+(a-centroid)*i/n+(b-centroid)*j/n)
   for i in range(n):
    for j in range(n-i):
     faces.append([grid[(i,j)],grid[(i+1,j)],grid[(i,j+1)]])
     if i+j<n-1:faces.append([grid[(i+1,j)],grid[(i+1,j+1)],grid[(i,j+1)]])
 coords=np.array(coords);a,b=polyverts[join['sharedEdge']];edge=b-a;t=np.clip(np.sum((coords-a)*edge,axis=1)/np.dot(edge,edge),0,1);distance=np.linalg.norm(coords-a-t[:,None]*edge,axis=1)
 # Perimeter stays exactly attached to the retained original faces.
 edges={tuple(sorted((x,y))) for fi in join['selectedFaces']for x,y in zip(join['faces'][fi],np.roll(join['faces'][fi],-1))};edges.remove(tuple(sorted(join['sharedEdge'])))
 boundaryDistance=np.full(len(coords),np.inf)
 for i,j in edges:
  x=polyverts[i];d=polyverts[j]-x;s=np.clip(np.sum((coords-x)*d,axis=1)/np.dot(d,d),0,1);boundaryDistance=np.minimum(boundaryDistance,np.linalg.norm(coords-x-s[:,None]*d,axis=1))
 y=(coords@R.T+ORIGIN)[:,1];amount=np.interp(y,[-2,0,2,4,6,8,11,14,16,19,21],[0,0,.32,.71,.28,.8,.42,.63,.17,0,0])
 contact=gate(2.6-distance,1.1)
 if join['rock']==3:
  # The actual host/neighbor intersection is inside face 2, not on the
  # neighbor's original shared edge. Ray inspection identified this surface
  # as the straight visible occluder. Carve only its narrow intersection band.
  contact=np.maximum(contact,gate(3.0-np.abs(coords[:,2]),1.1))
 amount*=3.0*contact*gate(boundaryDistance,.65)
 inward=center-coords;inward/=np.linalg.norm(inward,axis=1)[:,None];front=coords+amount[:,None]*inward;back=coords+3.7*inward;count=len(coords)
 allpoints=np.concatenate([front,back]);alloriginal=np.concatenate([coords,back]);allfaces=faces+[[x+count for x in f[::-1]]for f in faces]
 # Get actual union perimeter of both faces: common edge is internal, not an exposed cap.
 edgeCount={}
 for f in faces:
  for x,y in zip(f,np.roll(f,-1)):
   key=tuple(sorted((int(x),int(y))));edgeCount[key]=edgeCount.get(key,0)+1
 for f in faces:
  for x,y in zip(f,np.roll(f,-1)):
   if edgeCount[tuple(sorted((int(x),int(y)) ))]==1:allfaces.extend([[int(x),int(x)+count,int(y)+count],[int(x),int(y)+count,int(y)]])
 assert np.max(np.linalg.norm(front[boundaryDistance<1e-5]-coords[boundaryDistance<1e-5],axis=1))<1e-6
 corners=[polyverts[i]for i in set(join['faces'][join['selectedFaces'][0]]+join['faces'][join['selectedFaces'][1]])]
 return allpoints,alloriginal,allfaces,corners,polyverts
