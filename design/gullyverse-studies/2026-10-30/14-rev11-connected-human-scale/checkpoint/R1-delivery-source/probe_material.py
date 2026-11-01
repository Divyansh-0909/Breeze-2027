import bpy
for name in ['WORLD / warm grey limewash','WORLD / continuous roof concrete','WORLD / mineral concrete']:
 m=bpy.data.materials[name];print('MAT',name)
 for n in m.node_tree.nodes:
  print(n.type,[(i.name,list(i.default_value)if hasattr(i.default_value,'__len__')else i.default_value)for i in n.inputs if hasattr(i,'default_value')and i.name in ['Scale','Vector']])
 print('LINKS',[(l.from_node.type,l.from_socket.name,l.to_node.type,l.to_socket.name)for l in m.node_tree.links])
