import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=Path('reports/current-final-review-2026-10-11');x=json.load(open(r/'raw/resource-summary.json'));fig,axes=plt.subplots(1,2,figsize=(11,4));n=range(1,11)
axes[0].plot(n,x['settledThreeTextures'],'o-',label='Three textures');axes[0].plot(n,x['settledGLTextures'],'o-',label='Tracked GL textures');axes[0].set(xlabel='Completed playback / return cycle',ylabel='Settled resource count',title='Texture counters plateau');axes[0].set_ylim(20,35);axes[0].legend();axes[0].grid(alpha=.2)
axes[1].plot(n,[v/1e6 for v in x['heapBytes']],'o-');axes[1].set(xlabel='Completed playback / return cycle',ylabel='Post-GC JS heap (decimal MB)',title='Heap trend requires longer soak');axes[1].grid(alpha=.2);fig.suptitle('Chromium / SwiftShader, 1366×900, DPR 0.25 — counters are not driver VRAM');fig.tight_layout();fig.savefig(r/'resource-lifecycle.png',dpi=160);fig.savefig(r/'resource-lifecycle.svg');plt.close(fig)
p=json.load(open(r/'raw/current-performance.json'));fig,ax=plt.subplots(figsize=(9,4))
for label,name in [('Hub','hub-local-movement'),('Stage','aftermovie-local-movement')]:
 w=next(w for w in p['windows'] if w['name']==name);times=sorted(f['ms'] for f in w['frames'] if f.get('cpuRenderMs') is not None);ax.step(times,[(i+1)*100/len(times) for i in range(len(times))],where='post',label=f'{label}: {len(times)} rendered samples')
ax.set(xlabel='Frame interval (ms)',ylabel='Empirical percentile (%)',title='Actual software-rendered frame intervals; short windows, not physical GPU acceptance');ax.grid(alpha=.2);ax.legend();fig.tight_layout();fig.savefig(r/'frame-intervals.png',dpi=160);fig.savefig(r/'frame-intervals.svg');plt.close(fig)
