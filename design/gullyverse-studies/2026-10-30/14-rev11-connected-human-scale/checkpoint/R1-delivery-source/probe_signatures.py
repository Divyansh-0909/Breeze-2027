import sys,json
sys.path.insert(0,'/dev/shm/rev11/source');from scene_snapshot import snapshot
p=json.load(open('/dev/shm/rev11/evidence/source-signatures.json'))['objects'];n=snapshot('/dev/shm/rev11/source/Gullyverse-Rev11-Connected-Neighborhood.blend')[0]
for k in p:
 if p[k]!=n[k]:print(k,{x:[p[k][x],n[k][x]]for x in p[k]if p[k][x]!=n[k][x]})
