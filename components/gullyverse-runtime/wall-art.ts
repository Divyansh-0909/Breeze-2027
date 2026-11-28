import * as THREE from "three";
import type { Region } from "./dressing-textures";

/**
 * Canvas art for the zones (user requests, 28 Nov): the white EVENTS throw-up on the events shutter, the contact
 * counter's lanyards and stickers, and the accommodation wall's three enamel boards (ACCOMMODATION / HOSTEL & STAY
 * PASSES / CHECK-IN DESK →, after the user's reference). Everything is drawn here, no downloads.
 */

function random(seed: number) {
  let s = seed >>> 0;
  return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; };
}

/**
 * "EVENTS" in the organising-committee mural's own name lettering (user request, 28 Nov): the letters are lifted from
 * the mural art and re-inked (scripts/gullyverse/events-lettering.py → events-lettering.png): cream marker capitals,
 * a dark outline, the tapered underline. Fitted into the rect; the bottom 12% and the left 5% stay clear (the
 * shutter's click proxy samples there).
 */
export const eventsLettering = "/models/gullyverse/zone-art/events-lettering.png";
export function sprayEvents(g: CanvasRenderingContext2D, x: number, y: number, w: number, h: number, art: HTMLImageElement) {
  g.clearRect(x, y, w, h);
  const bx = x + w * 0.05, by = y + h * 0.01, bw = w * 0.94, bh = h * 0.86;
  const s = Math.min(bw / art.naturalWidth, bh / art.naturalHeight), dw = art.naturalWidth * s, dh = art.naturalHeight * s;
  g.drawImage(art, bx + (bw - dw) / 2, by + (bh - dh) / 2, dw, dh);
}

/** Titles for the older, half-covered gig posters around the live ones. */
export const pastGigs = ["CYPHER NIGHT", "B-BOY JAM", "OPEN MIC", "DJ CLASH", "SPRAY JAM", "BARS & BEATS", "GULLY FEST", "BEAT BATTLE",
  "RAP WAR", "BLOCK PARTY", "MIC CHECK", "KRUMP SESSION", "FREESTYLE FRIDAY", "VINYL NIGHT", "STREET SOUND", "UNDERGROUND"];

export type SignSheet = { texture: THREE.CanvasTexture; glow: THREE.CanvasTexture; boards: Region[]; lanyards: Region[]; stickers: Region[]; curtain: Region };

/**
 * One 1024 × 1536 sheet (half on small tiers): three 4:1 enamel boards, a strip of four lanyards (128 × 256 each) and
 * eight stickers (128 × 128 each), then the accommodation window's backlit curtain (384 × 512). `glow` is the matching
 * emissive map: black except the curtain.
 */
export function signSheet(big: boolean): SignSheet {
  const S = 1024, SH = 1536, k = big ? 1 : 0.5;
  const c = document.createElement("canvas"); c.width = S * k; c.height = SH * k;
  const g = c.getContext("2d")!;
  g.scale(k, k);
  const rand = random(0x51a7);
  const region = (x: number, y: number, w: number, h: number): Region => [x / S, 1 - (y + h) / SH, (x + w) / S, 1 - y / SH];

  const wear = (x: number, y: number, w: number, h: number, rust: string) => {
    // Grime streaks running down, chips (dark with a pale rim), rust blooms, darker edges.
    for (let i = 0; i < 70; i++) {
      const sx = x + rand() * w, len = h * (0.2 + rand() * 0.8);
      const run = g.createLinearGradient(0, y, 0, y + len);
      run.addColorStop(0, "rgba(40,30,20,0.18)"); run.addColorStop(1, "rgba(40,30,20,0)");
      g.fillStyle = run; g.fillRect(sx, y, 2 + rand() * 7, len);
    }
    for (let i = 0; i < 26; i++) {
      const bx = x + rand() * w, by = y + (rand() < 0.6 ? (rand() < 0.5 ? rand() * h * 0.25 : h - rand() * h * 0.25) : rand() * h);
      const r = 4 + rand() * 18;
      const bloom = g.createRadialGradient(bx, by, 0, bx, by, r);
      bloom.addColorStop(0, rust); bloom.addColorStop(1, "rgba(0,0,0,0)");
      g.fillStyle = bloom; g.beginPath(); g.arc(bx, by, r, 0, Math.PI * 2); g.fill();
    }
    for (let i = 0; i < 40; i++) {
      const bx = x + rand() * w, by = y + rand() * h, r = 1.5 + rand() * 5;
      g.fillStyle = "rgba(210,200,180,0.5)"; g.beginPath(); g.arc(bx, by, r + 1.5, 0, Math.PI * 2); g.fill();
      g.fillStyle = "rgba(30,26,22,0.9)"; g.beginPath(); g.arc(bx, by, r, 0, Math.PI * 2); g.fill();
    }
    for (let i = 0; i < 1600; i++) { g.fillStyle = `rgba(20,16,12,${0.08 * rand()})`; g.fillRect(x + rand() * w, y + rand() * h, 1 + 3 * rand(), 1 + 2 * rand()); }
    const edge = g.createRadialGradient(x + w / 2, y + h / 2, h * 0.4, x + w / 2, y + h / 2, w * 0.55);
    edge.addColorStop(0, "rgba(0,0,0,0)"); edge.addColorStop(1, "rgba(20,12,6,0.45)");
    g.fillStyle = edge; g.fillRect(x, y, w, h);
    for (const [rx, ry] of [[x + 18, y + 18], [x + w - 18, y + 18], [x + 18, y + h - 18], [x + w - 18, y + h - 18], [x + w / 2, y + 14], [x + w / 2, y + h - 14]]) {
      const run = g.createLinearGradient(0, ry, 0, ry + 60);
      run.addColorStop(0, "rgba(110,55,25,0.6)"); run.addColorStop(1, "rgba(110,55,25,0)");
      g.fillStyle = run; g.fillRect(rx - 4, ry, 8, 60);
      g.fillStyle = "#3a332c"; g.beginPath(); g.arc(rx, ry, 6.5, 0, Math.PI * 2); g.fill();
      g.fillStyle = "rgba(200,190,170,0.35)"; g.beginPath(); g.arc(rx - 1.5, ry - 1.5, 2.5, 0, Math.PI * 2); g.fill();
    }
  };
  const fitText = (text: string, font: (px: number) => string, px: number, max: number) => {
    g.font = font(px); while (g.measureText(text).width > max && px > 20) { px -= 2; g.font = font(px); }
    return px;
  };
  const condensed = (px: number) => `900 ${px}px Impact, "Arial Narrow", "Arial Black", sans-serif`;

  // 1. ACCOMMODATION: mustard enamel, dark brown letters.
  {
    const x = 0, y = 0, w = 1024, h = 256;
    const enamel = g.createLinearGradient(0, y, 0, y + h);
    enamel.addColorStop(0, "#d6a43a"); enamel.addColorStop(1, "#b98527");
    g.fillStyle = enamel; g.fillRect(x, y, w, h);
    g.strokeStyle = "rgba(80,48,18,0.85)"; g.lineWidth = 7; g.strokeRect(x + 26, y + 26, w - 52, h - 52);
    g.fillStyle = "#3d2614"; g.textAlign = "center"; g.textBaseline = "middle";
    fitText("ACCOMMODATION", condensed, 168, w - 110);
    g.save(); g.translate(x + w / 2, y + h / 2 + 6); g.scale(0.86, 1.12); g.fillText("ACCOMMODATION", 0, 0); g.restore();
    wear(x, y, w, h, "rgba(120,58,22,0.7)");
  }
  // 2. HOSTEL & STAY PASSES: off-white enamel, a blue band at the edges, dark teal letters.
  {
    const x = 0, y = 256, w = 1024, h = 256;
    g.fillStyle = "#dcd8cd"; g.fillRect(x, y, w, h);
    g.fillStyle = "#4f86a3"; g.fillRect(x, y, w, 22); g.fillRect(x, y + h - 22, w, 22);
    g.fillStyle = "#6f9fb8"; g.fillRect(x, y + 22, w, 6); g.fillRect(x, y + h - 28, w, 6);
    g.fillStyle = "#1d3c4c"; g.textAlign = "center"; g.textBaseline = "middle";
    fitText("HOSTEL & STAY PASSES", condensed, 150, w - 100);
    g.save(); g.translate(x + w / 2, y + h / 2 + 4); g.scale(0.9, 1.1); g.fillText("HOSTEL & STAY PASSES", 0, 0); g.restore();
    wear(x, y, w, h, "rgba(130,62,24,0.75)");
  }
  // 3. CHECK-IN DESK →: oxide red, cream italic letters and an arrow.
  {
    const x = 0, y = 512, w = 1024, h = 256;
    const enamel = g.createLinearGradient(0, y, 0, y + h);
    enamel.addColorStop(0, "#82382a"); enamel.addColorStop(1, "#692a1f");
    g.fillStyle = enamel; g.fillRect(x, y, w, h);
    g.strokeStyle = "rgba(230,214,188,0.55)"; g.lineWidth = 5; g.strokeRect(x + 24, y + 24, w - 48, h - 48);
    g.fillStyle = "#e7d8bd"; g.textAlign = "center"; g.textBaseline = "middle";
    fitText("CHECK-IN DESK", condensed, 140, w - 280);
    g.save(); g.translate(x + w / 2 - 70, y + h / 2 + 4); g.transform(1, 0, -0.2, 1, 0, 0); g.scale(0.92, 1.1);
    g.fillText("CHECK-IN DESK", 0, 0); g.restore();
    const ax = x + w - 190, ay = y + h / 2 + 4;
    g.fillRect(ax, ay - 12, 96, 24);
    g.beginPath(); g.moveTo(ax + 86, ay - 44); g.lineTo(ax + 150, ay); g.lineTo(ax + 86, ay + 44); g.closePath(); g.fill();
    wear(x, y, w, h, "rgba(60,26,14,0.7)");
  }

  // 4. Lanyards (128 × 256): a strap folded over the ledge edge, a clip, and an ID card.
  const lanyards: Region[] = [];
  const roles: [string, string][] = [["CREW", "#2f5d63"], ["STAFF", "#7a3324"], ["ARTIST", "#b98527"], ["VOLUNTEER", "#2f5d63"]];
  roles.forEach(([role, colour], i) => {
    const x = i * 128, y = 768;
    g.strokeStyle = colour; g.lineWidth = 9; g.lineCap = "round";
    g.beginPath(); g.moveTo(x + 40, y + 2); g.lineTo(x + 58, y + 124); g.stroke();
    g.beginPath(); g.moveTo(x + 88, y + 2); g.lineTo(x + 70, y + 124); g.stroke();
    g.strokeStyle = "rgba(240,235,225,0.6)"; g.lineWidth = 2;
    g.beginPath(); g.moveTo(x + 40, y + 6); g.lineTo(x + 57, y + 120); g.stroke();
    g.fillStyle = "#8d8f91"; g.fillRect(x + 54, y + 120, 20, 20);
    g.fillStyle = "#4a4c4e"; g.fillRect(x + 58, y + 124, 12, 12);
    // Card.
    const cx = x + 16, cy = y + 140, cw = 96, ch = 112;
    g.fillStyle = "#ece8de"; g.fillRect(cx, cy, cw, ch);
    g.fillStyle = colour; g.fillRect(cx, cy, cw, 30);
    g.fillStyle = "#f3efe6"; g.textAlign = "center"; g.textBaseline = "middle";
    g.font = '900 17px Impact, "Arial Black", sans-serif'; g.fillText(role, cx + cw / 2, cy + 16, cw - 8);
    g.fillStyle = "#6f6a62"; g.fillRect(cx + 10, cy + 40, 34, 40);
    g.fillStyle = "#a59c8e"; g.beginPath(); g.arc(cx + 27, cy + 54, 9, 0, Math.PI * 2); g.fill();
    g.fillRect(cx + 15, cy + 66, 24, 14);
    g.fillStyle = "#2a2724"; for (let l = 0; l < 3; l++) g.fillRect(cx + 50, cy + 44 + l * 12, 36 - l * 8, 5);
    g.font = '700 12px "Arial Narrow", Arial, sans-serif'; g.fillText("BREEZE '27", cx + cw / 2, cy + 96);
    g.strokeStyle = "rgba(40,36,30,0.35)"; g.lineWidth = 2; g.strokeRect(cx + 1, cy + 1, cw - 2, ch - 2);
    for (let n = 0; n < 160; n++) { g.fillStyle = `rgba(40,30,20,${0.12 * rand()})`; g.fillRect(cx + rand() * cw, cy + rand() * ch, 2, 2); }
    lanyards.push(region(x, y, 128, 256));
  });

  // 5. Stickers (128 × 128): crew and gully slaps, scuffed.
  const stickers: Region[] = [];
  const slaps: [string, string, string, "round" | "rect" | "tag"][] = [
    ["B'27", "#6e4127", "#eee6d6", "round"], ["CYPHER", "#151515", "#eee6d6", "rect"], ["GULLY", "#2f5d63", "#eee6d6", "tag"],
    ["HIP HOP", "#eee6d6", "#151515", "rect"], ["BARS", "#b98527", "#1c140c", "round"], ["B-BOY", "#7a3324", "#eee6d6", "tag"],
    ["RAP", "#eee6d6", "#7a3324", "round"], ["VERSE", "#1d3c4c", "#e4dccb", "rect"]];
  slaps.forEach(([text, bg, fg, shape], i) => {
    const x = 512 + (i % 4) * 128, y = 768 + Math.floor(i / 4) * 128, mx = x + 64, my = y + 64;
    g.save(); g.translate(mx, my); g.rotate((rand() - 0.5) * 0.4);
    g.fillStyle = "#f3efe6";
    if (shape === "round") { g.beginPath(); g.arc(0, 0, 54, 0, Math.PI * 2); g.fill(); g.fillStyle = bg; g.beginPath(); g.arc(0, 0, 48, 0, Math.PI * 2); g.fill(); }
    else if (shape === "rect") { g.fillRect(-58, -34, 116, 68); g.fillStyle = bg; g.fillRect(-53, -29, 106, 58); }
    else { g.fillRect(-58, -42, 116, 84); g.fillStyle = bg; g.fillRect(-53, -37, 106, 74); g.fillStyle = "#f3efe6"; g.fillRect(-53, -37, 106, 22); }
    g.fillStyle = shape === "tag" ? "#151515" : fg; g.textAlign = "center"; g.textBaseline = "middle";
    if (shape === "tag") { g.font = '800 15px "Arial Black", Arial, sans-serif'; g.fillText("HELLO", 0, -26); g.fillStyle = fg; }
    let px = 40; g.font = `900 ${px}px Impact, "Arial Black", sans-serif`;
    while (g.measureText(text).width > 96 && px > 14) { px -= 2; g.font = `900 ${px}px Impact, "Arial Black", sans-serif`; }
    g.fillText(text, 0, shape === "tag" ? 10 : 2);
    g.restore();
    // Scuffs and a torn corner.
    g.save(); g.beginPath(); g.rect(x, y, 128, 128); g.clip();
    g.globalCompositeOperation = "destination-out";
    for (let n = 0; n < 40; n++) { g.fillStyle = "rgba(0,0,0,0.9)"; g.fillRect(x + rand() * 128, y + rand() * 128, 1 + rand() * 6, 1 + rand() * 2); }
    if (i % 3 === 0) { g.beginPath(); g.moveTo(x + 128, y + 128); g.lineTo(x + 128, y + 82); g.lineTo(x + 84, y + 128); g.closePath(); g.fill(); }
    g.restore();
    for (let n = 0; n < 120; n++) { g.fillStyle = `rgba(30,24,16,${0.15 * rand()})`; g.fillRect(x + 10 + rand() * 108, y + 10 + rand() * 108, 2, 2); }
    stickers.push(region(x, y, 128, 128));
  });

  // 6. The curtain behind the accommodation window's bars: two sheer panels lit from behind by a bulb (upper right),
  // soft vertical folds, a darker parting, a grimy hem.
  const curtain = (ink: CanvasRenderingContext2D, gain: number) => {
    const x = 0, y = 1024, w = 384, h = 512;
    const back = ink.createRadialGradient(x + w * 0.68, y + h * 0.3, 8, x + w * 0.68, y + h * 0.3, w * 0.95);
    back.addColorStop(0, `rgba(255,228,180,${gain})`); back.addColorStop(0.4, `rgba(214,150,84,${gain})`); back.addColorStop(1, `rgba(86,48,22,${gain})`);
    ink.fillStyle = back; ink.fillRect(x, y, w, h);
    for (let f = 0; f < 22; f++) { // folds
      const fx = x + (f / 22) * w + Math.sin(f * 1.7) * 4, fw = w / 22;
      const fold = ink.createLinearGradient(fx, 0, fx + fw, 0);
      fold.addColorStop(0, `rgba(40,20,8,${0.32 * gain})`); fold.addColorStop(0.5, `rgba(255,236,200,${0.1 * gain})`); fold.addColorStop(1, `rgba(40,20,8,${0.32 * gain})`);
      ink.fillStyle = fold; ink.fillRect(fx, y, fw, h);
    }
    ink.fillStyle = `rgba(30,16,6,${0.55 * gain})`; ink.fillRect(x + w * 0.47, y, w * 0.05, h); // the parting
    ink.fillStyle = `rgba(30,16,6,${0.5 * gain})`; ink.fillRect(x, y, w, 14); // the rod
    const hem = ink.createLinearGradient(0, y + h * 0.8, 0, y + h);
    hem.addColorStop(0, "rgba(30,18,8,0)"); hem.addColorStop(1, `rgba(30,18,8,${0.6 * gain})`);
    ink.fillStyle = hem; ink.fillRect(x, y + h * 0.8, w, h * 0.2);
  };
  curtain(g, 1);
  const e = document.createElement("canvas"); e.width = S * k; e.height = SH * k;
  const eg = e.getContext("2d")!;
  eg.scale(k, k); eg.fillStyle = "#000"; eg.fillRect(0, 0, S, SH); curtain(eg, 0.85);

  const texture = new THREE.CanvasTexture(c);
  texture.colorSpace = THREE.SRGBColorSpace; texture.anisotropy = 8;
  const glow = new THREE.CanvasTexture(e);
  glow.colorSpace = THREE.SRGBColorSpace;
  return { texture, glow, curtain: region(0, 1024, 384, 512), boards: [region(0, 0, 1024, 256), region(0, 256, 1024, 256), region(0, 512, 1024, 256)], lanyards, stickers };
}
