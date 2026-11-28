import * as THREE from "three";
import { accommodation } from "@/lib/accommodation";

/**
 * Procedural canvas atlases for the Phase 2 courtyard dressing (courtyard-dressing.ts). Everything is drawn once per
 * visit at `size` (1024 on high-class devices, 512 otherwise) in the night palette: charcoal, rust, chalk, sodium,
 * with the cool tube accent. Regions are returned in UV space (u0, v0, u1, v1; v up) for the geometry builders.
 */
export type Region = [number, number, number, number];

function canvas(width: number, height: number) {
  const c = document.createElement("canvas");
  c.width = width; c.height = height;
  const g = c.getContext("2d")!;
  return { c, g };
}
function texture(c: HTMLCanvasElement, srgb = true) {
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
  t.anisotropy = 4;
  t.generateMipmaps = true;
  t.minFilter = THREE.LinearMipmapLinearFilter;
  return t;
}
/** Region (pixels, y down) → UV rect (v up). */
const uv = (x: number, y: number, w: number, h: number, W: number, H: number): Region => [x / W, 1 - (y + h) / H, (x + w) / W, 1 - y / H];
let seed = 0x51f2;
const rand = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; };

/** Lived-in window interiors and lamp lenses (one emissive atlas, 2:1). */
export function emissiveAtlas(size: number) {
  const W = size, H = size / 2, { c, g } = canvas(W, H);
  seed = 0x51f2;
  g.fillStyle = "#000"; g.fillRect(0, 0, W, H);
  const cell = W / 4;
  const windows: Region[] = [];
  for (let i = 0; i < 4; i++) {
    const x = i * cell, w = cell, h = H * 0.8;
    // Warm tungsten room: brighter toward a ceiling bulb, fading to dim corners.
    const bulbX = x + w * (0.3 + 0.4 * rand()), bulbY = h * 0.18;
    const room = g.createRadialGradient(bulbX, bulbY, 2, bulbX, bulbY, w * 0.95);
    room.addColorStop(0, "#ffe0ad"); room.addColorStop(0.35, "#d9944a"); room.addColorStop(1, "#2a1608");
    g.fillStyle = room; g.fillRect(x, 0, w, h);
    // A curtain on one side (variant 0, 2), a hanging cloth line (1), a figure-less cupboard shape (3).
    g.fillStyle = "rgba(40, 22, 10, 0.78)";
    if (i % 2 === 0) { const cw = w * (0.28 + 0.15 * rand()); g.fillRect(i === 0 ? x : x + w - cw, 0, cw, h); }
    if (i === 1) { g.fillRect(x, h * 0.32, w, h * 0.04); for (let k = 0; k < 4; k++) g.fillRect(x + w * (0.12 + k * 0.22), h * 0.34, w * 0.12, h * 0.22); }
    if (i === 3) g.fillRect(x + w * 0.55, h * 0.3, w * 0.35, h * 0.7);
    // Bars: vertical grille (all) and a horizontal rail (variants 2, 3), dark iron.
    g.fillStyle = "#0b0907";
    const bars = 5 + (i % 2);
    for (let b = 1; b < bars; b++) g.fillRect(x + (w * b) / bars - w * 0.012, 0, w * 0.024, h);
    if (i >= 2) g.fillRect(x, h * 0.48, w, h * 0.025);
    // Frame.
    g.strokeStyle = "#0b0907"; g.lineWidth = w * 0.05; g.strokeRect(x + g.lineWidth / 2, g.lineWidth / 2, w - g.lineWidth, h - g.lineWidth);
    windows.push(uv(x, 0, w, h, W, H));
  }
  // Lenses along the bottom strip: sodium work-lamp lens and a cool fluorescent tube.
  const y = H * 0.82, lh = H * 0.16;
  const sodium = g.createRadialGradient(W * 0.15, y + lh / 2, 1, W * 0.15, y + lh / 2, W * 0.14);
  sodium.addColorStop(0, "#fff2d8"); sodium.addColorStop(0.45, "#ffc27a"); sodium.addColorStop(1, "#c4883e");
  g.fillStyle = sodium; g.fillRect(0, y, W * 0.3, lh);
  const tube = g.createLinearGradient(0, y, 0, y + lh);
  tube.addColorStop(0, "#b9cfd6"); tube.addColorStop(0.5, "#f4fbfd"); tube.addColorStop(1, "#b9cfd6");
  g.fillStyle = tube; g.fillRect(W * 0.35, y, W * 0.6, lh);
  return { texture: texture(c), windows, sodiumLens: uv(0, y, W * 0.3, lh, W, H), tubeLens: uv(W * 0.35, y, W * 0.6, lh, W, H) };
}

/** Speaker boxes, plastic crates, the oil drum (one lit atlas, square). */
export function propAtlas(size: number) {
  const W = size, H = size, { c, g } = canvas(W, H);
  seed = 0x7a31;
  const q = W / 2;
  // Speaker front (0,0): matte black cabinet, perforated grille, two drivers.
  g.fillStyle = "#3a3c40"; g.fillRect(0, 0, q, q);
  g.fillStyle = "#4a4c52"; g.fillRect(q * 0.06, q * 0.06, q * 0.88, q * 0.88);
  for (let yy = q * 0.08; yy < q * 0.92; yy += q * 0.025) for (let xx = q * 0.08; xx < q * 0.92; xx += q * 0.025) {
    g.fillStyle = "#0a0a0a"; g.beginPath(); g.arc(xx, yy, q * 0.006, 0, Math.PI * 2); g.fill();
  }
  for (const [cy, r] of [[q * 0.34, q * 0.24], [q * 0.76, q * 0.12]] as const) {
    g.strokeStyle = "#7a7c84"; g.lineWidth = q * 0.03; g.beginPath(); g.arc(q / 2, cy, r, 0, Math.PI * 2); g.stroke();
  }
  g.fillStyle = "#888888"; g.fillRect(q * 0.42, q * 0.94, q * 0.16, q * 0.03); // badge
  // Speaker side (q,0): worn tolex, corner protectors.
  g.fillStyle = "#3b3c40"; g.fillRect(q, 0, q, q);
  for (let k = 0; k < 900; k++) { g.fillStyle = `rgba(255,255,255,${0.02 * rand()})`; g.fillRect(q + rand() * q, rand() * q, 2, 2); }
  g.fillStyle = "#464648"; for (const [x, y] of [[0, 0], [1, 0], [0, 1], [1, 1]]) g.fillRect(q + x * q * 0.86, y * q * 0.86, q * 0.14, q * 0.14);
  // Crate (0,q): faded slate-blue plastic with slots.
  g.fillStyle = "#56615f"; g.fillRect(0, q, q, q); // faded by sun
  g.fillStyle = "#1a2024";
  for (let r = 0; r < 4; r++) for (let k = 0; k < 6; k++) g.fillRect(q * (0.08 + k * 0.145), q + q * (0.12 + r * 0.2), q * 0.1, q * 0.12);
  for (let k = 0; k < 500; k++) { g.fillStyle = `rgba(210,200,180,${0.05 * rand()})`; g.fillRect(rand() * q, q + rand() * q, 3, 1); }
  // Scuffs and scratches, and dirt rising from the bottom edge.
  for (let k = 0; k < 160; k++) { g.strokeStyle = `rgba(200,192,176,${0.12 * rand()})`; g.lineWidth = 1;
    const x = rand() * q, y = q + rand() * q; g.beginPath(); g.moveTo(x, y); g.lineTo(x + (rand() - 0.5) * q * 0.2, y + (rand() - 0.5) * q * 0.06); g.stroke(); }
  const dirt = g.createLinearGradient(0, q * 2, 0, q * 1.45);
  dirt.addColorStop(0, "rgba(38,30,22,0.55)"); dirt.addColorStop(1, "rgba(38,30,22,0)");
  g.fillStyle = dirt; g.fillRect(0, q * 1.45, q, q * 0.55);
  // Drum (q,q): rust over chipped dull blue paint, two rolling hoops.
  const drum = g.createLinearGradient(q, 0, W, 0);
  drum.addColorStop(0, "#5c3820"); drum.addColorStop(0.5, "#825030"); drum.addColorStop(1, "#4e3222");
  g.fillStyle = drum; g.fillRect(q, q, q, q);
  for (let k = 0; k < 140; k++) { g.fillStyle = `rgba(52,70,82,${0.55 * rand()})`; g.fillRect(q + rand() * q, q + rand() * q, q * 0.08 * rand(), q * 0.05 * rand()); }
  for (let k = 0; k < 2200; k++) { g.fillStyle = `rgba(${110 + 40 * rand()},${55 + 20 * rand()},${25},${0.25 * rand()})`; g.fillRect(q + rand() * q, q + rand() * q, 2, 2); }
  g.fillStyle = "#23180f"; g.fillRect(q, q + q * 0.32, q, q * 0.04); g.fillRect(q, q + q * 0.64, q, q * 0.04);
  return {
    texture: texture(c), speakerFront: uv(0, 0, q, q, W, H), speakerSide: uv(q, 0, q, q, W, H),
    crate: uv(0, q, q, q, W, H), drum: uv(q, q, q, q, W, H),
  };
}

/** Soft round contact shadow (alpha). */
export function blobTexture() {
  const { c, g } = canvas(64, 64);
  const r = g.createRadialGradient(32, 32, 2, 32, 32, 31);
  r.addColorStop(0, "rgba(0,0,0,0.9)"); r.addColorStop(0.55, "rgba(0,0,0,0.45)"); r.addColorStop(1, "rgba(0,0,0,0)");
  g.fillStyle = r; g.fillRect(0, 0, 64, 64);
  return texture(c);
}

/**
 * Stencils (GULLY VERSE, BREEZE '27) and torn monochrome battle flyers (top W × W/2), plus the Phase 3 zone cells
 * (W × W square below: zone stencils, chalk and rate boards, key board, register, mesh grille). Alpha atlas, 2:3.
 */
export function decalAtlas(size: number) {
  const W = size, H = size / 2, full = H + size, { c, g } = canvas(W, full);
  seed = 0x2b9d;
  g.clearRect(0, 0, W, full);
  const font = (px: number) => `900 ${px}px Impact, "Arial Black", "Helvetica Neue", sans-serif`;
  /** Spray stencil: overspray haze, solid letters cut by stencil bridges, drips. */
  const stencil = (text: string, x: number, y: number, w: number, h: number, ink: string, haze: string) => {
    g.save();
    g.beginPath(); g.rect(x, y, w, h); g.clip();
    g.textAlign = "center"; g.textBaseline = "middle";
    let px = h * 0.78; g.font = font(px);
    while (g.measureText(text).width > w * 0.94 && px > 8) { px *= 0.94; g.font = font(px); }
    g.filter = `blur(${Math.max(2, h * 0.05)}px)`; g.fillStyle = haze; g.fillText(text, x + w / 2, y + h / 2);
    g.filter = "none"; g.fillStyle = ink; g.fillText(text, x + w / 2, y + h / 2);
    // stencil bridges
    g.globalCompositeOperation = "destination-out";
    for (let k = 0; k < text.length * 2; k++) g.fillRect(x + w * (0.04 + 0.92 * k / (text.length * 2)), y + h * (0.3 + 0.35 * rand()), w * 0.006, h * 0.08);
    g.globalCompositeOperation = "source-over";
    for (let k = 0; k < text.length; k++) { // drips
      const dx = x + w * (0.08 + 0.84 * rand()), dy = y + h * 0.66;
      g.fillStyle = ink; g.fillRect(dx, dy, w * 0.004, h * (0.08 + 0.18 * rand()));
    }
    // weathering: chip the paint
    g.globalCompositeOperation = "destination-out";
    for (let k = 0; k < 600; k++) { g.fillStyle = `rgba(0,0,0,${0.5 * rand()})`; g.fillRect(x + rand() * w, y + rand() * h, 1 + 3 * rand(), 1 + 2 * rand()); }
    g.globalCompositeOperation = "source-over";
    g.restore();
  };
  const gullyVerse = uv(0, 0, W, H * 0.42, W, full);
  stencil("GULLY VERSE", 0, 0, W, H * 0.42, "rgba(211,204,188,0.78)", "rgba(211,204,188,0.22)");
  const breeze = uv(0, H * 0.42, W * 0.46, H * 0.2, W, full);
  stencil("BREEZE '27", 0, H * 0.42, W * 0.46, H * 0.2, "rgba(214,206,190,0.85)", "rgba(214,206,190,0.25)");
  // Flyers: six torn monochrome posters on the bottom strip.
  const flyers: Region[] = [];
  /** Flyer cells in canvas pixels [x, y, w, h] and their titles, for repainting with photo cards (zone-dressing.ts). */
  const flyerCells: { rect: [number, number, number, number]; title: string }[] = [];
  const titles = ["CYPHER", "BATTLE", "MIC CHECK", "RAW BARS", "BREEZE '27", "GULLY"];
  const fw = W / 6, fy = H * 0.64, fh = H * 0.36;
  titles.forEach((title, i) => {
    const x = i * fw + fw * 0.06, y = fy + fh * 0.03, w = fw * 0.88, h = fh * 0.94;
    g.save();
    // torn outline
    g.beginPath();
    const steps = 18; const jag = () => (rand() - 0.5) * w * 0.05;
    g.moveTo(x + jag(), y + jag());
    for (let k = 1; k <= steps; k++) g.lineTo(x + (w * k) / steps + jag(), y + jag());
    for (let k = 1; k <= steps; k++) g.lineTo(x + w + jag(), y + (h * k) / steps + jag() * (k > steps * 0.7 ? 3 : 1));
    for (let k = steps - 1; k >= 0; k--) g.lineTo(x + (w * k) / steps + jag(), y + h + jag() * 2);
    g.closePath(); g.clip();
    const paper = i % 3 === 1 ? "#cfc8b8" : i % 3 === 2 ? "#b9b3a6" : "#ddd6c6";
    g.fillStyle = paper; g.fillRect(x - 5, y - 5, w + 10, h + 10);
    // xerox grime
    for (let k = 0; k < 700; k++) { g.fillStyle = `rgba(20,20,20,${0.12 * rand()})`; g.fillRect(x + rand() * w, y + rand() * h, 1 + 2 * rand(), 1); }
    // halftone silhouette block (a figure with a mic)
    g.fillStyle = "#151515";
    g.beginPath(); g.arc(x + w * 0.5, y + h * 0.38, w * 0.15, 0, Math.PI * 2); g.fill();
    g.fillRect(x + w * 0.3, y + h * 0.48, w * 0.4, h * 0.22);
    g.fillRect(x + w * 0.62, y + h * 0.3, w * 0.05, h * 0.2);
    g.font = font(h * 0.13); g.textAlign = "center"; g.textBaseline = "top";
    g.fillText(title, x + w / 2, y + h * 0.05, w * 0.9);
    g.font = `700 ${h * 0.055}px "Arial Narrow", Arial, sans-serif`;
    g.fillText("SAT · 9PM · THE YARD", x + w / 2, y + h * 0.78, w * 0.9);
    g.fillRect(x + w * 0.1, y + h * 0.88, w * 0.8, h * 0.012);
    g.restore();
    // tape
    g.fillStyle = "rgba(200,190,160,0.55)"; g.fillRect(x + w * 0.38, y - h * 0.02, w * 0.24, h * 0.06);
    flyers.push(uv(i * fw, fy, fw, fh, W, full));
    flyerCells.push({ rect: [x, y, w, h], title });
  });
  const zones = zoneCells(g, H, W, full);
  return { texture: texture(c), gullyVerse, breeze, flyers, flyerCells, zones };
}

/** Accommodation tiers on the rate board, from lib/accommodation.ts (at most four rows fit). */
const RATE_ROWS: [string, string][] = accommodation.tiers.slice(0, 4).map(tier => [tier.name, tier.price]);

/**
 * Phase 3 zone cells (drafted by Gemini 4 Hydrogen, reviewed): drawn into the S × S square at y = `oy` of the decal
 * atlas (W × H overall), regions in the atlas's UV space.
 */
function zoneCells(g: CanvasRenderingContext2D, oy: number, S: number, H: number) {
  const W = S;
  seed = 0x4e8a;
  g.clearRect(0, oy, S, S);
  const stencilFont = (px: number) => `900 ${px}px Impact, "Arial Black", "Helvetica Neue", sans-serif`;
  const narrowFont = (px: number) => `700 ${px}px "Arial Narrow", Arial, sans-serif`;
  const cell = (nx: number, ny: number, nw: number, nh: number) => [nx * S, oy + ny * S, nw * S, nh * S] as const;

  /** Shared spray-paint pass: overspray haze, solid shape, optional stencil bridges, drips, chipped weathering. */
  const spray = (
    x: number, y: number, w: number, h: number,
    ink: string, haze: string,
    drawShape: () => void,
    bridges: number,
    dripSpan: [number, number, number],
  ) => {
    g.save();
    g.beginPath(); g.rect(x, y, w, h); g.clip();
    g.filter = `blur(${Math.max(2, h * 0.05)}px)`; g.fillStyle = haze; drawShape();
    g.filter = "none"; g.fillStyle = ink; drawShape();
    if (bridges > 0) {
      g.globalCompositeOperation = "destination-out";
      for (let k = 0; k < bridges; k++) {
        g.fillRect(x + w * (0.04 + (0.92 * k) / bridges), y + h * (0.28 + 0.36 * rand()), Math.max(1, w * 0.005), h * 0.08);
      }
      g.globalCompositeOperation = "source-over";
    }
    const [drips, minX, maxX] = dripSpan;
    g.fillStyle = ink;
    for (let k = 0; k < drips; k++) {
      g.fillRect(x + w * (minX + (maxX - minX) * rand()), y + h * 0.66, Math.max(1, w * 0.004), h * (0.08 + 0.18 * rand()));
    }
    g.globalCompositeOperation = "destination-out";
    for (let k = 0; k < 500; k++) {
      g.fillStyle = `rgba(0,0,0,${0.48 * rand()})`;
      g.fillRect(x + rand() * w, y + rand() * h, 1 + 2.5 * rand(), 1 + 2 * rand());
    }
    g.globalCompositeOperation = "source-over";
    g.restore();
  };

  /** Multi-line or single-line spray stencil fitted inside a cell. */
  const stencil = (lines: Array<[string, number, string?]>, x: number, y: number, w: number, h: number, ink: string, haze: string, drips = true) => {
    const sizes = lines.map(([text, wt]) => {
      let px = (h / lines.length) * 0.76 * wt;
      g.font = stencilFont(px);
      while (g.measureText(text).width > w * 0.92 && px > 8) { px *= 0.94; g.font = stencilFont(px); }
      return px;
    });
    const chars = lines.reduce((n, [t]) => n + t.length, 0);
    const totalWt = lines.reduce((s, [, wt]) => s + wt, 0);
    spray(x, y, w, h, ink, haze, () => {
      g.textAlign = "center"; g.textBaseline = "middle";
      let cy = y + h * 0.06;
      const solid = g.filter === "none"; // the ink pass (the haze pass is blurred); a line may carry its own ink
      lines.forEach(([text, wt, own], i) => {
        if (solid && own) g.fillStyle = own; else if (solid) g.fillStyle = ink;
        const band = (h * 0.88 * wt) / totalWt;
        g.font = stencilFont(sizes[i]);
        g.fillText(text, x + w / 2, cy + band / 2);
        cy += band;
      });
    }, chars * 2, [drips ? Math.min(10, Math.max(3, Math.floor(chars / 3))) : 0, 0.08, 0.92]);
  };

  // 1-4. Text stencils (5:1, 5:1, 5:1, 4:1)
  const [lsX, lsY, lsW, lsH] = cell(0.015, 0.015, 0.475, 0.095);
  stencil([["LINEUP DROPPING SOON", 1]], lsX, lsY, lsW, lsH, "rgba(211,204,188,0.8)", "rgba(211,204,188,0.18)");
  const [msX, msY, msW, msH] = cell(0.51, 0.015, 0.475, 0.095);
  stencil([["MORE DROPPING SOON", 1]], msX, msY, msW, msH, "rgba(211,204,188,0.8)", "rgba(211,204,188,0.18)");
  const [ciX, ciY, ciW, ciH] = cell(0.015, 0.125, 0.475, 0.095);
  stencil([["CHECK-IN OPENS SOON", 1]], ciX, ciY, ciW, ciH, "rgba(211,204,188,0.7)", "rgba(211,204,188,0.16)");
  const [stX, stY, stW, stH] = cell(0.51, 0.125, 0.475, 0.11875);
  // Two-tone (realism rescue): chalk "STAY //" over rust "ACCOMMODATION".
  stencil([["STAY //", 1.25, "rgba(226,219,208,0.92)"], ["ACCOMMODATION", 0.78, "rgba(140,82,44,0.95)"]], stX, stY, stW, stH, "rgba(226,219,208,0.92)", "rgba(211,204,188,0.18)", false); // no drips: chalk ticks crossed the rust line

  // 5. Stencilled right arrow (2:1)
  const [arX, arY, arW, arH] = cell(0.015, 0.882, 0.21, 0.105);
  spray(arX, arY, arW, arH, "rgba(211,204,188,0.8)", "rgba(211,204,188,0.18)", () => {
    g.beginPath();
    g.moveTo(arX + arW * 0.08, arY + arH * 0.34);
    g.lineTo(arX + arW * 0.54, arY + arH * 0.34);
    g.lineTo(arX + arW * 0.54, arY + arH * 0.14);
    g.lineTo(arX + arW * 0.92, arY + arH * 0.50);
    g.lineTo(arX + arW * 0.54, arY + arH * 0.86);
    g.lineTo(arX + arW * 0.54, arY + arH * 0.66);
    g.lineTo(arX + arW * 0.08, arY + arH * 0.66);
    g.closePath();
    g.fill();
  }, 2, [3, 0.18, 0.65]);

  // 6. Rate board (4:3): riveted metal + chalk rows from RATE_ROWS
  const [rbX, rbY, rbW, rbH] = cell(0.015, 0.26, 0.31, 0.2325);
  g.save();
  g.beginPath(); g.rect(rbX, rbY, rbW, rbH); g.clip();
  g.fillStyle = "#2b2e31"; g.fillRect(rbX, rbY, rbW, rbH);
  for (let k = 0; k < 180; k++) { g.fillStyle = `rgba(211,204,188,${0.02 * rand()})`; g.fillRect(rbX + rand() * rbW, rbY + rand() * rbH, 2, 1); }
  g.strokeStyle = "rgba(211,204,188,0.22)"; g.lineWidth = 2; g.strokeRect(rbX + 1, rbY + 1, rbW - 2, rbH - 2);
  const ins = Math.max(4, rbW * 0.045), rr = Math.max(1.5, rbW * 0.012);
  for (const [rx, ry] of [[0.06, 0], [0.35, 0], [0.65, 0], [0.94, 0], [0.06, 1], [0.35, 1], [0.65, 1], [0.94, 1], [0.06, 0.5], [0.94, 0.5]] as const) {
    const cx = rx === 0.06 ? rbX + ins : rx === 0.94 ? rbX + rbW - ins : rbX + rbW * rx;
    const cy = ry === 0 ? rbY + ins : ry === 1 ? rbY + rbH - ins : rbY + rbH * 0.5;
    g.fillStyle = "#0b0907"; g.beginPath(); g.arc(cx, cy, rr * 1.25, 0, Math.PI * 2); g.fill();
    g.fillStyle = "rgba(211,204,188,0.32)"; g.beginPath(); g.arc(cx - rr * 0.2, cy - rr * 0.2, rr * 0.85, 0, Math.PI * 2); g.fill();
  }
  const rPadX = rbW * 0.1, rPadY = rbH * 0.14, rDivX = rbX + rbW * 0.7, rowH = (rbH - rPadY * 2) / RATE_ROWS.length;
  g.strokeStyle = "rgba(211,204,188,0.4)"; g.lineWidth = Math.max(1, rbW * 0.005);
  g.beginPath(); g.moveTo(rDivX, rbY + rPadY); g.lineTo(rDivX, rbY + rbH - rPadY); g.stroke();
  // Hand-chalked rows (realism pass): a handwriting face, each row slightly tilted and offset, drawn on a layer that is
  // then eroded (chalk skips on the board's grain) before it is laid on the board.
  const chalkLayer = document.createElement("canvas"); chalkLayer.width = Math.ceil(rbW); chalkLayer.height = Math.ceil(rbH);
  const ch = chalkLayer.getContext("2d")!;
  const chalkFont = (px: number) => `700 ${px}px "Segoe Print", "Bradley Hand", "Comic Sans MS", cursive`;
  ch.font = chalkFont(Math.min(rowH * 0.42, rbH * 0.12)); ch.textBaseline = "middle"; ch.fillStyle = "rgba(232,226,214,0.95)";
  RATE_ROWS.forEach(([label, price], i) => {
    const cy = rPadY + rowH * (i + 0.5);
    ch.save(); ch.translate(rPadX, cy + (rand() - 0.5) * rowH * 0.08); ch.rotate((rand() - 0.5) * 0.035);
    ch.textAlign = "left"; ch.fillText(label, 0, 0, rDivX - rbX - rPadX - rbW * 0.03); ch.restore();
    ch.save(); ch.translate(rbW - rPadX, cy + (rand() - 0.5) * rowH * 0.08); ch.rotate((rand() - 0.5) * 0.05);
    ch.textAlign = "right"; ch.fillText(price, 0, 0, rbX + rbW - rPadX - rDivX - rbW * 0.03); ch.restore();
  });
  ch.globalCompositeOperation = "destination-out";
  for (let k = 0; k < 2600; k++) { ch.fillStyle = `rgba(0,0,0,${0.25 + 0.5 * rand()})`; ch.fillRect(rand() * rbW, rand() * rbH, 1 + 2 * rand(), 1); }
  ch.globalCompositeOperation = "source-over";
  g.drawImage(chalkLayer, rbX, rbY);
  // A smudged wipe across the lower rows, where old prices were rubbed out.
  const wipe = g.createLinearGradient(rbX, rbY + rbH * 0.55, rbX + rbW, rbY + rbH * 0.8);
  wipe.addColorStop(0, "rgba(211,204,188,0)"); wipe.addColorStop(0.5, "rgba(211,204,188,0.07)"); wipe.addColorStop(1, "rgba(211,204,188,0)");
  g.fillStyle = wipe; g.fillRect(rbX + rbW * 0.08, rbY + rbH * 0.5, rbW * 0.84, rbH * 0.36);
  RATE_ROWS.forEach((_, i) => {
    if (i < RATE_ROWS.length - 1) {
      const ruleY = rbY + rPadY + rowH * (i + 1);
      g.strokeStyle = "rgba(211,204,188,0.32)";
      g.beginPath(); g.moveTo(rbX + rPadX, ruleY); g.lineTo(rbX + rbW - rPadX, ruleY); g.stroke();
    }
  });
  g.restore();

  // 7. Contact board (4:3): framed chalkboard with smudged chalk text
  const [cbX, cbY, cbW, cbH] = cell(0.345, 0.26, 0.31, 0.2325);
  g.save();
  g.beginPath(); g.rect(cbX, cbY, cbW, cbH); g.clip();
  g.fillStyle = "#3a2617"; g.fillRect(cbX, cbY, cbW, cbH);
  const fW = cbW * 0.055, biX = cbX + fW, biY = cbY + fW, biW = cbW - fW * 2, biH = cbH - fW * 2;
  g.fillStyle = "#232624"; g.fillRect(biX, biY, biW, biH);
  g.strokeStyle = "#0b0907"; g.lineWidth = Math.max(1, cbW * 0.006); g.strokeRect(biX, biY, biW, biH);
  for (let k = 0; k < 14; k++) {
    const sx = biX + rand() * biW, sy = biY + rand() * biH, sr = biW * (0.08 + 0.14 * rand());
    const sm = g.createRadialGradient(sx, sy, 1, sx, sy, sr);
    sm.addColorStop(0, `rgba(211,204,188,${0.06 * rand()})`); sm.addColorStop(1, "rgba(211,204,188,0)");
    g.fillStyle = sm; g.fillRect(biX, biY, biW, biH);
  }
  g.textAlign = "left"; g.textBaseline = "middle";
  g.font = narrowFont(biH * 0.13); g.fillStyle = "rgba(211,204,188,0.9)";
  g.fillText("TALK TO THE CREW", biX + biW * 0.07, biY + biH * 0.18, biW * 0.86);
  g.fillStyle = "rgba(211,204,188,0.4)"; g.fillRect(biX + biW * 0.07, biY + biH * 0.28, biW * 0.86, Math.max(1, biH * 0.012));
  g.font = narrowFont(biH * 0.105);
  ["MAIL  >  ASK AT THE WINDOW", "CALL  >  9PM - 1AM", "INSTA  >  @BREEZE.GULLYVERSE"].forEach((line, i) => {
    g.fillStyle = `rgba(211,204,188,${0.82 + 0.12 * rand()})`;
    g.fillText(line, biX + biW * 0.07, biY + biH * (0.44 + i * 0.2), biW * 0.86);
  });
  g.restore();

  // 8. Key-hook board (4:3): 2x6 brass hooks, 7 hanging keys with round tags
  const [kbX, kbY, kbW, kbH] = cell(0.675, 0.26, 0.31, 0.2325);
  g.save();
  g.beginPath(); g.rect(kbX, kbY, kbW, kbH); g.clip();
  g.fillStyle = "#3a2617"; g.fillRect(kbX, kbY, kbW, kbH);
  for (let k = 0; k < 35; k++) { g.fillStyle = `rgba(11,9,7,${0.12 * rand()})`; g.fillRect(kbX, kbY + rand() * kbH, kbW, Math.max(1, kbH * 0.008)); }
  g.strokeStyle = "#0b0907"; g.lineWidth = Math.max(1, kbW * 0.01); g.strokeRect(kbX, kbY, kbW, kbH);
  const keySlots = new Set([0, 1, 3, 5, 6, 8, 10]);
  for (let row = 0; row < 2; row++) {
    for (let col = 0; col < 6; col++) {
      const hx = kbX + kbW * (0.14 + col * 0.144), hy = kbY + kbH * (0.22 + row * 0.44);
      g.fillStyle = "#0b0907"; g.beginPath(); g.arc(hx, hy - kbH * 0.04, kbW * 0.014, 0, Math.PI * 2); g.fill();
      if (keySlots.has(row * 6 + col)) {
        g.save(); g.translate(hx, hy); g.rotate((rand() - 0.5) * 0.14);
        g.fillStyle = "#d3ccbc"; g.beginPath(); g.arc(kbW * 0.016, kbH * 0.11, kbW * 0.026, 0, Math.PI * 2); g.fill();
        g.fillStyle = "#0b0907"; g.beginPath(); g.arc(kbW * 0.016, kbH * 0.092, kbW * 0.005, 0, Math.PI * 2); g.fill();
        g.strokeStyle = "rgba(211,204,188,0.82)"; g.lineWidth = Math.max(1.2, kbW * 0.008);
        g.beginPath(); g.arc(-kbW * 0.006, kbH * 0.045, kbW * 0.016, 0, Math.PI * 2); g.stroke();
        g.fillStyle = "rgba(211,204,188,0.82)";
        g.fillRect(-kbW * 0.011, kbH * 0.06, kbW * 0.01, kbH * 0.14);
        g.fillRect(-kbW * 0.001, kbH * 0.14, kbW * 0.014, kbH * 0.02);
        g.fillRect(-kbW * 0.001, kbH * 0.175, kbW * 0.018, kbH * 0.02);
        g.restore();
      }
      g.strokeStyle = "#8a6a3a"; g.lineWidth = Math.max(1.5, kbW * 0.012);
      g.beginPath(); g.moveTo(hx, hy - kbH * 0.03); g.lineTo(hx, hy + kbH * 0.025);
      g.arc(hx + kbW * 0.012, hy + kbH * 0.025, kbW * 0.012, Math.PI, 0, true); g.stroke();
    }
  }
  g.restore();

  // 9. Open register book (3:2)
  const [rgX, rgY, rgW, rgH] = cell(0.015, 0.508, 0.54, 0.36);
  g.save();
  g.beginPath(); g.rect(rgX, rgY, rgW, rgH); g.clip();
  g.fillStyle = "#0b0907"; g.fillRect(rgX, rgY, rgW, rgH);
  const bPad = rgW * 0.035, pGap = rgW * 0.008, pageW = (rgW - bPad * 2 - pGap) / 2, pageH = rgH - bPad * 2;
  for (let side = 0; side < 2; side++) {
    const px = rgX + bPad + side * (pageW + pGap), py = rgY + bPad;
    g.fillStyle = "#cfc8b8"; g.fillRect(px, py, pageW, pageH);
    for (let r = 1; r <= 10; r++) {
      const ly = py + (pageH * r) / 11;
      g.strokeStyle = "rgba(43,46,49,0.22)"; g.lineWidth = Math.max(1, rgH * 0.004);
      g.beginPath(); g.moveTo(px + pageW * 0.06, ly); g.lineTo(px + pageW * 0.94, ly); g.stroke();
      if (r >= 2 && r <= 8 && rand() > 0.25) {
        g.strokeStyle = `rgba(43,46,49,${0.55 + 0.25 * rand()})`; g.lineWidth = Math.max(1, rgH * 0.007);
        g.beginPath();
        let sx = px + pageW * 0.16;
        g.moveTo(sx, ly - pageH * 0.015);
        for (let s = 0, segs = 6 + Math.floor(rand() * 8); s < segs; s++) {
          sx += pageW * (0.03 + 0.045 * rand());
          if (sx > px + pageW * 0.88) break;
          g.lineTo(sx, ly - pageH * (0.008 + 0.03 * rand()));
        }
        g.stroke();
      }
    }
    g.strokeStyle = "rgba(110,65,39,0.28)"; g.lineWidth = Math.max(1, rgH * 0.005);
    g.beginPath(); g.moveTo(px + pageW * 0.14, py + pageH * 0.04); g.lineTo(px + pageW * 0.14, py + pageH * 0.96); g.stroke();
  }
  const spine = g.createLinearGradient(rgX + rgW * 0.45, 0, rgX + rgW * 0.55, 0);
  spine.addColorStop(0, "rgba(11,9,7,0)"); spine.addColorStop(0.5, "rgba(11,9,7,0.48)"); spine.addColorStop(1, "rgba(11,9,7,0)");
  g.fillStyle = spine; g.fillRect(rgX + rgW * 0.45, rgY + bPad, rgW * 0.1, pageH);
  g.restore();

  // 10. Rusted metal mesh grille (1:1): 24 cells across on transparent background
  const [grX, grY, grW, grH] = cell(0.585, 0.508, 0.36, 0.36);
  g.save();
  g.beginPath(); g.rect(grX, grY, grW, grH); g.clip();
  // Counter grille (railway enquiry window): sparse thin bars, so the clerk behind it stays visible.
  const cells = 12, step = grW / cells, bar = Math.max(1.5, step * 0.09);
  const drawBar = (bx: number, by: number, bw: number, bh: number, vert: boolean) => {
    g.fillStyle = "#3a2617"; g.fillRect(bx, by, bw, bh);
    g.fillStyle = "#6e4127";
    for (let k = 0; k < 6; k++) {
      if (vert) g.fillRect(bx, by + rand() * (bh - step), bw, step * (0.4 + rand()));
      else g.fillRect(bx + rand() * (bw - step), by, step * (0.4 + rand()), bh);
    }
  };
  for (let i = 0; i <= cells; i++) {
    const pos = i * step;
    drawBar(i === cells ? grX + grW - bar : Math.max(grX, grX + pos - bar / 2), grY, bar, grH, true);
    drawBar(grX, i === cells ? grY + grH - bar : Math.max(grY, grY + pos - bar / 2), grW, bar, false);
  }
  g.strokeStyle = "#3a2617"; g.lineWidth = Math.max(2, bar * 1.4);
  g.strokeRect(grX + g.lineWidth / 2, grY + g.lineWidth / 2, grW - g.lineWidth, grH - g.lineWidth);
  g.restore();

  return {
      lineupSoon: uv(lsX, lsY, lsW, lsH, W, H),
      moreSoon: uv(msX, msY, msW, msH, W, H),
      stay: uv(stX, stY, stW, stH, W, H),
      checkIn: uv(ciX, ciY, ciW, ciH, W, H),
      arrow: uv(arX, arY, arW, arH, W, H),
      rateBoard: uv(rbX, rbY, rbW, rbH, W, H),
      contactBoard: uv(cbX, cbY, cbW, cbH, W, H),
      keyBoard: uv(kbX, kbY, kbW, kbH, W, H),
      register: uv(rgX, rgY, rgW, rgH, W, H),
      grille: uv(grX, grY, grW, grH, W, H),
  };
}

/** Soft fBm noise for the dust haze (greyscale, tileable enough at this scale). */
export function hazeTexture() {
  const N = 256, { c, g } = canvas(N, N);
  seed = 0x9e37;
  const img = g.createImageData(N, N);
  const lattice = (p: number) => { const a = new Float32Array(p * p); for (let i = 0; i < a.length; i++) a[i] = rand(); return a; };
  const octaves = [4, 8, 16, 32].map(p => ({ p, l: lattice(p) }));
  for (let y = 0; y < N; y++) for (let x = 0; x < N; x++) {
    let v = 0, amp = 1, total = 0;
    for (const { p, l } of octaves) {
      const fx = (x / N) * p, fy = (y / N) * p, ix = Math.floor(fx), iy = Math.floor(fy), tx = fx - ix, ty = fy - iy;
      const s = (t: number) => t * t * (3 - 2 * t);
      const at = (a: number, b: number) => l[((b % p) * p) + (a % p)];
      const top = at(ix, iy) + (at(ix + 1, iy) - at(ix, iy)) * s(tx), bottom = at(ix, iy + 1) + (at(ix + 1, iy + 1) - at(ix, iy + 1)) * s(tx);
      v += (top + (bottom - top) * s(ty)) * amp; total += amp; amp *= 0.55;
    }
    const k = (y * N + x) * 4, b = Math.round(255 * Math.pow(v / total, 1.15));
    img.data[k] = img.data[k + 1] = img.data[k + 2] = b; img.data[k + 3] = 255;
  }
  g.putImageData(img, 0, 0);
  const t = texture(c, false);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  return t;
}
