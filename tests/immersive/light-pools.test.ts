import assert from "node:assert/strict";
import { test } from "node:test";
import { PerspectiveCamera } from "three";
import { LightPools } from "../../components/gullyverse-runtime/light-pools";
import type { Budget } from "../../components/gullyverse-runtime/device-tier";

const at = (pools: LightPools, x: number, z: number, frames = 30) => {
  const camera = new PerspectiveCamera();
  camera.position.set(x, 8.9, z);
  for (let i = 0; i < frames; i++) pools.update(camera, 1 / 30);
  return pools.bound().filter(slot => slot.label).map(slot => slot.label).sort();
};

test("the pool registry binds the nearest pools for the camera and respects zone gates", () => {
  const pools = new LightPools({ tier: "low" } as Budget); // three slots
  pools.add({ x: 0, y: 11, z: -43.4 }, 15.5, "#9aa4b0", 0.3, { label: "screen" });
  pools.add({ x: 14.5, y: 18.4, z: -25.8 }, 13, "#c4883e", 2.6, { label: "balcony" });
  pools.add({ x: -11.5, y: 13.6, z: -49.2 }, 9, "#dbeaee", 0.75, { label: "back tube" });
  pools.add({ x: -2.4, y: 10.4, z: -11.8 }, 7.5, "#c4883e", 2, { label: "streetlamp", active: eye => eye.z > -24 });
  pools.add({ x: -14.9, y: 9.7, z: -31.1 }, 7, "#dbeaee", 1.1, { label: "events tube", active: eye => eye.x < -4 && eye.z < -22 });
  // At the gate: the streetlamp joins; the events tube is gated out.
  const gate = at(pools, 0, -8);
  assert.ok(gate.includes("streetlamp"));
  assert.ok(!gate.includes("events tube"));
  // At the events wall: the tube is bound, the streetlamp is gated out.
  const events = at(pools, -11, -31);
  assert.ok(events.includes("events tube"));
  assert.ok(!events.includes("streetlamp"));
  assert.equal(events.length, 3);
});
