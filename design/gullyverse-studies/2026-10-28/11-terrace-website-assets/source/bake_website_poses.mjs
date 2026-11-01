// Offline source-equivalence calculation. Does not start or build the website.
import fs from 'node:fs';
import path from 'node:path';
import {createRequire} from 'node:module';
import {fileURLToPath} from 'node:url';
const O=path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const depsRoot=process.env.GULLYVERSE_SOURCE_REPO??(fs.existsSync('/workspace/Breeze-2027-wip-push/package.json')?'/workspace/Breeze-2027-wip-push':path.join(O,'source/website/code'));
const require=createRequire(path.join(depsRoot,'package.json'));
const three=path.dirname(path.dirname(require.resolve('three')));
const THREE=await import(path.join(three,'build/three.module.js'));
const {GLTFLoader}=await import(path.join(three,'examples/jsm/loaders/GLTFLoader.js'));
const {mergeGeometries}=await import(path.join(three,'examples/jsm/utils/BufferGeometryUtils.js'));
const src=fs.readFileSync(path.join(O,'source/website/code/components/landing-page/stage3d/Crowd.tsx'),'utf8');
// Execute EXACT source bakePose implementation, with its TypeScript annotations removed.
let fn=src.slice(src.indexOf('function bakePose('),src.indexOf('\ntype Person'));
fn=fn.replace('root: THREE.Object3D, clips: THREE.AnimationClip[], time: number): THREE.BufferGeometry','root, clips, time)')
 .replace('const geoms: THREE.BufferGeometry[]','const geoms').replace('let merged: THREE.BufferGeometry | null','let merged')
 .replace('o as THREE.SkinnedMesh','o').replace(' as THREE.BufferAttribute','').replace('merged.boundingBox!','merged.boundingBox');
const bakePose=new Function('THREE','mergeGeometries',fn+'; return bakePose;')(THREE,mergeGeometries);
const rows=[];
for(const name of ['Man.glb','Animated-Woman.glb']){
 const bytes=fs.readFileSync(path.join(O,'source/website',name));
 const gltf=await new GLTFLoader().parseAsync(bytes.buffer.slice(bytes.byteOffset,bytes.byteOffset+bytes.byteLength),'');
 const bb=new THREE.Box3().setFromObject(gltf.scene),clip=gltf.animations.find(c=>/idle_neutral/i.test(c.name))??gltf.animations.find(c=>/idle/i.test(c.name))??gltf.animations[0];
 for(const t of [.35,1.35]){
  const geo=bakePose(gltf.scene,gltf.animations,t);geo.computeBoundingBox();
  rows.push({family:name,time:t,clip:clip?.name,nativeBounds:{min:bb.min.toArray(),max:bb.max.toArray()},normalizedBounds:{min:geo.boundingBox.min.toArray(),max:geo.boundingBox.max.toArray()},positions:Array.from(geo.attributes.position.array),normals:Array.from(geo.attributes.normal.array),indices:Array.from(geo.index.array),triangles:geo.index.count/3});
 }
}
fs.writeFileSync(path.join(O,'source/website/exact-baked-poses.json'),JSON.stringify(rows));
console.log(JSON.stringify(rows.map(({positions,normals,indices,...r})=>r),null,2));
