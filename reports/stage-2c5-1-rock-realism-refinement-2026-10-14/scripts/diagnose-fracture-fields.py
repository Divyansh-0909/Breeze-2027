from pathlib import Path
import sys,json
import numpy as np
sys.path.insert(0,'scripts/blender')
import foundation_geometry as a,refined_foundation_geometry as b
s,y=np.meshgrid(np.linspace(a.START+4,a.END-4,850),np.linspace(2,31,700));rows={}
for name,g in[('before',a),('refined',b)]:
    du=(g.rock_relief(s+.006,y)-g.rock_relief(s-.006,y))/.012
    dy=(g.rock_relief(s,y+.006)-g.rock_relief(s,y-.006))/.012
    rows[name]={'slopeP50':float(np.percentile(abs(du),50)),'slopeP95':float(np.percentile(abs(du),95)),
      'slopeP99':float(np.percentile(abs(du),99)),'steepSideFractionAbove2':float((abs(du)>2).mean()),
      'maxSlope':float(abs(du).max()),'heightSlopeP95':float(np.percentile(abs(dy),95))}
Path('reports/stage-2c5-1-rock-realism-refinement-2026-10-14/raw/fracture-field-diagnosis.json').write_text(json.dumps(rows,indent=2))
print(json.dumps(rows,indent=2))
