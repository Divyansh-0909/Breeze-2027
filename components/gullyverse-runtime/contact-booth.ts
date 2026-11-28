import * as THREE from "three";
import contactConfig from "./contact-space.json";
import frontage from "@/public/models/gullyverse/locked-rev15z-clean-v2/contact.json";
import { contactSpace } from "./native-space";

/**
 * Contact booth as a railway-style enquiry counter (user request, 28 Nov; reference: an Indian "unreserved ticket counter"
 * board): a bilingual (Hindi / English) enamel board over the window in the gully's night palette, a see-through grille
 * with a semicircular speaking cut at the bottom middle, and a clerk (one of the crowd's Rocketbox people) inside.
 *
 * The wall behind the window is solid, so the opening is cut in the shader: the facade and window materials discard
 * their fragments inside `windowHole` (fidelity.ts), and a booth box is built behind it (zone-dressing.ts).
 */
const { point } = contactSpace(contactConfig);
const normal = contactConfig.normal.map(x => x / Math.hypot(...contactConfig.normal));
const tangent = contactConfig.tangent.map(x => x / Math.hypot(...contactConfig.tangent));
const [left, right] = frontage.messageBoundsU, [bottom, top] = frontage.messageBoundsZ;

/** Booth depths along the contact frame's outward axis (the wall face is at frontage.depth, −22.01). */
export const booth = { left, right, bottom, top, mid: (left + right) / 2, grille: -21.9, clerk: -22.55, back: -23.2 };

/**
 * The window opening as an oriented box: [t0, t1, n0, n1, u0, u1, y0, y1, d0, d1] (u = x·t0 − z·t1, d = x·n0 − z·n1).
 * Inside the frame's reveal, from just in front of the old panel to past the wall's back face.
 */
export const windowHole = [tangent[0], tangent[1], normal[0], normal[1], left + 0.02, right - 0.02, bottom - 0.03, top + 0.03, -22.4, -21.83];

/** GLSL: discard inside the hole, or each of several holes (needs vBreezeWorld). */
export function holeCode(hole: number[] | number[][]): string {
  if (Array.isArray(hole[0])) return (hole as number[][]).map(h => holeCode(h)).join(`
`);
  const [t0, t1, n0, n1, u0, u1, y0, y1, d0, d1] = (hole as number[]).map(v => v.toFixed(4));
  return `{
  float hu = vBreezeWorld.x * ${t0} - vBreezeWorld.z * ${t1}, hd = vBreezeWorld.x * ${n0} - vBreezeWorld.z * ${n1};
  if (hu > ${u0} && hu < ${u1} && vBreezeWorld.y > ${y0} && vBreezeWorld.y < ${y1} && hd > ${d0} && hd < ${d1}) discard;
}`;
}


/** The clerk inside the booth (a crowd placement; rocketbox-crowd.ts). Faces out of the window. */
export function contactClerk() {
  const [x, , z] = point(booth.mid, booth.clerk, 0);
  const out = [normal[0], -normal[1]]; // world xz of +depth
  return { avatar: "Male_Adult_03", pose: "idle", position: [x, 7.2, z] as [number, number, number], yaw: Math.atan2(out[0], out[1]),
    height: 1.7, source: "BREEZE contact booth clerk" };
}

/**
 * Two more of the crew sitting inside on tall counter stools (user request, 28 Nov), one each side of the clerk, turned
 * different ways. Seat tops at 0.72 m so head and shoulders clear the 1 m sill; `stools` are the seat centres (u, d)
 * for the stool geometry (zone-dressing.ts).
 */
export const sitters = [
  { avatar: "Female_Adult_05", u: booth.mid - 1.55, d: -22.78, turn: 0.55, height: 1.62 },
  { avatar: "Male_Adult_10", u: booth.mid + 1.65, d: -22.88, turn: -1.05, height: 1.74 },
];
export const stoolSeat = 0.72;
export function contactSitters() {
  return sitters.map(s => {
    const [x, , z] = point(s.u, s.d, 0);
    const out = [normal[0], -normal[1]];
    const yaw = Math.atan2(out[0], out[1]) + s.turn;
    // The mesh's thighs rest sitAt.under × height above its feet; lift them onto the seat.
    const lift = contactConfig.floor + stoolSeat - 0.245 * s.height;
    return { avatar: s.avatar, pose: "sit", position: [x, lift, z] as [number, number, number], yaw, height: s.height,
      source: "BREEZE contact booth crew (seated)" };
  });
}

/**
 * The enamel board (2560 × 256, 10:1): a rust badge, "संपर्क करें" over "CONTACT US", and the crew's contact lines in both
 * languages, chalk-white on dark teal enamel, worn: grime, chips, rust bleeding from the rivets.
 */
export function enquiryBoard() {
  const W = 2560, H = 256; // 10:1
  const c = document.createElement("canvas"); c.width = W; c.height = H;
  const g = c.getContext("2d")!;
  let seed = 0x3c71;
  const rand = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };
  const enamel = g.createLinearGradient(0, 0, 0, H);
  enamel.addColorStop(0, "#2b4446"); enamel.addColorStop(1, "#1d3133");
  g.fillStyle = enamel; g.fillRect(0, 0, W, H);
  g.strokeStyle = "rgba(226,219,208,0.85)"; g.lineWidth = 5; g.strokeRect(14, 14, W - 28, H - 28);
  // Badge (as the railway's letter square): rust with a chalk "B".
  g.fillStyle = "#6e4127"; g.fillRect(34, 34, 188, 188);
  g.strokeStyle = "rgba(226,219,208,0.9)"; g.lineWidth = 4; g.strokeRect(44, 44, 168, 168);
  g.fillStyle = "#e4dccb"; g.textAlign = "center"; g.textBaseline = "middle";
  g.font = '900 132px Impact, "Arial Black", sans-serif'; g.fillText("B", 128, 124);
  g.font = '700 26px "Arial Narrow", Arial, sans-serif'; g.fillText("BREEZE '27", 128, 196);
  // Title: Hindi over English.
  const fit = (text: string, font: (px: number) => string, px: number, max: number) => {
    g.font = font(px); while (g.measureText(text).width > max && px > 12) { px -= 2; g.font = font(px); }
  };
  const deva = (px: number) => `700 ${px}px "Nirmala UI", "Mangal", "Noto Sans Devanagari", "Kohinoor Devanagari", sans-serif`;
  const latin = (px: number) => `900 ${px}px "Arial Black", Impact, sans-serif`;
  g.textAlign = "left"; g.fillStyle = "#e4dccb";
  fit("संपर्क करें", deva, 92, 760); g.fillText("संपर्क करें", 258, 86);
  fit("CONTACT US", latin, 78, 760); g.fillText("CONTACT US", 258, 186);
  // Divider and the crew's lines.
  g.fillStyle = "rgba(226,219,208,0.7)"; g.fillRect(1062, 40, 4, H - 80);
  const lines = ["ईमेल  MAIL  ›  ASK AT THE WINDOW", "कॉल  CALL  ›  9 PM – 1 AM  (रात 9 – 1)", "इंस्टा  INSTA  ›  @BREEZE.GULLYVERSE"];
  const mixed = (px: number) => `600 ${px}px "Nirmala UI", "Segoe UI", "Noto Sans Devanagari", Arial, sans-serif`;
  lines.forEach((line, i) => { fit(line, mixed, 48, W - 1094 - 50); g.fillStyle = "#e4dccb"; g.fillText(line, 1094, 62 + i * 66); });
  // Wear: grime, chips, rust bleeding from the four rivets, darker edges.
  for (let k = 0; k < 2600; k++) { g.fillStyle = `rgba(10,12,12,${0.1 * rand()})`; g.fillRect(rand() * W, rand() * H, 2 + 6 * rand(), 1 + 3 * rand()); }
  for (let k = 0; k < 340; k++) { g.fillStyle = `rgba(170,165,150,${0.25 * rand()})`; g.beginPath(); g.arc(rand() * W, rand() * H, 1 + 3 * rand(), 0, Math.PI * 2); g.fill(); }
  for (const [x, y] of [[26, 26], [W - 26, 26], [26, H - 26], [W - 26, H - 26]]) {
    const run = g.createLinearGradient(0, y, 0, y + 90);
    run.addColorStop(0, "rgba(110,65,39,0.65)"); run.addColorStop(1, "rgba(110,65,39,0)");
    g.fillStyle = run; g.fillRect(x - 5, y, 10, 90);
    g.fillStyle = "#3a3c3e"; g.beginPath(); g.arc(x, y, 9, 0, Math.PI * 2); g.fill();
  }
  const edge = g.createRadialGradient(W / 2, H / 2, H * 0.6, W / 2, H / 2, W * 0.55);
  edge.addColorStop(0, "rgba(0,0,0,0)"); edge.addColorStop(1, "rgba(0,0,0,0.35)");
  g.fillStyle = edge; g.fillRect(0, 0, W, H);
  const texture = new THREE.CanvasTexture(c);
  texture.colorSpace = THREE.SRGBColorSpace; texture.anisotropy = 8;
  return texture;
}
