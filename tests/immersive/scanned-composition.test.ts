import test from "node:test";
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {createHash} from "node:crypto";
import {carryScannedMaterialReview} from "../../components/immersive/scannedRockSampling";
import manifest from "../../public/models/gullyverse/recovered-c9-composition/manifest.json";

test("selected C9 persists across hub/stage URLs and cannot inherit another texture scale", () => {
  const search = "?quarryReview=scanned-composition&rockTextureScale=4&diagnostics";
  assert.equal(carryScannedMaterialReview("/aftermovie", search, true), "/aftermovie?quarryReview=scanned-composition");
  assert.equal(carryScannedMaterialReview("/?arrival=hub", search, true), "/?arrival=hub&quarryReview=scanned-composition");
  assert.equal(carryScannedMaterialReview("/aftermovie", search, false), "/aftermovie");
});

test("local C9 export is tied to the exact preserved host and uniform source transform", () => {
  const hash = (path: string) => createHash("sha256").update(readFileSync(path)).digest("hex");
  assert.equal(hash("public/models/gullyverse/recovered-c9-composition/composition-region.glb"), manifest.runtimeSHA256);
  assert.equal(hash("public/models/gullyverse/quarry-foundation-refined/foundation-geometry.glb"), manifest.hostGeometrySHA256);
  for (const value of manifest.singularValues) assert.ok(Math.abs(value - 0.9) < 1e-12);
  assert.equal(manifest.approvedTextureScale, 3);
  assert.equal(manifest.parts.length, 1);
  assert.equal(manifest.parts[0].nodes.length, 3);
  assert.equal(manifest.collisionChanged, false);
  assert.equal(manifest.lightingChanged, false);
  assert.equal(manifest.publicDefaultChanged, false);
  assert.equal(manifest.newPBRImages, 0);
});
