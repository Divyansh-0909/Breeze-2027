import {createRequire} from "node:module";
import {readFile, writeFile} from "node:fs/promises";
const require = createRequire(import.meta.url);
const validator = require(process.env.GULLYVERSE_GLTF_VALIDATOR_MODULE || "/workspace/recovery-phase2/validator-tools/node_modules/gltf-validator");
const rows = [];
for (const path of ["recovered-c8-material/scanned-materials.glb", "quarry-fidelity-correction/fidelity-region.glb", "quarry-fidelity-correction/fidelity-bake.glb"]) {
  const data = await readFile("public/models/gullyverse/" + path);
  const result = await validator.validateBytes(new Uint8Array(data), {uri: path.split("/").at(-1)});
  rows.push({path, bytes: data.length, result});
  console.log(path, result.issues.numErrors, "errors", result.issues.numWarnings, "warnings");
}
await writeFile("reports/recovery-quarry-fidelity-2026-10-19/raw/gltf-validation.json", JSON.stringify({validatorVersion: validator.version(), rows}, null, 2));
if (rows.some(row => row.result.issues.numErrors || row.result.issues.numWarnings)) process.exitCode = 1;
