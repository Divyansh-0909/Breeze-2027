import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {carryScannedMaterialReview} from "../../components/immersive/scannedRockSampling";
import manifest from "../../public/models/gullyverse/quarry-fidelity-correction/manifest.json";

test("fidelity previews persist privately without overriding the locked threefold sampling", () => {
  for (const selector of ["material-fidelity", "geology-fidelity"]) {
    const search = `?quarryReview=${selector}&rockTextureScale=4&diagnostics`;
    assert.equal(carryScannedMaterialReview("/aftermovie", search, true), `/aftermovie?quarryReview=${selector}`);
    assert.equal(carryScannedMaterialReview("/?arrival=hub", search, true), `/?arrival=hub&quarryReview=${selector}`);
    assert.equal(carryScannedMaterialReview("/aftermovie", search, false), "/aftermovie");
  }
  assert.equal(carryScannedMaterialReview("/aftermovie", "?diagnostics", true), "/aftermovie");
});

test("fidelity assets match the preserved host, local manifest and uniform source proportions", () => {
  const hash = (path: string) => createHash("sha256").update(readFileSync(path)).digest("hex");
  assert.equal(hash("public/models/gullyverse/quarry-fidelity-correction/fidelity-region.glb"), manifest.runtimeSHA256);
  assert.equal(hash("public/models/gullyverse/quarry-foundation-refined/foundation-geometry.glb"), manifest.hostGeometrySHA256);
  assert.equal(hash("public/models/gullyverse/recovered-c9-composition/composition-region.glb"), manifest.heroRuntimeDependencySHA256);
  assert.ok(Math.abs(manifest.regionLengthM - 35.55718478296376) < 1e-8);
  assert.equal(manifest.heroSourceUniformScale, 0.9);
  for (const source of manifest.sourceModels) {
    for (const scale of source.singularValues) assert.ok(Math.abs(scale - source.uniformScale) < 1e-10);
    assert.ok(source.uniformScale >= 0.75 && source.uniformScale <= 1.5);
  }
  assert.equal(manifest.approvedTextureScale, 3);
  assert.equal(manifest.newPBRImages, 0);
  assert.equal(manifest.parts.length, 1);
  assert.equal(manifest.parts[0].nodes.length, 3);
  assert.equal(manifest.collisionChanged, false);
  assert.equal(manifest.lightingChanged, false);
  assert.equal(manifest.publicDefaultChanged, false);
});
