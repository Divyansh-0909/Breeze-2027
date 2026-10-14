import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import manifest from '../../public/models/gullyverse/quarry-foundation-refined/manifest.json';
import baseline from '../../public/models/gullyverse/quarry-foundation/manifest.json';

function glb(directory:string,name:string){
 const file=readFileSync('public/models/gullyverse/'+directory+'/'+name),length=file.readUInt32LE(12);
 return{doc:JSON.parse(file.subarray(20,20+length).toString()),binary:file.subarray(28+length)};
}
function values(doc:any,binary:Buffer,id:number):number[][]{
 const a=doc.accessors[id],view=doc.bufferViews[a.bufferView],width=({SCALAR:1,VEC2:2,VEC3:3,VEC4:4}as Record<string,number>)[a.type];
 const size=({5126:4,5125:4,5123:2,5121:1}as Record<number,number>)[a.componentType],rows=[];
 assert.ok(size,'Supported actual export accessor');
 for(let i=0;i<a.count;i++){
  const row=[];for(let j=0;j<width;j++){
   const at=(view.byteOffset??0)+(a.byteOffset??0)+i*(view.byteStride??width*size)+j*size;
   let value=a.componentType===5126?binary.readFloatLE(at):a.componentType===5125?binary.readUInt32LE(at):a.componentType===5123?binary.readUInt16LE(at):binary.readUInt8(at);
   if(a.normalized)value/=a.componentType===5123?65535:255;row.push(value);
  }rows.push(row);
 }return rows;
}

test('refined candidate is limited to the same two adjacent regions and shared material family',()=>{
 assert.equal(createHash('sha256').update(readFileSync('public/models/gullyverse/blockout.layout.json')).digest('hex'),manifest.worldRegistrySHA256);
 assert.deepEqual(manifest.regions,baseline.regions);
 assert.deepEqual(manifest.parts.filter(p=>p.refined).map(p=>p.id),['Wall_13','Wall_14','Wall_15']);
 assert.equal(manifest.materialRuntime,baseline.materialRuntime);
 assert.deepEqual(manifest.materials,baseline.materials);
 assert.ok(manifest.trianglesByLOD.every((n,i)=>n<=baseline.trianglesByLOD[i]),'Shape refinement must not rely on increased triangle count');
 assert.ok(manifest.nodes.every(n=>n.zeroAreaFaces===0&&n.nonManifoldInteriorEdges===0));
});

test('accepted cliff image payloads remain identical; only outer-terrain maps may change',()=>{
 const before=glb('quarry-foundation',baseline.materialRuntime),after=glb('quarry-foundation-refined',manifest.materialRuntime);
 const images=(data:ReturnType<typeof glb>)=>new Map<string,string>(data.doc.images.map((im:any)=>{
  const v=data.doc.bufferViews[im.bufferView];return[im.name,createHash('sha256').update(data.binary.subarray(v.byteOffset??0,(v.byteOffset??0)+v.byteLength)).digest('hex')];
 }));
 const a=images(before),b=images(after);assert.equal(b.size,6);assert.equal(after.doc.materials.length,2);
 const rock=[...a.keys()].filter(n=>n.startsWith('dark-rock'));
 assert.equal(rock.length,3);for(const name of rock)assert.equal(b.get(name),a.get(name),name+' must retain approved cliff pixels');
});

test('remaining cliff positions and indices are unchanged in the actual runtime exports',()=>{
 const before=glb('quarry-foundation',baseline.runtime),after=glb('quarry-foundation-refined',manifest.runtime);
 for(const node of after.doc.nodes){
  const match=/^Foundation_Wall_(\d+)_LOD\d$/.exec(node.name??'');if(!match||[13,14,15].includes(Number(match[1])))continue;
  const prior=before.doc.nodes.find((n:any)=>n.name===node.name);assert.ok(prior);
  const a=after.doc.meshes[node.mesh].primitives[0],b=before.doc.meshes[prior.mesh].primitives[0];
  assert.deepEqual(values(after.doc,after.binary,a.attributes.POSITION),values(before.doc,before.binary,b.attributes.POSITION),node.name+' position preservation');
  assert.deepEqual(values(after.doc,after.binary,a.indices),values(before.doc,before.binary,b.indices),node.name+' topology preservation');
 }
});

test('actual exported frames and neutral mineral factors remain valid at all LODs',()=>{
 const {doc,binary}=glb('quarry-foundation-refined',manifest.runtime);assert.equal(doc.images,undefined);
 for(const mesh of doc.meshes)for(const primitive of mesh.primitives){
  const attr=primitive.attributes,n=values(doc,binary,attr.NORMAL),t=values(doc,binary,attr.TANGENT);
  for(const uv of values(doc,binary,attr.TEXCOORD_0))assert.ok(uv.every(Number.isFinite));
  for(const c of values(doc,binary,attr.COLOR_0)){
   assert.ok(c.every(v=>v>=.85&&v<=1));assert.ok(Math.max(...c.slice(0,3))-Math.min(...c.slice(0,3))<.025);
  }
  for(let i=0;i<n.length;i++){
   assert.ok(Math.abs(Math.hypot(...n[i])-1)<2e-4);assert.ok(Math.abs(Math.hypot(...t[i].slice(0,3))-1)<2e-4);
   assert.equal(Math.abs(t[i][3]),1);assert.ok(Math.abs(n[i][0]*t[i][0]+n[i][1]*t[i][1]+n[i][2]*t[i][2])<2e-3);
  }
 }
});

test('scree caps wind outward rather than producing inverted ground-contact faces',()=>{
 const {doc,binary}=glb('quarry-foundation-refined',manifest.runtime),node=doc.nodes.find((n:any)=>n.name==='Foundation_Foot_Scree_LOD0');
 const mesh=doc.meshes[node.mesh].primitives[0],p=values(doc,binary,mesh.attributes.POSITION),indices=values(doc,binary,mesh.indices).flat();
 let top=0,bottom=0;
 for(let i=0;i<indices.length;i+=3){
  const a=p[indices[i]],b=p[indices[i+1]],c=p[indices[i+2]];
  const crossY=(b[2]-a[2])*(c[0]-a[0])-(b[0]-a[0])*(c[2]-a[2]);
  if(a[1]<-.049&&b[1]<-.049&&c[1]<-.049){assert.ok(crossY<0);bottom++;}
  if(a[1]>.025&&b[1]>.025&&c[1]>.025){assert.ok(crossY>0);top++;}
 }
 assert.equal(top,45*4);assert.equal(bottom,45*4);
});
