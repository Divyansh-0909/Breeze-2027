import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import { existsSync, readFileSync } from "node:fs";
import { test } from "node:test";
import { BoxGeometry, Group, Mesh, MeshStandardMaterial, Vector3 } from "three";
import { batchStatic } from "../../components/gullyverse-runtime/static-batching";

const root = "public/models/gullyverse/";
const chunks = ["market-south", "market-north", "cypher-approach", "cypher-gate", "cypher-plaza", "cypher-audience"];
const glbJson = (file: string) => { const b = readFileSync(file); return JSON.parse(b.subarray(20, 20 + b.readUInt32LE(12)).toString()); };

test("chunks reference every shared road texture by URI, and each shared file matches its manifest", () => {
  const shared = JSON.parse(readFileSync(root + "locked-rev15z-shared/manifest.json", "utf8"));
  for (const entry of shared.files) {
    const data = readFileSync(root + "locked-rev15z-shared/" + entry.file);
    assert.equal(data.length, entry.bytes);
    assert.equal(createHash("sha256").update(data).digest("hex"), entry.sha256);
  }
  for (const chunk of chunks) for (const variant of ["optimized", "mobile"]) {
    const file = `${root}locked-rev15z-${chunk}/contact-frontage.${variant}.glb`;
    const json = glbJson(file);
    for (const image of json.images ?? []) {
      if (image.uri) assert.ok(existsSync(`${root}locked-rev15z-${chunk}/${image.uri}`), `${file}: ${image.uri}`);
      else assert.ok(image.bufferView < json.bufferViews.length, `${file}: ${image.name}`);
    }
    for (const accessor of json.accessors ?? []) assert.ok(accessor.bufferView === undefined || accessor.bufferView < json.bufferViews.length);
    const names = (json.images ?? []).filter((image: { uri?: string }) => !image.uri).map((image: { name: string }) => image.name);
    if (chunk !== "cypher-audience") for (const road of ["aggregate-1p2m-normal", "wet-road-world-roughness"]) assert.ok(!names.includes(road), `${chunk} still embeds ${road}`);
    const manifest = JSON.parse(readFileSync(`${root}locked-rev15z-${chunk}/manifest.json`, "utf8"));
    const listed = manifest.files.find((entry: { file: string }) => entry.file === `contact-frontage.${variant}.glb`);
    assert.equal(createHash("sha256").update(readFileSync(file)).digest("hex"), listed.sha256);
  }
});

test("static batching merges plain meshes per material and keeps world positions and special objects", () => {
  const group = new Group();
  const wall = new MeshStandardMaterial({ name: "wall" }), lamp = new MeshStandardMaterial({ name: "lamp" });
  const glass = new MeshStandardMaterial({ name: "glass", transparent: true });
  const at = (x: number, material: MeshStandardMaterial, userData: Record<string, unknown> = {}) => {
    const mesh = new Mesh(new BoxGeometry(1, 1, 1), material); mesh.position.set(x, 0, 0); mesh.userData = userData; group.add(mesh); return mesh;
  };
  at(0, wall, { runtimeOriginalSource: "a", shopId: "s1" }); at(3, wall); at(6, wall); at(52, wall); at(55, wall);
  const special = at(20, lamp, { streetLampId: "L01" }); at(25, lamp); const pane = at(30, glass); at(35, glass);
  const result = batchStatic(group);
  assert.equal(result.before, 9);
  // Walls merge within their 10 m cell (0-6 m -> one, 52-55 m -> one); lamp, lone lamp-material mesh and glass stay.
  assert.equal(result.after, 6);
  assert.ok(special.parent === group && pane.parent === group);
  const batched = group.children.find(child => child.userData.batchedFrom === 3) as Mesh;
  assert.ok(batched);
  batched.geometry.computeBoundingBox();
  const box = batched.geometry.boundingBox!;
  assert.deepEqual([box.min.x, box.max.x], [-0.5, 6.5]);
  assert.equal(batched.material, wall);
  assert.ok(new Vector3(6, 0, 0).distanceTo(new Vector3(box.max.x - 0.5, 0, 0)) < 1e-6);
  assert.ok(group.children.some(child => child.userData.batchedFrom === 2));
});

test("the arrival half of the gully loads first and every chunk loads exactly once", async () => {
  const { chunkOrder } = await import("../../components/gullyverse-runtime/chunk-order");
  const lane = chunkOrder(24), plaza = chunkOrder(-30);
  assert.deepEqual(lane.near, ["market-south", "market-north", "cypher-approach", "cypher-gate"]);
  assert.deepEqual(lane.later, ["cypher-plaza", "cypher-audience"]);
  assert.deepEqual(plaza.later, ["market-south", "market-north"]);
  for (const order of [lane, plaza]) assert.equal(new Set([...order.near, ...order.later]).size, 6);
});

test("people are identified by their archetype and seam normals average only across soft angles", async () => {
  const { isPerson, smoothSeams } = await import("../../components/gullyverse-runtime/person-shading");
  const { BufferAttribute, BufferGeometry, Object3D } = await import("three");
  const person = new Object3D(); person.userData = { archetype: "box-tee-straight-jeans" };
  assert.ok(isPerson(person) && !isPerson(new Object3D()));
  // Vertices 0-1 share a position (a UV seam) 30 degrees apart; 2-3 share one 90 degrees apart (a real edge).
  const g = new BufferGeometry();
  g.setAttribute("position", new BufferAttribute(new Float32Array([0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0]), 3));
  const n30 = [Math.sin(Math.PI / 6), Math.cos(Math.PI / 6), 0];
  g.setAttribute("normal", new BufferAttribute(new Float32Array([0, 1, 0, ...n30, 0, 1, 0, 1, 0, 0]), 3));
  assert.equal(smoothSeams(g, 60), 2);
  const n = g.getAttribute("normal");
  assert.ok(Math.abs(n.getX(0) - n.getX(1)) < 1e-6 && Math.abs(n.getY(0) - n.getY(1)) < 1e-6);
  assert.deepEqual([n.getX(2), n.getY(2), n.getX(3), n.getY(3)], [0, 1, 1, 0]);
});

test("people masks match the published chunks and hide only skin under clothing", async () => {
  for (const chunk of ["cypher-approach", "cypher-plaza", "cypher-audience"]) {
    const mask = JSON.parse(readFileSync(`${root}locked-rev15z-${chunk}/people-mask.json`, "utf8"));
    const json = glbJson(`${root}locked-rev15z-${chunk}/contact-frontage.optimized.glb`);
    const bySource = new Map(json.nodes.filter((n: { extras?: { archetype?: string } }) => n.extras?.archetype).map((n: { extras: { runtimeOriginalSource: string }; mesh: number }) => [n.extras.runtimeOriginalSource, n]));
    let hidden = 0, total = 0;
    for (const [key, entry] of Object.entries(mask.skins) as [string, { triangles: number; hidden: string }][]) {
      const [source, index] = key.split("#");
      const node = bySource.get(source) as { mesh: number } | undefined;
      assert.ok(node, `${chunk}: ${key}`);
      const primitive = json.meshes[node!.mesh].primitives[Number(index)];
      assert.match(json.materials[primitive.material].name, / material 0$/);
      assert.equal(json.accessors[primitive.indices].count / 3, entry.triangles);
      const bits = Buffer.from(entry.hidden, "base64");
      for (let t = 0; t < entry.triangles; t++) if (bits[t >> 3] & (1 << (t & 7))) hidden++;
      total += entry.triangles;
    }
    assert.ok(hidden / total > 0.02 && hidden / total < 0.1, `${chunk}: ${hidden}/${total}`);
  }
});
