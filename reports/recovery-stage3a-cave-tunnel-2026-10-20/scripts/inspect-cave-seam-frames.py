from pathlib import Path
import numpy as np,json,math
ROOT=Path.cwd();R=ROOT/'reports/recovery-stage3a-cave-tunnel-2026-10-20/raw';s=(R.parent/'scripts/validate-cave-geometry.py').read_text();scope={};exec(s[:s.index('new=load(')],scope);new=scope['load'](ROOT/'public/models/gullyverse/c9-cave-recovery/cave-entrance.glb')
rows=[]
for pa,pb,z in [('Throat','Passage1',-6),('Passage1','Passage2',-15),('Passage2','Passage3',-24),('Passage3','Passage4',-33)]:
 for la in range(3):
  for lb in range(3):
   a,_=new[f'Cave_{pa}_LOD{la}'];b,_=new[f'Cave_{pb}_LOD{lb}'];ai=np.where(abs(a['POSITION'][:,2]-z)<1e-5)[0];bi=np.where(abs(b['POSITION'][:,2]-z)<1e-5)[0];angles=[];uv=[];normal_errors=[]
   for i in ai:
    d=np.linalg.norm(b['POSITION'][bi]-a['POSITION'][i],axis=1);js=bi[d<2e-5];assert len(js)
    n=a['NORMAL'][i].astype('float64');ns=b['NORMAL'][js].astype('float64');dot=float(np.max((ns@n)/(np.linalg.norm(ns,axis=1)*np.linalg.norm(n))));angles.append(math.degrees(math.acos(np.clip(dot,-1,1))));uv.append(float(np.linalg.norm(b['TEXCOORD_0'][js]-a['TEXCOORD_0'][i],axis=1).min()));normal_errors.append(float(np.linalg.norm(ns-n,axis=1).min()))
   rows.append({'a':pa,'b':pb,'levels':[la,lb],'maximumMatchedUVError':max(uv),'maximumMatchedNormalVectorError':max(normal_errors),'normalAngleP50Degrees':float(np.median(angles)),'normalAngleP95Degrees':float(np.quantile(angles,.95)),'normalAngleMaximumDegrees':max(angles)})
maximum=max(r['maximumMatchedNormalVectorError']for r in rows)
result={'status':'PASS'if maximum<=1e-4 and max(r['maximumMatchedUVError']for r in rows)==0 else'FAIL','method':'Exact shared positions within unchanged2e-5m positional gate; best matching legitimate normal variant at UV/sharp seams. Angles calculated from normalized float64 vectors; raw component difference checked separately against the existing 1e-4 unit-frame precision gate.','rows':rows,'maximumNormalVectorError':maximum,'maximumNormalAngleDegrees':max(r['normalAngleMaximumDegrees']for r in rows),'maximumUVError':max(r['maximumMatchedUVError']for r in rows)}
(R/'cave-seam-frame-measurements.json').write_text(json.dumps(result,indent=2)+'\n');print('SHARED_NORMAL_FRAME_RESULT',result['status'],'NORMAL_VECTOR_MAX',maximum,'ANGLE_MAX',result['maximumNormalAngleDegrees'])
assert result['status']=='PASS'
