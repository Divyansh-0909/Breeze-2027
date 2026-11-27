/**
 * Captures fixed review-camera views (detail shots that the map stops do not frame), e.g. Phase 2 lamps and windows.
 *   CHROME_PATH=... node -r ./perf/results-2026-11-26-gtx1650/gpu-flag.cjs scripts/capture-views.mjs <folder> [extra query]
 * Views are [name, x, y, z, yaw, pitch, fov]; yaw 0 looks toward −z, +π/2 toward −x.
 */
import { mkdir } from "node:fs/promises";
import { chromium } from "playwright";
import { Euler, Quaternion } from "three";

const base = process.env.BREEZE_BASE_URL ?? "http://127.0.0.1:3001";
const folder = `screenshots/${process.argv[2] ?? "views"}`;
const extra = process.argv[3] ?? "";
const views = [
  ["view-right-wing-lamps", 3, 12, -29, -Math.PI / 2, 0.22, 70],
  ["view-left-wing-windows", -3, 12.5, -31, Math.PI / 2, 0.18, 70],
  ["view-back-and-truss", 0, 12, -30, 0, 0.12, 70],
  ["view-cypher-corner-props", -4.5, 9.4, -27.5, 2.21, -0.14, 60],
  ["view-stencil-wall", -8.5, 8.9, -45.0, Math.PI / 2, -0.02, 60],
  ["view-gate-wires", 0, 9.3, -22, Math.PI, 0.32, 70],
];
await mkdir(folder, { recursive: true });
const browser = await chromium.launch({ args: ["--ignore-gpu-blocklist", "--autoplay-policy=no-user-gesture-required"] });
const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
for (const [name, x, y, z, yaw, pitch, fov] of views) {
  const q = new Quaternion().setFromEuler(new Euler(pitch, yaw, 0, "YXZ"));
  const camera = [x, y, z, q.x, q.y, q.z, q.w, fov].map(v => v.toFixed(5)).join(",");
  const page = await context.newPage();
  await page.goto(`${base}/runtime-preview/cypher?start=plaza&diagnostics&reviewCamera=${camera}${extra ? "&" + extra : ""}`, { waitUntil: "domcontentloaded" });
  await page.waitForSelector(".gully-controls", { timeout: 600000 });
  await page.waitForTimeout(5000);
  await page.screenshot({ path: `${folder}/${name}.png` });
  console.log(name);
  await page.close();
}
await browser.close();
