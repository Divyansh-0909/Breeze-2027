from pathlib import Path
import json,math
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle,Polygon
import numpy as np
O=Path(__file__).resolve().parents[1];V=O/'review';V.mkdir(exist_ok=True)
OLD=O/'source/baseline'
before=json.loads((OLD/'evidence/crowd-composition.json').read_text())['people'];after=json.loads((O/'evidence/organic-crowd-authoring.json').read_text())['actors']
def visible(row,variant):
    label=row['label']
    return label.startswith(('Audience ','Organic audience '))or (variant=='B'and label.startswith('Festival extra '))or(variant=='C'and label.startswith('Balanced extra '))
def zone(x,y):
    r=math.hypot(x,45.8-y)
    return 'near_screen_r_lt_9'if r<9 else'middle_r_9_to_12'if r<12 else'outer_r_ge_12'
fig,axes=plt.subplots(3,2,figsize=(12,16));fig.patch.set_facecolor('#f1ede1');table=[]
xbins=np.arange(-15,15.01,2);ybins=np.arange(30,46.01,2)
for r,variant in enumerate(['A','B','C']):
    counts={}
    for c,(edition,rows)in enumerate([('before',before),('after',after)]):
        people=[p for p in rows if visible(p,variant)];points=[p['foot']for p in people]
        values=np.histogram2d([p[0]for p in points],[p[1]for p in points],bins=[xbins,ybins])[0]
        ax=axes[r,c];ax.imshow(values.T,origin='lower',extent=[-15,15,30,46],vmin=0,vmax=5,cmap='YlOrBr',aspect='equal')
        ax.scatter([p[0]for p in points],[p[1]for p in points],s=9,c='#234c57');ax.add_patch(Rectangle((-1.65,30),3.3,16,fill=False,edgecolor='#237b54',linestyle='--'))
        ax.plot([-7.28,7.28],[45.8,45.8],lw=5,c='#343f4d');ax.set_title(f'{variant} / {edition} / {len(people)} audience');ax.set_xlabel('X / metres');ax.set_ylabel('Y / metres')
        zones={k:sum(zone(p[0],p[1])==k for p in points)for k in ['near_screen_r_lt_9','middle_r_9_to_12','outer_r_ge_12']}
        counts[edition]={'actors':len(people),'occupied2mCells':int((values>0).sum()),'maxActorsIn2mCell':int(values.max()),'zones':zones,'left':sum(p[0]<0 for p in points),'right':sum(p[0]>0 for p in points),'insideProtectedAisle':sum(abs(p[0])<1.65 for p in points)}
    table.append({'variant':variant,**counts})
fig.suptitle('Audience density / same 2m cells before and after\nDots are foot centers; independent triangle-body tests verify non-overlap',fontsize=14)
fig.tight_layout(rect=[0,0,.99,.95]);fig.savefig(V/'density-occupancy.png',dpi=160);fig.savefig(V/'density-occupancy.svg');plt.close(fig)
(O/'evidence/audience-density-table.json').write_text(json.dumps({'status':'MEASURED','cellSizeM':2,'cellAreaM2':4,'footCenterMapOnly':True,'bodyCollisionProof':'body-overlap-validation.json','variants':table,'fixedLaneAndCypherPeopleUnchanged':9},indent=2)+'\n')
fig,axes=plt.subplots(1,2,figsize=(13,8));fig.patch.set_facecolor('#f1ede1')
for ax in axes:
    ax.set_facecolor('#f1ede1');ax.add_patch(Rectangle((-4.25,4),8.5,7.2,fc='#9c9c91',ec='#505d55'))
    ax.add_patch(Rectangle((-1.65,2.78),3.3,1,fc='#a76d42',ec='#624b32'));ax.text(0,3.28,'COUNTER\nEXACTLY FIXED',ha='center',va='center',fontsize=10)
    ax.set_xlim(-4.6,4.6);ax.set_ylim(1.8,11.8);ax.set_aspect('equal');ax.set_xlabel('Shop width / metres');ax.set_ylabel('Depth from lane / metres');ax.grid(alpha=.15)
axes[0].set_title('Actual current host / no interior void')
for y in [-2.3,0,2.3]:axes[0].add_patch(Rectangle((y-.825,3.58),1.65,.5,fc='#d4c68d',ec='#5f5e44'))
axes[0].text(0,7.2,'SOLID BUILDING MESH\nShelves moved here would be buried',ha='center',va='center',fontsize=11)
axes[1].set_title('Proposed exception / NOT applied')
axes[1].add_patch(Rectangle((-3.1,4),6.2,3.8,fc='#f2efe3',ec='#bf4a3e',linestyle='--',lw=2))
for side,u in [(-1,4.95),(-1,6.75),(1,5.85)]:axes[1].add_patch(Rectangle((side*2.78-.25,u-.825),.5,1.65,fc='#d4c68d',ec='#5f5e44'))
axes[1].plot([-3.1,3.1],[7.72,7.72],c='#8c5e3d',lw=3);axes[1].text(0,8.5,'Outer dimensions, signs, shutters\nand counters retained.\nOnly a local interior recess proposed.',ha='center',fontsize=10)
axes[1].annotate('6.2m opening',xy=(3.1,4),xytext=(0,4.35),ha='center',fontsize=9)
fig.suptitle('SHOP INTERIOR CLARIFICATION / protected geometry makes shelf-only relocation invisible\nThis is a measured proposal diagram, not evidence that the exception has been approved.',fontsize=13)
fig.tight_layout(rect=[0,0,1,.92]);fig.savefig(V/'shop-interior-exception-proposal.png',dpi=160);fig.savefig(V/'shop-interior-exception-proposal.svg');plt.close(fig)
print('DENSITY_AND_PROPOSAL_SAVED',table,flush=True)
