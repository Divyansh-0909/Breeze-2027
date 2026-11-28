/**
 * Events wall art (Phase 3, docs/runtime/PHASE3-ZONES-PLAN.md): preview-only fixture events for testing the wall's
 * 0 / 1 / 2-6 / 7+ states (`?events=N`), and the poster coherence pass that makes uploaded posters sit on the damp
 * wall (30% desaturation, concrete grime, fold shading, torn-paper edge). Drafted by Antigravity (Gemini 4 Hydrogen),
 * reviewed and adjusted before use.
 */
import type { CypherEvent } from "../../lib/events/cypher-catalog";

interface FixtureSeed {
  name: string;
  description: string;
  date: string;
  endDate: string;
  venue: "Cypher Plaza" | "Gate Lane" | "Events Wall";
  type: "music" | "dance" | "art";
}

const FIXTURE_CATALOG: readonly FixtureSeed[] = [
  {
    name: "GULLY RAP BATTLE",
    description: "Knockout 1v1 lyricist rounds under the main sodium lights.",
    date: "2027-03-28T18:30:00+05:30",
    endDate: "2027-03-28T20:00:00+05:30",
    venue: "Cypher Plaza",
    type: "music",
  },
  {
    name: "BEATBOX SHOWDOWN",
    description: "Solo vocal percussionists trading eight-bar rounds on stage.",
    date: "2027-03-28T19:30:00+05:30",
    endDate: "2027-03-28T21:00:00+05:30",
    venue: "Gate Lane",
    type: "music",
  },
  {
    name: "GRAFFITI WALL JAM",
    description: "Live aerosol murals painted across primed concrete panels.",
    date: "2027-03-28T20:00:00+05:30",
    endDate: "2027-03-28T22:30:00+05:30",
    venue: "Events Wall",
    type: "art",
  },
  {
    name: "BREAKING CREW BATTLE",
    description: "Four-on-four floor battles scored on footwork, freezes, and musicality.",
    date: "2027-03-28T21:15:00+05:30",
    endDate: "2027-03-28T23:00:00+05:30",
    venue: "Cypher Plaza",
    type: "dance",
  },
  {
    name: "CYPHER OPEN MIC",
    description: "Open street circle welcoming bilingual verses over live drums.",
    date: "2027-03-29T18:00:00+05:30",
    endDate: "2027-03-29T19:45:00+05:30",
    venue: "Gate Lane",
    type: "music",
  },
  {
    name: "STENCIL & MURAL LAB",
    description: "Collaborative paste-up posters and hand-cut stencils after dusk.",
    date: "2027-03-29T19:00:00+05:30",
    endDate: "2027-03-29T21:00:00+05:30",
    venue: "Events Wall",
    type: "art",
  },
  {
    name: "PRODUCER BEAT BATTLE",
    description: "Head-to-head sampler sets built from regional vinyl chops.",
    date: "2027-03-29T20:15:00+05:30",
    endDate: "2027-03-29T21:45:00+05:30",
    venue: "Cypher Plaza",
    type: "music",
  },
  {
    name: "POPPING & LOCKING CLASH",
    description: "Street funk rounds highlighting isolation, grooves, and crowd callouts.",
    date: "2027-03-29T22:00:00+05:30",
    endDate: "2027-03-29T23:30:00+05:30",
    venue: "Gate Lane",
    type: "dance",
  },
  {
    name: "CONCRETE DJ SET",
    description: "Late-night turntablism spinning boom-bap, grime, and desi bass.",
    date: "2027-03-30T18:30:00+05:30",
    endDate: "2027-03-30T20:15:00+05:30",
    venue: "Events Wall",
    type: "music",
  },
  {
    name: "WHEATPASTE POSTER RUN",
    description: "Rapid-fire printmaking and street-poster layering along the alley.",
    date: "2027-03-30T19:30:00+05:30",
    endDate: "2027-03-30T21:00:00+05:30",
    venue: "Events Wall",
    type: "art",
  },
  {
    name: "CYPHER FLOOR SHOWCASE",
    description: "Invited street dance collectives debuting original night routines.",
    date: "2027-03-30T20:30:00+05:30",
    endDate: "2027-03-30T22:00:00+05:30",
    venue: "Gate Lane",
    type: "dance",
  },
  {
    name: "FREESTYLE FINALS",
    description: "Championship cypher crowning the closing voice of Gully Verse.",
    date: "2027-03-30T22:15:00+05:30",
    endDate: "2027-03-30T23:55:00+05:30",
    venue: "Cypher Plaza",
    type: "music",
  },
];

export function fixtureEvents(count: number): CypherEvent[] {
  const safeCount = Number.isFinite(count) ? Math.floor(count) : 0;
  const clamped = Math.max(0, Math.min(12, safeCount));

  return FIXTURE_CATALOG.slice(0, clamped).map((item, index) => ({
    id: `fixture-${index + 1}`,
    event_name: item.name,
    event_description: item.description,
    event_org: "Breeze 2027",
    event_date: item.date,
    event_end_date: item.endDate,
    event_venue: item.venue,
    event_type: "Cultural", // the catalog's enum (Cultural | Technical); every fixture is a cultural event
    image_url: null,
    registration_open: index % 2 === 0,
  }));
}

function mulberry32(seed: number): () => number {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) | 0;
    let t = Math.imul(state ^ (state >>> 15), 1 | state);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function desaturatePoster(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  amount: number
): void {
  let imageData: ImageData;
  try {
    imageData = ctx.getImageData(0, 0, width, height);
  } catch {
    return; // a cross-origin (tainted) source: keep its colours rather than fail the poster
  }
  const { data } = imageData;

  for (let i = 0; i < data.length; i += 4) {
    const r = data[i];
    const g = data[i + 1];
    const b = data[i + 2];
    const lum = 0.2126 * r + 0.7152 * g + 0.0722 * b;
    data[i] = Math.round(r + (lum - r) * amount);
    data[i + 1] = Math.round(g + (lum - g) * amount);
    data[i + 2] = Math.round(b + (lum - b) * amount);
  }

  ctx.putImageData(imageData, 0, 0);
}

function applyConcreteGrime(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  rng: () => number
): void {
  const maxDim = Math.max(width, height);
  ctx.save();
  ctx.globalCompositeOperation = "multiply";

  // Low-frequency concrete blotches
  const blotchCount = 12;
  for (let i = 0; i < blotchCount; i++) {
    const cx = rng() * width;
    const cy = rng() * height;
    const radius = maxDim * (0.16 + rng() * 0.26);
    const tone = Math.round(65 + rng() * 45);
    const alpha = 0.12 + rng() * 0.06;

    const grad = ctx.createRadialGradient(cx, cy, radius * 0.1, cx, cy, radius);
    grad.addColorStop(0, `rgba(${tone}, ${tone - 3}, ${tone - 8}, 1)`);
    grad.addColorStop(1, `rgba(${tone}, ${tone - 3}, ${tone - 8}, 0)`);

    ctx.globalAlpha = alpha;
    ctx.fillStyle = grad;
    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, Math.PI * 2);
    ctx.fill();
  }

  // Fine mineral speckle
  const speckleCount = Math.min(2000, Math.max(180, Math.round((width * height) / 140)));
  for (let i = 0; i < speckleCount; i++) {
    const sx = rng() * width;
    const sy = rng() * height;
    const size = rng() < 0.78 ? 1 : 2;
    const tone = Math.round(45 + rng() * 65);
    ctx.globalAlpha = 0.12 + rng() * 0.06;
    ctx.fillStyle = `rgb(${tone}, ${tone - 2}, ${tone - 5})`;
    ctx.fillRect(sx, sy, size, size);
  }

  ctx.restore();
}

function applyFoldShading(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  rng: () => number
): void {
  const side = Math.floor(rng() * 4);
  const bandX = width * 0.11;
  const bandY = height * 0.11;

  let grad: CanvasGradient;
  if (side === 0) {
    grad = ctx.createLinearGradient(0, 0, bandX, 0);
  } else if (side === 1) {
    grad = ctx.createLinearGradient(width, 0, width - bandX, 0);
  } else if (side === 2) {
    grad = ctx.createLinearGradient(0, 0, 0, bandY);
  } else {
    grad = ctx.createLinearGradient(0, height, 0, height - bandY);
  }

  grad.addColorStop(0, "rgba(22, 18, 14, 0.11)");
  grad.addColorStop(0.55, "rgba(22, 18, 14, 0.04)");
  grad.addColorStop(1, "rgba(22, 18, 14, 0)");

  ctx.save();
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, width, height);
  ctx.restore();
}

function applyTornEdges(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  rng: () => number
): void {
  const steps = 18;
  const baseJitter = Math.min(width, height) * 0.025;
  const calmJitter = baseJitter * 0.55;
  const bottomJitter = baseJitter;

  ctx.save();
  ctx.globalCompositeOperation = "destination-in";
  ctx.beginPath();

  // Top edge (left -> right)
  for (let i = 0; i <= steps; i++) {
    const x = (i / steps) * width;
    const y = rng() * calmJitter;
    if (i === 0) {
      ctx.moveTo(x, y);
    } else {
      ctx.lineTo(x, y);
    }
  }

  // Right edge (top -> bottom)
  for (let i = 1; i <= steps; i++) {
    const x = width - rng() * calmJitter;
    const y = (i / steps) * height;
    ctx.lineTo(x, y);
  }

  // Bottom edge (right -> left, raggeder than the others)
  for (let i = 1; i <= steps; i++) {
    const x = width - (i / steps) * width;
    const y = height - (0.15 + rng() * 0.85) * bottomJitter;
    ctx.lineTo(x, y);
  }

  // Left edge (bottom -> top)
  for (let i = 1; i < steps; i++) {
    const x = rng() * calmJitter;
    const y = height - (i / steps) * height;
    ctx.lineTo(x, y);
  }

  ctx.closePath();
  ctx.fillStyle = "#000000";
  ctx.fill();

  // Remove one small torn corner triangle at a seed-chosen corner
  const corner = Math.floor(rng() * 4);
  const cutW = width * (0.07 + rng() * 0.05);
  const cutH = height * (0.07 + rng() * 0.05);
  const pad = 2;

  ctx.globalCompositeOperation = "destination-out";
  ctx.beginPath();
  if (corner === 0) {
    ctx.moveTo(-pad, -pad);
    ctx.lineTo(cutW, -pad);
    ctx.lineTo(-pad, cutH);
  } else if (corner === 1) {
    ctx.moveTo(width + pad, -pad);
    ctx.lineTo(width + pad, cutH);
    ctx.lineTo(width - cutW, -pad);
  } else if (corner === 2) {
    ctx.moveTo(width + pad, height + pad);
    ctx.lineTo(width - cutW, height + pad);
    ctx.lineTo(width + pad, height - cutH);
  } else {
    ctx.moveTo(-pad, height + pad);
    ctx.lineTo(-pad, height - cutH);
    ctx.lineTo(cutW, height + pad);
  }
  ctx.closePath();
  ctx.fill();
  ctx.restore();
}

export function weatherPoster(
  source: HTMLCanvasElement | HTMLImageElement,
  width: number,
  height: number,
  seed: number
): HTMLCanvasElement {
  const w = Math.max(1, Math.floor(Number.isFinite(width) ? width : 1));
  const h = Math.max(1, Math.floor(Number.isFinite(height) ? height : 1));

  const canvas = document.createElement("canvas");
  canvas.width = w;
  canvas.height = h;

  const ctx = canvas.getContext("2d");
  if (!ctx) {
    return canvas;
  }

  // Off-white paper base
  ctx.fillStyle = "#ddd6c6";
  ctx.fillRect(0, 0, w, h);

  const isImage =
    typeof HTMLImageElement !== "undefined" && source instanceof HTMLImageElement;
  const srcW = isImage ? source.naturalWidth : source.width;
  const srcH = isImage ? source.naturalHeight : source.height;

  if (srcW <= 0 || srcH <= 0 || (isImage && !source.complete)) {
    return canvas;
  }

  // "contain"-fit source onto paper
  const scale = Math.min(w / srcW, h / srcH);
  const drawW = srcW * scale;
  const drawH = srcH * scale;
  const dx = (w - drawW) / 2;
  const dy = (h - drawH) / 2;
  ctx.drawImage(source, dx, dy, drawW, drawH);

  const rng = mulberry32(Number.isFinite(seed) ? Math.trunc(seed) : 0);

  desaturatePoster(ctx, w, h, 0.3);
  applyConcreteGrime(ctx, w, h, rng);
  applyFoldShading(ctx, w, h, rng);
  applyTornEdges(ctx, w, h, rng);

  return canvas;
}

/** Placeholder poster photos (public/posters/, Unsplash License; see CREDITS.md) for events without artwork. */
export const placeholderPosters = Array.from({ length: 12 }, (_, i) => `/posters/poster-${String(i + 1).padStart(2, "0")}.webp`);

/** Loads an image (same-origin or CORS) or resolves null. */
export function loadPosterImage(url: string, signal?: { aborted: boolean }): Promise<HTMLImageElement | null> {
  return new Promise(resolve => {
    const image = new Image();
    image.crossOrigin = "anonymous";
    image.onload = () => resolve(signal?.aborted || !image.naturalWidth ? null : image);
    image.onerror = () => resolve(null);
    image.src = url;
  });
}

/**
 * A battle-poster card (384 × 512): the photo cover-fitted and pushed toward a high-contrast photocopy (luma curve,
 * 22% warm tint), a black title band with the event name in heavy chalk type, and a date / venue strip. Without a
 * photo the card is type only. Pass the result through weatherPoster for paper, grime and torn edges.
 */
export function posterCard(photo: HTMLImageElement | null, title: string, line: string, accent = "#c4883e") {
  const W = 384, H = 512;
  const canvas = document.createElement("canvas"); canvas.width = W; canvas.height = H;
  const g = canvas.getContext("2d");
  if (!g) return canvas;
  g.fillStyle = "#dcd4c2"; g.fillRect(0, 0, W, H); // aged newsprint
  if (photo) {
    const scale = Math.max(W / photo.naturalWidth, (H - 120) / photo.naturalHeight);
    const w = photo.naturalWidth * scale, h = photo.naturalHeight * scale;
    g.drawImage(photo, (W - w) / 2, 96 + (H - 120 - h) / 2, w, h);
    try { // photocopy: steep luma curve, slight warm tint (tainted images keep their colour)
      const data = g.getImageData(0, 96, W, H - 120);
      const d = data.data;
      for (let i = 0; i < d.length; i += 4) {
        const l = (0.2126 * d[i] + 0.7152 * d[i + 1] + 0.0722 * d[i + 2]) / 255;
        const c = Math.min(1, Math.max(0, (l - 0.03) * 2.4)) ** 0.7 * 255; // lifts dark concert photos into a readable photocopy
        d[i] = c * 0.78 + d[i] * 0.22; d[i + 1] = c * 0.74 + d[i + 1] * 0.2; d[i + 2] = c * 0.66 + d[i + 2] * 0.16;
      }
      g.putImageData(data, 0, 96);
    } catch { /* cross-origin without CORS: keep the photo as is */ }
  }
  g.fillStyle = "#dcd4c2"; g.fillRect(0, 0, W, 96);
  g.fillStyle = accent; g.fillRect(0, 90, W, 6);
  g.fillStyle = "#151515"; g.textAlign = "center"; g.textBaseline = "middle";
  let px = 54; g.font = `900 ${px}px Impact, "Arial Black", sans-serif`;
  const text = title.toUpperCase();
  while (g.measureText(text).width > W - 28 && px > 22) { px -= 2; g.font = `900 ${px}px Impact, "Arial Black", sans-serif`; }
  g.fillText(text, W / 2, 48);
  g.fillStyle = "#dcd4c2"; g.fillRect(0, H - 24, W, 24);
  g.fillStyle = "#151515"; g.font = '700 16px "Arial Narrow", Arial, sans-serif';
  g.fillText(line.toUpperCase(), W / 2, H - 12, W - 20);
  return canvas;
}
