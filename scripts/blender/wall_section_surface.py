"""Original fractured limestone morphology, metric local surface; fixed pentagonal rim.
No photograph texels, no repeated horizontal brick rows. All relief carves INTO current rock.
"""
import json
from pathlib import Path
import numpy as np
from rock_pilot_surface import value_noise
ROOT=Path(__file__).resolve().parents[2]
ANCHOR=json.loads((ROOT/'assets-source/gullyverse/first-wall-section/anchor.json').read_text())
POLYGON=np.array(ANCHOR['boundaryLocal']);LOW=POLYGON.min(axis=0);HIGH=POLYGON.max(axis=0);SIZE=HIGH-LOW
rng=np.random.default_rng(2401012)
# Long discontinuous joints with differing strike/dip and finite extents.
FRACTURES=[(-5.3,-6.4,-1.1,8.6,.085,.22),(-2.5,-8.3,3.7,7.1,.06,.17),(3.6,-7.8,6.2,2.6,.10,.29),(-6.4,.6,4.8,3.7,.052,.12),(-4.9,5.8,2.1,8.2,.067,.18),(1.1,-6.7,6.6,-4.2,.047,.14),(-6.2,-2.1,.7,-.8,.06,.13)]
# Unequal, oblique, interrupted bedding; none spans the whole wall.
BEDS=[(-5.8,-2.8,4.3,.073,.075),(-2.7,5.8,-4.1,-.058,.09),(-6.1,1.6,6.2,.13,.067),(1.5,5.9,1.2,-.15,.082)]
CAVITIES=[tuple(rng.uniform([-5.7,-7.2,.10,.075,.035],[6.1,8.0,.45,.30,.15])) for _ in range(27)]
CHIPS=[(-3.2,1.8,1.1,.7,.36),(2.2,4.4,.95,1.3,.31),(4.4,-2.2,1.4,.6,.42),(-1.1,-4.5,.7,.8,.25)]
PLANES=[(-5.2,6.5,.11,.05,-.015,0.),(-1.6,7.6,.40,-.025,.042,.8),(3.5,6.0,.22,.064,-.032,.4),
        (5.7,1.9,.45,-.031,.017,.2),(-4.8,1.2,.23,.055,.018,.3),(-.3,2.9,.50,-.027,-.038,.6),
        (1.3,-1.9,.19,.054,.022,.8),(-3.4,-3.5,.43,.031,-.037,.3),(4.5,-4.8,.34,-.067,.018,.9),
        (-5.2,-6.3,.16,.052,.026,.4),(.4,-6.7,.52,-.028,.044,.2)]
def edge_distance(x,y):
 result=np.full(np.broadcast(x,y).shape,np.inf)
 for a,b in zip(POLYGON,np.roll(POLYGON,-1,axis=0)):
  d=b-a;result=np.minimum(result,((x-a[0])*d[1]-(y-a[1])*d[0])*-1/np.linalg.norm(d))
 return result

def rim_weight(x,y):
 t=np.clip(edge_distance(x,y)/.62,0,1);return t*t*(3-2*t)

def relief(x,y):
 # Broad angular geological planes, locally clipped rather than regularly tessellated blocks.
 broad=.10+.065*value_noise(x*.34,y*.30,89)+.04*value_noise(x*.81,y*.69,131)
 folds=.018*np.abs(np.sin(x*.73+y*.28+value_noise(x*.27,y*.25,137)))
 first=np.full(np.broadcast(x,y).shape,np.inf);second=first.copy();p0=np.zeros_like(first);p1=p0.copy()
 for cx,cy,offset,sx,sy,power in PLANES:
  distance=(x-cx)**2*.73+(y-cy)**2-power
  plane=offset+sx*(x-cx)+sy*(y-cy)
  win=distance<first;runner=(distance<second)&~win
  second=np.where(win,first,np.where(runner,distance,second));p1=np.where(win,p0,np.where(runner,plane,p1));first=np.where(win,distance,first);p0=np.where(win,plane,p0)
 gap=np.sqrt(np.maximum(0,second))-np.sqrt(np.maximum(0,first));blend=np.clip(gap/.32,0,1)
 depth=broad+folds+(p0+p1)*.5*(1-blend)+p0*blend+.035*np.maximum(0,1-gap/.16)
 for i,(ax,ay,bx,by,width,amount) in enumerate(FRACTURES):
  dx,dy=bx-ax,by-ay;length2=dx*dx+dy*dy
  t=((x-ax)*dx+(y-ay)*dy)/length2;tc=np.clip(t,0,1)
  # Jagged fracture trace: bounded multi-frequency angular kinks, not sine-only stripes.
  bend=(value_noise(tc*11,np.full_like(tc,i*.7),157)-.5)*.18+(value_noise(tc*29,np.full_like(tc,i*.3),163)-.5)*.05
  signed=((x-ax)*dy-(y-ay)*dx)/np.sqrt(length2)+bend
  fade=np.clip(np.minimum(tc,1-tc)*8,0,1)*((t>=0)&(t<=1))
  trench=np.maximum(0,1-np.abs(signed)/(width*3.8))
  depth+=amount*trench**.55*fade
  # Different planar offsets on either side are localized to the fracture neighbourhood.
  depth+=(.045 if i%2 else .065)*np.clip(signed/(width*3.8),-1,1)*np.maximum(0,1-np.abs(signed)/1.6)*fade
 for i,(left,right,height,slope,width) in enumerate(BEDS):
  d=y-height-slope*x-(value_noise(x*.47,np.full_like(x,i*.73),173)-.5)*.2
  mask=np.clip((x-left)/.5,0,1)*np.clip((right-x)/.5,0,1)
  depth+=.08*np.maximum(0,1-np.abs(d)/(width*2.5))**.65*mask
 for i,(cx,cy,rx,ry,amount) in enumerate(CAVITIES):
  d=np.sqrt(((x-cx)/rx)**2+((y-cy)/ry)**2)
  depth+=amount*np.maximum(0,1-d)**.7
 for i,(cx,cy,rx,ry,amount) in enumerate(CHIPS):
  # Asymmetric sharp chipped polygons: maximum of unequal planes produces broken scar edges.
  px=(x-cx)/rx;py=(y-cy)/ry;shape=np.maximum.reduce([px+.25*py,-.72*px+.64*py,-.45*px-.85*py])
  depth+=amount*np.maximum(0,1-shape)*((shape<1)&(shape>-.5))
 depth+=(value_noise(x*3.7,y*4.1,191)-.5)*.032
 return -np.clip(depth,.014,1.18)*rim_weight(x,y)

def maps(x,y):
 large=value_noise(x*.48,y*.39,121);mid=value_noise(x*2.9+y*.31,y*3.15,127)
 grain=value_noise(x*44,y*48,139);fine=value_noise(x*116,y*120,149)
 pores=np.maximum(0,value_noise(x*21,y*24,157)-.76)
 variation=(large-.5)*22+(mid-.5)*11+(grain-.5)*8+(fine-.5)*4
 stain=np.clip((value_noise(x*.95+y*.12,y*.33,163)-.57)*2.9,0,1)
 calcite=np.maximum(0,value_noise(x*13,y*12.6,173)-.73)*28
 color=np.stack([184+variation,188+variation,193+variation],axis=-1)-stain[...,None]*14+calcite[...,None]
 color-=pores[...,None]*35
 # Preserve approved grey family in body; only a narrow rim blends into untouched current neighbours.
 w=rim_weight(x,y)
 border=np.array(ANCHOR['oldVertexColor']);border=np.where(border<=.0031308,border*12.92,1.055*border**(1/2.4)-.055)*255
 color=color*w[...,None]+border*(1-w[...,None])
 micro=((grain-.5)*.0018+(mid-.5)*.0013+(fine-.5)*.0008-pores*.006)*w
 rough=np.clip(.9+(grain-.5)*.09+(mid-.5)*.04+stain*.025+pores*.08,.82,.99)*w+.98*(1-w)
 cavity=np.clip(-relief(x,y)-.16,0,.45)
 ao=np.clip(.985-cavity*.39,.76,1)*w+(1-w)
 return np.clip(color,0,248),micro,rough,ao
