import { chromium } from "playwright";
import { Matrix4, Quaternion, Vector3 } from "three";
const out = process.argv[2];
const shots = process.env.SHOTS === "crowd" ? [
  { name: "lane-characters-front", eye: [2.3, 8.35, -5.2], at: [2.2, 7.9, -8.4] },
  { name: "crowd-from-stage", eye: [0, 9.6, -42.5], at: [0, 8.2, -30] },
  { name: "crowd-from-plaza", eye: [0.5, 9.6, -19], at: [0, 8.4, -36] },
] : [
  { name: "lane-characters-front", eye: [2.3, 8.35, -5.2], at: [2.2, 7.9, -8.4] },
  { name: "lane-characters-back", eye: [2.1, 8.35, -11.4], at: [2.2, 7.9, -8.4] },
  { name: "cypher-character", eye: [-6.2, 8.5, -16.6], at: [-6.28, 8.2, -18.84] },
];
const pose = ({ eye, at }) => {
  const m = new Matrix4().lookAt(new Vector3(...eye), new Vector3(...at), new Vector3(0, 1, 0));
  const q = new Quaternion().setFromRotationMatrix(m);
  return [...eye, q.x, q.y, q.z, q.w, 40].map(v => +v.toFixed(5)).join(",");
};
const browser = await chromium.launch();
const servers = process.env.SHOTS === "crowd" ? [["before", "http://127.0.0.1:43991"], ["after", "http://127.0.0.1:43993"]] : [["before", "http://127.0.0.1:43992"], ["after", "http://127.0.0.1:43991"]];
for (const [label, base] of servers) {
  for (const shot of shots) {
    const page = await browser.newPage({ viewport: process.env.SHOTS === "crowd" ? { width: 960, height: 600 } : { width: 640, height: 640 } });
    page.on("console", m => { if (m.type() === "warning" && /crowd/i.test(m.text())) console.log("warn", m.text()); });
    await page.goto(`${base}/runtime-preview/cypher?start=plaza&tier=balanced&diagnostics&reviewCamera=${pose(shot)}`, { waitUntil: "domcontentloaded" });
    await page.waitForSelector(".gully-controls", { timeout: 900000 });
    await page.waitForFunction(() => performance.getEntriesByName("breeze:world-ready").length > 0, null, { timeout: 900000 });
    await page.waitForTimeout(20000); // probes stream in after the chunks
    await page.screenshot({ path: `${out}/${shot.name}-${label}.png`, timeout: 600000 });
    console.log("shot", label, shot.name);
    await page.close();
  }
}
await browser.close();
