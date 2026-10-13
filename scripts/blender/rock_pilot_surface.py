"""Original geological surface model shared by the mesh and texture authoring.
Unequal beds, angular fault slabs, narrow bevel/recess boundaries, unique nonperiodic weathering.
All positions in metres. numpy implementation lets mesh and UV atlas sample exactly the same shape.
"""
import numpy as np
BEDS=[.69,1.54,2.28,3.48,4.11,5.44,6.23,7.39,8.6,9.36]
JOINTS=[(-4.8,1.9,.16),(-2.7,4.5,-.15),(.4,2.3,.11),(3.5,7.5,-.13),(5.1,4.6,.12),(-4.2,8.1,-.08),(1.1,8.7,.21),(2.3,5.1,.25)]
rng=np.random.default_rng(20271011)
CELLS=[(x,z,*rng.uniform([-.38,-.065,-.085],[.38,.065,.085])) for z in [.8,3.1,5.8,8.5] for x in [-5,-2.1,1.1,4.4]]
CELLS=[(x+float(rng.uniform(-.65,.65)),z+float(rng.uniform(-.58,.58)),d,a,b) for x,z,d,a,b in CELLS]
def value_noise(x,y,seed):
 ix=np.floor(x).astype(np.int64);iy=np.floor(y).astype(np.int64);fx=x-ix;fy=y-iy;fx=fx*fx*(3-2*fx);fy=fy*fy*(3-2*fy)
 def rnd(a,b):
  n=(a*374761393+b*668265263+seed*1442695041)&0xffffffff;n=(n^(n>>13))*1274126177&0xffffffff
  return ((n^(n>>16))&0xffffffff)/4294967295
 return (rnd(ix,iy)*(1-fx)+rnd(ix+1,iy)*fx)*(1-fy)+(rnd(ix,iy+1)*(1-fx)+rnd(ix+1,iy+1)*fx)*fy

def coordinates(u,v):
 top=np.interp(u,[0,.09,.17,.23,.34,.42,.56,.62,.74,.83,.93,1],[9.2,9.7,9.64,9.01,9.3,10.,9.56,9.4,10.02,9.92,9.,9.3])
 top+=(value_noise(u*59,u*2,5)-.5)*.055
 z=v*top;width=5.89+.09*np.sin(z*.91)+.04*np.sin(z*3.1)
 x=(u*2-1)*width+.045*np.sin(z*2.2)
 return x,z

def slabs(x,z):
 first=np.full_like(x,np.inf);second=np.full_like(x,np.inf);a=np.zeros_like(x);b=np.zeros_like(x)
 for i,(cx,cz,offset,tiltx,tiltz) in enumerate(CELLS):
  distance=(x-cx)**2+((z-cz)*1.05)**2
  plane=offset+tiltx*(x-cx)+tiltz*(z-cz)
  win=distance<first;runner=(distance<second)&~win
  second=np.where(win,first,np.where(runner,distance,second));b=np.where(win,a,np.where(runner,plane,b));first=np.where(win,distance,first);a=np.where(win,plane,a)
 gap=np.sqrt(second)-np.sqrt(first);weight=np.clip(gap/.12,0,1);weight=weight*weight*(3-2*weight)
 return (a+b)/2*(1-weight)+a*weight-.22*np.exp(-(gap/.052)**2),gap

def surface(u,v):
 x,z=coordinates(u,v);plane,gap=slabs(x,z)
 depth=1.4+.045*x+.027*z+plane+(value_noise(x*.59,z*.63,23)-.5)*.11
 for j,h in enumerate(BEDS):
  line=h+.08*np.sin(x*(.65+j*.09)+j*1.7)+.018*x
  delta=z-line;coverage=.42+.58*np.clip((value_noise(x*.42,np.full_like(x,j*.83),71)-.30)*2,0,1)
  depth-=.17*np.exp(-(delta/.044)**2)*coverage
  depth+=.095*np.tanh(delta/.017)*np.sin(j*2.73+.5)*coverage
 for j,(px,pz,slope) in enumerate(JOINTS):
  distance=x-px-slope*(z-pz)-.016*np.sin(z*8+j);fade=np.exp(-((z-pz)/1.9)**4)
  depth-=.19*np.exp(-(distance/.04)**2)*fade;depth+=.13*np.tanh(distance/.027)*fade
 depth+=(value_noise(x*3.1,z*3.4,51)-.5)*.023+(value_noise(x*9.3,z*10.1,57)-.5)*.012
 return x,-depth,z
