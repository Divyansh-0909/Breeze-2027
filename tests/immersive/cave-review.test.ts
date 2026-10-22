import test from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import {GLTFLoader, type GLTF} from 'three/examples/jsm/loaders/GLTFLoader.js';
import {naturalCaveReview, carryCaveReview} from '../../components/immersive/caveReview';
import {caveLegacyInterface, mapCaveLegacyMaterial} from '../../components/immersive/caveLegacyInterface';
import {tunnelOutsideQuarryRear} from '../../components/immersive/quarryRollout';
import {CaveEntranceSession} from '../../components/immersive/CaveEntranceSession';
import {GeologyFidelitySession} from '../../components/immersive/GeologyFidelitySession';
import {ImmersiveRuntime} from '../../components/immersive/runtime';
import manifest from '../../public/models/gullyverse/c9-cave-recovery/manifest.json';
import entry from '../../public/models/gullyverse/c9-cave-recovery/entry-clearance.json';

test('natural cave is private and explicitly selected; old URLs do not opt in', () => {
  assert.equal(naturalCaveReview('?entranceReview=natural-cave', false), false);
  assert.equal(naturalCaveReview('?quarryReview=geology-fidelity', true), false);
  assert.equal(naturalCaveReview('?entranceReview=cave-tunnel', true), false);
  assert.equal(naturalCaveReview('?entranceReview=natural-cave', true), true);
});
test('private scanned material mapping preserves every legacy position and provides genuine unit UV tangent frames', () => {
  const geometry=caveLegacyInterface(true);
  const positions=Array.from(geometry.getAttribute('position').array), normals=Array.from(geometry.getAttribute('normal').array);
  try {
    mapCaveLegacyMaterial(geometry);
    assert.deepEqual(Array.from(geometry.getAttribute('position').array),positions);
    assert.deepEqual(Array.from(geometry.getAttribute('normal').array),normals);
    const t=geometry.getAttribute('tangent'),n=geometry.getAttribute('normal');
    for(let i=0;i<t.count;i++) {
      assert.ok(Math.abs(Math.hypot(t.getX(i),t.getY(i),t.getZ(i))-1)<1e-5);
      assert.ok(Math.abs(t.getX(i)*n.getX(i)+t.getY(i)*n.getY(i)+t.getZ(i)*n.getZ(i))<1e-5);
      assert.equal(Math.abs(t.getW(i)),1);
    }
    assert.ok(Array.from(geometry.getAttribute('color').array).every(v=>v===1));
  } finally {geometry.dispose();}
});
test('travel and direct routes carry the cave with the accepted corrected quarry', () => {
  const start = '?entranceReview=natural-cave&quarryReview=scanned-composition';
  for (const href of ['/?arrival=hub', '/aftermovie', '/team?arrival=team#top']) {
    const u = new URL(carryCaveReview(href, start, true), 'https://breeze.invalid');
    assert.equal(u.searchParams.get('quarryReview'), 'geology-fidelity');
    assert.equal(u.searchParams.get('entranceReview'), 'natural-cave');
    assert.equal(u.pathname, new URL(href, u.origin).pathname);
    assert.equal(u.hash, new URL(href, u.origin).hash);
  }
  assert.equal(carryCaveReview('/aftermovie', start, false), '/aftermovie');
  assert.equal(carryCaveReview('/aftermovie', '?quarryReview=scanned-composition', true), '/aftermovie?quarryReview=scanned-composition');
});
test('the replacement removes only the complete legacy inner tube, preserving every exterior attribute', () => {
  const old = tunnelOutsideQuarryRear(), next = caveLegacyInterface(true), removed = 56 * 10 * 3 * 6;
  try {
    for (const [name, attribute] of Object.entries(old.attributes)) {
      assert.deepEqual(Array.from(next.getAttribute(name).array), Array.from(attribute.array.slice(removed * attribute.itemSize)));
    }
    assert.equal(old.getAttribute('position').count - next.getAttribute('position').count, removed);
  } finally { old.dispose(); next.dispose(); }
});
function asset(clearance=false) {
  const scene = new THREE.Group(), geometries: THREE.BufferGeometry[] = [];
  for (const name of clearance ? entry.runtimeNodes : manifest.parts.flatMap(p => p.nodes)) {
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.Float32BufferAttribute([0,0,0, 1,0,0, 0,1,0],3));
    g.computeVertexNormals(); g.setAttribute('uv', new THREE.Float32BufferAttribute([0,0,1,0,0,1],2));
    g.setAttribute('tangent', new THREE.Float32BufferAttribute([1,0,0,1,1,0,0,1,1,0,0,1],4));
    g.setAttribute('color', new THREE.Float32BufferAttribute([1,1,1,1,1,1,1,1,1],3));
    const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial()); m.name = name; scene.add(m); geometries.push(g);
  }
  return {data: {scene, scenes:[scene], animations:[], cameras:[], asset:{version:'2.0'}, parser:{}, userData:{}} as unknown as GLTF, geometries};
}
test('direct stage defers unseen cave assets; first visible request stays covered and loads once', async () => {
  const oldLoader=GLTFLoader.prototype.loadAsync, oldBase=GeologyFidelitySession.prototype.load;
  let localLoads=0, baseLoads=0;
  GLTFLoader.prototype.loadAsync=async url=>{localLoads++;return asset(url.includes('entry-clearance')).data;};
  GeologyFidelitySession.prototype.load=async()=>{baseLoads++;};
  try {
    const owner=new CaveEntranceSession(new ImmersiveRuntime('aftermovie',()=>{},false,()=>0));
    await owner.load();assert.equal(localLoads,0);assert.equal(baseLoads,1);
    assert.equal(owner.entranceDiagnostics().visibilityLoading.deferredWhileOffscreen,true);
    owner.requireCave();owner.prepared(owner.state.revision,0,'hub');assert.equal(owner.state.busy,true);
    await owner.load();assert.equal(owner.entranceReady,true);assert.equal(localLoads,2);
    assert.equal(owner.entranceDiagnostics().visibilityLoading.requested,true);
    owner.requireCave();await owner.load();assert.equal(localLoads,2);owner.dispose();
  }finally{GLTFLoader.prototype.loadAsync=oldLoader;GeologyFidelitySession.prototype.load=oldBase;}
});
test('late entrance completion after retirement disposes all geometry and never reloads the parent', async () => {
  const oldLoader=GLTFLoader.prototype.loadAsync, oldBase=GeologyFidelitySession.prototype.load;
  let resolve!: (g:GLTF)=>void, parentLoads=0, disposed=0;
  const source=asset(); source.geometries.forEach(g=>g.addEventListener('dispose',()=>disposed++));
  GLTFLoader.prototype.loadAsync=()=>new Promise(r=>{resolve=r;});
  GeologyFidelitySession.prototype.load=async()=>{parentLoads++;};
  try {
    const owner=new CaveEntranceSession(new ImmersiveRuntime('hub',()=>{},false,()=>0));
    const pending=owner.load();
    assert.throws(()=>owner.retire(), /Unmount cave consumers/);
    assert.equal(disposed,0);
    owner.setMode('off'); owner.prepared(owner.state.revision,0,'hub');
    owner.retire(); resolve(source.data); await pending;
    assert.equal(disposed, manifest.parts.length*3); assert.equal(parentLoads,0); assert.equal(owner.entranceReady,false);
  } finally {GLTFLoader.prototype.loadAsync=oldLoader;GeologyFidelitySession.prototype.load=oldBase;}
});
test('failed optional entrance preserves selected quarry loading and supports a clean retry', async () => {
  const oldLoader=GLTFLoader.prototype.loadAsync,oldBase=GeologyFidelitySession.prototype.load;
  let calls=0,parentLoads=0; const source=asset();
  GLTFLoader.prototype.loadAsync=async url=>{if(++calls===1)throw new Error('network');return url.includes('entry-clearance') ? asset(true).data : source.data;};
  GeologyFidelitySession.prototype.load=async()=>{parentLoads++;};
  try{
    const owner=new CaveEntranceSession(new ImmersiveRuntime('hub',()=>{},false,()=>0));
    await owner.load(); assert.equal(owner.entranceReady,false); assert.equal(parentLoads,1);
    assert.equal(owner.entranceDiagnostics().failed,true);
    owner.retryEntrance(); await owner.load(); assert.equal(owner.entranceReady,true); assert.equal(owner.textureScale,3);
    assert.equal(calls,3); owner.dispose();
  }finally{GLTFLoader.prototype.loadAsync=oldLoader;GeologyFidelitySession.prototype.load=oldBase;}
});
