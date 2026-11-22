import assert from "node:assert/strict";
import { test } from "node:test";
import { Euler, PerspectiveCamera, Vector3 } from "three";
import { createCypherSpace } from "../../components/gullyverse-runtime/cypher-space";
import { nextTeam, teamFocus, teamIndex, teamSlides, teamView } from "../../components/gullyverse-runtime/team-carousel";
import { ImmersiveRuntime } from "../../components/immersive/runtime";
import { world } from "../../components/immersive/world";
import plazaFootprint from "../../components/gullyverse-runtime/plaza-walk-space.json";

const cypher = createCypherSpace();
const advance = (runtime: ImmersiveRuntime, frames: number) => {
  for (let frame = 0; frame < frames; frame++) {
    runtime.tick(1 / 60);
    assert.ok(cypher.clearance(runtime.pose) >= 0);
  }
};

test("phone framing lowers the view without changing the walking pose or lens", () => {
  for (const space of [undefined, cypher.space]) {
    const runtime = new ImmersiveRuntime("hub", undefined, false, undefined, space);
    for (const [aspect, degrees] of [[0.6, 14], [2, 10]]) {
      const pose = { ...runtime.pose };
      const desktop = runtime.cameraPose(aspect);
      assert.deepEqual(runtime.cameraPose(aspect, true), { ...desktop, pitch: desktop.pitch - degrees * Math.PI / 180 });
      assert.deepEqual(runtime.pose, pose);
    }
  }
});

test("the authored team carousel wraps and the complete mural fits on a phone", () => {
  assert.equal(teamSlides.length, 8);
  assert.equal(teamSlides[0].team, "Organising Committee");
  assert.equal(teamSlides.reduce((people, slide) => people + slide.people.length, 0), 19);
  assert.equal(nextTeam(0, -1), 7);
  assert.equal(nextTeam(7, 1), 0);
  assert.equal(teamIndex("7"), 7);
  assert.equal(teamIndex("-1"), 0);
  assert.equal(teamIndex("8"), 0);
  const position = [teamFocus.x, teamFocus.y, teamFocus.z] as const;
  for (const aspect of [320 / 568, 390 / 664, 844 / 390, 1120 / 700]) {
    const frame = teamView(aspect, position);
    const camera = new PerspectiveCamera(frame.fov, aspect, 0.05, 120);
    camera.position.set(...position);
    camera.quaternion.setFromEuler(new Euler(frame.pitch, teamFocus.yaw, 0, "YXZ"));
    camera.updateMatrixWorld();
    for (const slide of teamSlides) {
      const [x, y, z] = slide.centre;
      for (const dx of [-0.5, 0.5]) for (const dy of [-0.5, 0.5]) {
        const corner = new Vector3(x, y + dy * slide.heightM, z + dx * slide.widthM).project(camera);
        assert.ok(Math.abs(corner.x) < 0.96 && Math.abs(corner.y) < 0.96);
      }
    }
  }
});

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

test("the extended cypher keeps the gate approach and both sides of the plaza walkable", () => {
  const plaza = createCypherSpace({ start: -29.5, end: 47.6, halfWidth: 16, spawnY: 19.3, plaza: true });
  const centre = plaza.resolve({ x: 0, z: -10 }, { x: 0, z: -21 });
  assert.ok(centre.z < -20.99);
  for (const side of [-1, 1]) {
    const alongEdge = plaza.resolve(centre, { x: side * 13, z: -21 });
    assert.ok(alongEdge.x * side > 12.98);
    const rear = plaza.resolve(alongEdge, { x: side * 13, z: -44.6 });
    assert.ok(rear.z < -44.58);
    assert.ok(plaza.resolve(rear, { x: side * 15, z: rear.z }).x * side < 13.23);
    assert.equal(plaza.grade(rear), 7.2);
  }
  assert.ok(plaza.resolve({ x: 0, z: -44.6 }, { x: 0, z: -47 }).z > -45.39);
  for (const [x, y] of plazaFootprint.people) {
    assert.ok(plaza.clearance({ x, z: -y }) < 0);
  }
  const returned = plaza.resolve(centre, { x: 0, z: 3 });
  assert.ok(returned.z > 2.98);
});
