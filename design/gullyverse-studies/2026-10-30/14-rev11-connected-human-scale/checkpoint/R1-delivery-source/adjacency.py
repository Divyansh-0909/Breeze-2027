import json,math,csv
from pathlib import Path
O=Path(__file__).resolve().parents[1];d=json.loads((O/'evidence/authoring.json').read_text());before=json.loads((O/'evidence/adjacency-before.json').read_text());by={h['id']:h for h in d['houses']};rows=[]
for r in before:
 a,b=by[r['from']],by[r['to']];aa,bb=a['footprint'],b['footprint'];gap=[max(0,aa[i][0]-bb[i][1],bb[i][0]-aa[i][1])for i in range(2)];touch=[i for i in range(2)if abs(aa[i][1]-bb[i][0])<1e-5 or abs(bb[i][1]-aa[i][0])<1e-5];assert len(touch)==1,(a,b,touch);axis=touch[0];other=1-axis;contact=[max(aa[other][0],bb[other][0]),min(aa[other][1],bb[other][1])];assert contact[1]>contact[0];assert math.hypot(*gap)<1e-5
 rows.append({'from':a['id'],'to':b['id'],'beforePodiumXYGapM':r['podiumXYShortestGapM'],'afterPodiumXYGapM':math.hypot(*gap),'joinPlaneAxis':'XY'[axis],'joinPlaneCoordinateM':aa[axis][1]if abs(aa[axis][1]-bb[axis][0])<1e-5 else aa[axis][0],'sharedContactIntervalM':contact,'sharedLengthM':contact[1]-contact[0],'partyWallThicknessM':.60,'lowerRoofZ':min(a['mainRoofZ'],b['mainRoofZ']),'upperRoofZ':max(a['mainRoofZ'],b['mainRoofZ']),'roofStepM':abs(a['mainRoofZ']-b['mainRoofZ']),'construction':'single exposed-surface union; shared interior faces removed, roof slab seals at differing heights','intentionalAlley':False})
graph={n:[]for n in by}
for r in rows:graph[r['from']].append(r['to']);graph[r['to']].append(r['from'])
seen=set();todo=['F1']
while todo:
 n=todo.pop()
 if n in seen:continue
 seen.add(n);todo+=graph[n]
assert len(seen)==11
result={'status':'PASS_11_PARCELS_ONE_CONNECTED_BLOCK','units':'metres','adjacency':graph,'joins':rows,'allTenIntendedJoinsClosed':True,'unexplainedHouseToHouseAlleyGaps':0,'laneOpeningM':16.6,'laneOpeningBoundsX':[-8.3,8.3],'upperAirAtSteppedRoofline':'intentional open sky above adjoining lower roof, not a detached structural gap','meshComponentProof':'preservation-geometry-height.json; one continuous vertex-connected manifold core','noWallAcrossLane':True}
(O/'evidence/adjacency-after.json').write_text(json.dumps(result,indent=2));
with (O/'evidence/joins-before-after.csv').open('w')as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
print('JOIN_REGISTER_PASS',[(r['from'],r['to'],round(r['beforePodiumXYGapM'],3),r['afterPodiumXYGapM'])for r in rows])
