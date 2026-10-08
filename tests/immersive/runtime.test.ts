import assert from "node:assert/strict";
import { test } from "node:test";
import { ImmersiveRuntime } from "../../components/immersive/runtime";
import { locationFromPath, spawnPose } from "../../components/immersive/navigation";

function advance(runtime: ImmersiveRuntime, seconds: number, hz = 60) {
  for (let i = 0; i < Math.ceil(seconds * hz); i++) runtime.tick(1 / hz);
}
function hub() {
  const runtime = new ImmersiveRuntime("hub"); runtime.markReady(0); runtime.enter(); advance(runtime, 7.3); return runtime;
}
test("landing owns controls, entrance reaches hub, and frames don't publish React state", () => {
  const runtime = new ImmersiveRuntime("hub"); runtime.input.forward = 1; advance(runtime, 1);
  assert.equal(runtime.pose.z, 8); runtime.markReady(0); assert.equal(runtime.getSnapshot().phase, "landing");
  runtime.enter(); advance(runtime, 7.3); assert.equal(runtime.getSnapshot().phase, "local"); assert.deepEqual(runtime.pose, spawnPose("hub"));
  let changes = 0; runtime.subscribe(() => changes++); runtime.input.strafe = 1; advance(runtime, 1);
  assert.ok(runtime.pose.x > 3.8); assert.equal(changes, 0);
});
test("physical threshold uses guided departure and never reveals before critical readiness", () => {
  const runtime = hub(); runtime.input.forward = 1; advance(runtime, 4);
  assert.equal(runtime.getSnapshot().phase, "departure"); advance(runtime, 2);
  assert.equal(runtime.getSnapshot().scene, "aftermovie"); assert.equal(runtime.opacity, 1);
  advance(runtime, 12); assert.equal(runtime.getSnapshot().phase, "covered");
  runtime.markReady(0); advance(runtime, 1); assert.equal(runtime.getSnapshot().phase, "covered");
  runtime.markReady(runtime.getSnapshot().serial); advance(runtime, 1.3);
  assert.equal(runtime.getSnapshot().phase, "local"); assert.equal(runtime.opacity, 0);
  assert.deepEqual(runtime.pose, spawnPose("aftermovie"));
});
test("local movement is delta-aware, diagonal speed is bounded, and stage/backstage are inaccessible", () => {
  const a = hub(), b = hub(); a.input.strafe = b.input.strafe = 1;
  advance(a, 2, 30); advance(b, 2, 60); assert.ok(Math.abs(a.pose.x - b.pose.x) < 0.08);
  const runtime = new ImmersiveRuntime("aftermovie"); runtime.markReady(0); advance(runtime, 0.7);
  runtime.input.forward = 1; runtime.input.strafe = 1; advance(runtime, 30);
  assert.equal(runtime.pose.x, 8); assert.equal(runtime.pose.z, 15.8);
  assert.equal(runtime.getSnapshot().phase, "local");
});
test("route commitment preserves the current walking velocity without a stop or jump", () => {
  const runtime = hub(); runtime.input.forward = 1;
  let previous = runtime.pose.z;
  for (let frame = 0; frame < 400 && runtime.getSnapshot().phase === "local"; frame++) { previous = runtime.pose.z; runtime.tick(1 / 60); }
  assert.equal(runtime.getSnapshot().phase, "departure");
  const lastWalkStep = Math.abs(runtime.pose.z - previous); previous = runtime.pose.z;
  runtime.tick(1 / 60); const firstGuidedStep = Math.abs(runtime.pose.z - previous);
  assert.ok(firstGuidedStep > lastWalkStep * 0.5 && firstGuidedStep < lastWalkStep * 1.7);
});
test("direct URL skips introduction, map and physical return share the destination request", () => {
  const arrivals: string[] = [];
  const runtime = new ImmersiveRuntime("aftermovie", (id, source) => arrivals.push(`${id}:${source}`));
  runtime.markReady(0); advance(runtime, 0.7); assert.deepEqual(arrivals, ["aftermovie:url"]);
  runtime.input.forward = -1; advance(runtime, 1.5); assert.equal(runtime.getSnapshot().destination, "hub");
  advance(runtime, 2); runtime.markReady(runtime.getSnapshot().serial); advance(runtime, 1.3);
  assert.equal(runtime.getSnapshot().scene, "hub"); assert.equal(arrivals[1], "hub:physical");
  runtime.setMap(true); runtime.request("aftermovie", "map"); assert.equal(runtime.getSnapshot().map, false);
  advance(runtime, 0.4); runtime.markReady(runtime.getSnapshot().serial); advance(runtime, 0.7);
  assert.equal(arrivals[2], "aftermovie:map");
  assert.equal(locationFromPath("/aftermovie"), "aftermovie"); assert.equal(locationFromPath("/events"), null);
});
test("superseding navigation invalidates old readiness; background restore cannot leap across routes", () => {
  const runtime = hub(); runtime.request("aftermovie", "map"); advance(runtime, 0.4);
  const old = runtime.getSnapshot().serial; runtime.request("hub", "url"); advance(runtime, 0.4);
  runtime.markReady(old); advance(runtime, 2); assert.equal(runtime.getSnapshot().phase, "covered");
  runtime.markReady(runtime.getSnapshot().serial); advance(runtime, 0.7);
  runtime.input.strafe = 1; runtime.suspended = true; const x = runtime.pose.x; advance(runtime, 5); assert.equal(runtime.pose.x, x);
  runtime.suspended = false; runtime.tick(20); assert.ok(runtime.pose.x - x < 0.22);
});
test("reduced motion preserves readiness gating and playback restores the visitor's pose", () => {
  const runtime = new ImmersiveRuntime("aftermovie"); runtime.reduced = true; runtime.markReady(0); advance(runtime, 0.3);
  runtime.input.strafe = 1; advance(runtime, 0.5); runtime.clearInput(); const pose = { ...runtime.pose };
  runtime.setMovie(true); advance(runtime, 1); assert.equal(runtime.pose.y, 5.9);
  runtime.setMovie(false); advance(runtime, 1); assert.deepEqual(runtime.pose, pose);
  runtime.request("hub", "map"); advance(runtime, 0.3); assert.equal(runtime.opacity, 1); assert.equal(runtime.getSnapshot().phase, "covered");
});
test("changing motion preferences publishes immediately without taking away local controls", () => {
  const runtime = hub(); const before = { ...runtime.pose }; const notifications: boolean[] = [];
  runtime.input.forward = 1;
  runtime.subscribe(() => notifications.push(runtime.getSnapshot().reduced));
  runtime.reduced = true;
  assert.deepEqual(notifications, [true]); assert.deepEqual(runtime.pose, before);
  assert.equal(runtime.getSnapshot().phase, "local"); assert.equal(runtime.input.forward, 1);
});

test("context restoration keeps the visitor's pose and rejects readiness from before loss", () => {
  const runtime = hub(); runtime.input.strafe = 1; advance(runtime, 0.5);
  const pose = { ...runtime.pose }, old = runtime.getSnapshot().serial;
  runtime.loseContext(); assert.equal(runtime.opacity, 1); assert.equal(runtime.input.strafe, 0);
  advance(runtime, 5); runtime.markReady(old); assert.equal(runtime.getSnapshot().phase, "context-lost");
  runtime.restoreContext(); runtime.markReady(old); assert.equal(runtime.getSnapshot().phase, "recovering");
  runtime.markReady(runtime.getSnapshot().serial); advance(runtime, 1);
  assert.equal(runtime.getSnapshot().phase, "local"); assert.equal(runtime.opacity, 0); assert.deepEqual(runtime.pose, pose);
});

test("context loss pauses entrance choreography and recovers initial preparation", () => {
  const runtime = new ImmersiveRuntime("hub"); runtime.loseContext(); runtime.restoreContext();
  runtime.markReady(runtime.getSnapshot().serial); assert.equal(runtime.getSnapshot().phase, "landing");
  runtime.enter(); advance(runtime, 3); const pose = { ...runtime.pose };
  runtime.loseContext(); advance(runtime, 10); runtime.restoreContext(); runtime.markReady(runtime.getSnapshot().serial);
  assert.deepEqual(runtime.pose, pose); advance(runtime, 4.3);
  assert.equal(runtime.getSnapshot().phase, "local"); assert.deepEqual(runtime.pose, spawnPose("hub"));
});

test("URL navigation during recovery supersedes the interrupted destination after preparation", () => {
  const runtime = hub(); runtime.request("aftermovie", "map"); advance(runtime, 0.4);
  runtime.loseContext(); runtime.request("hub", "url"); runtime.restoreContext();
  const serial = runtime.getSnapshot().serial; runtime.markReady(serial);
  assert.equal(runtime.getSnapshot().phase, "departure"); advance(runtime, 0.4);
  runtime.markReady(serial); assert.equal(runtime.getSnapshot().phase, "covered");
  runtime.markReady(runtime.getSnapshot().serial); advance(runtime, 0.7);
  assert.equal(runtime.getSnapshot().scene, "hub"); assert.equal(runtime.getSnapshot().phase, "local");
});

test("context loss exits film focus and returns to the saved walking pose", () => {
  const runtime = new ImmersiveRuntime("aftermovie"); runtime.markReady(0); advance(runtime, 0.7);
  runtime.input.strafe = 1; advance(runtime, 0.5); runtime.clearInput(); const pose = { ...runtime.pose };
  let stopped = false;
  runtime.movieActions = { play() {}, stop() { stopped = true; }, sound() {}, status: () => ({ phase: "playing", currentTime: 1, paused: false, muted: true }) };
  runtime.setMovie(true); advance(runtime, 1); runtime.loseContext();
  assert.equal(stopped, true); assert.equal(runtime.getSnapshot().movie, false);
  runtime.restoreContext(); runtime.markReady(runtime.getSnapshot().serial); advance(runtime, 1);
  assert.deepEqual(runtime.pose, pose); assert.equal(runtime.getSnapshot().phase, "local");
});
