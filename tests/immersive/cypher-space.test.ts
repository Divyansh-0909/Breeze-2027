import assert from "node:assert/strict";
import { test } from "node:test";
import { createCypherSpace } from "../../components/gullyverse-runtime/cypher-space";
import { ImmersiveRuntime } from "../../components/immersive/runtime";
import { world } from "../../components/immersive/world";

const cypher = createCypherSpace();
const advance = (runtime: ImmersiveRuntime, frames: number) => {
  for (let frame = 0; frame < frames; frame++) {
    runtime.tick(1 / 60);
    assert.ok(cypher.clearance(runtime.pose) >= 0);
  }
};

test("the original controller walks both ways through a continuous native lane and ramp", () => {
  const runtime = new ImmersiveRuntime("hub", undefined, false, undefined, cypher.space);
  runtime.markReady(0);
  advance(runtime, 60);
  assert.equal(runtime.pose.z, 27);
  assert.equal(runtime.pose.y, 6 + world.eyeHeight);
  runtime.input.forward = 1;
  advance(runtime, 690);
  assert.ok(runtime.pose.z < -21);
  assert.equal(runtime.pose.y, 7.2 + world.eyeHeight);
  runtime.input.forward = -1;
  advance(runtime, 750);
  assert.ok(runtime.pose.z > 29);
  assert.equal(runtime.pose.y, 6 + world.eyeHeight);
});

test("the open gate allows passage but its leaf, jamb and wall prevent shortcuts", () => {
  assert.ok(cypher.resolve({ x: 0, z: -12 }, { x: 0, z: -17 }).z < -16.9);
  const wing = cypher.resolve({ x: 2, z: -12 }, { x: 2, z: -17 });
  assert.ok(wing.z > -14.99 + world.playerRadius);
  const leaf = cypher.resolve({ x: 0, z: -13.8 }, { x: -2, z: -13.8 });
  assert.ok(leaf.x >= -0.8575 + world.playerRadius);
  const jamb = cypher.resolve({ x: 0, z: -15.1 }, { x: 1, z: -15.1 });
  assert.ok(jamb.x <= 0.9 - world.playerRadius);
  const opposite = cypher.resolve({ x: 2, z: -17 }, { x: 2, z: -12 });
  assert.ok(opposite.z < -15.21 - world.playerRadius);
});

test("diagonal motion slides along the lane and stays on the grade at joins", () => {
  const p = cypher.resolve({ x: 3.1, z: 9 }, { x: 4, z: 7 });
  assert.ok(p.x <= 3.6 - world.playerRadius && p.z < 7.01);
  for (const [sourceY, expected] of [[-10, 6], [0, 6.5], [5, 6.75], [14, 7.2]]) {
    assert.ok(Math.abs(cypher.grade({ x: 0, z: -sourceY })! - expected) < 1e-6);
    assert.ok(cypher.clearance({ x: 0, z: -sourceY }) > 0);
  }
});

test("the upper ramp route passes under the navigation sign while keeping clear of its base and figures", () => {
  const p = cypher.resolve({ x: 0, z: -8.82 }, { x: 3.4, z: -8.82 });
  assert.ok(p.x <= 2.612 - world.playerRadius);
  const base = cypher.resolve({ x: 0, z: -11 }, { x: 3.4, z: -11 });
  assert.ok(base.x <= 2.875 - world.playerRadius);
  assert.ok(cypher.resolve({ x: 0, z: -4.8 }, { x: 0, z: -12 }).z < -11.99);
});
