import bpy
m=bpy.data.objects['REV11 / ONE continuous shared-wall structural shell'].data;a=[[]for v in m.vertices]
for e in m.edges:u,v=e.vertices;a[u].append(v);a[v].append(u)
seen=set()
for i in range(len(a)):
 if i in seen:continue
 todo=[i];seen.add(i);ids=[]
 while todo:
  u=todo.pop();ids.append(u)
  for v in a[u]:
   if v not in seen:seen.add(v);todo.append(v)
 print('COMPONENT',len(ids),[(min(m.vertices[v].co[k]for v in ids),max(m.vertices[v].co[k]for v in ids))for k in range(3)])
