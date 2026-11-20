/** Build only the private representative chunk. Never modifies a production route. */
import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import crypto from "node:crypto";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import * as esbuild from "esbuild";
const root = path.resolve(
  path.dirname(fileURLToPath(import.meta.url)),
  "../..",
);
const source = process.argv[2];
if (!source)
  throw new Error(
    "Usage: node scripts/gullyverse/build-pilot.mjs /absolute/frozen-master.blend [output-directory]",
  );
const out = path.resolve(
  process.argv[3] ??
    path.join(root, "public/models/gullyverse/locked-rev15z-clean-v2"),
);
const plan = JSON.parse(
  await fs.readFile(
    path.join(root, "scripts/gullyverse/export-plan.json"),
    "utf8",
  ),
);
const sha = (b) => crypto.createHash("sha256").update(b).digest("hex");
if (sha(await fs.readFile(source)) !== plan.source.sha256)
  throw Error("Frozen native hash mismatch");
await fs.mkdir(out, { recursive: true });
const temp = await fs.mkdtemp(path.join(os.tmpdir(), "breeze-export-"));
plan.source.path = path.resolve(source);
const planPath = path.join(temp, "plan.json");
await fs.writeFile(planPath, JSON.stringify(plan));
const env = { ...process.env, GULLYVERSE_OUT: out, GULLYVERSE_PLAN: planPath };
function run(command, args) {
  const r = spawnSync(command, args, { cwd: root, env, stdio: "inherit" });
  if (r.status !== 0) throw Error(`${command} failed with ${r.status}`);
}
try {
  run(process.env.BLENDER ?? "blender", [
    "-b",
    "--python-exit-code",
    "1",
    "-t",
    "4",
    "--python",
    "scripts/gullyverse/inventory.py",
  ]);
  run(process.env.BLENDER ?? "blender", [
    "-b",
    "--python-exit-code",
    "1",
    "-t",
    "4",
    "--python",
    "scripts/gullyverse/export_locked.py",
    "--",
    "--plan",
    planPath,
    "--out",
    out,
  ]);
  for (const script of [
    "bake_lighting.py",
    "finish_lightmap.py",
    "reexport.py",
    "collision.py", "export_graffiti.py",
    "verify-uv.py",
  ])
    run(process.env.BLENDER ?? "blender", [
      "-b",
      "--python-exit-code",
      "1",
      "-t",
      "4",
      "--python",
      `scripts/gullyverse/${script}`,
    ]);
  run(process.execPath, ["scripts/gullyverse/postprocess.mjs", out]);
  for (const file of ["index.html", "pilot.css"])
    await fs.copyFile(
      path.join(root, "components/gullyverse-runtime", file),
      path.join(out, file),
    );
  await fs.writeFile(
    path.join(out, "contact.json"),
    JSON.stringify(plan.contact, null, 2) + "\n",
  );
  await fs.mkdir(path.join(out, "transcoders"), { recursive: true });
  for (const file of ["basis_transcoder.js", "basis_transcoder.wasm"])
    await fs.copyFile(
      path.join(root, "node_modules/three/examples/jsm/libs/basis", file),
      path.join(out, "transcoders", file),
    );
  await fs.copyFile(
    path.join(root, "node_modules/three/LICENSE"),
    path.join(out, "transcoders/LICENSE-three"),
  );
  await esbuild.build({
    entryPoints: [
      path.join(root, "components/gullyverse-runtime/PrivatePilot.tsx"),
    ],
    bundle: true,
    format: "esm",
    platform: "browser",
    outfile: path.join(out, "pilot.js"),
    minify: true,
    define: { "process.env.NODE_ENV": '"production"' },
  });
  run("python", [
    "scripts/gullyverse/validate-output.py",
    out,
    path.join(out, "source-inventory.json"),
    path.join(out, "validation"),
  ]);
  run("python", ["scripts/gullyverse/finalize-manifest.py", out]);
  if (sha(await fs.readFile(source)) !== plan.source.sha256)
    throw Error("Native source changed during export");
  console.log(
    `Private representative preview ready: python -m http.server 8893 --bind 127.0.0.1 --directory ${out}`,
  );
} finally {
  await fs.rm(temp, { recursive: true, force: true });
}
