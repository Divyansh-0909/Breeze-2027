"""One existing host rock, sculpted as a closed volume. No texture generation.
All outer original edges/corners remain; five internal face creases gain geological continuity.
"""
from pathlib import Path
import json,numpy as np
from rock_pilot_surface import value_noise
ROOT=Path(__file__).resolve().parents[2]
HOST=json.loads((ROOT/'assets-source/gullyverse/first-wall-corrected/host.json').read_text())
ANCHOR=json.loads((ROOT/'assets-source/gullyverse/first-wall-section/anchor.json').read_text())
R=np.array([ANCHOR['uAxis'],ANCHOR['vAxis'],ANCHOR['normal']]).T;ORIGIN=np.array(ANCHOR['anchor'])
VERTICES=(np.array(HOST['vertices'])-ORIGIN)@R;CENTER=VERTICES.mean(axis=0)
FACES=[f['indices'] for f in HOST['faces']];TARGET=3
ADJ={a['id']:a['shared'] for a in HOST['adjacent']}
EDGES={tuple(sorted((a,b))) for face in FACES for a,b in zip(face,np.roll(face,-1))}
JOIN_EDGES={tuple(sorted(e)) for e in ADJ.values()};PROTECTED=EDGES-JOIN_EDGES
LOW=np.min(np.array(ANCHOR['boundaryLocal']),axis=0);HIGH=np.max(np.array(ANCHOR['boundaryLocal']),axis=0);SIZE=HIGH-LOW
POLYLINES=[([(-6.3,-6.8),(-4.5,-4.8),(-4.7,-1.1),(-2.9,2.4),(-3.4,5.1),(-1.8,9.5)],.19,.65),
 ([(4.8,-8.8),(3.0,-5.4),(3.9,-2.0),(2.1,.7),(2.5,4.8),(5.5,7.6)],.25,.84),
 ([(-6.8,2.3),(-3.1,1.9),(-1.3,3.2),(1.4,2.8),(4.8,4.2)],.14,.43),
 ([(-3.0,-4.5),(-.8,-3.7),(.3,-4.2),(2.5,-2.8)],.12,.39),
 ([(2.2,.5),(.4,1.5),(-.6,3.1),(-1.9,4.4)],.11,.46),
 ([(-.8,-3.7),(-.4,-1.8),(-1.4,-.2)],.10,.36),
 ([(3.9,-2),(5.8,-.5),(6.9,1.8)],.14,.45)]
BLOCKS=[(-5.6,6.6,.15,.04,-.026),(-2.5,7.5,.58,-.032,.04),(2.6,7.3,.27,.065,-.02),(5.6,3.5,.63,-.017,.037),
 (-5.1,1.3,.35,.044,.02),(-.5,3.1,.76,-.02,-.02),(2.0,-.6,.31,.043,.016),(-3.8,-3.0,.65,.033,-.03),(4.3,-4.3,.53,-.05,.018),(-4.6,-7.0,.26,.038,.025),(.1,-6.3,.72,-.028,.04)]
def edge_distance(p,segments):
 out=np.full(p.shape[:-1],np.inf)
 for a,b in segments:
  u=VERTICES[a];d=VERTICES[b]-u;t=np.clip(np.sum((p-u)*d,axis=-1)/np.dot(d,d),0,1)
  out=np.minimum(out,np.linalg.norm(p-u-t[...,None]*d,axis=-1))
 return out
def gate(d,width):
 t=np.clip(d/width,0,1);return t*t*(3-2*t)
def collar_coordinates(p,face):
 pair=ADJ[face];a,b=VERTICES[pair];e=b-a;length=np.linalg.norm(e);e=e/length;centroid=VERTICES[FACES[face]].mean(axis=0);out=centroid-a;out-=e*np.dot(out,e);out/=np.linalg.norm(out)
 t=np.sum((p-a)*e,axis=-1)/length;d=np.sum((p-a)*out,axis=-1)
 # Unequal finite geological cut lines; not straight borders or periodic sine waves.
 knots=np.array([-.12,0,.13,.26,.39,.57,.69,.86,1,1.12]);heights=np.array([0,2.0,3.1,2.25,4.1,2.8,3.65,2.25,1.3,0])
 shift=(face%3)*.37;extent=np.interp(t,knots,heights)+.65*(value_noise(t*12,np.full_like(t,face*.73),83)-.5)
 extent=np.maximum(0,extent+shift)*((t>-.12)&(t<1.12));return t,d,extent

def region(p,face):
 if face==TARGET:return np.ones(p.shape[:-1])
 if face not in ADJ:return np.zeros(p.shape[:-1])
 _,d,extent=collar_coordinates(p,face);return gate(extent-d,.48)

def morphology(p):
 x,y,z=p[...,0],p[...,1],p[...,2]
 # Angular unequal rock units; geological faces with short weathered breaks, not soft stacked slabs.
 best=np.full(x.shape,np.inf);second=best.copy();v0=np.zeros_like(x);v1=v0.copy()
 for i,(cx,cy,offset,sx,sy) in enumerate(BLOCKS):
  metric=(x-cx)**2*.75+(y-cy)**2 +.17*z*z+(i%3)*.31
  plane=offset+sx*(x-cx)+sy*(y-cy)+.025*z
  win=metric<best;runner=(metric<second)&~win
  second=np.where(win,best,np.where(runner,metric,second));v1=np.where(win,v0,np.where(runner,plane,v1));best=np.where(win,metric,best);v0=np.where(win,plane,v0)
 gap=np.sqrt(np.maximum(0,second))-np.sqrt(np.maximum(0,best));transition=np.clip(gap/.55,0,1)
 depth=.2+v0*transition+(v0+v1)*.5*(1-transition)+.17*np.maximum(0,1-gap/.45)
 for k,(points,width,amount) in enumerate(POLYLINES):
  trench=np.zeros_like(x)
  for j,(a,b) in enumerate(zip(points,points[1:])):
   a=np.array(a);delta=np.array(b)-a;l=np.dot(delta,delta);t=((x-a[0])*delta[0]+(y-a[1])*delta[1])/l;tc=np.clip(t,0,1)
   signed=((x-a[0])*delta[1]-(y-a[1])*delta[0])/np.sqrt(l)+(value_noise(tc*4,np.full_like(tc,k*.63+j),107)-.5)*.045+.045*z
   w=width*2.7*(.78+.4*value_noise(tc*7,np.full_like(tc,k+j*.31),113));finite=gate(np.minimum(t+.08,1.08-t),.10);profile=np.maximum(0,1-np.abs(signed)/w)**1.0
   trench=np.maximum(trench,profile*finite*(.73+.27*value_noise(tc*4,np.full_like(tc,j*.6),127)))
  # Interrupt minor branches while retaining the primary continuous fault segments.
  depth+=amount*trench
 # A few asymmetric broken scars, no uniformly jagged spike field.
 for cx,cy,rx,ry,h in [(-3.1,.8,.9,.65,.35),(2.4,4.1,1.2,.8,.42),(4.1,-4.4,1.0,.55,.28),(-.5,-6.1,.55,.9,.3)]:
  u=(x-cx)/rx;v=(y-cy)/ry;shape=np.maximum.reduce([u+.2*v,-.8*u+.5*v,-.3*u-.9*v]);depth+=h*np.maximum(0,1-shape)*gate(1-shape,.2)
 depth+=(value_noise(x*1.9+z*.4,y*2.2,137)-.5)*.08
 return np.clip(depth,.12,2.35)

def sculpt(p,face):
 p=np.asarray(p);mask=region(p,face);protected=gate(edge_distance(p,PROTECTED),.75)
 inward=CENTER-p;length=np.linalg.norm(inward,axis=-1);inward/=length[...,None]
 amount=morphology(p)*mask*protected
 if face in ADJ:
  _,d,extent=collar_coordinates(p,face);amount+=.12*np.maximum(0,1-np.abs(d-extent)/.6)*protected
 return p+inward*amount[...,None]

def uv(p,face):
 p=np.asarray(p);flat=p.copy()
 if face in ADJ:
  # Rigidly unfold the neighbouring face onto the former front plane (metric UV scale).
  pair=ADJ[face];a,b=VERTICES[pair];axis=(b-a)/np.linalg.norm(b-a);center=VERTICES[FACES[face]].mean(axis=0);normal=np.cross(VERTICES[FACES[face][1]]-VERTICES[FACES[face][0]],VERTICES[FACES[face][2]]-VERTICES[FACES[face][0]]);normal/=np.linalg.norm(normal)
  target=np.array([0.,0.,1.]);angle=np.arctan2(np.dot(axis,np.cross(normal,target)),np.dot(normal,target));d=p-a
  flat=a+d*np.cos(angle)+np.cross(axis,d)*np.sin(angle)+axis*np.sum(d*axis,axis=-1)[...,None]*(1-np.cos(angle))
 base=(flat[...,:2]-LOW)/SIZE
 # UV-only edge repair: reflect into the same approved image's interior texels.
 # Unit slope preserves metric scale. Central body UVs remain exactly unchanged.
 limits=[(.08,.92),(.06,.94)]
 for i,(lo,hi) in enumerate(limits):
  period=2*(hi-lo);q=(base[...,i]-lo)%period;base[...,i]=lo+np.where(q<=hi-lo,q,period-q)
 fine=np.stack([(flat[...,0]+6)/12,(flat[...,1]+5)/10],axis=-1)
 return base,fine
