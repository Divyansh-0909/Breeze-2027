import assert from "node:assert/strict";
import { test } from "node:test";
import { ImmersiveRuntime } from "../../components/immersive/runtime";
import { contactSpace } from "../../components/gullyverse-runtime/native-space";
import config from "../../components/gullyverse-runtime/contact-space.json";
import { cypherContact } from "../../components/gullyverse-runtime/cypher-contact";
import { createCypherSpace } from "../../components/gullyverse-runtime/cypher-space";
import { hasIsolatedPreviewBackend } from "../../lib/preview-backend";
const native=contactSpace(config);
const advance=(runtime:ImmersiveRuntime,seconds:number,hz=60)=>{for(let i=0;i<seconds*hz;i++)runtime.tick(1/hz);};
function ready(){const runtime=new ImmersiveRuntime("hub",undefined,false,undefined,native.space);runtime.markReady(0);advance(runtime,1);return runtime;}
test("native frame round-trips source coordinates without scaling",()=>{
  for(const u of [-14,-12,-10])for(const depth of [-21,-18,-16]){
    const [x,y,z]=native.point(u,depth);const result=native.local({x,z});
    assert.ok(Math.abs(result.u-u)<1e-6);assert.ok(Math.abs(result.depth-depth)<1e-6);assert.equal(y,8.9);
  }
});
test("native walking keeps original speed, delta clamp, radius and grounded eye height",()=>{
  const a=ready(),b=ready();a.input.forward=b.input.forward=1;advance(a,.4,30);advance(b,.4,60);
  assert.ok(Math.hypot(a.pose.x-b.pose.x,a.pose.z-b.pose.z)<.08);
  assert.ok(Math.hypot(a.pose.x-native.spawn().x,a.pose.z-native.spawn().z)<4.2*.4);
  a.tick(10);assert.ok(native.clearance(a.pose)>=-1e-6);assert.equal(a.pose.y,8.9);
  advance(a,30);assert.ok(native.clearance(a.pose)>=-1e-6);assert.ok(native.near(a.pose));
  a.input.strafe=1;advance(a,30);assert.ok(native.clearance(a.pose)>=-1e-6);
});
test("enquiry uses original focus easing, holds input, and returns exact walking position and angles",()=>{
  const r=ready();r.input.forward=1;advance(r,.7);r.clearInput();r.pose.yaw+=.23;r.pose.pitch=.14;const saved={...r.pose};
  assert.equal(r.focusInteraction(native.focus()),true);assert.equal(r.focusInteraction(native.focus()),false);r.input.forward=1;advance(r,2);
  assert.deepEqual(r.pose,native.focus());r.setMap(true);assert.equal(r.getSnapshot().map,false);
  assert.equal(r.handleEscape(),true);advance(r,1);assert.deepEqual(r.pose,saved);assert.equal(r.interacting,false);
});
test("map returns to native position and reduced motion still restores interaction",()=>{
  const r=ready(),saved={...r.pose};r.setMap(true);advance(r,2);assert.ok(r.cameraPose().y>saved.y);r.setMap(false);advance(r,2);assert.deepEqual(r.pose,saved);
  r.reduced=true;r.focusInteraction(native.focus());advance(r,.1);assert.deepEqual(r.pose,native.focus());r.focusInteraction(null);advance(r,.1);assert.deepEqual(r.pose,saved);
});
test("context recovery retains focused enquiry and rejects stale readiness",()=>{
  const r=ready();r.focusInteraction(native.focus());advance(r,1);const focused={...r.pose};r.loseContext();const serial=r.getSnapshot().serial;r.restoreContext();r.markReady(serial-1);assert.equal(r.getSnapshot().phase,"recovering");r.markReady(serial);advance(r,.1);assert.deepEqual(r.pose,focused);assert.equal(r.interacting,true);
});

test("the plaza enquiry is reachable on the original deck and returns the route pose", () => {
  const plaza = createCypherSpace({ start: -29.5, end: 47.6, halfWidth: 16, plaza: true, spawnY: 19.3 });
  const runtime = new ImmersiveRuntime("hub", undefined, false, undefined, plaza.space);
  runtime.markReady(0);
  advance(runtime, 2);
  runtime.input.strafe = 1;
  for (let i = 0; i < 240 && !cypherContact.near(runtime.pose); i++) runtime.tick(1 / 60);
  assert.ok(cypherContact.near(runtime.pose));
  const saved = { ...runtime.pose };
  assert.ok(plaza.clearance(saved) > 0 && plaza.clearance(cypherContact.focus) > 0);
  assert.ok(plaza.clearance(cypherContact.spawn) > 0 && cypherContact.near(cypherContact.spawn));
  const via = plaza.resolve(saved, cypherContact.focus);
  assert.ok(Math.hypot(via.x - cypherContact.focus.x, via.z - cypherContact.focus.z) < 0.01);
  assert.equal(runtime.focusInteraction(cypherContact.focus), true);
  runtime.input.strafe = 1;
  advance(runtime, 1.2);
  assert.deepEqual(runtime.pose, cypherContact.focus);
  assert.equal(runtime.handleEscape(), true);
  advance(runtime, 0.95);
  assert.deepEqual(runtime.pose, saved);
});

test("preview submissions require an explicitly enabled disposable loopback database", () => {
  const env = { GULLYVERSE_RUNTIME_PREVIEW: "1", GULLYVERSE_ISOLATED_TEST_BACKEND: "1" };
  assert.equal(hasIsolatedPreviewBackend({ ...env, DATABASE_URL: "postgresql://127.0.0.1:55432/breeze_runtime_tests_cypher" }), true);
  assert.equal(hasIsolatedPreviewBackend({ ...env, DATABASE_URL: "postgresql://db.example.invalid/breeze_runtime_tests" }), false);
  assert.equal(hasIsolatedPreviewBackend({ ...env, DATABASE_URL: "postgresql://localhost/breeze" }), false);
  assert.equal(hasIsolatedPreviewBackend({ ...env, DATABASE_URL: "https://localhost/breeze_runtime_tests" }), false);
  assert.equal(hasIsolatedPreviewBackend({ ...env, GULLYVERSE_ISOLATED_TEST_BACKEND: "0", DATABASE_URL: "postgresql://localhost/breeze_runtime_tests" }), false);
});
