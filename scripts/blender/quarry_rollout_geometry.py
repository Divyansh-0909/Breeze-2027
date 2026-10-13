"""Fit limestone geology to the CURRENT rock envelopes, not a historic quarry.
Original approved material is imported elsewhere; this module never writes textures.
"""
from pathlib import Path
import json,numpy as np
from rock_pilot_surface import value_noise
from corrected_wall_geometry import R as PILOT_R,ORIGIN as PILOT_ORIGIN
from corrected_wall_joins import JOINS,build_join
ROOT=Path(__file__).resolve().parents[2]
SOURCE=json.loads((ROOT/'assets-source/gullyverse/quarry-rollout/source-topology.json').read_text())
QUARRY_CENTER=np.array([-.9,0.,-103.75])
def gate(d,w):
 t=np.clip(d/w,0,1);return t*t*(3-2*t)
def reflect(x,lo,hi):
 q=(x-lo)%(2*(hi-lo));return lo+np.where(q<=hi-lo,q,2*(hi-lo)-q)
def distance_edges(p,vertices,edges):
 out=np.full(len(p),np.inf)
 for i,j in edges:
  a=vertices[i];d=vertices[j]-a;t=np.clip(((p-a)*d).sum(axis=1)/np.dot(d,d),0,1);out=np.minimum(out,np.linalg.norm(p-a-t[:,None]*d,axis=1))
 return out
class Geology:
 def __init__(self,rock):
  self.rock=rock;self.id=rock['id'];self.v=np.array(rock['vertices']);self.c=np.array(rock['center']);self.faces=rock['faces'];n=QUARRY_CENTER-self.c;n[1]=0;n/=np.linalg.norm(n);u=np.array([n[2],0,-n[0]]);self.basis=np.stack([u,[0,1,0],n],axis=1)
  rng=np.random.default_rng(20261012+self.id*977);self.phase=rng.uniform(-2.2,2.2,2);self.angle=rng.uniform(-.36,.36);self.multiplier=rng.uniform(.85,1.16)
  span=np.ptp(self.local(self.v),axis=0);self.depth_scale=float(np.clip(np.sqrt(span[0]*span[1]/(15.57*19.89)),1,2.4))
  self.blocks=[(*rng.uniform([-7,-9],[7,9]),rng.uniform(.12,.82),*rng.uniform(-.065,.065,2))for _ in range(12)]
  self.scars=[(*rng.uniform([-5.7,-7.2],[5.7,7.2]),rng.uniform(.45,1.25),rng.uniform(.4,1.0),rng.uniform(.22,.46))for _ in range(5)]
  self.cracks=[]
  for j in range(3):
   yy=np.array([-10,-6.8,-2.4,1.6,5.4,9.8])+rng.uniform(-.6,.6,6);xx=rng.uniform(-5.8,5.8)+np.cumsum(rng.uniform(-1.6,1.6,6));self.cracks.append((np.stack([xx,yy],axis=1),rng.uniform(.31,.62),rng.uniform(.45,.86)))
  for j in range(5):
   start=rng.uniform([-6,-7],[4,6]);points=np.array([start,start+rng.uniform([1.1,-1.5],[3.0,1.8]),start+rng.uniform([3.3,-2.2],[6.6,3.0])]);self.cracks.append((points,rng.uniform(.18,.38),rng.uniform(.24,.55)))
  self.normals=[]
  for face in self.faces:
   p=self.v[face];normal=np.cross(p[1]-p[0],p[2]-p[0]);normal/=np.linalg.norm(normal);self.normals.append(normal)
  edges={}
  for i,f in enumerate(self.faces):
   for a,b in zip(f,np.roll(f,-1)):edges.setdefault(tuple(sorted((a,int(b)))),[]).append(i)
  self.protected=[]
  for edge,faceids in edges.items():
   if min(self.v[list(edge),1])<=0:continue
   for eye in [[0,1.72,-51],[-10.5,1.72,-110.8],[-18,1.72,-72.55],[17.4,1.72,-72.55]]:
    signs=[np.dot(self.normals[i],np.array(eye)-self.v[self.faces[i]].mean(axis=0))for i in faceids]
    if min(signs)<=0<=max(signs):self.protected.append(edge);break
  self.join=next((j for j in JOINS if j['rock']==self.id),None)
  self.join_edges=[]
  if self.join:
   edges={tuple(sorted((a,int(b))))for fi in self.join['selectedFaces']for a,b in zip(self.join['faces'][fi],np.roll(self.join['faces'][fi],-1))};edges.remove(tuple(sorted(self.join['sharedEdge'])));self.join_edges=list(edges)
 def local(self,p):return(np.asarray(p)-self.c)@self.basis
 def depth(self,p):
  q=self.local(p);envelope=self.local(self.v);span=np.ptp(envelope,axis=0);q[:,0]*=15.57/span[0];q[:,1]*=19.89/span[1];q[:,:2]+=self.phase;x=q[:,0]*np.cos(self.angle)-q[:,1]*np.sin(self.angle);y=q[:,0]*np.sin(self.angle)+q[:,1]*np.cos(self.angle)
  best=np.full(len(q),np.inf);second=best.copy();p0=np.zeros(len(q));p1=p0.copy()
  for j,(cx,cy,offset,sx,sy)in enumerate(self.blocks):
   metric=(x-cx)**2*(.65+.1*(j%4))+(y-cy)**2;plane=offset+sx*(x-cx)+sy*(y-cy);win=metric<best;runner=(metric<second)&~win;second=np.where(win,best,np.where(runner,metric,second));p1=np.where(win,p0,np.where(runner,plane,p1));best=np.where(win,metric,best);p0=np.where(win,plane,p0)
  gap=np.sqrt(np.maximum(0,second))-np.sqrt(np.maximum(0,best));blend=np.clip(gap/.65,0,1);depth=.22+p0*blend+(p0+p1)*.5*(1-blend)+.2*np.maximum(0,1-gap/.55)
  for k,(points,width,amount)in enumerate(self.cracks):
   trench=np.zeros(len(q))
   for j,(a,b)in enumerate(zip(points,points[1:])):
    d=b-a;t=((x-a[0])*d[0]+(y-a[1])*d[1])/np.dot(d,d);tc=np.clip(t,0,1);signed=((x-a[0])*d[1]-(y-a[1])*d[0])/np.linalg.norm(d);signed+=(value_noise(tc*4,np.full_like(tc,k*.63+j),100+self.id)-.5)*.055+.023*q[:,2];w=width*(.8+.35*value_noise(tc*5,np.full_like(tc,j),200+self.id));finite=gate(np.minimum(t+.08,1.08-t),.11);trench=np.maximum(trench,np.maximum(0,1-np.abs(signed)/w)*finite)
   depth+=amount*trench
  # Unequal short mineral breaks, not a uniform spike/noise field.
  for cx,cy,rx,ry,amount in self.scars:
   u=(x-cx)/rx;v=(y-cy)/ry;shape=np.maximum.reduce([u+.2*v,-.8*u+.5*v,-.3*u-.9*v]);depth+=amount*np.maximum(0,1-shape)*gate(1-shape,.2)
  depth+=(value_noise(x*1.4+q[:,2]*.31,y*1.7,300+self.id)-.5)*.07
  return np.clip(depth*self.multiplier,.10,2.35)*self.depth_scale
 def sculpt(self,p):
  p=np.asarray(p);corner=np.min(np.linalg.norm(p[:,None]-self.v[None,:],axis=2),axis=1);protected=gate(corner,.7)*(.25+.75*gate(distance_edges(p,self.v,self.protected),.65))
  # Keep the existing geological foot in contact with the unchanged terrain.
  # Radial recesses must not lift low sloping faces away from the ground.
  contact=2.3+.65*value_noise(p[:,0]*.09,p[:,2]*.09,480+self.id)
  protected*=gate(p[:,1]-contact,2.0)
  if self.join_edges:protected*=gate(distance_edges(p,self.v,self.join_edges),.8)
  inward=self.c-p;radius=np.linalg.norm(inward,axis=1);inward/=radius[:,None];return p+inward*np.minimum(self.depth(p)*protected,radius*.32)[:,None]
 def uv(self,p,face):
  q=self.local(p);normal=self.normals[face]@self.basis
  if abs(normal[1])>.64:s,t=q[:,0],q[:,2]
  elif abs(normal[2])>.38:s,t=q[:,0],q[:,1]
  else:s,t=q[:,2],q[:,1]
  fine=np.stack([(s+6)/12,(t+5)/10],axis=1);base=np.stack([reflect((s+self.phase[0]+7.36)/15.57,.08,.92),reflect((t+self.phase[1]+9.65)/19.89,.06,.94)],axis=1);return base,fine

def triangulate_rock(rock,n=32):
 geology=Geology(rock);v=geology.v;points=[];faces=[];faceids=[];lookup={}
 def add(p):
  key=tuple(np.round(p,6))
  if key not in lookup:lookup[key]=len(points);points.append(p)
  return lookup[key]
 for fi,ids in enumerate(rock['faces']):
  poly=v[ids];center=poly.mean(axis=0)
  for a,b in zip(poly,np.roll(poly,-1,axis=0)):
   grid={}
   for i in range(n+1):
    for j in range(n+1-i):grid[(i,j)]=add(center+(a-center)*i/n+(b-center)*j/n)
   for i in range(n):
    for j in range(n-i):
     faces.append([grid[(i,j)],grid[(i+1,j)],grid[(i,j+1)]]);faceids.append(fi)
     if i+j<n-1:faces.append([grid[(i+1,j)],grid[(i+1,j+1)],grid[(i,j+1)]]);faceids.append(fi)
 points=np.array(points);moved=geology.sculpt(points)
 if geology.join:
  assert n==36
  joint,original,_,_,_=build_join(geology.join,n=n);count=len(joint)//2;mapping={tuple(np.round(p@PILOT_R.T+PILOT_ORIGIN,6)):joint[i]@PILOT_R.T+PILOT_ORIGIN for i,p in enumerate(original[:count])}
  # Keep the approved actual contact faces exactly, including their uneven occluder carve.
  selected=set(i for f,fi in zip(faces,faceids)if fi in geology.join['selectedFaces']for i in f)
  for i in selected:moved[i]=mapping[tuple(np.round(points[i],6))]
 base=np.zeros((len(faces)*3,2));fine=base.copy();faces=np.array(faces,dtype=np.int32);faceids=np.array(faceids);ids=faces.reshape(-1)
 for fi in range(12):
  mask=np.repeat(faceids==fi,3);a,b=geology.uv(points[ids[mask]],fi);base[mask]=a;fine[mask]=b
 return moved,faces,base,fine,geology
