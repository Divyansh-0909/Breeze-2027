// Procedural wheatpaste posters: photo-forward when artist art exists, bold
// typographic field when it doesn't. Cream/red/blue/gold palette, clean
// sans throughout (readable at a distance), torn edges and drips keep the
// wheatpaste look. Source is swappable per-act via `posterUrl`.
import * as THREE from "three";
import { mk, finish, rng } from "../textures";
import { formatShortIST } from "./timelineMath";
import type { DerivedStatus, TimelineEvent } from "./types";

const SANS = "system-ui, 'Segoe UI', Roboto, Arial, sans-serif";
const CREAM = "#f4efe2";
const INK = "#141210";
const RED = "#d0342a";
const BLUE = "#1f4f9c";
const GOLD = "#ffc24b";
const YELLOW = "#e5a81c";

/** Wall ribbon baked into the poster top. Null = no ribbon. */
export type PosterRibbon = "NOW" | "NEXT" | "DELAYED" | "CANCELLED" | null;

const cache = new Map<string, THREE.CanvasTexture>();

function fit(
  ctx: CanvasRenderingContext2D,
  text: string,
  maxW: number,
  base: number,
  weight = 800
): number {
  let size = base;
  ctx.font = `${weight} ${size}px ${SANS}`;
  while (size > 30 && ctx.measureText(text).width > maxW) {
    size -= 4;
    ctx.font = `${weight} ${size}px ${SANS}`;
  }
  return size;
}

/** Cover-crop an image into a rect (no stretch, no letterbox). */
function drawCover(
  ctx: CanvasRenderingContext2D,
  img: HTMLImageElement,
  x: number,
  y: number,
  w: number,
  h: number
): void {
  const ia = img.width / img.height;
  const ta = w / h;
  let sw: number;
  let sh: number;
  let sx: number;
  let sy: number;
  if (ia > ta) {
    sh = img.height;
    sw = sh * ta;
    sx = (img.width - sw) / 2;
    sy = 0;
  } else {
    sw = img.width;
    sh = sw / ta;
    sx = 0;
    sy = (img.height - sh) / 2;
  }
  ctx.drawImage(img, sx, sy, sw, sh, x, y, w, h);
}

function ribbonStyle(ribbon: Exclude<PosterRibbon, null>): {
  bg: string;
  fg: string;
  label: string;
} {
  switch (ribbon) {
    case "NOW":
      return { bg: RED, fg: CREAM, label: "● NOW" };
    case "NEXT":
      return { bg: BLUE, fg: CREAM, label: "NEXT" };
    case "DELAYED":
      return { bg: GOLD, fg: INK, label: "DELAYED" };
    case "CANCELLED":
      return { bg: "#222222", fg: CREAM, label: "CANCELLED" };
  }
}

function drawPoster(
  ctx: CanvasRenderingContext2D,
  W: number,
  H: number,
  ev: TimelineEvent,
  status: DerivedStatus,
  ribbon: PosterRibbon,
  photo: HTMLImageElement | undefined,
  seed: number
): void {
  const r = rng(seed);
  const RIBBON_H = ribbon ? 64 : 0;

  // ---- ground: photo large, or a bold ink field when there is none ----
  if (photo) {
    ctx.fillStyle = INK;
    ctx.fillRect(0, 0, W, H);
    drawCover(ctx, photo, 0, RIBBON_H, W, 500);
    // scrim so the name sits on the photo, not in it
    const scrim = ctx.createLinearGradient(0, RIBBON_H, 0, RIBBON_H + 500);
    scrim.addColorStop(0, "rgba(5,5,8,0.15)");
    scrim.addColorStop(0.55, "rgba(5,5,8,0.25)");
    scrim.addColorStop(1, "rgba(5,5,8,0.88)");
    ctx.fillStyle = scrim;
    ctx.fillRect(0, RIBBON_H, W, 500);
    // cream stock below the photo for the time block
    ctx.fillStyle = CREAM;
    ctx.fillRect(0, RIBBON_H + 500, W, H - RIBBON_H - 500);
  } else {
    // no art: near-black field, accent top band — type does all the work
    const accent = [RED, BLUE, YELLOW][seed % 3];
    ctx.fillStyle = INK;
    ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = accent;
    ctx.fillRect(0, RIBBON_H, W, 150);
    // faint oversized initial for texture (never the information carrier)
    ctx.fillStyle = "rgba(244,239,226,0.08)";
    ctx.font = `900 460px ${SANS}`;
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText((ev.artist.charAt(0) || "?").toUpperCase(), W / 2, H * 0.52);
  }

  ctx.textAlign = "center";
  ctx.textBaseline = "middle";

  // ---- ribbon ----
  if (ribbon) {
    const s = ribbonStyle(ribbon);
    ctx.fillStyle = s.bg;
    ctx.fillRect(0, 0, W, RIBBON_H);
    ctx.fillStyle = s.fg;
    fit(ctx, s.label, W - 60, 40);
    ctx.fillText(s.label, W / 2, RIBBON_H / 2);
  }

  const name = ev.artist.toUpperCase();
  if (photo) {
    // name over the photo's scrimmed foot, cream with a hard shadow
    ctx.shadowColor = "rgba(0,0,0,0.9)";
    ctx.shadowBlur = 18;
    ctx.fillStyle = CREAM;
    fit(ctx, name, W - 48, 76);
    ctx.fillText(name, W / 2, RIBBON_H + 400, W - 40);
    ctx.shadowBlur = 0;
    // start time BIG on the cream stock
    ctx.fillStyle = INK;
    fit(ctx, formatShortIST(ev.startTime), W - 48, 64);
    ctx.fillText(formatShortIST(ev.startTime), W / 2, RIBBON_H + 560);
    // stage as a small dark pill badge
    ctx.font = `700 34px ${SANS}`;
    const pillW = ctx.measureText(ev.stage.toUpperCase()).width + 44;
    ctx.fillStyle = INK;
    ctx.fillRect(W / 2 - pillW / 2, RIBBON_H + 606, pillW, 48);
    ctx.fillStyle = CREAM;
    ctx.fillText(ev.stage.toUpperCase(), W / 2, RIBBON_H + 631);
    // a few drips off the photo edge
    ctx.fillStyle = "rgba(20,18,16,0.5)";
    for (let i = 0; i < 5; i++) {
      const x = 30 + r() * (W - 60);
      ctx.fillRect(x, RIBBON_H + 500, 3 + r() * 3, 8 + r() * 30);
    }
  } else {
    ctx.fillStyle = CREAM;
    fit(ctx, name, W - 48, 88);
    ctx.fillText(name, W / 2, RIBBON_H + 300, W - 40);
    ctx.fillStyle = GOLD;
    fit(ctx, formatShortIST(ev.startTime), W - 48, 64);
    ctx.fillText(formatShortIST(ev.startTime), W / 2, RIBBON_H + 420);
    ctx.fillStyle = "rgba(244,239,226,0.85)";
    fit(ctx, ev.stage.toUpperCase(), W - 48, 34, 700);
    ctx.fillText(ev.stage.toUpperCase(), W / 2, RIBBON_H + 490);
  }

  // scratched-out stroke for past/cancelled acts
  if (status === "done" || status === "cancelled") {
    ctx.strokeStyle = status === "cancelled" ? RED : "rgba(244,239,226,0.85)";
    ctx.lineWidth = 16;
    ctx.lineCap = "round";
    const y0 = RIBBON_H + 300;
    ctx.beginPath();
    ctx.moveTo(20, y0 - 60);
    ctx.lineTo(W - 20, y0 + 60);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(W - 24, y0 - 60);
    ctx.lineTo(30, y0 + 60);
    ctx.stroke();
  }

  // grain
  const img = ctx.getImageData(0, 0, W, H);
  const d = img.data;
  for (let i = 0; i < d.length; i += 16) {
    const n = (r() - 0.5) * 14;
    d[i] += n;
    d[i + 1] += n;
    d[i + 2] += n;
  }
  ctx.putImageData(img, 0, 0);
}

/** Torn-edge alpha: rough top/bottom so the quad reads as wheatpaste. */
function tornAlpha(W: number, H: number, r: () => number): HTMLCanvasElement {
  const { c, ctx } = mk(W, H);
  ctx.fillStyle = "#fff";
  ctx.fillRect(0, 0, W, H);
  ctx.globalCompositeOperation = "destination-out";
  for (const y of [0, H]) {
    for (let x = 0; x < W; x += 6) {
      const bite = y === 0 ? r() * 14 : H - r() * 14;
      ctx.fillRect(x, Math.min(y, bite), 6, Math.abs(bite - y) || 2);
    }
  }
  return c;
}

export function posterKey(
  ev: TimelineEvent,
  status: DerivedStatus,
  ribbon: PosterRibbon = null,
  hasPhoto = false
): string {
  return `${ev.id}:${status}:${ribbon ?? "-"}:${hasPhoto ? "img" : "-"}:${ev.updatedAt}`;
}

const haloCache = new Map<string, THREE.CanvasTexture>();

/**
 * Thin glowing outline + soft outer glow for the live/focused frame.
 * Transparent centre, so it reads as a frame rather than a misregistered
 * slab behind the poster. One cached texture per colour.
 */
export function makeHaloTexture(color: string): THREE.CanvasTexture {
  const hit = haloCache.get(color);
  if (hit) return hit;
  const W = 256;
  const H = 384;
  const { c, ctx } = mk(W, H);
  ctx.clearRect(0, 0, W, H);
  ctx.strokeStyle = color;
  ctx.lineWidth = 9;
  ctx.shadowColor = color;
  ctx.shadowBlur = 26;
  const frame = () => {
    ctx.beginPath();
    // roundRect needs Safari 16+; rect fallback keeps older phones glowing
    if (typeof ctx.roundRect === "function") ctx.roundRect(14, 14, W - 28, H - 28, 18);
    else ctx.rect(14, 14, W - 28, H - 28);
  };
  // two passes: a soft wide glow underneath, a crisp line on top
  frame();
  ctx.stroke();
  ctx.shadowBlur = 0;
  ctx.lineWidth = 4;
  frame();
  ctx.stroke();
  const t = finish(c);
  t.anisotropy = 4;
  haloCache.set(color, t);
  return t;
}

export function makePosterTexture(
  ev: TimelineEvent,
  status: DerivedStatus,
  ribbon: PosterRibbon = null,
  photo?: HTMLImageElement
): THREE.CanvasTexture {
  const key = posterKey(ev, status, ribbon, !!photo);
  const hit = cache.get(key);
  if (hit) return hit;
  const W = 512;
  const H = 768;
  const seed = [...ev.id].reduce((a, c) => a + c.charCodeAt(0), 7);
  const r = rng(seed);
  const { c, ctx } = mk(W, H);
  drawPoster(ctx, W, H, ev, status, ribbon, photo, seed);
  // punch the torn edge into the alpha channel
  const alpha = tornAlpha(W, H, r);
  ctx.globalCompositeOperation = "destination-in";
  ctx.drawImage(alpha, 0, 0);
  ctx.globalCompositeOperation = "source-over";
  const t = finish(c);
  t.anisotropy = 4;
  cache.set(key, t);
  // bounded: posters recycle through a small window, but never grow past it
  if (cache.size > 24) {
    const first = cache.keys().next().value;
    if (first) {
      cache.get(first)?.dispose();
      cache.delete(first);
    }
  }
  return t;
}
