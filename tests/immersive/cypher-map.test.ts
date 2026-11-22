import assert from "node:assert/strict";
import { test } from "node:test";
import { Euler, PerspectiveCamera, Vector3 } from "three";
import { arrivalPose, cypherStarts, isCypherStart, mapStops, startHref } from "../../components/gullyverse-runtime/cypher-map";
import { cypherContact } from "../../components/gullyverse-runtime/cypher-contact";
import { teamFocus } from "../../components/gullyverse-runtime/team-carousel";
import { aftermovieFocus } from "../../components/gullyverse-runtime/cypher-aftermovie";
import { accommodationFocus } from "../../components/gullyverse-runtime/cypher-accommodation";
import { ImmersiveRuntime } from "../../components/immersive/runtime";

const { plaza } = cypherStarts;
const advance = (runtime: ImmersiveRuntime, seconds: number) => {
  for (let frame = 0; frame < seconds * 60; frame++) runtime.tick(1 / 60);
};
function walking() {
  const runtime = new ImmersiveRuntime("hub", undefined, false, undefined, plaza.space);
  runtime.markReady(0);
  advance(runtime, 1);
  assert.equal(runtime.getSnapshot().phase, "local");
  return runtime;
}

test("map travel only starts from the open map and lands on each stop's walking pose", () => {
  for (const stop of mapStops) {
    const runtime = walking();
    const target = arrivalPose(stop.id);
    assert.equal(runtime.travelFromMap(target), false);
    runtime.setMap(true);
    assert.equal(runtime.travelFromMap(target), false, "ascent is not interactive yet");
    advance(runtime, 1.5);
    assert.equal(runtime.getSnapshot().mapStage, "open");
    assert.equal(runtime.travelFromMap({ ...target, x: Number.NaN }), false);
    assert.equal(runtime.travelFromMap(target), true);
    assert.equal(runtime.getSnapshot().mapStage, "descent");
    assert.equal(runtime.travelFromMap(target), false);
    advance(runtime, 1.2);
    assert.equal(runtime.getSnapshot().map, false);
    assert.deepEqual(runtime.pose, target, stop.id);
    assert.ok(plaza.clearance(runtime.pose) >= 0, stop.id);
    // Walking still works from the new position on the same runtime.
    runtime.input.forward = 1;
    advance(runtime, 0.2);
    assert.ok(plaza.clearance(runtime.pose) >= 0);
  }
});

test("reduced motion travels too, and closing without a choice returns to the visitor", () => {
  const runtime = walking();
  const saved = { ...runtime.pose };
  runtime.reduced = true;
  runtime.setMap(true);
  advance(runtime, 0.2);
  assert.equal(runtime.travelFromMap(arrivalPose("team")), true);
  advance(runtime, 0.2);
  assert.deepEqual(runtime.pose, arrivalPose("team"));
  runtime.setMap(true);
  advance(runtime, 0.2);
  runtime.setMap(false);
  advance(runtime, 0.2);
  assert.deepEqual(runtime.pose, arrivalPose("team"));
  assert.notDeepEqual(runtime.pose, saved);
});

test("each destination stop lands where its action is offered", () => {
  const reach = (from: { x: number; z: number }, focus: { x: number; z: number }) => {
    const reached = plaza.resolve(from, focus);
    return Math.hypot(from.x - focus.x, from.z - focus.z) <= 4 && Math.hypot(reached.x - focus.x, reached.z - focus.z) < 0.01;
  };
  assert.ok(reach(arrivalPose("team"), teamFocus));
  assert.ok(reach(arrivalPose("aftermovie"), aftermovieFocus));
  assert.ok(reach(arrivalPose("accommodation"), accommodationFocus));
  assert.ok(reach(arrivalPose("events"), { x: -9.7, z: -31.05 }));
  assert.ok(cypherContact.near(arrivalPose("contact")));
});

test("the aerial map frames every stop between the header and toolbar", () => {
  const sizes = [[1440, 900], [1120, 700], [844, 390], [667, 375], [390, 664], [390, 844], [320, 568]];
  for (const [width, height] of sizes) {
    const aspect = width / height;
    const view = plaza.space.mapCamera(aspect);
    const camera = new PerspectiveCamera(view.fov, aspect, 0.05, 120);
    camera.position.set(view.x, view.y, view.z);
    camera.quaternion.setFromEuler(new Euler(view.pitch, view.yaw, 0, "YXZ"));
    camera.updateMatrixWorld();
    const band = aspect > 1.9 ? [0.2, 0.28] : [0.17, 0.21];
    for (const stop of mapStops) {
      const point = new Vector3(...stop.marker).project(camera);
      const fromTop = (1 - point.y) / 2;
      assert.ok(Math.abs(point.x) < 1, `${stop.id} at ${width}x${height}`);
      assert.ok(fromTop > band[0] - 0.01 && fromTop < 1 - band[1] + 0.01, `${stop.id} at ${width}x${height}: ${fromTop}`);
      assert.ok(point.z > -1 && point.z < 1, `${stop.id} inside the depth range`);
    }
    // Landscape runs from the market on the left to the screen on the right.
    const market = new Vector3(...mapStops[0].marker).project(camera);
    const screen = new Vector3(...mapStops.at(-1)!.marker).project(camera);
    if (aspect >= 1) assert.ok(market.x < screen.x);
    else assert.ok(market.y < screen.y);
  }
});

test("map stops cover every walkable start and keep refreshable URLs", () => {
  assert.deepEqual(mapStops.map(stop => stop.id).sort(), Object.keys(cypherStarts).sort());
  assert.equal(new Set(mapStops.map(stop => stop.label)).size, mapStops.length);
  assert.equal(isCypherStart("team"), true);
  assert.equal(isCypherStart("quarry"), false);
  assert.equal(isCypherStart("toString"), false);
  assert.equal(isCypherStart(undefined), false);
  const base = "http://127.0.0.1/runtime-preview/cypher?start=plaza&team=3";
  assert.equal(startHref(base, "team"), "http://127.0.0.1/runtime-preview/cypher?start=team&team=3");
  assert.equal(startHref(base, "events"), "http://127.0.0.1/runtime-preview/cypher?start=events");
  assert.equal(startHref(base, "market"), "http://127.0.0.1/runtime-preview/cypher");
});
