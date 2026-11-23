/**
 * Moves road textures that every walkable chunk embeds (the same source images, encoded identically or
 * near-identically) out of the chunk GLBs into shared KTX2 files, so a visit downloads, transcodes and
 * uploads each one once instead of four or five times.
 *
 *   node scripts/gullyverse/share-textures.mjs            # rewrite the published chunks in place
 *   node scripts/gullyverse/share-textures.mjs --check    # report only
 *
 * An image is shared when the same name appears in two or more chunks of a variant and every chunk's
 * manifest records the same source image sha256 for it, or when its bytes are identical across chunks.
 * The first chunk's encoding becomes the shared file; the others reference it by URI. Meshes, materials,
 * samplers and every other byte of the GLB are unchanged; the binary chunk is compacted. Manifests record
 * the new GLB size and hash plus the shared files. Run after any chunk is republished.
 */
import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync, existsSync } from "node:fs";

const root = "public/models/gullyverse/";
const chunks = ["market-south", "market-north", "cypher-approach", "cypher-gate", "cypher-plaza", "cypher-audience"];
const shared = "locked-rev15z-shared";
const check = process.argv.includes("--check");
const sha = data => createHash("sha256").update(data).digest("hex");

function parse(file) {
  const glb = readFileSync(file);
  if (glb.readUInt32LE(0) !== 0x46546c67) throw Error(`${file}: not a GLB`);
  const jsonLength = glb.readUInt32LE(12), json = JSON.parse(glb.subarray(20, 20 + jsonLength).toString());
  const binHeader = 20 + jsonLength, binLength = glb.readUInt32LE(binHeader);
  return { json, bin: glb.subarray(binHeader + 8, binHeader + 8 + binLength) };
}
const imageBytes = ({ json, bin }, image) => {
  const view = json.bufferViews[image.bufferView];
  return bin.subarray(view.byteOffset ?? 0, (view.byteOffset ?? 0) + view.byteLength);
};
function sourceShas(chunk) {
  const manifest = JSON.parse(readFileSync(`${root}locked-rev15z-${chunk}/manifest.json`, "utf8")), byName = new Map();
  for (const material of manifest.materials ?? []) for (const image of material.sourceImages ?? []) {
    byName.set(image.name.replace(/\.[a-z]+$/, ""), image.sha256);
  }
  return byName;
}

/** Removes the given bufferViews, reindexes references and compacts buffer 0. */
function rewrite({ json, bin }, removeViews) {
  const keep = json.bufferViews.map((_, i) => !removeViews.has(i)), remap = [];
  let next = 0; keep.forEach((k, i) => { remap[i] = k ? next++ : -1; });
  const views = json.bufferViews.filter((_, i) => keep[i]);
  // Ranges in buffer 0: plain views and meshopt-compressed payloads.
  const ranges = [];
  for (const view of views) {
    const meshopt = view.extensions?.EXT_meshopt_compression;
    if (meshopt && meshopt.buffer === 0) ranges.push({ owner: meshopt, offset: meshopt.byteOffset ?? 0, length: meshopt.byteLength });
    if (view.buffer === 0) ranges.push({ owner: view, offset: view.byteOffset ?? 0, length: view.byteLength });
  }
  ranges.sort((a, b) => a.offset - b.offset);
  const parts = [], moved = new Map();
  let size = 0;
  for (const range of ranges) {
    const key = `${range.offset}:${range.length}`;
    if (!moved.has(key)) {
      size = Math.ceil(size / 16) * 16;
      moved.set(key, size);
      parts.push({ at: size, data: bin.subarray(range.offset, range.offset + range.length) });
      size += range.length;
    }
    range.owner.byteOffset = moved.get(key);
  }
  const out = Buffer.alloc(Math.ceil(size / 4) * 4);
  for (const part of parts) part.data.copy(out, part.at);
  json.bufferViews = views;
  json.buffers[0].byteLength = out.length;
  const reindex = holder => { if (holder && holder.bufferView !== undefined) holder.bufferView = remap[holder.bufferView]; };
  for (const accessor of json.accessors ?? []) {
    reindex(accessor);
    if (accessor.sparse) { reindex(accessor.sparse.indices); reindex(accessor.sparse.values); }
  }
  for (const image of json.images ?? []) reindex(image);
  return out;
}
function encode(json, bin) {
  let text = Buffer.from(JSON.stringify(json));
  text = Buffer.concat([text, Buffer.alloc((4 - text.length % 4) % 4, 0x20)]);
  const header = Buffer.alloc(12), jsonHeader = Buffer.alloc(8), binHeader = Buffer.alloc(8);
  header.writeUInt32LE(0x46546c67, 0); header.writeUInt32LE(2, 4);
  jsonHeader.writeUInt32LE(text.length, 0); jsonHeader.writeUInt32LE(0x4e4f534a, 4);
  binHeader.writeUInt32LE(bin.length, 0); binHeader.writeUInt32LE(0x004e4942, 4);
  header.writeUInt32LE(12 + 8 + text.length + 8 + bin.length, 8);
  return Buffer.concat([header, jsonHeader, text, binHeader, bin]);
}

if (!check) mkdirSync(root + shared, { recursive: true });
const sharedManifest = { schemaVersion: 1, note: "Road textures shared by the walkable chunks; see scripts/gullyverse/share-textures.mjs", files: [] };
for (const variant of ["optimized", "mobile"]) {
  const docs = chunks.map(chunk => ({ chunk, file: `${root}locked-rev15z-${chunk}/contact-frontage.${variant}.glb` }))
    .filter(d => existsSync(d.file)).map(d => ({ ...d, glb: parse(d.file), sources: sourceShas(d.chunk) }));
  // Candidates: image names embedded in two or more chunks.
  const byName = new Map();
  for (const doc of docs) (doc.glb.json.images ?? []).forEach((image, index) => {
    if (image.bufferView === undefined || !image.name) return;
    const entry = byName.get(image.name) ?? []; entry.push({ doc, index, bytes: imageBytes(doc.glb, image) }); byName.set(image.name, entry);
  });
  const plan = new Map(); // doc -> Map(imageIndex -> uri)
  let saved = 0;
  for (const [name, uses] of byName) {
    if (uses.length < 2) continue;
    const hashes = new Set(uses.map(u => sha(u.bytes)));
    const sourceHashes = new Set(uses.map(u => u.doc.sources.get(name)));
    const sameSource = sourceHashes.size === 1 && !sourceHashes.has(undefined);
    if (hashes.size !== 1 && !sameSource) continue;
    const canonical = uses[0].bytes, digest = sha(canonical).slice(0, 12);
    const fileName = `${name}.${variant}.${digest}.ktx2`;
    if (!check) writeFileSync(`${root}${shared}/${fileName}`, canonical);
    sharedManifest.files.push({ file: fileName, image: name, variant, bytes: canonical.length, sha256: sha(canonical), chunks: uses.map(u => u.doc.chunk), sourceSha256: sameSource ? [...sourceHashes][0] : null });
    for (const use of uses) {
      const images = plan.get(use.doc) ?? new Map(); images.set(use.index, `../${shared}/${fileName}`); plan.set(use.doc, images);
      saved += use.bytes.length;
    }
    saved -= canonical.length;
    console.log(`${variant}: ${name} ${(canonical.length / 1e6).toFixed(2)} MB in ${uses.length} chunks${hashes.size === 1 ? " (identical bytes)" : " (same source image)"}`);
  }
  for (const [doc, images] of plan) {
    const { json } = doc.glb, removeViews = new Set();
    for (const [index, uri] of images) {
      const image = json.images[index];
      removeViews.add(image.bufferView);
      delete image.bufferView;
      image.uri = uri;
    }
    // A view still used by anything else stays.
    for (const accessor of json.accessors ?? []) removeViews.delete(accessor.bufferView);
    for (const image of json.images ?? []) if (image.bufferView !== undefined) removeViews.delete(image.bufferView);
    const bin = rewrite(doc.glb, removeViews), glb = encode(json, bin);
    const before = readFileSync(doc.file).length;
    console.log(`  ${doc.chunk}.${variant}: ${(before / 1e6).toFixed(2)} -> ${(glb.length / 1e6).toFixed(2)} MB`);
    if (check) continue;
    writeFileSync(doc.file, glb);
    const manifestFile = `${root}locked-rev15z-${doc.chunk}/manifest.json`, manifest = JSON.parse(readFileSync(manifestFile, "utf8"));
    const name = `contact-frontage.${variant}.glb`;
    for (const list of [manifest.files, manifest.runtime?.files]) for (const entry of list ?? []) {
      if (entry.file === name) { entry.bytes = glb.length; entry.sha256 = sha(glb); entry.sharedImages = [...images.values()].map(uri => uri.split("/").pop()); }
    }
    writeFileSync(manifestFile, JSON.stringify(manifest, null, 2) + "\n");
  }
  console.log(`${variant}: ${(saved / 1e6).toFixed(1)} MB fewer bytes per full visit`);
}
if (!check) writeFileSync(`${root}${shared}/manifest.json`, JSON.stringify(sharedManifest, null, 2) + "\n");
