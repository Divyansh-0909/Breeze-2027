import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
exec(Path('reports/stage-2b-wall-geometry-correction-2026-10-12/scripts/check-scene-seams.py').read_text().split("old=scene")[0])
ranges=[(m['hostRange']['start'],m['hostRange']['count'])]+[(p['start'],p['count'])for p in m['joinRanges']];mask=np.ones(len(allpos),dtype=bool)
for start,count in ranges:mask[start:start+count]=False
base=allpos[mask];labels=np.arange(len(allpos))[mask][::3];p,f=glb('public/models/gullyverse/first-wall-corrected/first-wall-corrected.glb');points=base.tolist()+p;faces=np.arange(len(base)).reshape(-1,3).tolist()+[[v+len(base)for v in face]for face in f];tree=BVHTree.FromPolygons(points,faces);position=np.array([29,5,-60]);forward=np.array([42.1893,6.5,-63.6718])-position;forward/=np.linalg.norm(forward);right=np.cross(forward,[0,1,0]);right/=np.linalg.norm(right);up=np.cross(right,forward)
for pixel in [(950,400),(1000,400),(980,700),(900,200),(425,400)]:
 x,y=pixel;d=forward+right*(2*x/1366-1)*np.tan(29*np.pi/180)*(1366/900)+up*(1-2*y/900)*np.tan(29*np.pi/180);d/=np.linalg.norm(d);hit=tree.ray_cast(Vector(position),Vector(d),700);i=hit[2];print(pixel,'source vertex',int(labels[i])if i<len(labels)else'new candidate','location',list(hit[0]),'normal',list(hit[1]))
