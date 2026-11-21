import fs from "node:fs/promises";
import path from "node:path";
import { spawnSync } from "node:child_process";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
const root = path.resolve(
    path.dirname(fileURLToPath(import.meta.url)),
    "../..",
  ),
  out = path.resolve(
    process.argv[2] ??
      path.join(root, "public/models/gullyverse/locked-rev15z-clean-v2"),
  ),
  tools = process.env.GULLYVERSE_TOOLS ?? "/dev/shm/gullyverse-runtime-tools",
  ktx =
    process.env.KTX_BIN ??
    path.join(tools, "ktx/KTX-Software-4.4.2-Linux-x86_64/bin");
const env = {
  ...process.env,
  TMPDIR: process.env.TMPDIR ?? "/dev/shm/gullyverse-runtime-tmp",
  PATH: ktx + ":" + process.env.PATH,
};
function run(command, args) {
  const r = spawnSync(command, args, { env, encoding: "utf8", maxBuffer: 2e6 });
  if (r.status !== 0) throw Error(r.stdout + "\n" + r.stderr);
  process.stdout.write(r.stdout);
}
const cli = path.join(tools, "node_modules/.bin/gltf-transform");
if (!process.argv.includes("--finish-only")) {
  run(cli, [
    "dedup",
    path.join(out, "contact-frontage.png.glb"),
    path.join(out, "contact-frontage.dedup.glb"),
  ]);
  await fs.copyFile(
    path.join(out, "contact-frontage.dedup.glb"),
    path.join(out, "contact-frontage.png.glb"),
  );
  const descriptor = JSON.parse(await fs.readFile(path.join(out, "manifest.json"), "utf8"));
  let geometry = path.join(out, "contact-frontage.png.glb");
  if (descriptor.chunk === "cypher-audience") {
    // Each opaque actor already has its own baked world-space UV chart.
    // Combining compatible primitives preserves those UVs and cuts draw calls.
    const joined = path.join(out, "contact-frontage.audience-joined.glb");
    run(cli, ["join", geometry, joined, "--keepNamed", "false", "--keepMeshes", "false"]);
    geometry = joined;
  }
  run(cli, [
    "uastc",
    geometry,
    path.join(out, "contact-frontage.ktx.glb"),
    "--level",
    "2",
    "--zstd",
    "18",
    "--rdo-multithreading",
    "false",
  ]);
  run(cli, [
    "meshopt",
    path.join(out, "contact-frontage.ktx.glb"),
    path.join(out, "contact-frontage.optimized.glb"),
    "--level",
    "medium",
    "--quantize-position",
    "16",
    "--quantize-normal",
    "14",
    "--quantize-texcoord",
    "16",
  ]);
  run(cli, [
    "resize",
    geometry,
    path.join(out, "contact-frontage.mobile.png.glb"),
    "--width",
    "1024",
    "--height",
    "1024",
  ]);
  run(cli, [
    "uastc",
    path.join(out, "contact-frontage.mobile.png.glb"),
    path.join(out, "contact-frontage.mobile.ktx.glb"),
    "--level",
    "2",
    "--zstd",
    "18",
    "--rdo-multithreading",
    "false",
  ]);
  run(cli, [
    "meshopt",
    path.join(out, "contact-frontage.mobile.ktx.glb"),
    path.join(out, "contact-frontage.mobile.glb"),
    "--level",
    "medium",
    "--quantize-position",
    "16",
    "--quantize-normal",
    "14",
    "--quantize-texcoord",
    "16",
  ]);
}
if (process.argv.includes("--geometry-only")) process.exit(0);
// Preserve numeric alpha and precomputed linear-HDR mipmaps.
const bakeManifest=JSON.parse(await fs.readFile(path.join(out,"manifest.json"),"utf8"));
run(path.join(ktx,"toktx"),["--t2","--zcmp","18","--mipmap","--assign_oetf","linear","--assign_primaries","bt709",path.join(out,"lightmap.ktx2"),...bakeManifest.bake.mipmaps.map(f=>path.join(out,f))]);
const manifest = JSON.parse(
  await fs.readFile(path.join(out, "manifest.json"), "utf8"),
);
const names = [
  "contact-frontage.png.glb",
  "contact-frontage.optimized.glb",
  "contact-frontage.mobile.glb",
  "lightmap.hdr",
  "lightmap.png",
  "lightmap.ktx2",
  ...(manifest.collision?.uri === "contact-frontage.collision.glb" ? ["contact-frontage.collision.glb", "triggers.json"] : []),
];
const rows = [];
for (const file of names) {
  const bytes = await fs.readFile(path.join(out, file));
  rows.push({
    file,
    bytes: bytes.length,
    sha256: crypto.createHash("sha256").update(bytes).digest("hex"),
  });
}
manifest.runtime = {
  baseline: "contact-frontage.png.glb",
  desktop: "contact-frontage.optimized.glb",
  mobile: "contact-frontage.mobile.glb",
  lightmap: "lightmap.ktx2",
  compression:
    "PBR: KTX2 UASTC with mipmaps + Meshopt; lightmap: lossless RGBA8 KTX2/zstd to preserve numeric alpha; 16-bit positions and normalized lightmap UVs, 14-bit normals; repeating source UVs outside [0,1] retained as floats; no decimation",
  files: rows,
};
await fs.writeFile(
  path.join(out, "manifest.json"),
  JSON.stringify(manifest, null, 2) + "\n",
);
console.log(JSON.stringify({ status: "PASS", files: rows }));
