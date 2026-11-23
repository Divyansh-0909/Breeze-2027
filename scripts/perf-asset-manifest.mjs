/**
 * Writes perf/asset-manifest.json: every runtime asset the gully (/) loads, with transfer size, decoded
 * geometry, texture dimensions/format, an estimated GPU allocation, which part of the walk uses it, when
 * it loads, and whether it is shared or duplicated.
 *
 *   node scripts/perf-asset-manifest.mjs
 *
 * GPU estimates: KTX2 UASTC/ETC1S transcode to a 4x4 block format (1 byte per texel; ASTC/BC7) with mips
 * (x 4/3), or RGBA8 (4 bytes per texel) where the device lacks block compression; lossless RGBA8 KTX2
 * lightmaps are 4 bytes per texel; HDR probes become 128-pixel PMREM cube-UV targets (half float).
 * Geometry is decoded vertex + index bytes. These are estimates, not driver VRAM.
 */
import { createHash } from "node:crypto";
import { existsSync, readFileSync, statSync, writeFileSync, mkdirSync } from "node:fs";
import { gzipSync } from "node:zlib";

const root = "public/models/gullyverse/";
const chunkOrder = { lane: ["market-south", "market-north", "cypher-approach", "cypher-gate"], later: ["cypher-plaza", "cypher-audience"] };
const destination = { "market-south": "market lane (south)", "market-north": "market lane (north)", "cypher-approach": "navigation board / sponsor LEDs",
  "cypher-gate": "cypher gate", "cypher-plaza": "plaza: houses, Events, Team, Contact, Accommodation, Aftermovie screen", "cypher-audience": "plaza crowd" };
const sha = data => createHash("sha256").update(data).digest("hex").slice(0, 12);
const ktxInfo = data => ({ width: data.readUInt32LE(20), height: data.readUInt32LE(24), levels: data.readUInt32LE(40), vkFormat: data.readUInt32LE(12), supercompression: data.readUInt32LE(44) });
const blockBytes = (w, h, levels) => { let total = 0; for (let l = 0; l < Math.max(1, levels); l++) total += Math.ceil(Math.max(1, w >> l) / 4) * Math.ceil(Math.max(1, h >> l) / 4) * 16; return total; };
const typeBytes = { 5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4 }, comps = { SCALAR: 1, VEC2: 2, VEC3: 3, VEC4: 4, MAT4: 16 };
const assets = [], seen = new Map();

function glb(file, chunk, variant) {
  const b = readFileSync(file), jsonLength = b.readUInt32LE(12), json = JSON.parse(b.subarray(20, 20 + jsonLength)), bin = 20 + jsonLength + 8;
  let triangles = 0, vertices = 0, geometryBytes = 0;
  const counted = new Set();
  for (const mesh of json.meshes) for (const p of mesh.primitives) {
    const indices = p.indices !== undefined ? json.accessors[p.indices] : null, position = json.accessors[p.attributes.POSITION];
    triangles += (indices ? indices.count : position.count) / 3; vertices += position.count;
    for (const index of [...Object.values(p.attributes), p.indices].filter(i => i !== undefined)) {
      if (counted.has(index)) continue; counted.add(index);
      const a = json.accessors[index]; geometryBytes += a.count * comps[a.type] * typeBytes[a.componentType];
    }
  }
  const textures = (json.images ?? []).map(image => {
    if (image.uri) return { name: image.name, external: image.uri };
    const view = json.bufferViews[image.bufferView], data = b.subarray(bin + (view.byteOffset ?? 0), bin + (view.byteOffset ?? 0) + view.byteLength);
    const info = ktxInfo(data), key = sha(data);
    const entry = { name: image.name, bytes: view.byteLength, ...info, gpuBlockBytes: blockBytes(info.width, info.height, info.levels), sha: key };
    seen.set(key, (seen.get(key) ?? 0) + 1);
    return entry;
  });
  return { file: file.replace("public", ""), chunk, variant, kind: "glb", bytes: b.length, gzipBytes: gzipSync(b, { level: 6 }).length,
    usedBy: destination[chunk], loads: chunkOrder.lane.includes(chunk) ? "initial (lane arrival); later for plaza arrivals" : "streamed after walking starts (initial for plaza arrivals)",
    meshes: json.meshes.length, materials: (json.materials ?? []).length, triangles: Math.round(triangles), vertices, decodedGeometryBytes: geometryBytes,
    embeddedTextureBytes: textures.reduce((s, t) => s + (t.bytes ?? 0), 0), textures,
    gpuEstimateBytes: geometryBytes + textures.reduce((s, t) => s + (t.gpuBlockBytes ?? 0), 0) };
}
for (const variant of ["optimized", "mobile"]) for (const chunk of [...chunkOrder.lane, ...chunkOrder.later]) {
  const base = `${root}locked-rev15z-${chunk}/`;
  assets.push(glb(`${base}contact-frontage.${variant}.glb`, chunk, variant));
  if (variant === "optimized") {
    const lightmap = readFileSync(base + "lightmap.ktx2"), info = ktxInfo(lightmap);
    assets.push({ file: `${base.replace("public", "")}lightmap.ktx2`, chunk, variant: "all", kind: "lightmap", bytes: lightmap.length, ...info,
      gpuEstimateBytes: info.width * info.height * 4, usedBy: destination[chunk], loads: "with its chunk" });
  }
}
for (const file of JSON.parse(readFileSync(root + "locked-rev15z-shared/manifest.json", "utf8")).files) {
  const data = readFileSync(root + "locked-rev15z-shared/" + file.file), info = ktxInfo(data);
  assets.push({ file: `/models/gullyverse/locked-rev15z-shared/${file.file}`, kind: "shared-texture", variant: file.variant, bytes: data.length, ...info,
    gpuEstimateBytes: blockBytes(info.width, info.height, info.levels), usedBy: file.chunks.join(", "), loads: "once, with the first chunk that needs it", shared: true });
}
const fidelity = JSON.parse(readFileSync(root + "locked-rev15z-fidelity/fidelity.json", "utf8"));
for (const [name, t] of Object.entries(fidelity.textures)) for (const [variant, file] of [["optimized", t.file], ["mobile", t.mobileFile]]) {
  const data = readFileSync(root + "locked-rev15z-fidelity/" + file), info = ktxInfo(data);
  assets.push({ file: `/models/gullyverse/locked-rev15z-fidelity/${file}`, kind: "fidelity-texture", variant, name, bytes: data.length, ...info,
    gpuEstimateBytes: blockBytes(info.width, info.height, info.levels), usedBy: name === "aggregate" ? "road colour (all chunks)" : "shutter murals / supporting graffiti", loads: "initial" });
}
for (const probe of fidelity.probes) for (const [variant, file] of [["optimized (no longer loaded)", probe.file], ["all", probe.mobileFile]]) {
  assets.push({ file: `/models/gullyverse/locked-rev15z-fidelity/${file}`, kind: "probe-hdr", variant, bytes: statSync(root + "locked-rev15z-fidelity/" + file).size,
    gpuEstimateBytes: variant === "all" ? 128 * 4 * 128 * 4 * 8 * 1.5 : 0, usedBy: `reflections near ${probe.id}`, loads: "background, after chunks" });
}
for (const [file, used] of [["/after-movie-720.mp4", "plaza screen loop (starts after the world has streamed)"], ["/after-movie.mp4", "Watch Aftermovie (full quality, from the start)"]]) {
  assets.push({ file, kind: "video", bytes: statSync("public" + file).size, usedBy: used, loads: "streamed (range requests)", gpuEstimateBytes: file.includes("720") ? 1280 * 720 * 4 : 1920 * 1080 * 4 });
}
for (const [key, count] of seen) if (count > 1) for (const a of assets) for (const t of a.textures ?? []) if (t.sha === key) t.duplicateOf = count;
assets.sort((a, b) => b.bytes - a.bytes);
mkdirSync("perf", { recursive: true });
const totals = {};
for (const a of assets) { const k = `${a.kind}:${a.variant}`; totals[k] = (totals[k] ?? 0) + a.bytes; }
writeFileSync("perf/asset-manifest.json", JSON.stringify({ generatedAt: new Date().toISOString(), totals, assets }, null, 1) + "\n");
console.log(Object.entries(totals).map(([k, v]) => `${k} ${(v / 1e6).toFixed(1)} MB`).join("\n"));
