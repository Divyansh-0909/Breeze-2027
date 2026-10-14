import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import manifest from '../../public/models/gullyverse/quarry-foundation/manifest.json';

function glb(name:string){
 const data=readFileSync('public/models/gullyverse/quarry-foundation/'+name),size=data.readUInt32LE(12);
 const doc=JSON.parse(data.subarray(20,20+size).toString()),binary=data.subarray(28+size);
 return{doc,binary};
}
function values(doc:any,binary:Buffer,id:number){
 const a=doc.accessors[id],v=doc.bufferViews[a.bufferView],n=({SCALAR:1,VEC2:2,VEC3:3,VEC4:4}as Record<string,number>)[a.type];
 const size=a.componentType===5126?4:a.componentType===5123?2:1,rows:number[][]=[];
 for(let i=0;i<a.count;i++){
  const row=[];for(let j=0;j<n;j++){
   const offset=(v.byteOffset??0)+(a.byteOffset??0)+i*(v.byteStride??n*size)+j*size;
   let value=a.componentType===5126?binary.readFloatLE(offset):a.componentType===5123?binary.readUInt16LE(offset):binary.readUInt8(offset);
   if(a.normalized)value/=a.componentType===5123?65535:255;row.push(value);
  }rows.push(row);
 }return rows;
}

test('foundation export preserves anchors and contains only two adjacent art regions',()=>{
 assert.equal(createHash('sha256').update(readFileSync('public/models/gullyverse/blockout.layout.json')).digest('hex'),manifest.worldRegistrySHA256);
 assert.equal(manifest.regions.length,2);assert.equal(manifest.regions[0].arc[1],manifest.regions[1].arc[0]);
 assert.deepEqual(manifest.parts.filter(p=>p.refined).map(p=>p.id),['Wall_13','Wall_14','Wall_15']);
 assert.ok(manifest.nodes.every(n=>n.zeroAreaFaces===0&&n.nonManifoldInteriorEdges===0));
});
test('exported stone vertex colour cannot wrap into blue/black patches',()=>{
 const{doc,binary}=glb(manifest.runtime);
 for(const mesh of doc.meshes)for(const primitive of mesh.primitives){
  for(const c of values(doc,binary,primitive.attributes.COLOR_0)){
   assert.ok(c.every((v:number)=>v>=.85&&v<=1),'Linear mineral factors must remain within normalized colour range');
   assert.ok(Math.max(...c.slice(0,3))-Math.min(...c.slice(0,3))<.025,'Dark neutral colour direction must not acquire saturated channels');
  }
 }
});
test('geometry-only exports have finite metre UVs and orthogonal glTF tangent frames',()=>{
 const{doc,binary}=glb(manifest.runtime);assert.equal(doc.images,undefined);
 for(const mesh of doc.meshes)for(const primitive of mesh.primitives){
  const attr=primitive.attributes,normals=values(doc,binary,attr.NORMAL),tangents=values(doc,binary,attr.TANGENT);
  for(const uv of values(doc,binary,attr.TEXCOORD_0))assert.ok(uv.every(Number.isFinite));
  for(let i=0;i<normals.length;i++){
   const n=normals[i],t=tangents[i];assert.ok(Math.abs(Math.hypot(...n)-1)<2e-4);
   assert.ok(Math.abs(Math.hypot(...t.slice(0,3))-1)<2e-4);assert.equal(Math.abs(t[3]),1);
   assert.ok(Math.abs(n[0]*t[0]+n[1]*t[1]+n[2]*t[2])<2e-3);
  }
 }
});
