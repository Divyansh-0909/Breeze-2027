import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
import * as THREE from "three";
import {ScannedRockSampling, rockTextureScale, carryScannedMaterialReview} from "../../components/immersive/scannedRockSampling";
import manifest from "../../public/models/gullyverse/recovered-c8-material/manifest.json";
import {boundaryClearance, constrainInterior} from "../../components/immersive/navigation";

test("approved 3x means three times larger features, including invalid/default URLs", () => {
  assert.equal(rockTextureScale(null), 3);
  for (const bad of ["0", "-3", "NaN", "1.5", "3x", "5", "", "03"]) assert.equal(rockTextureScale(bad), 3);
  assert.equal(rockTextureScale("1"), 1);
  assert.equal(rockTextureScale("4"), 4);
  const material = new THREE.MeshStandardMaterial();
  material.map = new THREE.Texture();
  material.map.repeat.set(manifest.baseUVRepeat, manifest.baseUVRepeat);
  new ScannedRockSampling().apply(material, 3);
  const marblePeriod = 2 / material.map.repeat.x / 6;
  assert.ok(Math.abs(marblePeriod - 1.798437 * 3) < 1e-6);
  assert.ok(material.map.repeat.x < manifest.baseUVRepeat);
  assert.equal(material.map.repeat.x, manifest.approvedUVRepeat);
});

test("repeated scale changes align UV0 channels without new images, cumulative drift or UV1 changes", () => {
  const material = new THREE.MeshStandardMaterial();
  const images = [new THREE.Texture(), new THREE.Texture(), new THREE.Texture()];
  for (const texture of images) { texture.repeat.set(manifest.baseUVRepeat, manifest.baseUVRepeat); texture.offset.set(0, 0.8146538725941841); }
  [material.map, material.normalMap, material.roughnessMap] = images;
  material.metalnessMap = material.roughnessMap;
  const geometryNormal = new THREE.Texture();
  geometryNormal.channel = 1;
  geometryNormal.repeat.set(0.713, 0.918);
  material.aoMap = geometryNormal;
  const beforeUV1 = geometryNormal.matrix.clone(), uv1Repeat = geometryNormal.repeat.clone();
  const uuids = images.map(texture => texture.uuid), versions = images.map(texture => texture.version);
  const sampling = new ScannedRockSampling();
  for (let cycle = 0; cycle < 10; cycle++) for (const scale of [3, 4, 1, 2, 3] as const) {
    sampling.apply(material, scale);
    for (const texture of images) {
      assert.equal(texture.repeat.x, manifest.baseUVRepeat / scale);
      assert.equal(texture.repeat.y, manifest.baseUVRepeat / scale);
      assert.equal(texture.offset.y, 0.8146538725941841);
    }
    assert.deepEqual(geometryNormal.repeat, uv1Repeat);
    assert.deepEqual(geometryNormal.matrix, beforeUV1);
  }
  assert.deepEqual(images.map(texture => texture.uuid), uuids);
  assert.deepEqual(images.map(texture => texture.version), versions, "sampling does not re-upload pixels");
});

test("private material selection survives hub/stage URLs and never leaks through a closed gate", () => {
  const search = "?diagnostics&quarryReview=scanned-material-multi&rockTextureScale=3";
  const next = carryScannedMaterialReview("/aftermovie", search, true);
  assert.equal(next, "/aftermovie?quarryReview=scanned-material-multi&rockTextureScale=3");
  assert.equal(carryScannedMaterialReview("/?arrival=hub", search, true), "/?arrival=hub&quarryReview=scanned-material-multi&rockTextureScale=3");
  assert.equal(carryScannedMaterialReview("/aftermovie", search, false), "/aftermovie");
  assert.equal(carryScannedMaterialReview("/aftermovie", "?diagnostics", true), "/aftermovie");
  assert.equal(carryScannedMaterialReview("/aftermovie", "?quarryReview=foundation-refined", true), "/aftermovie");
});

test("material preview uses the authentic C5.1 geometry and only its documented existing sector", () => {
  const geometry = readFileSync("public/models/gullyverse/quarry-foundation-refined/foundation-geometry.glb");
  assert.equal(createHash("sha256").update(geometry).digest("hex"), manifest.hostGeometrySHA256);
  assert.equal(manifest.hostGeometrySHA256, "134cbf9609e77df09cea1feb28b9e52f3c880c3320ba79f63ecb84ecbe53586f");
  assert.deepEqual(manifest.selectedNodes, ["Foundation_Wall_15_LOD0", "Foundation_Wall_15_LOD1", "Foundation_Wall_15_LOD2"]);
  assert.equal(manifest.geometryChanged, false);
  assert.equal(manifest.uniqueRuntimeImages, 3);
  assert.equal(manifest.estimatedRGBA8MipBytes, 32 * 1024 * 1024);
});

test("the three historical visitor positions remain inside the unchanged walking envelope", () => {
  for (const [x, y, z] of [[-18, 1.72, -55], [-18, 1.72, -62], [-17, 1.72, -69]]) {
    const pose = {x, y, z, yaw: 0, pitch: 0}, expected = {...pose};
    constrainInterior("hub", pose);
    assert.deepEqual(pose, expected);
    assert.ok(boundaryClearance("hub", pose) > 0);
  }
});
