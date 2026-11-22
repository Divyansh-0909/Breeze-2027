import assert from "node:assert/strict";
import { test } from "node:test";
import { Euler, Group, Mesh, MeshBasicMaterial, PerspectiveCamera, Vector3, VideoTexture } from "three";
import {
  accommodationApproach, accommodationFocus, accommodationView, revealAccommodationHouseWall,
} from "../../components/gullyverse-runtime/cypher-accommodation";
import { aftermovieFocus, aftermovieView, bindAftermovie, findAftermoviePanels } from "../../components/gullyverse-runtime/cypher-aftermovie";
import { createCypherSpace } from "../../components/gullyverse-runtime/cypher-space";
import { nextTeam, teamFocus, teamIndex, teamSlides, teamView } from "../../components/gullyverse-runtime/team-carousel";
import { ImmersiveRuntime } from "../../components/immersive/runtime";
import { world } from "../../components/immersive/world";
import { ownVideoTexture, retireVideoTexture } from "../../components/landing-page/stage3d/videoTextureOwnership";
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
  assert.equal(teamFocus.pitch, 0);
  const floor = createCypherSpace({ start: -29.5, end: 47.6, halfWidth: 16, spawnY: 19.3, plaza: true }).grade(teamFocus);
  assert.ok(floor !== undefined && teamFocus.y > floor + world.eyeHeight + 0.4);
  for (const [width, height] of [[320, 568], [390, 664], [844, 390], [1120, 700]]) {
    const frame = teamView(width, height, position);
    const camera = new PerspectiveCamera(frame.fov, width / height, 0.05, 120);
    camera.position.set(...position);
    camera.quaternion.setFromEuler(new Euler(teamFocus.pitch, teamFocus.yaw, 0, "YXZ"));
    camera.setViewOffset(width, height, 0, frame.offsetY, width, height);
    camera.updateMatrixWorld();
    for (const slide of teamSlides) {
      const [x, y, z] = slide.centre;
      for (const side of [-0.5, 0.5]) {
        const top = new Vector3(x, y + slide.heightM / 2, z + side * slide.widthM).project(camera);
        const bottom = new Vector3(x, y - slide.heightM / 2, z + side * slide.widthM).project(camera);
        assert.ok(Math.abs(top.x) < 0.96 && top.y < 0.96 && bottom.y > -0.96);
        assert.ok(Math.abs(top.x - bottom.x) < 1e-8);
      }
    }
  }
});

test("the accommodation graffiti is reached from the gate and fits without tilting the view", () => {
  const plaza = createCypherSpace({ start: -29.5, end: 47.6, halfWidth: 16, spawnY: 19.3, plaza: true });
  const distance = (a: { x: number; z: number }, b: { x: number; z: number }) => Math.hypot(a.x - b.x, a.z - b.z);
  const gate = { x: 0, z: -17.1 };
  const approached = plaza.resolve(gate, accommodationApproach);
  assert.ok(distance(approached, accommodationApproach) < 0.01);
  assert.ok(plaza.clearance(accommodationFocus) > 0);
  assert.ok(distance(plaza.resolve(approached, accommodationFocus), accommodationFocus) < 0.01);
  assert.equal(accommodationFocus.pitch, 0);
  const eye = [accommodationFocus.x, accommodationFocus.y, accommodationFocus.z] as const;
  for (const [width, height] of [[320, 568], [390, 664], [844, 390], [1120, 700]]) {
    const frame = accommodationView(width, height, eye);
    const camera = new PerspectiveCamera(frame.fov, width / height, 0.05, 120);
    camera.position.set(...eye);
    camera.quaternion.setFromEuler(new Euler(0, accommodationFocus.yaw, 0, "YXZ"));
    camera.setViewOffset(width, height, 0, frame.offsetY, width, height);
    camera.updateMatrixWorld();
    for (const x of [-13.165, -10.865]) for (const y of [8.353333, 9.886667]) {
      const corner = new Vector3(x, y, -14.009).project(camera);
      assert.ok(Math.abs(corner.x) < 0.96 && corner.y < 0.96);
      assert.ok((1 - corner.y) * height / 2 < height - 76);
    }
    const lamp = new Vector3(-12.015, 10.38, -14.46).project(camera);
    assert.ok(Math.abs(lamp.x) < 0.96 && lamp.y < 0.96);
  }
});

test("accommodation uses the house facade behind the separate baked plaster overlay", () => {
  const plaza = new Group();
  const [overlay, graffiti, house, lamp] = [
    "Normal house plaster finish", "COMING above SOON graffiti", "REV15N / Existing Events house shell",
    "Accommodation shaded wall-lamp fixture",
  ].map(name => {
    const object = new Group();
    object.userData.runtimeOriginalSource = "REV15Z / " + name;
    plaza.add(object);
    return object;
  });
  revealAccommodationHouseWall(plaza);
  assert.equal(overlay.visible, false);
  assert.ok(graffiti.visible && house.visible && lamp.visible);
});

test("the Aftermovie view is reachable and fits the authored screen on phones", () => {
  const plaza = createCypherSpace({ start: -29.5, end: 47.6, halfWidth: 16, spawnY: 33.5, plaza: true });
  const reached = plaza.resolve({ x: 0, z: -33.5 }, aftermovieFocus);
  assert.ok(Math.hypot(reached.x - aftermovieFocus.x, reached.z - aftermovieFocus.z) < 0.01);
  for (const [width, height] of [[320, 568], [390, 664], [844, 390], [1120, 700]]) {
    const position = [aftermovieFocus.x, aftermovieFocus.y, aftermovieFocus.z] as const;
    const frame = aftermovieView(width, height, position);
    const camera = new PerspectiveCamera(frame.fov, width / height, 0.05, 120);
    camera.position.set(...position);
    camera.setViewOffset(width, height, 0, frame.offsetY, width, height);
    camera.updateMatrixWorld();
    for (const x of [-7.28, 7.28]) for (const y of [8.6, 14.58]) {
      const corner = new Vector3(x, y, -45.72).project(camera);
      assert.ok(Math.abs(corner.x) < 0.96 && corner.y < 0.96);
      assert.ok((1 - corner.y) * height / 2 < Math.max(height - 112, height * 0.65));
    }
  }
});

test("the three Aftermovie panels share one video lease and restore the authored still", () => {
  const group = new Group();
  const original = new MeshBasicMaterial();
  for (const side of ["left", "center", "right"]) {
    const mesh = new Mesh(undefined, original);
    mesh.userData.runtimeOriginalSource = "REV15Z / Existing Aftermovie / " + side;
    group.add(mesh);
  }
  const panels = findAftermoviePanels(group);
  assert.ok(panels);
  const video = new VideoTexture({} as HTMLVideoElement);
  let retired = 0;
  video.addEventListener("dispose", () => retired++);
  ownVideoTexture(video);
  const unbind = bindAftermovie(panels, video);
  const material = panels[0].material;
  assert.ok(material instanceof MeshBasicMaterial && material.map === video && material !== original);
  assert.ok(panels.every(panel => panel.material === material));
  assert.equal(video.flipY, false);
  retireVideoTexture(video);
  assert.equal(retired, 0);
  unbind();
  assert.ok(panels.every(panel => panel.material === original));
  assert.equal(retired, 1);
  // A film that ends before the scene commits leaves the still in place.
  const late = new VideoTexture({} as HTMLVideoElement);
  ownVideoTexture(late);
  retireVideoTexture(late);
  const skipped = bindAftermovie(panels, late);
  assert.ok(panels.every(panel => panel.material === original));
  skipped();
  assert.ok(panels.every(panel => panel.material === original));
  group.remove(group.children[0]);
  assert.equal(findAftermoviePanels(group), null);
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
