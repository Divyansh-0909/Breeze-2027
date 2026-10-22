import test from "node:test";
import assert from "node:assert/strict";
import * as THREE from "three";
import {renderQuarryPreparation} from "../../components/immersive/quarryPreparation";

test("private quarry preparation excludes stage meshes and restores camera, geometry and light layers", () => {
  const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera();
  const quarry = new THREE.Group(), wall = new THREE.Mesh(), stage = new THREE.Mesh();
  const activeLight = new THREE.DirectionalLight(), inactiveLight = new THREE.PointLight();
  inactiveLight.layers.set(2);
  quarry.add(wall); scene.add(quarry, stage, activeLight, inactiveLight);
  const saved = new Map<THREE.Object3D, number>(); scene.traverse(object => saved.set(object, object.layers.mask));
  const originalCamera = camera.layers.mask;
  let rendered = 0;
  renderQuarryPreparation({render(actualScene, actualCamera) {
    rendered++; assert.equal(actualScene, scene); assert.equal(actualCamera, camera);
    assert.equal(wall.layers.test(camera.layers), true);
    assert.equal(stage.layers.test(camera.layers), false);
    assert.equal(activeLight.layers.test(camera.layers), true);
    assert.equal(inactiveLight.layers.test(camera.layers), false);
  }}, scene, camera, quarry);
  assert.equal(rendered, 1); assert.equal(camera.layers.mask, originalCamera);
  scene.traverse(object => assert.equal(object.layers.mask, saved.get(object)));
  assert.throws(() => renderQuarryPreparation({render() { throw new Error("simulated context interruption"); }}, scene, camera, quarry));
  assert.equal(camera.layers.mask, originalCamera);
  scene.traverse(object => assert.equal(object.layers.mask, saved.get(object)));
});

test("an environment using every render layer retains the original safe preparation path", () => {
  const scene = new THREE.Scene(), camera = new THREE.PerspectiveCamera(), quarry = new THREE.Group();
  const reserved = new THREE.Object3D(); reserved.layers.enableAll(); scene.add(reserved, quarry);
  const mask = camera.layers.mask, reservedMask = reserved.layers.mask; let rendered = false;
  renderQuarryPreparation({render(actualScene, actualCamera) {
    assert.equal(actualScene, scene); assert.equal(actualCamera.layers.mask, mask); rendered = true;
  }}, scene, camera, quarry);
  assert.equal(rendered, true); assert.equal(reserved.layers.mask, reservedMask); assert.equal(camera.layers.mask, mask);
});
