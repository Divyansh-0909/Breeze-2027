import {test} from 'node:test';
import assert from 'node:assert/strict';
import * as THREE from 'three';
import {CaveTextureSampling} from '../../components/immersive/caveTextureSampling';

test('tunnel sampling doubles feature size once, preserves shared quarry maps and reuses the ORM image', () => {
  const albedo = new THREE.DataTexture(new Uint8Array(16), 2, 2);
  const normal = new THREE.DataTexture(new Uint8Array(16), 2, 2);
  const orm = new THREE.DataTexture(new Uint8Array(16), 2, 2);
  albedo.colorSpace = THREE.SRGBColorSpace;
  for (const texture of [albedo, normal, orm]) {
    texture.repeat.set(.061782042468605296, .061782042468605296);
    texture.offset.set(0, .12356408493721059);
  }
  const quarry = new THREE.MeshStandardMaterial({map: albedo, normalMap: normal,
    roughnessMap: orm, metalnessMap: orm, aoMap: orm});
  const material = quarry.clone(), owner = new CaveTextureSampling();
  owner.apply(material, 2);
  const wrappers = [material.map, material.normalMap, material.aoMap];
  assert.equal(owner.diagnostics().ownedTextureWrappers, 3);
  assert.equal(material.roughnessMap, material.aoMap);
  assert.equal(material.metalnessMap, material.aoMap);
  for (const [source, cave] of [[albedo, material.map], [normal, material.normalMap], [orm, material.aoMap]] as const) {
    assert.ok(cave); assert.notEqual(cave, source); assert.equal(cave.source, source.source);
    assert.equal(cave.image, source.image); assert.equal(cave.channel, source.channel);
    assert.equal(cave.colorSpace, source.colorSpace); assert.deepEqual(cave.offset, source.offset);
    assert.equal(source.repeat.x, .061782042468605296);
    assert.equal(cave.repeat.x, .030891021234302648);
  }
  owner.apply(material, 1); owner.apply(material, 2); owner.apply(material, 2);
  assert.deepEqual([material.map, material.normalMap, material.aoMap], wrappers);
  assert.equal(material.map!.repeat.x, .030891021234302648);
  assert.equal(quarry.map, albedo); assert.equal(quarry.normalMap, normal);
  let sharedDisposals = 0, localDisposals = 0;
  for (const map of [albedo, normal, orm]) map.addEventListener('dispose', () => sharedDisposals++);
  for (const map of wrappers) map!.addEventListener('dispose', () => localDisposals++);
  owner.dispose(); owner.dispose();
  assert.equal(sharedDisposals, 0); assert.equal(localDisposals, 3);
  material.dispose(); quarry.dispose();
});


test('deep-rock pilot stays private and carries accepted C9 through destination routes', async () => {
  const {naturalCaveReview, carryCaveReview} = await import('../../components/immersive/caveReview');
  assert.equal(naturalCaveReview('?entranceReview=deep-rock', false), false);
  assert.equal(naturalCaveReview('', true), false);
  assert.equal(naturalCaveReview('?entranceReview=deep-rock', true), true);
  for (const href of ['/?arrival=hub', '/aftermovie', '/team#top']) {
    const u = new URL(carryCaveReview(href, '?entranceReview=deep-rock', true), 'https://breeze.invalid');
    assert.equal(u.searchParams.get('entranceReview'), 'deep-rock');
    assert.equal(u.searchParams.get('quarryReview'), 'geology-fidelity');
    assert.equal(u.hash, new URL(href, u.origin).hash);
    assert.equal(carryCaveReview(href, '?entranceReview=deep-rock', false), href);
  }
});


test('distinct glTF ORM wrappers share one owned view, while different UV channels stay separate', () => {
  const orm = new THREE.DataTexture(new Uint8Array(16), 2, 2);
  const roughness = orm.clone(), metalness = orm.clone(), ao = orm.clone();
  for (const t of [roughness, metalness, ao]) t.repeat.set(.06178204218546549, .06178204218546549);
  const material = new THREE.MeshStandardMaterial({roughnessMap: roughness, metalnessMap: metalness, aoMap: ao});
  const owner = new CaveTextureSampling(); owner.apply(material, 2);
  assert.equal(owner.diagnostics().borrowedTextureWrappers, 3);
  assert.equal(owner.diagnostics().ownedTextureWrappers, 1);
  assert.equal(material.roughnessMap, material.metalnessMap); assert.equal(material.roughnessMap, material.aoMap);
  assert.equal(material.aoMap!.repeat.x, roughness.repeat.x / 2);
  const uv1 = orm.clone(); uv1.channel = 1; uv1.repeat.copy(roughness.repeat); material.aoMap = uv1;
  owner.apply(material, 2);
  assert.equal(owner.diagnostics().ownedTextureWrappers, 2);
  assert.notEqual(material.aoMap, material.roughnessMap); assert.equal(material.aoMap!.channel, 1);
  let closed = 0, shared = 0;
  material.roughnessMap!.addEventListener('dispose', () => closed++);
  for (const t of [orm, roughness, metalness, ao, uv1]) t.addEventListener('dispose', () => shared++);
  owner.dispose(); owner.dispose(); assert.equal(closed, 1); assert.equal(shared, 0); material.dispose();
});
