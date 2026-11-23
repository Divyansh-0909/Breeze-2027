/**
 * Precomputes which body (skin) triangles of the people poke through their clothing (see
 * hideCoveredSkin in components/gullyverse-runtime/person-shading.ts) and writes one small mask per chunk:
 * public/models/gullyverse/locked-rev15z-<chunk>/people-mask.json. The browser applies it when the chunk
 * loads (an index filter), so the ray tests never run on the visitor's device.
 *
 *   npx tsx scripts/gullyverse/people-mask.mts
 *
 * Masks are keyed by the person node's runtimeOriginalSource and primitive index, and verified against both the desktop and mobile GLBs (their
 * geometry is identical). Rerun after any chunk is republished.
 */
import { createRequire } from "node:module";
import { readFileSync, writeFileSync } from "node:fs";
import { BufferAttribute, BufferGeometry, Matrix4 } from "three";
import { hideCoveredSkin } from "../../components/gullyverse-runtime/person-shading";

const require = createRequire(import.meta.url);
const toolchain = new URL("./toolchain/node_modules/", import.meta.url).pathname;
const { NodeIO } = require(toolchain + "@gltf-transform/core");
const { ALL_EXTENSIONS } = require(toolchain + "@gltf-transform/extensions");
const { MeshoptDecoder } = require(toolchain + "meshoptimizer");

const root = "public/models/gullyverse/";
const chunks = ["cypher-approach", "cypher-plaza", "cypher-audience", "market-south", "market-north", "cypher-gate"];
await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({ "meshopt.decoder": MeshoptDecoder });

function attribute(accessor: any) {
  const count = accessor.getCount(), size = accessor.getElementSize(), out = new Float32Array(count * size), element: number[] = [];
  for (let i = 0; i < count; i++) { accessor.getElement(i, element); for (let c = 0; c < size; c++) out[i * size + c] = element[c]; }
  return new BufferAttribute(out, size);
}

/**
 * Chunk-wide, in world space: the crowd was batched by material, so one node can hold many people's skin
 * while their tops and trousers sit in other nodes.
 */
async function masks(file: string) {
  const document = await io.read(file);
  const result: Record<string, { triangles: number; hidden: string }> = {};
  const parts: any[] = [];
  let people = 0;
  for (const node of document.getRoot().listNodes()) {
    const extras = node.getExtras() as { archetype?: string; runtimeOriginalSource?: string };
    const mesh = node.getMesh();
    if (!mesh || typeof extras.archetype !== "string") continue;
    people++;
    const matrix = new Matrix4().fromArray(node.getWorldMatrix());
    mesh.listPrimitives().forEach((primitive: any, i: number) => {
      const geometry = new BufferGeometry();
      geometry.setAttribute("position", attribute(primitive.getAttribute("POSITION")));
      geometry.setAttribute("normal", attribute(primitive.getAttribute("NORMAL")));
      geometry.applyMatrix4(matrix);
      const indices = primitive.getIndices();
      geometry.setIndex(Array.from(indices.getArray()));
      parts.push({ geometry, material: { name: primitive.getMaterial()?.getName() ?? "" }, original: indices.getCount() / 3,
        key: `${extras.runtimeOriginalSource}#${i}`, before: Array.from(indices.getArray()) });
    });
  }
  const hidden = hideCoveredSkin(parts, 0.03);
  let total = 0;
  for (const part of parts) {
    if (!/material 0$/.test(part.material.name)) continue;
    const original = part.before, kept = part.geometry.index!.array, bits = new Uint8Array(Math.ceil(part.original / 8));
    let k = 0;
    for (let t = 0; t < part.original; t++) {
      const same = k < kept.length && kept[k] === original[t * 3] && kept[k + 1] === original[t * 3 + 1] && kept[k + 2] === original[t * 3 + 2];
      if (same) k += 3; else bits[t >> 3] |= 1 << (t & 7);
    }
    total += part.original;
    if (part.key.startsWith("undefined") || result[part.key]) throw Error(`missing or duplicate person key ${part.key}`);
    result[part.key] = { triangles: part.original, hidden: Buffer.from(bits).toString("base64") };
  }
  return { result, people, hidden, total };
}

for (const chunk of chunks) {
  const desktop = await masks(`${root}locked-rev15z-${chunk}/contact-frontage.optimized.glb`);
  if (!desktop.people) continue;
  const mobile = await masks(`${root}locked-rev15z-${chunk}/contact-frontage.mobile.glb`);
  if (JSON.stringify(mobile.result) !== JSON.stringify(desktop.result)) throw Error(`${chunk}: desktop and mobile people differ`);
  const file = `${root}locked-rev15z-${chunk}/people-mask.json`;
  writeFileSync(file, JSON.stringify({ schemaVersion: 1, reachMetres: 0.03, note: "Skin triangles hidden under clothing; bit t of hidden = triangle t (scripts/gullyverse/people-mask.mts)", skins: desktop.result }) + "\n");
  console.log(`${chunk}: ${desktop.people} people, ${desktop.hidden} of ${desktop.total} skin triangles hidden (${(100 * desktop.hidden / desktop.total).toFixed(1)}%), ${(readFileSync(file).length / 1024).toFixed(1)} KB`);
}
