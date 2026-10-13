import test from "node:test";
import assert from "node:assert/strict";
import * as THREE from "three";
import type { GLTF } from "three/examples/jsm/loaders/GLTFLoader.js";
import { ImmersiveRuntime } from "../../components/immersive/runtime";
import { QUARRY } from "../../components/immersive/wallSection";
import { LimestoneExcavationSession, LIMESTONE_EXCAVATION } from "../../components/immersive/LimestoneExcavationSession";

function fixture(names: string[], material: THREE.Material) {
  const scene = new THREE.Group();
  for (const name of names) { const mesh = new THREE.Mesh(new THREE.BoxGeometry(), material); mesh.name = name; scene.add(mesh); }
  return { scene } as unknown as GLTF;
}

test("continuous-excavation review is bounded and does not eagerly load the Stage2C comparison asset", () => {
  const session = new LimestoneExcavationSession(new ImmersiveRuntime("hub", () => {}, false));
  assert.equal(session.style, "detailed");assert.equal(session.assets.size, 0);
  assert.equal(session.asset, null);
  assert.deepEqual(session.partsForRendering(), LIMESTONE_EXCAVATION.variants.detailed.parts);
  assert.equal(LIMESTONE_EXCAVATION.material, "Quarry_Pilot_Grey_Limestone_PBR");
  session.dispose();
});

test("inactive geometry retirement cannot evict borrowed limestone maps or the active baseline", () => {
  const session = new LimestoneExcavationSession(new ImmersiveRuntime("hub", () => {}, false)), material = new THREE.MeshStandardMaterial();
  const baseline = fixture(QUARRY.parts.flatMap(p => p.nodes), material);
  const detailed = fixture(LIMESTONE_EXCAVATION.variants.detailed.parts.flatMap(p => p.nodes), material);
  let matDisposed = 0, geometryDisposed = 0;
  material.addEventListener("dispose", () => matDisposed++);
  detailed.scene.traverse(o => { if (o instanceof THREE.Mesh) o.geometry.addEventListener("dispose", () => geometryDisposed++); });
  session.assets.set("baseline", baseline);session.assets.set("detailed", detailed);session.asset = detailed;
  assert.throws(() => session.retireExcavation());
  session.style = "baseline";session.asset = baseline;session.state = { ...session.state, busy: false };
  session.retireExcavation();
  assert.equal(geometryDisposed, LIMESTONE_EXCAVATION.variants.detailed.parts.length * 3);
  assert.equal(matDisposed, 0);assert.equal(session.asset, baseline);
  assert.equal(session.assets.has("detailed"), false);
  const clone = session.cloneForRendering()!;
  for (const p of QUARRY.parts) for (const name of p.nodes) assert.ok(clone.getObjectByName(name));
  session.dispose();assert.equal(matDisposed, 1);
});

test("switching review style clears held input and never exposes nodes from the prior candidate", () => {
  class ProbeSession extends LimestoneExcavationSession { override async load() {} }
  const runtime = new ImmersiveRuntime("hub", () => {}, false), session = new ProbeSession(runtime);
  const material = new THREE.MeshStandardMaterial(), old = fixture(QUARRY.parts.flatMap(p => p.nodes), material);
  session.assets.set("baseline", old);session.asset = old;
  session.style = "baseline";session.state = { ...session.state, busy: false, assetReady: true };
  runtime.input.forward = 1;session.setExcavation("macro");
  assert.equal(runtime.input.forward, 0);assert.equal(session.state.busy, true);
  assert.equal(session.state.assetReady, false);assert.equal(session.cloneForRendering(), null);
  assert.deepEqual(session.partsForRendering(), LIMESTONE_EXCAVATION.variants.macro.parts);
  session.dispose();
});
