import * as THREE from "three";

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
  g.fillStyle = "#4c5e68"; g.fillRect(0, q, q, q);
  g.fillStyle = "#1a2024";
  for (let r = 0; r < 4; r++) for (let k = 0; k < 6; k++) g.fillRect(q * (0.08 + k * 0.145), q + q * (0.12 + r * 0.2), q * 0.1, q * 0.12);
  for (let k = 0; k < 500; k++) { g.fillStyle = `rgba(210,200,180,${0.05 * rand()})`; g.fillRect(rand() * q, q + rand() * q, 3, 1); }
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

/** Stencils (GULLY VERSE, BREEZE '27) and torn monochrome battle flyers (alpha atlas, 2:1). */
export function decalAtlas(size: number) {
  const W = size, H = size / 2, { c, g } = canvas(W, H);
  seed = 0x2b9d;
  g.clearRect(0, 0, W, H);
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
  const gullyVerse = uv(0, 0, W, H * 0.42, W, H);
  stencil("GULLY VERSE", 0, 0, W, H * 0.42, "rgba(211,204,188,0.78)", "rgba(211,204,188,0.22)");
  const breeze = uv(0, H * 0.42, W * 0.46, H * 0.2, W, H);
  stencil("BREEZE '27", 0, H * 0.42, W * 0.46, H * 0.2, "rgba(214,206,190,0.85)", "rgba(214,206,190,0.25)");
  // Flyers: six torn monochrome posters on the bottom strip.
  const flyers: Region[] = [];
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
    flyers.push(uv(i * fw, fy, fw, fh, W, H));
  });
  return { texture: texture(c), gullyVerse, breeze, flyers };
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
