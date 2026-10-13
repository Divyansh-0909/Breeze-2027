import test from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { ImmersiveRuntime } from "../../components/immersive/runtime";
import { LimestoneExcavationSession } from "../../components/immersive/LimestoneExcavationSession";

function glb(path: string) {
  const buffer = readFileSync(path), jsonLength = buffer.readUInt32LE(12);
  const document = JSON.parse(buffer.toString("utf8", 20, 20 + jsonLength));
  return { document, binary: buffer.subarray(28 + jsonLength) };
}

test("connected quarry uses the original darker rock family by default; limestone is an explicit comparison", () => {
  const runtime = new ImmersiveRuntime("hub", () => {}, false);
  const active = new LimestoneExcavationSession(runtime);
  const comparison = new LimestoneExcavationSession(runtime, "detailed", "limestone");
  assert.equal(active.look, "rock");assert.equal(comparison.look, "limestone");
  assert.deepEqual(active.partsForRendering(), comparison.partsForRendering());
  active.dispose();comparison.dispose();
});

test("restored material keeps the original Stage2A PBR parameters and image payloads exactly", () => {
  const source = glb("public/models/gullyverse/pilot-rock/quarry-rock-pilot.glb");
  const restored = glb("public/models/gullyverse/rock-look-restore/rock-pilot-material.glb");
  assert.deepEqual(restored.document.materials, source.document.materials);
  assert.deepEqual(restored.document.textures, source.document.textures);
  assert.deepEqual(restored.document.samplers, source.document.samplers);
  assert.equal(restored.document.materials[0].name, "Quarry_Pilot_Original_Stone_PBR");
  const imageHashes = ({ document, binary }: ReturnType<typeof glb>) => document.images.map((image: { name: string; bufferView: number }) => {
    const view = document.bufferViews[image.bufferView];
    return { name: image.name, sha256: createHash("sha256").update(binary.subarray(view.byteOffset ?? 0, (view.byteOffset ?? 0) + view.byteLength)).digest("hex") };
  });
  assert.deepEqual(imageHashes(restored), imageHashes(source));
  assert.equal(restored.document.meshes.length, 1);
  assert.equal(restored.document.nodes[0].name, "Original_Rock_Material_Holder_Not_Rendered");
});
