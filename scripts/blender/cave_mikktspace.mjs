// Offline correction using Three's already bundled MikkTSpace authoring tool.
// No runtime loader dependency. Rebuild frames from actual exported UVs/normals,
// splitting a vertex where real tangent seams require different corner frames.
import {readFile, writeFile} from "node:fs/promises";
import assert from "node:assert/strict";
import * as Mikk from "three/examples/jsm/libs/mikktspace.module.js";

await Mikk.ready;
const path=process.argv[2];assert.ok(path);
const data=await readFile(path),jsonLength=data.readUInt32LE(12);
const frameArg=process.argv.indexOf('--shared-normals');
const canonicalFrames=frameArg>=0?JSON.parse(await readFile(process.argv[frameArg+1],'utf8')):[];
const positionKey=p=>Array.from(p,x=>Math.round(x*1e5)).join('/');
const commonNormals=new Map(canonicalFrames.map(f=>[positionKey(f.position),f.normal]));
const document=JSON.parse(data.subarray(20,20+jsonLength)),binary=data.subarray(28+jsonLength);
const widths={SCALAR:1,VEC2:2,VEC3:3,VEC4:4},sizes={5121:1,5123:2,5125:4,5126:4};
function read(index) {
  const a=document.accessors[index],v=document.bufferViews[a.bufferView],w=widths[a.type];
  const out=a.componentType===5126||a.normalized?new Float32Array(a.count*w):new Uint32Array(a.count*w);
  const start=(v.byteOffset||0)+(a.byteOffset||0),stride=v.byteStride||w*sizes[a.componentType];
  for(let i=0;i<a.count;i++)for(let j=0;j<w;j++) {
    const p=start+i*stride+j*sizes[a.componentType];
    out[i*w+j]=a.componentType===5126?binary.readFloatLE(p):a.componentType===5125?binary.readUInt32LE(p):a.componentType===5123?binary.readUInt16LE(p):binary.readUInt8(p);
    if(a.normalized)out[i*w+j]/=a.componentType===5123?65535:255;
  }
  return out;
}
const buffers=[],views=[],accessors=[],rows=[];let offset=0,sign=null;
function append(array,type,componentType,target,min,max) {
  const bytes=Buffer.from(array.buffer,array.byteOffset,array.byteLength),padding=(4-offset%4)%4;
  if(padding){buffers.push(Buffer.alloc(padding));offset+=padding;}
  const vi=views.length;views.push({buffer:0,byteOffset:offset,byteLength:bytes.length,target});buffers.push(bytes);offset+=bytes.length;
  const i=accessors.length;accessors.push({bufferView:vi,componentType,count:array.length/widths[type],type,...(min?{min,max}:{})});return i;
}
for(const node of document.nodes) {
  if(node.mesh===undefined)continue;
  const level=Number(node.name.match(/LOD(\d)/)[1]);
  for(const primitive of document.meshes[node.mesh].primitives) {
    const source={};for(const [name,index]of Object.entries(primitive.attributes))source[name]=read(index);
    if(/Cave_(Throat|Passage)/.test(node.name))for(let i=0;i<source.POSITION.length/3;i++){
      const n=commonNormals.get(positionKey(source.POSITION.subarray(i*3,i*3+3)));
      if(n)source.NORMAL.set(n,i*3);
    }
    const indices=read(primitive.indices),uv=source["TEXCOORD_0"];
    const positions=new Float32Array(indices.length*3),normals=new Float32Array(indices.length*3),coords=new Float32Array(indices.length*2);
    for(let i=0;i<indices.length;i++) {
      const j=indices[i];positions.set(source.POSITION.subarray(j*3,j*3+3),i*3);normals.set(source.NORMAL.subarray(j*3,j*3+3),i*3);coords.set(uv.subarray(j*2,j*2+2),i*2);
    }
    const tangents=Mikk.generateTangents(positions,normals,coords);let same=0,opposite=0,agreement=0,samples=0;
    for(let i=0;i<indices.length;i++) {
      const j=indices[i],a=source.TANGENT.subarray(j*4,j*4+4),b=tangents.subarray(i*4,i*4+4);
      if(Math.hypot(...a.subarray(0,3))<.99)continue;
      if(a[3]===b[3])same++;else opposite++;
      agreement+=a[0]*b[0]+a[1]*b[1]+a[2]*b[2];samples++;
    }
    if(level===0){sign=same>=opposite?1:-1;assert.ok(Math.max(same,opposite)/(same+opposite)>.99,"Cannot infer existing near-material handedness");}
    assert.ok(sign===1||sign===-1);
    const lookup=new Map(),newIndices=new Uint32Array(indices.length),attributes={};
    for(const name of Object.keys(source))attributes[name]=[];
    let count=0;
    for(let corner=0;corner<indices.length;corner++) {
      const old=indices[corner],t=Array.from(tangents.subarray(corner*4,corner*4+4));t[3]*=sign;
      assert.ok(Math.abs(Math.hypot(...t.slice(0,3))-1)<1e-4&&Math.abs(t[3])===1,
        'Invalid genuine Mikk derivative '+JSON.stringify({node:node.name,corner,tangent:t,normal:Array.from(normals.subarray(corner*3,corner*3+3)),uv:Array.from(coords.subarray(corner*2,corner*2+2))}));
      const key=old+"/"+t.join(",");let index=lookup.get(key);
      if(index===undefined) {
        index=count++;lookup.set(key,index);
        for(const name of Object.keys(source)) {
          const width=widths[document.accessors[primitive.attributes[name]].type];
          attributes[name].push(...(name==="TANGENT"?t:source[name].subarray(old*width,old*width+width)));
        }
      }
      newIndices[corner]=index;
    }
    const originalAccessors={...primitive.attributes};primitive.attributes={};
    for(const [name,values]of Object.entries(attributes)) {
      const original=document.accessors[originalAccessors[name]],a=new Float32Array(values);
      primitive.attributes[name]=append(a,original.type,5126,34962,original.min,original.max);
    }
    primitive.indices=append(count<65536?new Uint16Array(newIndices):newIndices,"SCALAR",count<65536?5123:5125,34963);
    rows.push({LOD:level,normalUV:0,oldVertices:source.POSITION.length/3,newVertices:count,
      referenceHandedness:sign,oldTangentDirectionMeanDot:agreement/samples,actualUVFramesRegenerated:true});
  }
}
let payload=Buffer.concat(buffers);if(payload.length%4)payload=Buffer.concat([payload,Buffer.alloc(4-payload.length%4)]);
document.accessors=accessors;document.bufferViews=views;document.buffers=[{byteLength:payload.length}];
let encoded=Buffer.from(JSON.stringify(document));if(encoded.length%4)encoded=Buffer.concat([encoded,Buffer.alloc(4-encoded.length%4,32)]);
const header=Buffer.alloc(20);header.writeUInt32LE(0x46546c67,0);header.writeUInt32LE(2,4);header.writeUInt32LE(28+encoded.length+payload.length,8);header.writeUInt32LE(encoded.length,12);header.writeUInt32LE(0x4e4f534a,16);
const binHeader=Buffer.alloc(8);binHeader.writeUInt32LE(payload.length,0);binHeader.writeUInt32LE(0x004e4942,4);
if(!process.argv.includes("--audit"))await writeFile(path,Buffer.concat([header,encoded,binHeader,payload]));
console.log(JSON.stringify({readOnlyAudit:process.argv.includes("--audit"),method:"Actual exported UV0/UV1 MikkTSpace, existing near-material handedness, real tangent-seam vertex splits",rows,bytes:28+encoded.length+payload.length}));
