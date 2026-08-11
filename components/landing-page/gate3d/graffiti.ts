// Procedural graffiti for the tunnel past the arch. Same rule as textures.ts:
// every surface is drawn to a canvas at runtime, so the scene stays
// self-contained — no image downloads, nothing to 404 on deploy.
//
// EVERYTHING here is drawn from the boards already printed on the arch
// (`public/gate/*.webp`). Those posters are screenprints, and their language
// is specific:
//
//   - aged cream stock, weathered, under a halftone dot screen
//   - HUGE black display lettering as the dominant element, always
//   - red and blue copies of that lettering knocked slightly off-register
//     behind it, the way a misaligned screenprint pulls
//   - red starbursts and blue washes UNDER the type, never over it
//   - ink drips hanging off every letterform and every block
//   - colour blocks carrying a word, ruled above and below
//   - small hand tags crowded round the edges
//
// So that is all this file draws. Earlier versions filled the walls with
// blobby throw-ups, angular wildstyle and stencilled boomboxes — none of
// which appear anywhere on those boards, which is exactly why the tunnel
// stopped looking like the arch it comes out of.
//
// The shell is ONE non-tiling texture: u runs the tunnel's whole length,
// v runs around the cross-section (left floor → wall → roof → wall → right
// floor). Non-tiling matters — a distinctive word repeating down a corridor
// reads as wallpaper.
import * as THREE from "three";
import { TUNNEL, VAULT } from "./palette";
import { finish, mk, rng } from "./textures";

/** The menu's face, so the tunnel and the arrival are lettered by one hand. */
export const TAG_FONT =
  "'Aerosoldier', 'Impact', 'Haettenschweiler', 'Arial Black', system-ui, sans-serif";
/**
 * The same stack with Aerosoldier taken off the front — what the tunnel used to
 * fall back to when the OTF was slow, now asked for deliberately.
 *
 * It carries the act names, and only the act names. Aerosoldier is a display
 * face: it does the fest's own words (GULLYVERSE, BREEZE, the year blocks)
 * beautifully because those are short and known, and it does a real band's name
 * less well — a name is the one string on this wall that has to survive being
 * read at speed by someone who has never seen it written down. Impact's tighter
 * fitting and plainer letterforms are what buy that, and the contrast between
 * the two faces is now doing work: the fest's voice in one, the lineup in the
 * other.
 */
const FALLBACK_FONT =
  "'Impact', 'Haettenschweiler', 'Arial Black', system-ui, sans-serif";

/**
 * Which face a given string can safely be set in.
 *
 * Aerosoldier is a personal-use release, and its DIGITS are not digits: every
 * numeral draws the foundry's "PERSONAL USE ONLY / Aerosoldier" notice instead
 * of a glyph. So `2025` under a piece came out as that notice stamped four
 * times, each one overlapping the last — which is the overlapping, broken text
 * on these walls, and it was never a layout problem at all.
 *
 * Tested rather than hard-coded per call site, because the failure is silent and
 * the next person to add "BREEZE 2027" to the wall words would hit it again with
 * no way to know why. Letters keep the display face; anything with a number in
 * it drops to the fallback, which sets digits properly.
 */
const faceFor = (text: string): string =>
  /[0-9]/.test(text) ? FALLBACK_FONT : TAG_FONT;
const DEVA =
  "'Nirmala UI', 'Noto Sans Devanagari', 'Mangal', 'Devanagari Sangam MN', 'Kohinoor Devanagari', sans-serif";

/**
 * Canvas draws with whatever font is resolved AT THAT MOMENT — an OTF still
 * in flight silently falls back to Impact and bakes the wrong letterforms
 * into the texture forever. Callers await this first.
 */
let fontReady: Promise<void> | null = null;
export function ensureTagFont(): Promise<void> {
  if (fontReady) return fontReady;
  fontReady = (async () => {
    if (typeof document === "undefined" || !document.fonts) return;
    try {
      await document.fonts.load("900 100px Aerosoldier");
      await document.fonts.ready;
    } catch {
      /* fall back to Impact, which is what the stack is for */
    }
  })();
  return fontReady;
}

// The three spray colours the boards are built from — everything that isn't
// ink black or paper. Deliberately only three: the posters get their punch
// from a tight palette on warm stock, and a fourth hue reads as noise.
const SPRAY = [VAULT.red, VAULT.blue, VAULT.yellow];

// ---- the shell's scale ----
//
// The shell canvas is solved, not chosen: v spans the section's arc length and
// u spans the tunnel's whole length, so the two axes only carry square texels
// if the canvas has the same ratio the tunnel does. Deriving it means retuning
// the tunnel's proportions can't quietly leave the paint stretched along one
// axis, which is the failure mode a hand-picked "≈ 80 px/m" pair invites.
const SHELL_H = 1152;
const SHELL_W = Math.round(SHELL_H * (TUNNEL.length / TUNNEL.profileS));
/** Canvas pixels per world metre on the shell — equal on both axes by construction. */
const PPM = SHELL_H / TUNNEL.profileS;
/**
 * Metres → shell canvas pixels.
 *
 * Sizes here are authored in metres rather than as fractions of the band, so
 * "a 4 m wash" stays 4 m of wall whichever band it lands on. Fractions of a
 * 5 m wall band and fractions of a 4.6 m roof band are different lengths, and
 * reading the numbers gives you no way to tell.
 */
const m = (metres: number): number => metres * PPM;

/** What the walls say, apart from the lineup (which lives on its own quads). */
const WALL_WORDS = ["GULLYVERSE", "BREEZE", "SNU", "APNA SHOR", "GALI", "BRZ", "SHEHAR"];
const WALL_DEVA = ["गली", "अपना शोर", "शहर", "हवा"];
const TAG_WORDS = ["BRZ", "SNU", "GV", "27", "GULLY", "SHOR", "AKS", "TMK"];

const TAU = Math.PI * 2;
const pick = <T,>(arr: readonly T[], r: () => number): T =>
  arr[Math.floor(r() * arr.length) % arr.length];

/**
 * Whether this device can actually draw Devanagari. Windows ships Nirmala UI,
 * macOS Devanagari Sangam, Android Noto — but a stripped Linux box has none,
 * and the browser silently substitutes the missing-glyph box. `೿` is
 * unassigned so it ALWAYS draws that box; if a real letter draws identical
 * pixels, the script isn't installed.
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

// ---- aerosol and print primitives ----

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
    const a = rand() * TAU;
    const d = r * (0.55 + rand() * 0.85);
    ctx.globalAlpha = 0.04 + rand() * 0.18;
    ctx.beginPath();
    ctx.arc(x + Math.cos(a) * d, y + Math.sin(a) * d, 0.5 + rand() * 1.8, 0, TAU);
    ctx.fill();
  }
  ctx.globalAlpha = 1;
}

/** Paint runs — too much ink, held too long. On these boards, everything runs. */
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
    const w = 1.6 + rand() * 3.6;
    const len = maxLen * (0.2 + rand() * 1.0);
    ctx.fillRect(x, y, w, len);
    // the bead of paint that collects at the bottom of a run
    ctx.beginPath();
    ctx.arc(x + w / 2, y + len, w * 0.78, 0, TAU);
    ctx.fill();
  }
}

/** A loose one-stroke hand tag — the marks that go up in seconds. */
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

/** The stubby arrow that grows out of the corner of a tag. */
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
 * The red starburst that sits under CHAAR DIWAARI on the right-hand board
 * and under GULLYVERSE on the beam. Rough-edged and hand-cut, never a clean
 * polygon, and always wet enough to run.
 */
function splat(
  ctx: CanvasRenderingContext2D,
  cx: number,
  cy: number,
  r: number,
  color: string,
  rand: () => number
): void {
  const spikes = 7 + Math.floor(rand() * 4);
  ctx.fillStyle = color;
  ctx.globalAlpha = 0.72 + rand() * 0.26;
  ctx.beginPath();
  for (let i = 0; i <= spikes * 2; i++) {
    const a = (i / (spikes * 2)) * TAU;
    const rad = i % 2 ? r * (0.34 + rand() * 0.16) : r * (0.78 + rand() * 0.35);
    const px = cx + Math.cos(a) * rad;
    const py = cy + Math.sin(a) * rad * 0.92;
    i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
  }
  ctx.closePath();
  ctx.fill();
  ctx.globalAlpha = 1;
  runs(ctx, cx - r * 0.6, cx + r * 0.6, cy + r * 0.5, r * 0.8, color, 5, rand);
}

/**
 * A single thrown patch of white — the ones that go up by the canful rather
 * than by the roller. Used to break up the roller work in `whitewash`.
 *
 * Thrown rather than rolled: a torn edge, droplets carrying past it, and the
 * runs down the wall that any wet paint on vertical brick gives you.
 */
function whiteSplash(
  ctx: CanvasRenderingContext2D,
  cx: number,
  cy: number,
  r: number,
  rand: () => number,
  wide = 1.15
): void {
  const white = VAULT.whitewash;
  ctx.save();
  ctx.fillStyle = white;

  // the body — squatter than it is wide, because a name is
  const spikes = 9 + Math.floor(rand() * 5);
  ctx.globalAlpha = 0.88 + rand() * 0.12;
  ctx.beginPath();
  for (let i = 0; i <= spikes * 2; i++) {
    const a = (i / (spikes * 2)) * TAU;
    const rad = i % 2 ? r * (0.54 + rand() * 0.2) : r * (0.82 + rand() * 0.3);
    const px = cx + Math.cos(a) * rad * wide;
    const py = cy + Math.sin(a) * rad * 0.72;
    i === 0 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
  }
  ctx.closePath();
  ctx.fill();

  // what carried past the edge of it
  for (let i = 0; i < 90; i++) {
    const a = rand() * TAU;
    const d = r * (0.76 + rand() * 0.85);
    ctx.globalAlpha = 0.3 + rand() * 0.6;
    ctx.beginPath();
    ctx.arc(cx + Math.cos(a) * d * wide, cy + Math.sin(a) * d * 0.8, 1 + rand() * 5, 0, TAU);
    ctx.fill();
  }
  ctx.globalAlpha = 1;
  ctx.restore();

  // and it runs. Kept short deliberately — these textures are quads with an
  // edge, and a drip that reaches the bottom of one stops being a drip and
  // becomes a visible cut where the paint meets nothing.
  runs(ctx, cx - r * 0.85 * wide, cx + r * 0.85 * wide, cy + r * 0.46, r * 0.55, white, 12, rand);
}

/**
 * One pass of a roller, at whatever angle it happened to be held.
 *
 * Angle is the whole point: a coat laid in nothing but vertical passes reads as
 * a machine-printed gradient, because the one thing every real roller job has
 * is somebody changing their grip — going across where the wall is low, up on
 * the diagonal where they were reaching, back the other way to spread what was
 * left on the sleeve. So each pass here takes its own direction.
 *
 * The nap streaks are cut rather than painted. This runs on the whitewash's own
 * layer, so `destination-out` takes the coat back off along the line of the
 * stroke and the brick underneath comes through — which is what a single coat
 * of emulsion on masonry actually looks like, the faces covered and the joints
 * still dark. Painting a darker line instead would only put grey on the white.
 */
function rollerPass(
  lx: CanvasRenderingContext2D,
  cx: number,
  cy: number,
  len: number,
  wid: number,
  angle: number,
  rand: () => number
): void {
  lx.save();
  lx.translate(cx, cy);
  lx.rotate(angle);

  lx.fillStyle = VAULT.whitewash;
  // Nearly opaque. A pass at half alpha does not read as paint at all — it
  // reads as haze, and the wall's "incompleteness" then comes from everything
  // being thin rather than from anywhere being bare, which is the wrong idea.
  lx.globalAlpha = 0.62 + rand() * 0.38;
  lx.beginPath();
  // rounded, because a roller lifts off rather than stopping square
  lx.roundRect(-len / 2, -wid / 2, len, wid, wid * 0.45);
  lx.fill();

  // ...and one in six leaves the nap behind. Rare and faint on purpose: at a
  // third of strokes and twice this strength these cuts ate the middle out of
  // every pass and the coat came out as a row of white fingers, more like
  // something clawed off the wall than rolled onto it.
  if (rand() < 0.17) {
    lx.globalCompositeOperation = "destination-out";
    lx.globalAlpha = 0.12 + rand() * 0.18;
    const sy = (rand() - 0.5) * wid * 0.6;
    lx.fillRect(-len * 0.4, sy, len * (0.4 + rand() * 0.35), wid * (0.05 + rand() * 0.07));
    lx.globalCompositeOperation = "source-over";
  }

  lx.restore();
}

/**
 * The half-finished coat of white over the brick — what the wall IS, before a
 * single word goes on it.
 *
 * Somebody started painting this tunnel out and never got to the end of it,
 * which is the most ordinary thing that happens to a wall like this and the
 * reason it ends up covered: fresh white is what a writer is looking for, and a
 * wall that is half fresh white and half bare brick is the one that gets hit.
 * So the graffiti above this reads as a consequence of the paint rather than as
 * decoration sitting on top of it.
 *
 * Built as its own layer and composited down, because "incomplete" here means
 * holes — flaked patches where the brick comes back through the middle of a
 * painted stretch. Those can only be cut with `destination-out`, and doing that
 * on the shell itself would take the brick out with the white.
 *
 * Three things make it read as unfinished rather than as a texture:
 *   - it stops short of the roof, because nobody brought scaffolding, so there
 *     is bare brick above every stretch and the tunnel keeps a dark line under
 *     its dark ceiling;
 *   - it comes in stretches with raw brick BETWEEN them, not as one coat with
 *     the opacity turned down — patchy alpha reads as dirty paint, whereas an
 *     edge with bare brick beside it reads as somebody stopping;
 *   - the coverage is streaky within a stretch, since a roller on brick only
 *     ever touches the faces and leaves the joints dark until the second coat
 *     that never came.
 *
 * ---- how it comes to ~70% of the wall ----
 * Three independent factors multiply, so each one has to be generous for the
 * product not to collapse — at the first pass's 70% × 90% × 56% the wall was a
 * third painted, which looked like neglect rather than an abandoned job:
 *   - along the wall: stretches average 8.5 m against 1.05 m gaps → 0.89
 *   - within a stretch: overlapping random passes cover ~0.88 of it
 *   - up the wall: the coat reaches ~4.15 m of the 5 m section → 0.83
 * → about 0.65, before the thrown splashes add a little back and the flaking
 * takes a little more off. Near enough 70% that the wall reads as mostly
 * painted; the knobs to move it are the gap and the reach, in that order.
 */
function whitewash(
  ctx: CanvasRenderingContext2D,
  x0: number,
  y0: number,
  w: number,
  h: number,
  rand: () => number
): void {
  // its own layer, in the band's local coordinates: 0 is the roof end, h the floor
  const { c: lc, ctx: lx } = mk(Math.ceil(w), Math.ceil(h));
  const floor = h;

  // ---- roller stretches ----
  // start off the left edge so the first one is already in progress
  let x = -m(1 + rand() * 2.5);
  while (x < w) {
    const stretchW = m(5 + rand() * 7);
    const gap = m(0.3 + rand() * 1.5); // the brick nobody got to
    // As high as a roller on a pole goes, and it wanders as the wall goes on.
    // Kept clear of the clamp below on purpose: a range that runs past it would
    // pin half the stretches to the same height and rule a dead-straight line
    // along the top of the wall, which is the one edge that has to look human.
    const reach = m(3.6 + rand() * 1.1);
    let top = floor - reach;

    top = Math.min(Math.max(top, m(0.2)), floor - m(0.6));

    // How many passes it takes to cover the stretch. Overlapping strokes thrown
    // down at random land as a Poisson process, so coverage is 1 − e^(−k) for
    // k times the region's own area laid down — k = 3 gets ~95% of it, and the
    // strokes that spill out over the edges bring the real figure to just under
    // 90%. Solved rather than picked, because the stroke sizes below are the
    // kind of number that gets nudged, and a fixed count would quietly change
    // how much of the wall ends up painted every time one of them moved.
    const area = stretchW * (floor - top);
    const passes = Math.ceil((3 * area) / (m(1.15) * m(0.41)));

    // The direction THIS stretch was worked in. Fully random per stroke was the
    // first attempt and it came out as scratches — nobody rolls a wall by
    // spinning the handle between passes, and an even scatter of angles has no
    // grain at all, so the eye reads it as damage rather than as paint. One
    // lean per stretch with about 30° of play in it keeps every direction on
    // the wall while making each patch look worked.
    const lean = rand() * TAU;

    for (let i = 0; i < passes; i++) {
      if (rand() < 0.06) continue; // the odd one they simply missed
      rollerPass(
        lx,
        x + rand() * stretchW,
        top + rand() * (floor - top),
        // a roller sleeve is about 230 mm and a pass about a metre — these run
        // wider and shorter than the first attempt's 0.16 × 1.5, which was the
        // proportion of a brush stroke and looked like one
        m(0.6 + rand() * 1.1),
        m(0.26 + rand() * 0.3),
        lean + (rand() - 0.5) * 1.1,
        rand
      );
    }

    // paint pools and runs at the top edge where the roller was overloaded
    lx.globalAlpha = 1;
    runs(lx, x, x + stretchW, floor - reach, m(0.5), VAULT.whitewash, 9, rand);

    x += stretchW + gap;
  }

  // a few cansful thrown at it on top of the roller work
  lx.globalAlpha = 1;
  for (let i = 0; i < Math.max(2, Math.round(w / m(11))); i++) {
    whiteSplash(lx, rand() * w, h * (0.42 + rand() * 0.4), m(0.5 + rand() * 0.9), rand, 1.3);
  }

  // ---- and where it has come back off ----
  // cut rather than painted over: this is the brick returning through the
  // coat, so it has to remove white and leave whatever is underneath
  lx.globalCompositeOperation = "destination-out";
  for (let i = 0; i < Math.round(w / m(1.5)); i++) {
    const cx = rand() * w;
    const cy = h * (0.3 + rand() * 0.7);
    const r = m(0.12 + rand() * 0.75);
    const g = lx.createRadialGradient(cx, cy, r * (0.1 + rand() * 0.5), cx, cy, r);
    // hard-cored, soft-edged: a flake has a definite middle and a frayed rim
    g.addColorStop(0, "rgba(0,0,0,0.95)");
    g.addColorStop(1, "rgba(0,0,0,0)");
    lx.fillStyle = g;
    lx.fillRect(cx - r, cy - r, r * 2, r * 2);
  }
  // the damp line along the floor takes the bottom of the coat with it
  const foot = lx.createLinearGradient(0, floor, 0, floor - m(0.55));
  foot.addColorStop(0, "rgba(0,0,0,0.8)");
  foot.addColorStop(1, "rgba(0,0,0,0)");
  lx.fillStyle = foot;
  lx.fillRect(0, floor - m(0.55), w, m(0.55));
  lx.globalCompositeOperation = "source-over";

  ctx.drawImage(lc, x0, y0);
}

// ---- keeping the legible things off each other ----
//
// Everything on this wall used to be placed at a random x and left to land
// where it landed, which is right for the scrawl and wrong for anything with
// words in it: a plate dropped across a 3 m headline doesn't read as layered
// paint, it reads as a mistake. So the big items now claim the ground they
// stand on and the next one has to find space of its own.
//
// Deliberately NOT applied to the scrawls, arrows, washes and overspray. Those
// are the crowding — the marks that go over everything else are most of what
// makes a wall look used, and spacing them out would leave a tidy poster.

type Claim = { x: number; y: number; w: number; h: number };

function overlaps(a: Claim, b: Claim, pad: number): boolean {
  return (
    a.x - pad < b.x + b.w &&
    b.x - pad < a.x + a.w &&
    a.y - pad < b.y + b.h &&
    b.y - pad < a.y + a.h
  );
}

/**
 * Somewhere in the given box to put a `cw × ch` thing that nothing has claimed
 * yet, claimed on the way out. Null when there is nowhere left, and null is a
 * real answer: a wall with one plate fewer on it is finished, a wall with two
 * plates on the same spot is broken.
 */
function claimSpot(
  taken: Claim[],
  cw: number,
  ch: number,
  x0: number,
  w: number,
  yLo: number,
  yHi: number,
  pad: number,
  rand: () => number,
  tries = 60
): Claim | null {
  const spanX = Math.max(1, w - cw);
  const spanY = Math.max(1, yHi - yLo - ch);
  for (let i = 0; i < tries; i++) {
    const c = { x: x0 + rand() * spanX, y: yLo + rand() * spanY, w: cw, h: ch };
    if (!taken.some((t) => overlaps(c, t, pad))) {
      taken.push(c);
      return c;
    }
  }
  return null;
}

/** A wide dry-brush wash, like the blue sweeps across the boards' panels. */
function wash(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  color: string,
  rand: () => number
): void {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate((rand() - 0.5) * 0.5);
  ctx.fillStyle = color;
  for (let i = 0; i < 26; i++) {
    ctx.globalAlpha = 0.05 + rand() * 0.26;
    const bh = h * (0.06 + rand() * 0.2);
    ctx.fillRect(-w / 2 + rand() * w * 0.2, -h / 2 + rand() * h, w * (0.5 + rand() * 0.6), bh);
  }
  ctx.restore();
  ctx.globalAlpha = 1;
}

/**
 * BIG DISPLAY TYPE with the print misregistered behind it — the single most
 * characteristic thing on both boards, and now the thing the walls are
 * mostly made of. Red and blue pulls knocked a few thousandths off true,
 * black on top doing the actual reading, ink running off the baseline.
 */
function posterType(
  ctx: CanvasRenderingContext2D,
  text: string,
  cx: number,
  cy: number,
  size: number,
  rand: () => number,
  deva = false,
  face = TAG_FONT
): void {
  const font = `900 ${size}px ${deva ? DEVA : face}`;
  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate((rand() - 0.5) * 0.07);
  ctx.font = font;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";

  const w = ctx.measureText(text).width;

  // the off-register colour pulls, underneath
  ctx.globalAlpha = 0.9;
  ctx.fillStyle = VAULT.red;
  ctx.fillText(text, -size * 0.035, size * 0.022);
  ctx.fillStyle = VAULT.blue;
  ctx.fillText(text, size * 0.032, -size * 0.02);
  ctx.globalAlpha = 1;

  // the black pull, on top and on register
  ctx.fillStyle = VAULT.ink;
  ctx.fillText(text, 0, 0);
  ctx.restore();

  // and the ink running off it
  runs(ctx, cx - w / 2, cx + w / 2, cy + size * 0.3, size * 0.8, VAULT.ink, 10, rand);
}

/** A colour block carrying one word, ruled above and below — BREEZE / 2027. */
function labelBlock(
  ctx: CanvasRenderingContext2D,
  cx: number,
  cy: number,
  h: number,
  text: string,
  color: string,
  rand: () => number
): void {
  // years live in these blocks, so this is the one that most needs `faceFor`
  ctx.font = `900 ${h * 0.62}px ${faceFor(text)}`;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  const w = ctx.measureText(text).width + h * 0.7;
  const x = cx - w / 2;
  const y = cy - h / 2;

  ctx.fillStyle = color;
  ctx.fillRect(x, y, w, h);
  ctx.fillStyle = VAULT.ink;
  ctx.fillRect(x, y - h * 0.16, w, h * 0.1);
  ctx.fillRect(x, y + h * 1.06, w, h * 0.1);
  ctx.fillText(text, cx, cy + h * 0.03);
  runs(ctx, x, x + w, y + h, h * 0.9, color, 5, rand);
}

/** A rounded-corner plate, like the boards' framed image panels. */
function panel(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  w: number,
  h: number,
  rand: () => number
): void {
  ctx.save();
  ctx.strokeStyle = VAULT.ink;
  ctx.lineWidth = Math.max(2, h * 0.028);
  ctx.beginPath();
  ctx.roundRect(x, y, w, h, h * 0.14);
  ctx.stroke();
  ctx.clip();
  wash(ctx, x + w / 2, y + h / 2, w, h, rand() < 0.6 ? VAULT.blue : VAULT.red, rand);
  for (let i = 0; i < 3; i++) {
    scrawl(
      ctx,
      x + w * 0.1,
      y + h * (0.25 + rand() * 0.5),
      w * 0.8,
      h * 0.12,
      VAULT.ink,
      2 + rand() * 3,
      rand
    );
  }
  ctx.restore();
  runs(ctx, x, x + w, y + h, h * 0.4, VAULT.ink, 5, rand);
}

/**
 * The printed dot screen both boards sit under.
 *
 * Drawn ONCE into a small tile and then repeat-filled, rather than dotted
 * across the shell directly: at this texture's size that was ~72,000 arc
 * fills, which is most of a second of blocked main thread on a scene that
 * mounts behind a loading gate. The tile is ~190 arcs and the fill is one
 * rect.
 */
let dotTile: HTMLCanvasElement | null = null;
function halftone(
  ctx: CanvasRenderingContext2D,
  x0: number,
  y0: number,
  w: number,
  h: number,
  rand: () => number
): void {
  if (!dotTile) {
    const S = 98; // not a multiple of the 7px pitch, so the tiling never lines up
    const { c: tc, ctx: tx } = mk(S, S);
    tx.fillStyle = "rgba(28,24,18,0.11)";
    for (let y = 0; y < S; y += 7) {
      for (let x = 0; x < S; x += 7) {
        const r = rand() * 1.9;
        if (r < 0.55) continue;
        tx.beginPath();
        tx.arc(x, y, r * 0.85, 0, TAU);
        tx.fill();
      }
    }
    dotTile = tc;
  }
  const pattern = ctx.createPattern(dotTile, "repeat");
  if (!pattern) return;
  ctx.save();
  ctx.fillStyle = pattern;
  ctx.fillRect(x0, y0, w, h);
  ctx.restore();
}

/**
 * The brick module, in metres — one brick plus the joint it is laid on.
 *
 * Well over the 215 × 65 mm a real wall is built from: this is a block, closer
 * to what a service tunnel actually gets lined with than to house brick. Partly
 * a look — coarse units give the walls a scale you read at speed, where a fine
 * domestic bond turns into texture — and partly resolution. The shell canvas
 * works out at about 71 px per metre, so a true 65 mm course lands on five
 * pixels and the bed joints mush into a grey haze under the mipmaps; at 140 mm
 * a course holds ten and the courses survive being seen from the flight line.
 * Raising SHELL_H is the other way to buy that, and costs memory on every phone
 * that loads the scene.
 *
 * The 2.9 : 1 face is close to a real stretcher's 3.3, so the bond still reads
 * as masonry rather than as tiling however far these are scaled.
 */
const BRICK_COURSE = 0.14;
const BRICK_LEN = 0.4;

/**
 * Where every brick in a band sits, in band-local pixels.
 *
 * Pulled out of the drawing so the SAME wall can be walked twice — once to
 * paint it and once to build its height — off one seed. The two passes have to
 * agree brick for brick: a bump map half a course out of step with the colour
 * under it is worse than no bump map at all, because the eye gets a highlight
 * where it can see there is no arris.
 *
 * The seed here is the bond's alone, separate from the `rand` the colour pass
 * spends on tones and alpha. That is the whole trick: the two passes consume
 * their own randomness at their own rates and still lay identical bricks.
 */
type Brick = { x: number; y: number; w: number; h: number };

function brickLayout(w: number, h: number, seed: number): Brick[] {
  const r = rng(seed);
  const ch = m(BRICK_COURSE);
  const bl = m(BRICK_LEN);
  // joints stay at least a pixel: below that the mortar is dashed away by
  // rounding and the courses break up into a dotted line
  const joint = Math.max(1, m(0.018));
  const out: Brick[] = [];
  for (let y = 0, row = 0; y < h; y += ch, row++) {
    // running bond, with a little drift on each course so the perpends never
    // stack into a vertical seam down the wall
    const off = (row % 2) * (bl / 2) + (r() - 0.5) * bl * 0.14;
    // laid past both edges and clipped by the caller, rather than fitted to the
    // band — the bands sit hard against each other on this canvas, so a
    // stretcher running long would otherwise print onto the roof
    for (let x = -off - bl; x < w; x += bl) {
      out.push({
        x: x + joint,
        y: y + joint,
        w: bl - joint * 2,
        h: ch - joint * 2,
      });
    }
  }
  return out;
}

/** The bond each band is laid to — shared by the colour and the height pass. */
const BOND_LEFT = 3311;
const BOND_ROOF = 3312;
const BOND_RIGHT = 3313;

/**
 * The wall the paint goes on: brick, laid in running bond and weathered.
 *
 * Warm brick rather than the cold soot the tunnel started as — the arch it runs
 * out of is printed on cream stock and lit gold, and the masonry has to sit in
 * that same light. It is also the reason the mortar is limed nearly to the
 * poster's colour: the joints are what you actually read at speed, and a wall
 * of pale lines on warm brick carries the arch's palette down the whole tunnel.
 *
 * Laid course by course rather than tiled. A tile is far cheaper, but brick is
 * the one surface where a repeat is unmissable — the eye locks onto a stretcher
 * with a distinctive burn and then finds it again every 2 m, and the tunnel
 * turns into wallpaper. ~3.5k rects a band is a few ms, once, behind the gate.
 */
function brick(
  ctx: CanvasRenderingContext2D,
  x0: number,
  y0: number,
  w: number,
  h: number,
  rand: () => number,
  seed: number
): void {
  ctx.save();
  ctx.beginPath();
  ctx.rect(x0, y0, w, h);
  ctx.clip();
  ctx.translate(x0, y0);

  // the bed the bricks are laid into — every joint is this showing through
  ctx.fillStyle = VAULT.mortar;
  ctx.fillRect(0, 0, w, h);

  // How proud of the joint a brick sits, in pixels of drawn edge. This is what
  // turns a grid of coloured rectangles into masonry: a face has a lit top
  // arris and a shaded underside, and without them the wall is a printed
  // pattern that happens to be brick-shaped — which is exactly how it read.
  const lip = Math.max(1, m(0.012));

  for (const b of brickLayout(w, h, seed)) {
    const t = rand();
    ctx.fillStyle =
      t < 0.09 ? VAULT.brickDark : t < 0.24 ? VAULT.brickPale : VAULT.brick;
    // no two bricks out of the same kiln come out the same
    ctx.globalAlpha = 0.78 + rand() * 0.22;
    ctx.fillRect(b.x, b.y, b.w, b.h);

    // the arrises. Light from above, because that is where the tunnel's own
    // fixtures are — so the top of each face catches and the bed joint beneath
    // it goes dark, the one cue that says these things stick out of the wall
    ctx.globalAlpha = 0.34 + rand() * 0.16;
    ctx.fillStyle = "rgba(255,241,222,1)";
    ctx.fillRect(b.x, b.y, b.w, lip);
    ctx.globalAlpha = 0.4 + rand() * 0.2;
    ctx.fillStyle = "rgba(26,16,10,1)";
    ctx.fillRect(b.x, b.y + b.h - lip, b.w, lip);
    ctx.fillRect(b.x + b.w - lip, b.y, lip, b.h);
  }
  ctx.globalAlpha = 1;
  ctx.restore();

  const area = (w * h) / 1e6;

  // efflorescence and damp — the salt bloom that comes through brick, and the
  // dark patches where water sits in it
  for (let i = 0; i < 14 * area; i++) {
    const cx = x0 + rand() * w;
    const cy = y0 + rand() * h;
    const r = 50 + rand() * 240;
    const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
    g.addColorStop(0, rand() < 0.55 ? "rgba(28,20,14,0.34)" : "rgba(226,220,204,0.26)");
    g.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = g;
    ctx.fillRect(cx - r, cy - r, r * 2, r * 2);
  }

  // grit — the dust in the pores and the odd chipped arris catching the light
  for (let i = 0; i < 2600 * area; i++) {
    ctx.fillStyle = rand() < 0.5 ? "rgba(30,20,14,0.15)" : "rgba(255,244,226,0.12)";
    ctx.fillRect(x0 + rand() * w, y0 + rand() * h, 1 + rand() * 2, 1 + rand() * 2);
  }

  // cracks, which in masonry run through the joints rather than across a face
  ctx.strokeStyle = "rgba(38,26,18,0.42)";
  for (let i = 0; i < 16 * area; i++) {
    let x = x0 + rand() * w;
    let y = y0 + rand() * h;
    ctx.lineWidth = 0.6 + rand() * 1.4;
    ctx.beginPath();
    ctx.moveTo(x, y);
    for (let k = 0; k < 6; k++) {
      x += (rand() - 0.5) * 70;
      y += (rand() - 0.5) * 70;
      ctx.lineTo(x, y);
    }
    ctx.stroke();
  }
}

/**
 * One band of wall, painted in the boards' own order of operations: stock,
 * screen, colour underneath, then all the black on top. Colour never carries
 * a word here — black does — which is the rule that stops this reading as a
 * generic rainbow graffiti wall.
 *
 * `reach` scales how far up the paint goes: the walls are 5 m and nobody
 * brought scaffolding, so the top of them stays bare stock.
 */
function wallPaint(
  ctx: CanvasRenderingContext2D,
  x0: number,
  y0: number,
  w: number,
  h: number,
  rand: () => number,
  big: number
): void {
  const band = (lo: number, hi: number) => y0 + h * (lo + rand() * (hi - lo));

  // ---- colour underneath ----
  // Washes are sized in metres and kept SHORT. Scaled off the band they ran
  // 4–12 m long against 1.5–3.5 m tall, and from the flight line the camera
  // never sees the ends of one: it reads as a coloured gradient sliding past
  // rather than as paint. A sweep about as long as a person's reach is wide
  // is what an arm actually leaves behind.
  for (let i = 0; i < 13; i++) {
    wash(ctx, x0 + rand() * w, band(0.3, 0.76), m(1.5 + rand() * 2.2), m(0.9 + rand() * 1.5), rand() < 0.6 ? VAULT.blue : VAULT.red, rand);
  }
  for (let i = 0; i < 14; i++) {
    splat(ctx, x0 + rand() * w, band(0.3, 0.72), m(0.4 + rand() * 0.7), rand() < 0.75 ? VAULT.red : VAULT.yellow, rand);
  }
  for (let i = 0; i < 16; i++) {
    overspray(ctx, x0 + rand() * w, band(0.25, 0.78), m(0.35 + rand() * 0.6), pick(SPRAY, rand), 380, rand);
  }

  // everything with words in it claims its ground, in the order it went up
  const taken: Claim[] = [];
  const pad = m(0.3);

  // ---- the type, which is what this wall mostly IS ----
  //
  // One word per slot, so the headlines can never collide with each other
  // whatever the jitter does. A word too wide for its slot is set smaller
  // rather than dropped or allowed to run into its neighbour — these are the
  // wall's backbone, and a gap where one should be is more obvious than a
  // headline half a size down.
  const deva = devanagariAvailable();
  const slot = w / big;
  for (let i = 0; i < big; i++) {
    const useDeva = deva && rand() < 0.22;
    const text = useDeva ? pick(WALL_DEVA, rand) : pick(WALL_WORDS, rand);
    const face = useDeva ? DEVA : faceFor(text);
    let size = h * (useDeva ? 0.15 : 0.19 + rand() * 0.1);
    ctx.font = `900 ${size}px ${face}`;
    let tw = ctx.measureText(text).width;
    if (tw > slot - pad) {
      size *= (slot - pad) / tw;
      tw = slot - pad;
    }
    // the jitter is whatever room the slot has left once the word is in it,
    // so a long word simply sits still instead of being nudged into next door
    const cx = x0 + slot * (i + 0.5) + (rand() - 0.5) * Math.max(0, slot - pad - tw);
    const cy = band(0.36, 0.62);
    posterType(ctx, text, cx, cy, size, rand, useDeva, face);
    // the claim covers the ink and the drips that come off it
    taken.push({ x: cx - tw / 2, y: cy - size * 0.7, w: tw, h: size * 2.1 });
  }

  // ---- plates and colour blocks ----
  for (let i = 0; i < Math.max(2, big - 2); i++) {
    const pw = h * (0.45 + rand() * 0.5);
    const ph = h * (0.22 + rand() * 0.16);
    const at = claimSpot(taken, pw, ph, x0, w, y0 + h * 0.3, y0 + h * 0.62, pad, rand);
    if (at) panel(ctx, at.x, at.y, pw, ph, rand);
  }
  for (let i = 0; i < big; i++) {
    const bh = h * 0.1;
    const text = pick(TAG_WORDS, rand);
    ctx.font = `900 ${bh * 0.62}px ${faceFor(text)}`;
    const bw = ctx.measureText(text).width + bh * 0.7;
    const at = claimSpot(taken, bw, bh * 1.4, x0, w, y0 + h * 0.62, y0 + h * 0.84, pad, rand);
    if (at) labelBlock(ctx, at.x + bw / 2, at.y + bh * 0.7, bh, text, pick(SPRAY, rand), rand);
  }

  // ---- hand tags crowding the gaps ----
  for (let i = 0; i < 46; i++) {
    scrawl(ctx, x0 + rand() * w, band(0.3, 0.82), h * (0.14 + rand() * 0.34), h * 0.09, rand() < 0.74 ? VAULT.ink : pick(SPRAY, rand), 1.6 + rand() * 3.4, rand);
  }
  for (let i = 0; i < 14; i++) {
    arrow(ctx, x0 + rand() * w, band(0.35, 0.7), h * (0.05 + rand() * 0.07), rand() * TAU, VAULT.ink);
  }

  // grime from the floor, soot from the roof
  const up = ctx.createLinearGradient(0, y0 + h, 0, y0 + h * 0.72);
  up.addColorStop(0, "rgba(22,18,12,0.85)");
  up.addColorStop(1, "rgba(22,18,12,0)");
  ctx.fillStyle = up;
  ctx.fillRect(x0, y0 + h * 0.72, w, h * 0.28);

  const down = ctx.createLinearGradient(0, y0, 0, y0 + h * 0.3);
  down.addColorStop(0, "rgba(18,15,12,0.8)");
  down.addColorStop(1, "rgba(18,15,12,0)");
  ctx.fillStyle = down;
  ctx.fillRect(x0, y0, w, h * 0.3);
}

/**
 * The roof: the same brick as the walls, burnt black, and unpainted.
 *
 * The walls are the whole point of the walk, and a ceiling tagged as densely as
 * they are was competing with them — the frame had colour top to bottom and
 * nowhere to rest. Sooted black instead, so the roof reads as the dark the two
 * lit walls hang in and the lineup is the only thing up there to look at.
 *
 * It is still laid, though, and not a flat `#080706`. Two reasons, and they are
 * the same reason: the lamps ride along the ceiling with the camera, and a
 * single value under a moving light is what makes a surface look like nothing
 * at all — while courses that survive the soot are what says this is the roof of
 * the same tunnel rather than a lid dropped on top of two brick walls. The glaze
 * is heavy enough to kill the colour and thin enough to leave the joints.
 */
function roofPaint(
  ctx: CanvasRenderingContext2D,
  x0: number,
  y0: number,
  w: number,
  h: number,
  rand: () => number
): void {
  brick(ctx, x0, y0, w, h, rand, BOND_ROOF);

  // the soot itself: enough to take the brick to near-black, laid over the
  // whole band in one pass rather than mixed into the masonry, so the two can
  // be tuned against each other
  ctx.fillStyle = "rgba(6,5,4,0.88)";
  ctx.fillRect(x0, y0, w, h);

  // soot bloom — big, soft, barely-there patches, in metres so they stay the
  // same size on the ceiling however the tunnel's section is retuned
  for (let i = 0; i < 90; i++) {
    const cx = x0 + rand() * w;
    const cy = y0 + rand() * h;
    const r = m(0.7 + rand() * 2.4);
    const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, r);
    // both ways off the base: pooled soot and the brick showing back through it
    g.addColorStop(0, rand() < 0.45 ? "rgba(46,42,38,0.28)" : "rgba(0,0,0,0.5)");
    g.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = g;
    // the patch's own box, not the whole band — 90 full-width fills across a
    // canvas this long is a visible hitch on the frame the texture is built in
    ctx.fillRect(cx - r, cy - r, r * 2, r * 2);
  }

  // and dead black where the roof meets the walls, so the springing line reads
  // as a corner going dark rather than as the edge of the wall's texture
  for (const [y, dir] of [
    [y0, 1],
    [y0 + h, -1],
  ] as const) {
    const g = ctx.createLinearGradient(0, y, 0, y + dir * h * 0.32);
    g.addColorStop(0, "rgba(0,0,0,0.92)");
    g.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = g;
    ctx.fillRect(x0, dir > 0 ? y : y - h * 0.32, w, h * 0.32);
  }
}

/**
 * The tunnel's shell texture. u runs the WHOLE length (no tiling — a word
 * repeating down a corridor reads as wallpaper), v runs around the section
 * from the left floor to the right floor.
 */
export function makeShellTexture(): THREE.CanvasTexture {
  const W = SHELL_W;
  const H = SHELL_H;
  const { c, ctx } = mk(W, H);
  const r = rng(7717);

  // v = 0 is the BOTTOM row of the canvas once three flips it, so the left
  // wall lives at the bottom of the image and the right wall at the top
  const leftTop = H * (1 - TUNNEL.wallEndV);
  const ceilTop = H * (1 - TUNNEL.ceilEndV);

  // the order the wall was actually built in: brick, the coat somebody gave up
  // on, then everything anyone has written on it since
  brick(ctx, 0, leftTop, W, H - leftTop, r, BOND_LEFT);
  whitewash(ctx, 0, leftTop, W, H - leftTop, r);
  halftone(ctx, 0, leftTop, W, H - leftTop, r);
  wallPaint(ctx, 0, leftTop, W, H - leftTop, r, 7);

  // no halftone over the roof: it is the printed-stock overlay, and there is no
  // stock up there any more to print on
  roofPaint(ctx, 0, ceilTop, W, leftTop - ceilTop, r);

  // The RIGHT wall's band runs the opposite way round the section AND is seen
  // from the opposite side, so drawn as-is its paint would sit upside down
  // and every word would read backwards. Flipping the band on both axes
  // cancels both at once: local +y still falls toward its floor, and local
  // +x still reads forward along the tunnel.
  ctx.save();
  ctx.translate(W, ceilTop);
  ctx.scale(-1, -1);
  const rr = rng(4402); // its own seed, so the two sides never mirror
  brick(ctx, 0, 0, W, ceilTop, rr, BOND_RIGHT);
  whitewash(ctx, 0, 0, W, ceilTop, rr);
  halftone(ctx, 0, 0, W, ceilTop, rr);
  wallPaint(ctx, 0, 0, W, ceilTop, rr, 7);
  ctx.restore();

  const t = finish(c);
  t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
  return t;
}

/**
 * The shell's HEIGHT — the thing that makes the brick a wall rather than a
 * picture of one.
 *
 * Baked arrises in the colour map get you most of the way, but they are painted
 * shadows: they point the same direction no matter where the light is, so the
 * moment one of the travelling lamps slides past, the wall stays lit exactly as
 * it was drawn and the whole surface reads as a flat sheet with brick printed
 * on it. A bump map is what puts the courses into the lighting itself — the
 * lamp rakes across the bed joints as it goes by, every course lights on its
 * top edge and shades underneath, and the relief moves with the camera because
 * it is being computed rather than remembered.
 *
 * Same bond as the colour, off the same three seeds, so every face here is the
 * face that is painted over there.
 *
 * Half resolution on purpose. Height carries no detail finer than a joint and
 * three interpolates it smoothly, so the second full-size canvas this would
 * otherwise cost — about 12 MB on every phone that opens the site — buys
 * nothing a quarter of it doesn't.
 */
const BUMP_DIV = 2;

function bumpBand(
  ctx: CanvasRenderingContext2D,
  x0: number,
  y0: number,
  w: number,
  h: number,
  seed: number
): void {
  ctx.save();
  ctx.beginPath();
  ctx.rect(x0, y0, w, h);
  ctx.clip();
  ctx.translate(x0, y0);

  // the joint, sitting back from the faces
  ctx.fillStyle = "#4c4c4c";
  ctx.fillRect(0, 0, w, h);

  const r = rng(seed + 977);
  const lip = Math.max(1, m(0.014));
  for (const b of brickLayout(w, h, seed)) {
    // faces vary — a wall of identically proud bricks is a tiled floor
    const v = 198 + Math.floor(r() * 46);
    ctx.fillStyle = `rgb(${v},${v},${v})`;
    ctx.fillRect(b.x, b.y, b.w, b.h);
    // and roll off into the joint rather than meeting it as a cliff, which
    // under a moving light reads as a chamfer instead of a cut edge
    ctx.fillStyle = "rgba(120,120,120,0.6)";
    ctx.fillRect(b.x, b.y + b.h - lip, b.w, lip);
    ctx.fillRect(b.x + b.w - lip, b.y, lip, b.h);
  }
  ctx.restore();
}

export function makeShellBump(): THREE.CanvasTexture {
  const { c, ctx } = mk(
    Math.round(SHELL_W / BUMP_DIV),
    Math.round(SHELL_H / BUMP_DIV)
  );
  // drawn in the colour map's own coordinates and scaled down on the way in,
  // so the two are the same wall and neither has to know the other's size
  ctx.scale(1 / BUMP_DIV, 1 / BUMP_DIV);

  const leftTop = SHELL_H * (1 - TUNNEL.wallEndV);
  const ceilTop = SHELL_H * (1 - TUNNEL.ceilEndV);

  bumpBand(ctx, 0, leftTop, SHELL_W, SHELL_H - leftTop, BOND_LEFT);
  bumpBand(ctx, 0, ceilTop, SHELL_W, leftTop - ceilTop, BOND_ROOF);

  // the right wall takes the same flip its paint does, or its bond would run
  // the other way round the section from the colour sitting on top of it
  ctx.save();
  ctx.translate(SHELL_W, ceilTop);
  ctx.scale(-1, -1);
  bumpBand(ctx, 0, 0, SHELL_W, ceilTop, BOND_RIGHT);
  ctx.restore();

  const t = finish(c);
  t.wrapS = t.wrapT = THREE.ClampToEdgeWrapping;
  // height, not colour: through sRGB this would be silently gamma-decoded and
  // the relief would come out shallower at the top end than it was drawn
  t.colorSpace = THREE.NoColorSpace;
  return t;
}

// ---- the lineup, on its own quads ----

/**
 * One act from the lineup: the name in heavy ink over a splat with the
 * colour pulls behind it, drips off the letterforms, and the year in a
 * ruled colour block beneath — a direct quote of the BREEZE / 2027 blocks
 * on the arch's own beam.
 */
export function makePieceTexture(
  entry: { act: string; year: string },
  seed: number
): THREE.CanvasTexture {
  const r = rng(seed);
  const H = 340;
  const size = 138;

  // measured in the face it will be DRAWN in — the two fit differently, and
  // measuring in the other one either clips the name or floats it in padding
  const { ctx: pc } = mk(8, 8);
  pc.font = `900 ${size}px ${FALLBACK_FONT}`;
  const W = Math.min(2048, Math.max(360, Math.ceil(pc.measureText(entry.act).width + size * 1.5)));
  const { c, ctx } = mk(W, H);

  const cx = W / 2;
  const cy = H * 0.38;
  const accent = pick(SPRAY, r);

  // No white backing here — the wall itself carries it now, so a patch on this
  // quad would be a second one stacked on the first with a visible edge where
  // the texture ends.
  splat(ctx, cx, cy, Math.max(W * 0.3, H * 0.46), accent, r);
  overspray(ctx, cx, cy, Math.max(W, H) * 0.3, accent, 700, r);
  posterType(ctx, entry.act, cx, cy, size, r, false, FALLBACK_FONT);
  labelBlock(ctx, cx, H * 0.82, size * 0.5, entry.year, accent, r);

  return finish(c);
}

/**
 * A hand-written name tag — an act and its year scrawled up quickly, the way
 * the same names get written over and over on a wall like this. Five big
 * pieces are a lineup poster; the same five names tagged twenty times
 * between them is a wall people keep coming back to.
 */
export function makeNameTagTexture(
  entry: { act: string; year: string },
  seed: number
): THREE.CanvasTexture {
  const r = rng(seed);
  const H = 140;
  const size = 66;
  const label = `${entry.act} '${entry.year.slice(2)}`;

  const { ctx: pc } = mk(8, 8);
  pc.font = `900 ${size}px ${FALLBACK_FONT}`;
  const W = Math.min(2048, Math.max(180, Math.ceil(pc.measureText(label).width + size * 0.9)));
  const { c, ctx } = mk(W, H);

  const cx = W / 2;
  const cy = H * 0.44;
  const ink = r() < 0.78 ? VAULT.ink : pick(SPRAY, r);

  ctx.save();
  ctx.translate(cx, cy);
  ctx.rotate((r() - 0.5) * 0.1);
  ctx.font = `900 ${size}px ${FALLBACK_FONT}`;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillStyle = ink;
  ctx.fillText(label, 0, 0);
  // the underline every tag gets, kicked up at the end
  ctx.strokeStyle = ink;
  ctx.lineWidth = size * 0.1;
  ctx.lineCap = "round";
  ctx.beginPath();
  ctx.moveTo(-W * 0.36, size * 0.44);
  ctx.quadraticCurveTo(0, size * 0.58, W * 0.36, size * 0.3);
  ctx.stroke();
  ctx.restore();

  runs(ctx, cx - W * 0.34, cx + W * 0.34, cy + size * 0.3, size * 0.5, ink, 4, r);
  return finish(c);
}
