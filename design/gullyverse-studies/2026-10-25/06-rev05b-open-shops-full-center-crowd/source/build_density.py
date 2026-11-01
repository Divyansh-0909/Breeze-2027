from pathlib import Path
import json,csv,math
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
O=Path(__file__).resolve().parents[1];R=O/'review'
old=json.loads((O/'source/baseline/organic-crowd-authoring.json').read_text())['actors'];new=json.loads((O/'evidence/rev05b-authoring.json').read_text())['actors']
def visible(r,v):
    return not r['label'].startswith(('Festival extra','Balanced extra'))or(v=='B'and r['label'].startswith('Festival extra'))or(v=='C'and r['label'].startswith('Balanced extra'))
fig,axes=plt.subplots(3,2,figsize=(12,17));table=[]
for i,v in enumerate(['A','B','C']):
    rec={'variant':v}
    for j,(edition,rows)in enumerate([('before',old),('after',new)]):
        points=np.array([r['foot'][:2]for r in rows if visible(r,v)]);ax=axes[i,j]
        binsx=np.arange(-16,16.1,2);binsy=np.arange(20,46.1,2);hist,xx,yy=np.histogram2d(points[:,0],points[:,1],bins=[binsx,binsy]);ax.pcolormesh(xx,yy,hist.T,cmap='YlOrBr',vmin=0,vmax=8,shading='flat');ax.scatter(points[:,0],points[:,1],s=11,c='#202b3a',alpha=.8)
        ax.plot([0,0],[20,36.5],c='#027b9a',lw=1.4,label='Unchanged straight camera route')
        ax.add_patch(Rectangle((-1.65,30.5),3.3,14.6,fill=False,ls='--',lw=1,ec='#b03e40',label='Previous broad gap'))
        if edition=='after':ax.add_patch(Rectangle((-.45,23.4),.9,13.55,fill=False,lw=1.1,ec='#00927e',label='Narrow body clearance until Y36.95'))
        ax.axhline(45.8,c='#653447',lw=2);ax.text(-15.5,45.9,'Screen anchor',fontsize=8)
        ax.set(xlim=(-16,16),ylim=(20,46.5),aspect='equal',xlabel='X / metres',ylabel='Y / metres',title=f'{v} / {edition.upper()} / {len(points)} audience')
        ax.grid(alpha=.15);rec[edition]={'audience':len(points),'occupied2mCells':int((hist>0).sum()),'maxActorsPer4m2Cell':int(hist.max()),'centerInsideOldGapAboveY37':int(((abs(points[:,0])<1.65)&(points[:,1]>37)).sum())}
    table.append(rec)
handles,labels=axes[-1,-1].get_legend_handles_labels();fig.legend(handles,labels,loc='lower center',ncol=1,fontsize=9)
fig.suptitle('Rev05A -> Rev05B / 2m occupancy cells and actual foot centers\nBody collision and camera tolerances are validated separately; these are density diagrams, not renders.',fontsize=12)
fig.tight_layout(rect=[0,.065,1,.965]);fig.savefig(R/'density-occupancy.png',dpi=150);fig.savefig(R/'density-occupancy.svg');plt.close(fig)
roles={'board':(6,11*3.6),'transition':(14,17*4.5),'middle':(36,21*5.1),'dense':(92,21.6*5.9),'left_wing':(14,4.9*11.9),'right_wing':(14,4.9*12.2)}
zones=[]
for v in ['A','B','C']:
    for role,(_,area)in roles.items():
        count=sum(r['role']==role and visible(r,v)for r in new);zones.append({'variant':v,'authoredZone':role,'actualActors':count,'samplingDomainAreaM2':area,'actorsPerSamplingDomainM2':count/area})
fig,ax=plt.subplots(figsize=(10,5));names=['board','transition','middle','dense']
for j,v in enumerate(['A','B','C']):
    ys=[next(x['actorsPerSamplingDomainM2']for x in zones if x['variant']==v and x['authoredZone']==n)for n in names];ax.plot(names,ys,marker='o',label=v)
ax.set(title='Low -> medium -> dense: authored population gradient',ylabel='Actors / m2 of sampling domain');ax.legend(title='Variant');ax.grid(alpha=.2);fig.tight_layout();fig.savefig(R/'density-gradient.png',dpi=150);plt.close(fig)
(O/'evidence/density-table.json').write_text(json.dumps({'status':'MEASURED','cellSideM':2,'gridOriginXY':[-16,20],'gridBoundsXY':[[-16,16],[20,46]],'beforeAfter':table,'authoredZones':zones,'zoneAreaCaveat':'Sampling domains overlap at their edges; these are comparative authored-zone measures, not summed physical occupied floor area or an art score. Cell counts are compared on this same grid, whose X origin differs from the prior Rev05A standalone chart.','fixedLaneCypherPeopleExcluded':9},indent=2)+'\n')
with (O/'evidence/density-zones.csv').open('w',newline='')as f:
    w=csv.DictWriter(f,fieldnames=list(zones[0]));w.writeheader();w.writerows(zones)
print('DENSITY_MAPS_COMPLETE',table)
