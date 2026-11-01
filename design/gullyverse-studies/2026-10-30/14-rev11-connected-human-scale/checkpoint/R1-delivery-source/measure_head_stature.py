import bpy,json,statistics
from pathlib import Path
O=Path(__file__).resolve().parents[1];d=json.load(open(O/'evidence/before-survey.json'));rows=[]
for a in d['actors']:
 h=next(bpy.data.objects[n]for n in a['objects']if n.endswith(' head'));z=max((h.matrix_basis@v.co).z for v in h.data.vertices)-a['bounds'][0][2];rows.append({'label':a['label'],'headTopStatureM':z,'totalActorEnvelopeM':a['heightM'],'raisedAboveHeadM':a['heightM']-z})
values=[r['headTopStatureM']for r in rows];out={'method':'World-space head-mesh top above exact original feet; excludes raised arms. Geometric proxy, not a biological measurement.','original':{'minM':min(values),'medianM':statistics.median(values),'maxM':max(values)},'proposed7Percent':{'minM':min(values)*1.07,'medianM':statistics.median(values)*1.07,'maxM':max(values)*1.07},'actors':rows};(O/'evidence/head-top-stature.json').write_text(json.dumps(out,indent=2));print('HEAD_TOP_STATURE',out['original'],out['proposed7Percent'])
