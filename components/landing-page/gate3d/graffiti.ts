// Procedural graffiti for the tunnel past the arch. Same rule as textures.ts:
// every surface is drawn to a canvas at runtime, so the scene stays
// self-contained — no image downloads, nothing to 404 on deploy.
//
// The theme is GULLYVERSE — Indian street hip-hop — so the vocabulary here is
// aerosol writing plus the objects that culture is built on: cans, boomboxes,
// decks, mics, cassettes, and the auto-rickshaw. Copy runs in both Devanagari
// and Latin; the Devanagari is drawn only when the platform actually has the
// script (see `devanagariAvailable`), because a wall of tofu boxes is worse
// than a wall of transliteration.
//
// The tunnel's shell is ONE tiling texture whose v axis runs around the
// cross-section (left floor → wall → roof → wall → right floor), so the wall
// bands and the ceiling band are painted differently from the same canvas.
// Everything on that shell is deliberately abstract or pictorial — blobs,
// stencils, line-work. Legible words live on separate quads mounted flat on
// the walls (`makePieceTexture`), where their orientation is set by the mesh
// rather than by which way round the shell's UVs happen to run.
import * as THREE from "three";
import { TUNNEL, VAULT } from "./palette";
import { finish, mk, rng } from "./textures";

const HEAVY =
  "'Impact', 'Haettenschweiler', 'Arial Black', system-ui, sans-serif";
const DEVA =
  "'Nirmala UI', 'Noto Sans Devanagari', 'Mangal', 'Devanagari Sangam MN', 'Kohinoor Devanagari', sans-serif";

// Aerosol palette, taken from the posters already printed on the arch so the
// tunnel reads as the same world rather than a generic graffiti wall.
const AEROSOL = [
  "#d0392c", // poster red
  "#f2b30f", // poster yellow
  "#1f5fd0",
  "#2f9e5a",
  "#d6357f",
  "#efe6cf", // the posters' aged cream
];

const pick = <T,>(arr: readonly T[], r: () => number): T =>
  arr[Math.floor(r() * arr.length) % arr.length];

/**
 * Whether this device can actually draw Devanagari.
 *
 * Windows ships Nirmala UI and Mangal, macOS/iOS ship Devanagari Sangam, and
 * Android ships Noto — but a stripped Linux box has none of them, and the
 * browser silently substitutes the missing-glyph box. `೿` is unassigned,
 * so it ALWAYS draws that box; if a real letter draws identical pixels, the
 * script isn't installed and every Devanagari tag in here would be a rectangle.
 */
let devaCache: boolean | null = null;
function devanagariAvailable(): boolean {
  if (devaCache !== null) return devaCache;
  const S = 28;
  const { ctx } = mk(S, S);
  const shot = (ch: string) => {
    ctx.clearRect(0, 0, S, S);
    ctx.font = `22px ${DEVA}`;
    ctx.textBaseline = "middle";
    ctx.fillStyle = "#fff";
    ctx.fillText(ch, 2, S / 2);
    return ctx.getImageData(0, 0, S, S).data.join(",");
  };
  devaCache = shot("ग") !== shot("೿");
  return devaCache;
}

/** The word to actually paint, given the script this device can render. */
export function scriptFor(word: { text: string; deva?: string }): string {
  return word.deva && devanagariAvailable() ? word.deva : word.text;
}

// ---- aerosol primitives ----

/**
 * The scatter of dots around a sprayed edge. A canvas fill has a razor edge
 * and reads as vinyl; overspray is what makes the same shape read as paint
 * that came out of a can.
 */
function overspray(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  r: number,
  color: string,
  n: number,
  rand: () => number
): void {
  ctx.fillStyle = color;
  for (let i = 0; i < n; i++) {
    const a = rand() * Math.PI * 2;
    const d = r * (0.55 + rand() * 0.85);
    ctx.globalAlpha = 0.04 + rand() * 0.18;
    ctx.beginPath();
    ctx.arc(x + Math.cos(a) * d, y + Math.sin(a) * d, 0.5 + rand() * 1.8, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.globalAlpha = 1;
}

/** Paint runs off the underside of a shape — too much paint, held too long. */
function runs(
  ctx: CanvasRenderingContext2D,
  x0: number,
  x1: number,
  y: number,
  maxLen: number,
  color: string,
  n: number,
  rand: () => number
): void {
  ctx.fillStyle = color;
  for (let i = 0; i < n; i++) {
    const x = x0 + rand() * (x1 - x0);
    const w = 1.6 + rand() * 3.4;
    const len = maxLen * (0.25 + rand() * 0.95);
    ctx.fillRect(x, y, w, len);
    // the bead of paint that collects at the bottom of a run
    ctx.beginPath();
    ctx.arc(x + w / 2, y + len, w * 0.78, 0, Math.PI * 2);
    ctx.fill();
  }
}

type Lump = { x: number; y: number; rx: number; ry: number };

/**
 * A throw-up: fat rounded letterforms in two passes — every lump drawn
 * oversize in the outline colour first, then again at true size in the fill.
 * Two passes rather than stroking each lump, because stroking overlapping
 * shapes leaves the internal seams showing and it stops reading as one word.
 */
function throwUp(
  ctx: CanvasRenderingContext2D,
  lumps: Lump[],
  fill: string,
  outline: string,
  weight: number
): void {
  const pass = (grow: number, color: string) => {
    ctx.fillStyle = color;
    for (const l of lumps) {
      ctx.beginPath();
      ctx.ellipse(l.x, l.y, l.rx + grow, l.ry + grow, 0, 0, Math.PI * 2);
      ctx.fill();
    }
  };
  pass(weight, outline);
  pass(0, fill);
}

/** Builds the lumps for a `len`-lump throw-up along a baseline. */
function lumpRun(
  x: number,
  y: number,
  len: number,
  size: number,
  rand: () => number
): Lump[] {
  const out: Lump[] = [];
  let cx = x;
  for (let i = 0; i < len; i++) {
    const rx = size * (0.42 + rand() * 0.3);
    const ry = size * (0.5 + rand() * 0.4);
    out.push({ x: cx + rx, y: y + (rand() - 0.5) * size * 0.35, rx, ry });
    cx += rx * (1.35 + rand() * 0.5);
  }
  return out;
}

/** A loose one-stroke tag — the marks that go up in seconds, over everything. */
function scrawl(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  color: string,
  width: number,
  rand: () => number
): void {
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.beginPath();
  ctx.moveTo(x, y);
  const steps = 5 + Math.floor(rand() * 5);
  for (let i = 1; i <= steps; i++) {
    const t = i / steps;
    ctx.quadraticCurveTo(
      x + (t - 0.5 / steps) * w + (rand() - 0.5) * w * 0.2,
      y + (rand() - 0.5) * h * 1.5,
      x + t * w,
      y + (rand() - 0.5) * h * 0.7
    );
  }
  ctx.stroke();
}

/** The stubby arrow every throw-up seems to grow out of one corner. */
function arrow(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  size: number,
  angle: number,
  color: string
): void {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);
  ctx.fillStyle = color;
  ctx.beginPath();
  ctx.moveTo(0, -size * 0.16);
  ctx.lineTo(size * 0.6, -size * 0.16);
  ctx.lineTo(size * 0.6, -size * 0.42);
  ctx.lineTo(size, 0);
  ctx.lineTo(size * 0.6, size * 0.42);
  ctx.lineTo(size * 0.6, size * 0.16);
  ctx.lineTo(0, size * 0.16);
  ctx.closePath();
  ctx.fill();
  ctx.restore();
}

/**
 * Wildstyle: the interlocking angular shards a piece breaks into once the
 * writer stops caring whether you can read it. Genuine wildstyle is a lettered
 * construction, but at the size these sit on the wall the silhouette is the
 * whole read, so shards + arrows get there without pretending to spell.
 */
function wildstyle(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  fill: string,
  rand: () => number
): void {
  const bars = 3 + Math.floor(rand() * 3);
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate((rand() - 0.5) * 0.24);
  for (let i = 0; i < bars; i++) {
    const bx = (i / bars) * w;
    const bw = (w / bars) * (0.72 + rand() * 0.5);
    const skew = (rand() - 0.5) * h * 0.7;
    for (const [grow, color] of [
      [h * 0.11, "#0b0b0d"],
      [0, fill],
    ] as const) {
      ctx.fillStyle = color;
      ctx.beginPath();
      ctx.moveTo(bx - grow, -h / 2 - grow);
      ctx.lineTo(bx + bw + grow, -h / 2 + skew - grow);
      ctx.lineTo(bx + bw * 0.7 + grow, h / 2 + skew + grow);
      ctx.lineTo(bx - grow, h / 2 + grow);
      ctx.closePath();
      ctx.fill();
    }
  }
  arrow(ctx, w * 0.95, -h * 0.35, h * 0.8, -0.7, fill);
  ctx.restore();
}

// ---- hip-hop stencils ----
// Cut-and-spray silhouettes: no shading, no outline, just mass. They read at
// any size and from any angle, which is what makes stencils the one graffiti
// form that survives being glimpsed at speed from a moving camera.

type Icon =
  | "can"
  | "boombox"
  | "cassette"
  | "vinyl"
  | "mic"
  | "cap"
  | "cans2"
  | "headphones"
  | "chain"
  | "rickshaw"
  | "crown";

const ICONS: Icon[] = [
  "can",
  "boombox",
  "cassette",
  "vinyl",
  "mic",
  "cap",
  "cans2",
  "headphones",
  "chain",
  "rickshaw",
  "crown",
];

/** Drawn into a 1 × 1 box centred on the origin; the caller scales and rotates. */
function drawIcon(ctx: CanvasRenderingContext2D, kind: Icon): void {
  const rect = (x: number, y: number, w: number, h: number) => ctx.fillRect(x, y, w, h);
  const disc = (x: number, y: number, r: number) => {
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.fill();
  };
  const ring = (x: number, y: number, r: number, t: number) => {
    ctx.lineWidth = t;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, Math.PI * 2);
    ctx.stroke();
  };
  ctx.strokeStyle = ctx.fillStyle;
  ctx.lineCap = "round";

  switch (kind) {
    case "can": // the spray can itself — the tool as the tag
      rect(-0.16, -0.34, 0.32, 0.68);
      rect(-0.09, -0.44, 0.18, 0.1);
      rect(-0.05, -0.5, 0.1, 0.07);
      rect(-0.14, -0.06, 0.28, 0.1); // label band
      break;
    case "cans2": // a pair, one knocked over
      rect(-0.34, -0.3, 0.24, 0.6);
      rect(-0.28, -0.38, 0.12, 0.08);
      ctx.save();
      ctx.rotate(1.35);
      rect(-0.1, 0.06, 0.22, 0.54);
      ctx.restore();
      break;
    case "boombox":
      rect(-0.5, -0.24, 1, 0.52);
      disc(-0.26, 0.02, 0.16);
      disc(0.26, 0.02, 0.16);
      rect(-0.1, -0.16, 0.2, 0.12); // deck
      ring(0, -0.34, 0.28, 0.05); // handle
      break;
    case "cassette":
      rect(-0.44, -0.28, 0.88, 0.56);
      ctx.globalCompositeOperation = "destination-out";
      rect(-0.3, -0.16, 0.6, 0.22);
      ctx.globalCompositeOperation = "source-over";
      disc(-0.15, -0.05, 0.07);
      disc(0.15, -0.05, 0.07);
      break;
    case "vinyl":
      disc(0, 0, 0.46);
      ctx.globalCompositeOperation = "destination-out";
      disc(0, 0, 0.16);
      for (let i = 1; i <= 3; i++) ring(0, 0, 0.2 + i * 0.07, 0.015);
      ctx.globalCompositeOperation = "source-over";
      disc(0, 0, 0.05);
      break;
    case "mic":
      disc(0, -0.22, 0.2);
      rect(-0.05, -0.06, 0.1, 0.34);
      rect(-0.18, 0.28, 0.36, 0.07);
      break;
    case "cap": // snapback: dome and a flat brim
      ctx.beginPath();
      ctx.arc(0, 0.04, 0.34, Math.PI, 0);
      ctx.closePath();
      ctx.fill();
      rect(-0.05, -0.4, 0.1, 0.12);
      ctx.beginPath();
      ctx.ellipse(0.16, 0.06, 0.34, 0.09, 0, Math.PI, 0);
      ctx.fill();
      break;
    case "headphones":
      ctx.lineWidth = 0.09;
      ctx.beginPath();
      ctx.arc(0, 0.02, 0.36, Math.PI, 0);
      ctx.stroke();
      rect(-0.46, 0, 0.2, 0.3);
      rect(0.26, 0, 0.2, 0.3);
      break;
    case "chain":
      ctx.lineWidth = 0.07;
      for (let i = -1; i <= 1; i++) {
        ctx.beginPath();
        ctx.ellipse(i * 0.26, i % 2 ? 0.08 : -0.08, 0.16, 0.11, 0, 0, Math.PI * 2);
        ctx.stroke();
      }
      break;
    case "rickshaw": // the auto — the single most gully object there is
      ctx.beginPath();
      ctx.moveTo(-0.44, 0.22);
      ctx.lineTo(-0.44, -0.06);
      ctx.quadraticCurveTo(-0.3, -0.34, 0.02, -0.34);
      ctx.quadraticCurveTo(0.3, -0.34, 0.38, -0.02);
      ctx.lineTo(0.46, 0.22);
      ctx.closePath();
      ctx.fill();
      ctx.globalCompositeOperation = "destination-out";
      rect(-0.3, -0.2, 0.28, 0.2);
      rect(0.04, -0.2, 0.26, 0.2);
      ctx.globalCompositeOperation = "source-over";
      disc(-0.3, 0.3, 0.11);
      disc(0.32, 0.3, 0.11);
      break;
    case "crown": // the writer's signature since the first subway car
      ctx.beginPath();
      ctx.moveTo(-0.44, 0.22);
      ctx.lineTo(-0.34, -0.26);
      ctx.lineTo(-0.12, 0.02);
      ctx.lineTo(0, -0.32);
      ctx.lineTo(0.12, 0.02);
      ctx.lineTo(0.34, -0.26);
      ctx.lineTo(0.44, 0.22);
      ctx.closePath();
      ctx.fill();
      break;
  }
}

function stencil(
  ctx: CanvasRenderingContext2D,
  kind: Icon,
  x: number,
  y: number,
  size: number,
  color: string,
  rand: () => number
): void {
  overspray(ctx, x, y, size * 0.62, color, 120, rand);
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate((rand() - 0.5) * 0.3);
  ctx.scale(size, size);
  ctx.fillStyle = color;
  ctx.strokeStyle = color;
  drawIcon(ctx, kind);
  ctx.restore();
}

// ---- the vault shell ----

/** Soot-darkened brick, mottled and unevenly damp. Mostly gets painted over. */
function brickwork(
  ctx: CanvasRenderingContext2D,
  x0: number,
  y0: number,
  w: number,
  h: number,
  courseH: number,
  rand: () => number
): void {
  ctx.fillStyle = VAULT.mortar;
  ctx.fillRect(x0, y0, w, h);
  const brickW = courseH * 2.4;
  for (let y = y0, row = 0; y < y0 + h; y += courseH, row++) {
    const off = row % 2 ? brickW / 2 : 0;
    for (let x = x0 - off; x < x0 + w; x += brickW) {
      const k = 0.72 + rand() * 0.56;
      ctx.fillStyle = `rgb(${(36 * k) | 0},${(29 * k) | 0},${(26 * k) | 0})`;
      ctx.fillRect(x + 0.7, y + 0.7, brickW - 1.4, courseH - 1.4);
    }
  }
}

/**
 * The roof's black-and-white line-work: the dense, tag-over-tag scribble that
 * covers the ceiling of a real painted tunnel, drawn in one pale ink over
 * near-black. It has to be dense enough to read as *coverage* — sparse marks
 * look like a dirty ceiling rather than a painted one.
 */
function lineWork(
  ctx: CanvasRenderingContext2D,
  x0: number,
  y0: number,
  w: number,
  h: number,
  rand: () => number
): void {
  ctx.fillStyle = VAULT.ceiling;
  ctx.fillRect(x0, y0, w, h);

  ctx.strokeStyle = VAULT.chalk;
  ctx.lineCap = "round";
  for (let i = 0; i < 520; i++) {
    const x = x0 + rand() * w;
    const y = y0 + rand() * h;
    const s = 12 + rand() * 96;
    ctx.globalAlpha = 0.16 + rand() * 0.5;
    ctx.lineWidth = 1 + rand() * 2.6;
    const kind = rand();
    ctx.beginPath();
    if (kind < 0.28) {
      const turns = 2 + rand() * 3;
      for (let t = 0; t <= 1; t += 0.03) {
        const a = t * turns * Math.PI * 2;
        const r = t * s * 0.5;
        const px = x + Math.cos(a) * r;
        const py = y + Math.sin(a) * r * 0.8;
        t === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
      }
    } else if (kind < 0.5) {
      for (let k = 1; k <= 3; k++) {
        ctx.ellipse(x, y, (s * k) / 7, (s * k) / 10, rand() * 3, 0, Math.PI * 2);
      }
    } else if (kind < 0.72) {
      const n = 4 + Math.floor(rand() * 7);
      for (let k = 0; k < n; k++) {
        ctx.moveTo(x + k * 4, y);
        ctx.lineTo(x + k * 4 - s * 0.3, y + s * 0.5);
      }
    } else {
      let px = x;
      let py = y;
      ctx.moveTo(px, py);
      for (let k = 0; k < 5; k++) {
        const nx = px + (rand() - 0.3) * s * 0.6;
        const ny = py + (rand() - 0.5) * s * 0.5;
        ctx.quadraticCurveTo(px + (rand() - 0.5) * s, py + (rand() - 0.5) * s, nx, ny);
        px = nx;
        py = ny;
      }
    }
    ctx.stroke();
  }
  ctx.globalAlpha = 1;

  // outlined crowns, arrows and hardware scattered through the scribble, so
  // the ceiling is recognisably hip-hop rather than generic doodle
  for (let i = 0; i < 46; i++) {
    ctx.globalAlpha = 0.3 + rand() * 0.45;
    const kind = pick(["crown", "vinyl", "cassette", "can", "mic"] as const, rand);
    ctx.save();
    ctx.translate(x0 + rand() * w, y0 + rand() * h);
    ctx.rotate((rand() - 0.5) * 1.2);
    ctx.scale(34 + rand() * 46, 34 + rand() * 46);
    ctx.fillStyle = VAULT.chalk;
    ctx.strokeStyle = VAULT.chalk;
    drawIcon(ctx, kind);
    ctx.restore();
  }
  for (let i = 0; i < 26; i++) {
    ctx.globalAlpha = 0.28 + rand() * 0.4;
    arrow(ctx, x0 + rand() * w, y0 + rand() * h, 20 + rand() * 46, rand() * 6.3, VAULT.chalk);
  }
  ctx.globalAlpha = 1;
}

/** Layers of paint on one wall band: throw-ups, wildstyle, stencils, tags. */
function wallPaint(
  ctx: CanvasRenderingContext2D,
  x0: number,
  y0: number,
  w: number,
  h: number,
  rand: () => number
): void {
  // faded ghost layer first — the pieces nobody has gone over yet
  for (let i = 0; i < 16; i++) {
    const cx = x0 + rand() * w;
    const cy = y0 + h * (0.2 + rand() * 0.6);
    const size = h * (0.16 + rand() * 0.2);
    ctx.globalAlpha = 0.22 + rand() * 0.2;
    throwUp(
      ctx,
      lumpRun(cx, cy, 2 + Math.floor(rand() * 3), size, rand),
      pick(AEROSOL, rand),
      "#0b0b0d",
      size * 0.14
    );
  }
  ctx.globalAlpha = 1;

  // the live layer
  for (let i = 0; i < 20; i++) {
    const cx = x0 + rand() * w;
    const cy = y0 + h * (0.22 + rand() * 0.52);
    const size = h * (0.18 + rand() * 0.26);
    const fill = pick(AEROSOL, rand);

    if (rand() < 0.3) {
      wildstyle(ctx, cx, cy, size * 4, size * 1.5, fill, rand);
      continue;
    }

    const lumps = lumpRun(cx, cy, 2 + Math.floor(rand() * 4), size, rand);
    const right = lumps[lumps.length - 1];

    overspray(ctx, cx + size, cy, size * 1.5, fill, 90, rand);
    throwUp(ctx, lumps, fill, "#0b0b0d", size * 0.16);

    // highlight slash — one stroke of white on the top-left of each lump
    ctx.strokeStyle = "rgba(255,255,255,0.42)";
    ctx.lineWidth = Math.max(1.5, size * 0.09);
    ctx.lineCap = "round";
    for (const l of lumps) {
      ctx.beginPath();
      ctx.moveTo(l.x - l.rx * 0.5, l.y - l.ry * 0.55);
      ctx.lineTo(l.x + l.rx * 0.1, l.y - l.ry * 0.68);
      ctx.stroke();
    }

    runs(ctx, cx, right.x, cy + size * 0.7, size * 0.85, fill, 2 + Math.floor(rand() * 3), rand);
    if (rand() < 0.45) {
      arrow(ctx, right.x + right.rx, right.y - size * 0.5, size * 0.9, -0.5 + rand(), "#0b0b0d");
    }
  }

  // the culture's hardware, cut and sprayed over the pieces
  for (let i = 0; i < 13; i++) {
    stencil(
      ctx,
      pick(ICONS, rand),
      x0 + rand() * w,
      y0 + h * (0.24 + rand() * 0.5),
      h * (0.3 + rand() * 0.4),
      rand() < 0.55 ? "#0b0b0d" : pick(AEROSOL, rand),
      rand
    );
  }

  // tags over the top of everything, the way they actually go up
  for (let i = 0; i < 34; i++) {
    scrawl(
      ctx,
      x0 + rand() * w,
      y0 + h * (0.15 + rand() * 0.7),
      h * (0.2 + rand() * 0.45),
      h * 0.1,
      rand() < 0.7 ? "#0b0b0d" : pick(AEROSOL, rand),
      1.5 + rand() * 3.5,
      rand
    );
  }

  // grime creeping up from the floor — the band nobody paints
  const up = ctx.createLinearGradient(0, y0 + h, 0, y0 + h * 0.72);
  up.addColorStop(0, "rgba(6,6,8,0.92)");
  up.addColorStop(1, "rgba(6,6,8,0)");
  ctx.fillStyle = up;
  ctx.fillRect(x0, y0 + h * 0.72, w, h * 0.28);

  // and soot down from the roof. These walls are 5 m now, well past what
  // anyone reaches with a can, so the top of them has to look like nobody
  // ever has — otherwise the paint runs floor to ceiling and reads as wallpaper
  const down = ctx.createLinearGradient(0, y0, 0, y0 + h * 0.26);
  down.addColorStop(0, "rgba(5,5,7,0.94)");
  down.addColorStop(1, "rgba(5,5,7,0)");
  ctx.fillStyle = down;
  ctx.fillRect(x0, y0, w, h * 0.26);
}

/**
 * The tunnel's shell texture. u runs along the tunnel (and tiles), v runs
 * around the cross-section from the left floor to the right floor.
 *
 * `Tunnel.tsx` builds its UVs to match, so the band boundaries come from the
 * shared `TUNNEL` constants — retune the vault's proportions and the paint
 * re-lays itself onto the new walls.
 */
export function makeShellTexture(): THREE.CanvasTexture {
  const W = 2048;
  const H = 2048;
  const { c, ctx } = mk(W, H);
  const r = rng(7717);

  // v = 0 is the BOTTOM row of the canvas once three flips it, so the left
  // wall lives at the bottom of the image and the right wall at the top
  const leftTop = H * (1 - TUNNEL.wallEndV);
  const ceilTop = H * (1 - TUNNEL.ceilEndV);

  brickwork(ctx, 0, leftTop, W, H - leftTop, 9, r);
  brickwork(ctx, 0, 0, W, ceilTop, 9, r);
  lineWork(ctx, 0, ceilTop, W, leftTop - ceilTop, r);

  // The left wall's band runs top-of-wall → floor down the canvas, which is
  // the way anything drawn into it expects. The RIGHT wall's band runs the
  // other way — v keeps climbing past the roof, so its floor is at canvas y=0
  // — and painting it as-is puts the grime along the ceiling and stands every
  // stencil on its head. Flipping the band cancels both at once.
  wallPaint(ctx, 0, leftTop, W, H - leftTop, r);
  ctx.save();
  ctx.translate(0, ceilTop);
  ctx.scale(1, -1);
  // its own seed, so the two sides never come out as mirrors of each other
  wallPaint(ctx, 0, 0, W, ceilTop, rng(4402));
  ctx.restore();

  // paint carrying a little way onto the roof from both sides — a hard line
  // where the wall art stops looks like a mask, not a reach limit
  for (const [y, dir] of [
    [leftTop, -1],
    [ceilTop, 1],
  ] as const) {
    for (let i = 0; i < 14; i++) {
      const size = 26 + r() * 54;
      ctx.globalAlpha = 0.5 + r() * 0.4;
      throwUp(
        ctx,
        lumpRun(r() * W, y + dir * r() * 90, 2, size, r),
        pick(AEROSOL, r),
        "#0b0b0d",
        size * 0.15
      );
    }
  }
  ctx.globalAlpha = 1;

  const t = finish(c);
  t.wrapS = THREE.RepeatWrapping;
  t.wrapT = THREE.ClampToEdgeWrapping;
  return t;
}

// ---- the focal pieces mounted on the walls ----

/**
 * One legible piece on transparent ground, for a quad hung flat on a wall.
 *
 * Block letters in three passes — drop shadow, fat outline, fill — because
 * that stack is what separates a graffiti piece from text with a stroke on it.
 * Devanagari gets a lighter outline and no italic shear: the script's headline
 * (शिरोरेखा) is a horizontal bar, and a heavy graffiti outline closes the
 * counters under it until the word is a solid brick.
 */
export function makePieceTexture(
  word: { text: string; deva?: string },
  seed: number
): THREE.CanvasTexture {
  const r = rng(seed);
  const str = scriptFor(word);
  const isDeva = str !== word.text;

  const H = 256;
  const size = isDeva ? 128 : 150;
  const font = `900 ${size}px ${isDeva ? DEVA : HEAVY}`;

  const { ctx: pc } = mk(8, 8);
  pc.font = font;
  const W = Math.min(2048, Math.max(256, Math.ceil(pc.measureText(str).width + size * 1.1)));
  const { c, ctx } = mk(W, H);

  const fill = pick(AEROSOL, r);
  const cx = W / 2;
  const cy = H * 0.58;

  // spray cloud behind the letters, so the piece sits on the wall in a haze
  // of its own overspray rather than floating cleanly on the brick
  overspray(ctx, cx, cy - size * 0.18, Math.max(W, H) * 0.34, fill, 900, r);

  ctx.font = font;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.lineJoin = "round";
  ctx.miterLimit = 2;

  // the offset block behind, which is what gives a piece its depth
  ctx.fillStyle = "rgba(6,6,9,0.9)";
  ctx.fillText(str, cx + size * 0.07, cy + size * 0.07);

  ctx.strokeStyle = "#0b0b0d";
  ctx.lineWidth = size * (isDeva ? 0.14 : 0.24);
  ctx.strokeText(str, cx, cy);
  ctx.strokeStyle = "#f4efe2";
  ctx.lineWidth = size * (isDeva ? 0.06 : 0.1);
  ctx.strokeText(str, cx, cy);
  ctx.fillStyle = fill;
  ctx.fillText(str, cx, cy);

  // a highlight bar across the top third of the letters
  ctx.save();
  ctx.beginPath();
  ctx.rect(0, cy - size * 0.44, W, size * 0.16);
  ctx.clip();
  ctx.fillStyle = "rgba(255,255,255,0.34)";
  ctx.fillText(str, cx, cy);
  ctx.restore();

  runs(ctx, cx - W * 0.34, cx + W * 0.34, cy + size * 0.34, size * 0.42, fill, 7, r);
  scrawl(ctx, W * 0.1, H * 0.24, W * 0.8, H * 0.1, "#0b0b0d", 3, r);

  return finish(c);
}
