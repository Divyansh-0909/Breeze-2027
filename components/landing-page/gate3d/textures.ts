// Every surface in the gate scene is drawn to a 2D canvas and uploaded as a
// texture — no image or font downloads, so the scene is self-contained and
// there is nothing to 404 on deploy. Printed panels, paving, foliage and the
// hanging theme letters all come from here.
import * as THREE from "three";
import { GATE, NIGHT, SIGN } from "./palette";

const SANS = "system-ui, 'Segoe UI', Roboto, Arial, sans-serif";
const SERIF = "Georgia, 'Times New Roman', serif";

/** Deterministic PRNG — scenes must look identical on every load. */
export function rng(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function mk(w: number, h: number) {
  const c = document.createElement("canvas");
  c.width = w;
  c.height = h;
  return { c, ctx: c.getContext("2d")! };
}

export function finish(
  c: HTMLCanvasElement,
  repeat?: [number, number]
): THREE.CanvasTexture {
  const t = new THREE.CanvasTexture(c);
  t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  if (repeat) {
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    t.repeat.set(repeat[0], repeat[1]);
  }
  t.needsUpdate = true;
  return t;
}

/** Per-pixel noise — the single most effective cure for CG flatness. */
export function grain(
  ctx: CanvasRenderingContext2D,
  w: number,
  h: number,
  amount: number,
  seed = 1
): void {
  const r = rng(seed);
  const img = ctx.getImageData(0, 0, w, h);
  const d = img.data;
  for (let i = 0; i < d.length; i += 4) {
    const n = (r() - 0.5) * amount;
    d[i] += n;
    d[i + 1] += n;
    d[i + 2] += n;
  }
  ctx.putImageData(img, 0, 0);
}

// ---- letter-spaced text (canvas has no tracking control) ----
function spacedWidth(
  ctx: CanvasRenderingContext2D,
  text: string,
  sp: number
): number {
  let w = 0;
  for (const ch of text) w += ctx.measureText(ch).width + sp;
  return w - sp;
}
function spacedFill(
  ctx: CanvasRenderingContext2D,
  text: string,
  x: number,
  y: number,
  sp: number
): number {
  let cx = x;
  ctx.textAlign = "left";
  for (const ch of text) {
    ctx.fillText(ch, cx, y);
    cx += ctx.measureText(ch).width + sp;
  }
  return cx - sp;
}

/** The printed-panel base: cool white vinyl with shading, seams and grain. */
function printedBase(
  ctx: CanvasRenderingContext2D,
  w: number,
  h: number,
  seed: number
): void {
  // deliberately below paper-white: the floods and emissive lift these panels
  // toward white, and starting at 1.0 leaves no headroom before they clip and
  // the print washes out
  const g = ctx.createLinearGradient(0, 0, 0, h);
  g.addColorStop(0, "#e3eaf2");
  g.addColorStop(0.5, "#d5dee8");
  g.addColorStop(1, "#bcc7d4");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, w, h);
  grain(ctx, w, h, 9, seed);
}

/** Small blue ZEISS lozenge, as printed on the real beam. */
function zeissMark(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  h: number
): number {
  const w = h * 3.1;
  ctx.fillStyle = "#0b3f8f";
  ctx.fillRect(x, y - h / 2, w, h);
  ctx.fillStyle = "#ffffff";
  ctx.font = `700 ${h * 0.56}px ${SANS}`;
  ctx.textBaseline = "middle";
  const t = "ZEISS";
  const sp = h * 0.09;
  const tw = spacedWidth(ctx, t, sp);
  spacedFill(ctx, t, x + (w - tw) / 2, y, sp);
  return w;
}

/** The BREEZE '26 fest lockup that sits at the top-right of the beam. */
function festMark(
  ctx: CanvasRenderingContext2D,
  cx: number,
  cy: number,
  scale: number
): void {
  ctx.textBaseline = "middle";
  ctx.fillStyle = "#12463c";
  ctx.font = `800 ${58 * scale}px ${SANS}`;
  const sp = 3 * scale;
  const w1 = spacedWidth(ctx, SIGN.fest[0], sp);
  spacedFill(ctx, SIGN.fest[0], cx - w1 / 2, cy - 30 * scale, sp);

  ctx.font = `800 ${64 * scale}px ${SANS}`;
  const w2 = spacedWidth(ctx, SIGN.fest[1], sp);
  spacedFill(ctx, SIGN.fest[1], cx - w2 / 2, cy + 30 * scale, sp);
}

/**
 * Top beam: sponsor lockup left, product centre, fest mark right.
 *
 * The canvas is sized from the beam's real proportions and every position is
 * derived from the world layout, so changing the pillar or opening dimensions
 * re-lays the artwork instead of stretching it.
 */
export function makeBeamTexture(): THREE.CanvasTexture {
  const W = 2048;
  const beamW = GATE.halfW * 2;
  const H = Math.round((W * GATE.beamH) / beamW);
  const u = H / 384; // type scale, relative to the original layout
  const { c, ctx } = mk(W, H);
  printedBase(ctx, W, H, 11);

  /** world x → canvas x */
  const wx = (x: number) => ((x + GATE.halfW) / beamW) * W;

  // panel seams fall on the pillar edges, as on the real printed gate
  ctx.strokeStyle = "rgba(110,128,146,0.16)";
  ctx.lineWidth = 2;
  for (const x of [-GATE.openingW / 2, 0, GATE.openingW / 2]) {
    ctx.beginPath();
    ctx.moveTo(wx(x), 0);
    ctx.lineTo(wx(x), H);
    ctx.stroke();
  }

  ctx.textBaseline = "middle";

  // --- sponsor lockup, confined to the left pillar's span ---
  // Each block is measured and shrunk to the panel it sits on, so narrowing
  // the pillars can never push the sponsor mark into the product name.
  const sponsorSpan = wx(-GATE.openingW / 2);
  const padX = 44 * u;
  const measureSponsor = (k: number) => {
    ctx.font = `300 ${86 * u * k}px ${SANS}`;
    const a = spacedWidth(ctx, SIGN.sponsor, 9 * u * k);
    ctx.font = `400 ${66 * u * k}px ${SERIF}`;
    const b = spacedWidth(ctx, SIGN.sponsorAlt, 4 * u * k);
    return a + 94 * u * k + b;
  };
  const sponsorAvail = sponsorSpan - padX * 1.4;
  const k = Math.min(1, sponsorAvail / measureSponsor(1));

  ctx.fillStyle = "#1a2028";
  ctx.font = `300 ${86 * u * k}px ${SANS}`;
  const vEnd = spacedFill(ctx, SIGN.sponsor, padX * 0.6, 120 * u, 9 * u * k);
  ctx.strokeStyle = "rgba(26,32,40,0.45)";
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(vEnd + 34 * u * k, 78 * u);
  ctx.lineTo(vEnd + 34 * u * k, 162 * u);
  ctx.stroke();
  ctx.font = `400 ${66 * u * k}px ${SERIF}`;
  ctx.fillStyle = "#2a323b";
  spacedFill(ctx, SIGN.sponsorAlt, vEnd + 60 * u * k, 122 * u, 4 * u * k);

  // --- product name, fitted to the opening it spans ---
  const nameAvail = wx(GATE.openingW / 2) - wx(-GATE.openingW / 2) - 30 * u;
  ctx.font = `300 ${132 * u}px ${SANS}`;
  const rawW = spacedWidth(ctx, SIGN.product, 6 * u);
  const nk = Math.min(1, nameAvail / rawW);
  ctx.fillStyle = "#171d24";
  ctx.font = `300 ${132 * u * nk}px ${SANS}`;
  const pw = spacedWidth(ctx, SIGN.product, 6 * u * nk);
  spacedFill(ctx, SIGN.product, (W - pw) / 2, 176 * u, 6 * u * nk);

  // --- "Co-engineered with [ZEISS]" ---
  ctx.font = `400 ${40 * u}px ${SANS}`;
  ctx.fillStyle = "#3b444e";
  const sw = ctx.measureText(SIGN.productSub).width;
  const markH = 34 * u;
  const total = sw + 20 * u + markH * 3.1;
  const sx = (W - total) / 2;
  ctx.textAlign = "left";
  ctx.fillText(SIGN.productSub, sx, 272 * u);
  zeissMark(ctx, sx + sw + 20 * u, 272 * u, markH);

  // --- fest mark, centred over the right pillar and fitted to it ---
  ctx.font = `800 ${58 * u}px ${SANS}`;
  const festRaw = spacedWidth(ctx, SIGN.fest[0], 3 * u);
  const festAvail = W - wx(GATE.openingW / 2) - padX * 1.4;
  festMark(ctx, wx(GATE.pillarX), 130 * u, u * Math.min(1, festAvail / festRaw));

  return finish(c);
}

/** Draw a stylised phone product shot (body + camera island). */
function phone(
  ctx: CanvasRenderingContext2D,
  cx: number,
  cy: number,
  w: number,
  angle: number,
  body: string,
  rim: string
): void {
  const h = w * 2.05;
  const r = w * 0.13;
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate(angle);

  ctx.shadowColor = "rgba(0,0,0,0.45)";
  ctx.shadowBlur = w * 0.3;
  ctx.shadowOffsetY = w * 0.08;

  const g = ctx.createLinearGradient(-w / 2, -h / 2, w / 2, h / 2);
  g.addColorStop(0, body);
  g.addColorStop(0.5, rim);
  g.addColorStop(1, body);
  ctx.fillStyle = g;
  ctx.beginPath();
  ctx.roundRect(-w / 2, -h / 2, w, h, r);
  ctx.fill();
  ctx.shadowColor = "transparent";

  // camera island
  const ix = -w * 0.16;
  const iy = -h * 0.3;
  const ir = w * 0.3;
  ctx.fillStyle = "rgba(255,255,255,0.10)";
  ctx.beginPath();
  ctx.arc(ix, iy, ir, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = "rgba(255,255,255,0.28)";
  ctx.lineWidth = w * 0.015;
  ctx.stroke();

  const lens: [number, number][] = [
    [ix - ir * 0.38, iy - ir * 0.34],
    [ix + ir * 0.36, iy - ir * 0.3],
    [ix - ir * 0.02, iy + ir * 0.42],
  ];
  for (const [lx, ly] of lens) {
    ctx.fillStyle = "#0a0c10";
    ctx.beginPath();
    ctx.arc(lx, ly, ir * 0.27, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "rgba(140,180,255,0.5)";
    ctx.beginPath();
    ctx.arc(lx - ir * 0.07, ly - ir * 0.07, ir * 0.09, 0, Math.PI * 2);
    ctx.fill();
  }

  // specular sweep across the body
  const s = ctx.createLinearGradient(-w / 2, -h / 2, w / 2, h * 0.1);
  s.addColorStop(0, "rgba(255,255,255,0)");
  s.addColorStop(0.45, "rgba(255,255,255,0.16)");
  s.addColorStop(0.6, "rgba(255,255,255,0)");
  ctx.fillStyle = s;
  ctx.beginPath();
  ctx.roundRect(-w / 2, -h / 2, w, h, r);
  ctx.fill();

  ctx.restore();
}

/**
 * Pillar face: spec copy on white at the top, big product panel below.
 * `side` picks which of the two reference boards to print.
 */
export function makePillarTexture(side: "left" | "right"): THREE.CanvasTexture {
  const W = 512;
  const H = Math.round((W * GATE.pillarH) / GATE.pillarW);
  const { c, ctx } = mk(W, H);
  printedBase(ctx, W, H, side === "left" ? 23 : 41);

  // the spec band is a fixed physical height, so on a taller board it simply
  // occupies a smaller fraction rather than scaling up with it
  const specTop = Math.round((H * 0.62) / GATE.pillarH);
  const spec = side === "left" ? SIGN.leftSpec : SIGN.rightSpec;

  // ---- product panel (everything below the spec band) ----
  const panelH = H - specTop - 18;
  const panelMid = specTop + panelH * 0.5; // keeps the product centred however tall the board gets
  ctx.save();
  ctx.beginPath();
  ctx.rect(18, specTop, W - 36, panelH);
  ctx.clip();

  if (side === "left") {
    // deep red silk backdrop
    const g = ctx.createRadialGradient(
      W * 0.62,
      specTop + panelH * 0.2,
      20,
      W * 0.5,
      specTop + panelH * 0.45,
      W * 1.15
    );
    g.addColorStop(0, "#c0202c");
    g.addColorStop(0.55, "#8c1220");
    g.addColorStop(1, "#3f070f");
    ctx.fillStyle = g;
    ctx.fillRect(0, specTop, W, H);
    // soft fabric folds
    const r = rng(7);
    for (let i = 0; i < 16; i++) {
      ctx.strokeStyle = `rgba(255,${90 + r() * 60},${90 + r() * 40},${0.05 + r() * 0.06})`;
      ctx.lineWidth = 10 + r() * 40;
      ctx.beginPath();
      const y0 = specTop + r() * (H - specTop);
      ctx.moveTo(-40, y0);
      ctx.bezierCurveTo(W * 0.3, y0 - 120 * r(), W * 0.7, y0 + 140 * r(), W + 40, y0 + 40);
      ctx.stroke();
    }
    phone(ctx, W * 0.5, panelMid, W * 0.45, -0.06, "#7d0d18", "#d0333f");
  } else {
    // soft ribbed pastel backdrop
    const g = ctx.createLinearGradient(0, specTop, W, H);
    g.addColorStop(0, "#e9d9dd");
    g.addColorStop(0.5, "#d8bfc6");
    g.addColorStop(1, "#b9959f");
    ctx.fillStyle = g;
    ctx.fillRect(0, specTop, W, H);
    for (let i = 0; i < 46; i++) {
      ctx.strokeStyle = `rgba(255,255,255,${0.05 + (i % 3) * 0.03})`;
      ctx.lineWidth = 5;
      const x = (i / 46) * (W + 120) - 60;
      ctx.beginPath();
      ctx.moveTo(x, specTop);
      ctx.lineTo(x - 70, H);
      ctx.stroke();
    }
    phone(ctx, W * 0.52, panelMid, W * 0.44, 0.09, "#efe7e2", "#cdbcb4");
  }

  // grade the product panel down — it is printed vinyl, not a lightbox
  ctx.fillStyle = "rgba(10,12,18,0.10)";
  ctx.fillRect(0, specTop, W, H);
  ctx.restore();

  // ---- spec copy on the white band ----
  ctx.textBaseline = "middle";
  ctx.textAlign = "left";
  const x = 34;
  let y = 64;
  ctx.fillStyle = NIGHT.ink;
  ctx.font = `800 46px ${SANS}`;
  ctx.fillText(spec[0], x, y);
  y += 58;
  ctx.font = `400 40px ${SANS}`;
  ctx.fillStyle = "#242a32";
  ctx.fillText(spec[1], x, y);
  y += 52;
  ctx.fillText(spec[2], x, y);

  return finish(c);
}

// ---- colour maths for surfaces that are tinted from artwork ----
function hexToRgb(hex: string): [number, number, number] {
  const h = hex.replace("#", "");
  return [
    parseInt(h.slice(0, 2), 16),
    parseInt(h.slice(2, 4), 16),
    parseInt(h.slice(4, 6), 16),
  ];
}
function rgbToHex(r: number, g: number, b: number): string {
  const cl = (v: number) => Math.max(0, Math.min(255, Math.round(v)));
  return `#${((1 << 24) | (cl(r) << 16) | (cl(g) << 8) | cl(b)).toString(16).slice(1)}`;
}
function shade(hex: string, k: number): string {
  const [r, g, b] = hexToRgb(hex);
  return rgbToHex(r * k, g * k, b * k);
}
/**
 * Mix a colour toward `toward` (white by default) by `t` — 0 leaves it
 * unchanged, 1 returns the target outright.
 *
 * Distinct from `shade` with k > 1: scaling channels blows out whichever one
 * is already brightest and pushes the hue, while mixing keeps the relationship
 * between channels. Passing a warm target lightens and tints in one step.
 */
export function lighten(hex: string, t: number, toward = "#ffffff"): string {
  const [r, g, b] = hexToRgb(hex);
  const [tr, tg, tb] = hexToRgb(toward);
  const m = (v: number, to: number) => v + (to - v) * t;
  return rgbToHex(m(r, tr), m(g, tg), m(b, tb));
}

/**
 * Average colour of the strip of a board texture that meets the ground.
 *
 * The plinths carry no artwork of their own, so they take their colour from
 * whatever is printed at the foot of the pillar above them — the base then
 * reads as the bottom of one continuous printed object instead of a white
 * shelf the poster is standing on. The cover-crop `offset`/`repeat` are
 * honoured, so we sample the pixels actually visible on the board, not the
 * part cropped away.
 */
export function sampleBottomColor(tex: THREE.Texture, fallback: string): string {
  const img = tex.image as (HTMLImageElement | HTMLCanvasElement) & {
    width: number;
    height: number;
  };
  if (!img || !img.width || !img.height) return fallback;

  // v=0 is the bottom of the image (flipY), so canvas y = height * (1 - v)
  const sx = img.width * tex.offset.x;
  const sw = Math.max(1, img.width * tex.repeat.x);
  const bandH = Math.max(1, Math.round(img.height * tex.repeat.y * 0.05));
  const sy = Math.max(0, img.height * (1 - tex.offset.y) - bandH);

  try {
    const { c, ctx } = mk(16, 4);
    ctx.drawImage(img, sx, sy, sw, bandH, 0, 0, 16, 4);
    const d = ctx.getImageData(0, 0, 16, 4).data;
    let r = 0;
    let g = 0;
    let b = 0;
    for (let i = 0; i < d.length; i += 4) {
      r += d[i];
      g += d[i + 1];
      b += d[i + 2];
    }
    const n = d.length / 4;
    c.width = c.height = 0; // release the scratch canvas
    return rgbToHex(r / n, g / n, b / n);
  } catch {
    return fallback; // tainted canvas (art served cross-origin)
  }
}

/**
 * Low plinth board: unlettered, tinted to the foot of the pillar it carries.
 * Same vinyl shading and grain as the printed panels so it still reads as
 * board rather than flat colour.
 */
export function makePlinthTexture(base: string): THREE.CanvasTexture {
  const W = 1024;
  const H = Math.round((W * GATE.plinthH) / GATE.plinthW);
  const { c, ctx } = mk(W, H);

  const g = ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, shade(base, 1.05));
  g.addColorStop(0.55, base);
  g.addColorStop(1, shade(base, 0.78)); // the base sits in its own shadow
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);
  grain(ctx, W, H, 9, 59);

  return finish(c);
}

/**
 * Tileable cement-block paving, running bond — the concrete pavers the whole
 * approach in the reference is laid with.
 *
 * The joints have to be a genuinely darker colour than the block faces, drawn
 * first and left showing through the gaps; painting blocks in the same colour
 * as the backdrop leaves the ground reading as flat grey with no pattern at
 * all. Each face then gets its own tone, a lit top-left bevel and a shadowed
 * bottom-right one, so the blocks look laid rather than printed.
 */
export function makePaverTexture(warm: boolean): THREE.CanvasTexture {
  const S = 1024;
  const { c, ctx } = mk(S, S);

  // lifted a step above true stone-grey: the path must read brighter than
  // the grass and mud around it even where the fixture spill doesn't reach
  const joint = warm ? [34, 21, 19] : [33, 35, 40];
  const face = warm ? [128, 82, 72] : [132, 134, 142];

  ctx.fillStyle = `rgb(${joint[0]},${joint[1]},${joint[2]})`;
  ctx.fillRect(0, 0, S, S);

  const bw = 128; // 8 across the tile
  const bh = 64; // 16 down  → 0.30 m × 0.15 m in world
  const gap = 5; // joint width
  const r = rng(warm ? 91 : 17);

  for (let row = 0; row * bh < S; row++) {
    const off = (row % 2) * (bw / 2); // running bond
    for (let col = -1; col * bw < S + bw; col++) {
      const x = col * bw + off + gap / 2;
      const y = row * bh + gap / 2;
      const w = bw - gap;
      const h = bh - gap;

      const v = (r() - 0.5) * 34; // per-block tone
      const cr = face[0] + v;
      const cg = face[1] + v;
      const cb = face[2] + v;
      ctx.fillStyle = `rgb(${cr},${cg},${cb})`;
      ctx.fillRect(x, y, w, h);

      // cast bevel: lit top/left, shadowed bottom/right
      ctx.fillStyle = "rgba(255,255,255,0.10)";
      ctx.fillRect(x, y, w, 2);
      ctx.fillRect(x, y, 2, h);
      ctx.fillStyle = "rgba(0,0,0,0.30)";
      ctx.fillRect(x, y + h - 2, w, 2);
      ctx.fillRect(x + w - 2, y, 2, h);

      // aggregate speckle in the cement
      for (let i = 0; i < 26; i++) {
        const t = r();
        ctx.fillStyle =
          t > 0.5
            ? `rgba(255,255,255,${0.03 + t * 0.05})`
            : `rgba(0,0,0,${0.04 + t * 0.08})`;
        ctx.fillRect(x + r() * w, y + r() * h, 1 + r() * 2, 1 + r() * 2);
      }
    }
  }

  // wear and staining pooled across the blocks — filled to each blot's own
  // bounding box, not the whole canvas, which is ~40× less fill work
  const d = rng(warm ? 5 : 33);
  for (let i = 0; i < 70; i++) {
    const cx = d() * S;
    const cy = d() * S;
    const rad = 40 + d() * 150;
    const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, rad);
    g.addColorStop(0, `rgba(0,0,0,${0.05 + d() * 0.09})`);
    g.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = g;
    ctx.fillRect(cx - rad, cy - rad, rad * 2, rad * 2);
  }

  grain(ctx, S, S, 16, warm ? 3 : 9);

  const t = finish(c, [1, 1]);
  t.anisotropy = 16; // the ground is seen at a hard grazing angle
  return t;
}

/**
 * Tileable poured-cement for the shoulder between walkway and road: smooth
 * light-grey concrete with tonal blotches and an expansion joint on each tile
 * edge (one tile ≈ 2.4 m, so joints land every 2.4 m like real slabwork).
 */
export function makeConcreteTexture(): THREE.CanvasTexture {
  const S = 512;
  const { c, ctx } = mk(S, S);
  ctx.fillStyle = "#82888f";
  ctx.fillRect(0, 0, S, S);

  const r = rng(619);
  for (let i = 0; i < 34; i++) {
    const cx = r() * S;
    const cy = r() * S;
    const rad = 30 + r() * 110;
    const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, rad);
    const dark = r() > 0.5;
    g.addColorStop(0, dark ? `rgba(40,44,50,${0.05 + r() * 0.08})` : `rgba(200,205,210,${0.04 + r() * 0.06})`);
    g.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = g;
    ctx.fillRect(cx - rad, cy - rad, rad * 2, rad * 2);
  }

  // expansion joints on the tile seams
  ctx.fillStyle = "rgba(30,33,38,0.55)";
  ctx.fillRect(0, 0, 4, S);
  ctx.fillRect(S - 4, 0, 4, S);

  grain(ctx, S, S, 11, 12);
  const t = finish(c, [1, 1]);
  t.anisotropy = 8;
  return t;
}

/**
 * Tileable asphalt for the road outside the ring: near-black with coarse
 * aggregate grain, oil-dark wear blotches and a worn dashed centre line. One
 * tile spans ~6.4 m of road length; v runs across the road's width.
 */
export function makeAsphaltTexture(): THREE.CanvasTexture {
  const W = 512;
  const H = 256;
  const { c, ctx } = mk(W, H);
  // a step lighter than true asphalt-black: under the night grade + vignette
  // anything darker vanishes entirely
  ctx.fillStyle = "#2b2d33";
  ctx.fillRect(0, 0, W, H);

  const r = rng(577);
  // wear: darker wheel-track bands and lighter patches
  for (let i = 0; i < 40; i++) {
    const cx = r() * W;
    const cy = r() * H;
    const rad = 24 + r() * 80;
    const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, rad);
    const dark = r() > 0.45;
    g.addColorStop(0, dark ? `rgba(8,9,12,${0.10 + r() * 0.12})` : `rgba(120,124,132,${0.04 + r() * 0.05})`);
    g.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = g;
    ctx.fillRect(cx - rad, cy - rad, rad * 2, rad * 2);
  }

  // worn dashed centre line
  ctx.fillStyle = "rgba(210,205,190,0.5)";
  ctx.fillRect(30, H / 2 - 4, 190, 8);
  ctx.fillRect(300, H / 2 - 4, 190, 8);

  grain(ctx, W, H, 14, 8);
  const t = finish(c, [1, 1]);
  t.anisotropy = 8;
  return t;
}

/**
 * Tileable packed-earth for the central ground: trodden mud with tonal
 * blotches, faint dry cracks and scuffed lighter patches. Deliberately free of
 * any repeating element bigger than a blotch so the tiling never shows across
 * a field this large.
 */
export function makeMudTexture(): THREE.CanvasTexture {
  const S = 512;
  const { c, ctx } = mk(S, S);
  ctx.fillStyle = "#2b211a";
  ctx.fillRect(0, 0, S, S);

  const r = rng(431);
  // broad tonal variation
  for (let i = 0; i < 60; i++) {
    const cx = r() * S;
    const cy = r() * S;
    const rad = 20 + r() * 90;
    const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, rad);
    const dark = r() > 0.5;
    g.addColorStop(0, dark ? `rgba(12,8,5,${0.10 + r() * 0.12})` : `rgba(92,72,52,${0.06 + r() * 0.09})`);
    g.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = g;
    ctx.fillRect(cx - rad, cy - rad, rad * 2, rad * 2);
  }
  // faint dry cracks
  ctx.strokeStyle = "rgba(10,7,4,0.28)";
  ctx.lineWidth = 1.4;
  for (let i = 0; i < 26; i++) {
    let x = r() * S;
    let y = r() * S;
    ctx.beginPath();
    ctx.moveTo(x, y);
    for (let s = 0; s < 4; s++) {
      x += (r() - 0.5) * 70;
      y += (r() - 0.5) * 70;
      ctx.lineTo(x, y);
    }
    ctx.stroke();
  }
  grain(ctx, S, S, 18, 6);
  const t = finish(c, [1, 1]);
  t.anisotropy = 8;
  return t;
}

/**
 * A clump of leaves with alpha. Instanced a few hundred times this builds a
 * believable canopy — far better than cones, and at night the silhouette is
 * what sells it.
 */
export function makeLeafClusterTexture(): THREE.CanvasTexture {
  const S = 256;
  const { c, ctx } = mk(S, S);
  ctx.clearRect(0, 0, S, S);
  const r = rng(1234);

  for (let i = 0; i < 54; i++) {
    const a = r() * Math.PI * 2;
    const rad = Math.pow(r(), 0.65) * S * 0.42;
    const x = S / 2 + Math.cos(a) * rad;
    const y = S / 2 + Math.sin(a) * rad;
    const lw = 18 + r() * 24;
    const lh = lw * (0.5 + r() * 0.3);
    const rot = r() * Math.PI * 2;
    const shade = 46 + r() * 60;
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(rot);
    ctx.fillStyle = `rgba(${Math.round(shade * 0.55)},${Math.round(shade)},${Math.round(shade * 0.6)},${0.82 + r() * 0.18})`;
    ctx.beginPath();
    ctx.ellipse(0, 0, lw / 2, lh / 2, 0, 0, Math.PI * 2);
    ctx.fill();
    // midrib
    ctx.strokeStyle = `rgba(${Math.round(shade * 0.3)},${Math.round(shade * 0.6)},${Math.round(shade * 0.35)},0.5)`;
    ctx.lineWidth = 1.2;
    ctx.beginPath();
    ctx.moveTo(-lw / 2, 0);
    ctx.lineTo(lw / 2, 0);
    ctx.stroke();
    ctx.restore();
  }
  return finish(c);
}

/** Night sky: deep zenith easing to a faint horizon lift. */
export function makeSkyTexture(): THREE.CanvasTexture {
  const W = 64;
  const H = 512;
  const { c, ctx } = mk(W, H);
  const g = ctx.createLinearGradient(0, 0, 0, H);
  g.addColorStop(0, "#04060e"); // canvas top → v=1 → zenith
  g.addColorStop(0.5, NIGHT.sky);
  g.addColorStop(0.84, NIGHT.skyHorizon);
  g.addColorStop(1, "#243250");
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);
  grain(ctx, W, H, 5, 2);
  return finish(c);
}
