// Design tokens + world layout for the night entry gate.
//
// The geometry mirrors the real Breeze arch from the reference photos: a wide
// squat structure — two thick pillar boards on low plinths carrying one full
// width beam — not a tall thin archway. Everything is authored in metres with
// the opening centred on the origin, front face toward +z (the camera).

export const NIGHT = {
  // the sky is deliberately a touch above black — the canopy and treeline are
  // read as silhouettes against it, and pure black would swallow them
  sky: "#070c18",
  skyHorizon: "#16203a",
  fog: "#070a14",

  board: "#eef3f8", // printed white panels
  // the posters' aged-paper base — the boards' side returns carry it so the
  // structure reads as one printed object rather than art stuck on grey slabs
  boardEdge: "#c6b99c",
  // what the plinth tint is mixed toward: a warm cream rather than pure white,
  // so the bases pick up the posters' aged-paper warmth instead of reading as
  // grey concrete under the gold floods
  baseCream: "#f7e7b8",
  ink: "#161b22",

  gold: "#ffc24b", // Breeze brand gold (matches navbar_text_select)
  bulb: "#ffd9a0", // warm practical bulbs
  amber: "#ff9d43",
  moon: "#93a9d6", // cool key from above

  leaf: "#37543a",
  bark: "#0d0f12",
  paver: "#54545a",
  paverWarm: "#6b4a44", // the reddish band in the foreground paving
  tent: "#06070b",
  grass: "#16251a",
} as const;

// ---- proportions driven by the printed artwork in public/gate/ ----
// The boards are sized to their posters rather than the posters cropped to
// fit: change the art and update these two ratios, and the whole facade
// (and the camera framing that solves off it) follows.
//
// board-left.webp is 853×1844 (1 : 2.162) and board-right.webp 809×1942
// (1 : 2.400). The pillars take the midpoint, so each poster is centre-cropped
// by ~2.5% per edge instead of one being visibly stretched.
const POSTER_HW = 2.281; // pillar height ÷ width
const BEAM_WH = 4.525; // beam.webp is 2172×480

const openingW = 4.6;
const pillarD = 0.58;
const plinthH = 0.5;
const pillarH = 4.5;
const pillarW = pillarH / POSTER_HW;
// derived so beam.webp maps edge-to-edge with no distortion
const beamH = (openingW + 2 * pillarW) / BEAM_WH;

export const GATE = {
  openingW,
  pillarW,
  pillarD,
  plinthH,
  pillarH,
  beamH,
  plinthW: pillarW + 0.16,
  plinthD: pillarD + 0.14,

  pillarX: openingW / 2 + pillarW / 2, // 3.29 — centre of each pillar
  halfW: openingW / 2 + pillarW, // 4.27 — half the whole facade
  pillarTopY: plinthH + pillarH, // 5.00 — underside of the beam
  totalH: plinthH + pillarH + beamH, // 6.89
  faceZ: pillarD / 2 + 0.006, // signage plane, just proud of the box
} as const;

// ---- the graffiti tunnel behind the arch ----
// A flat-roofed brick tunnel, cut to the arch's OWN opening rather than to
// numbers of its own: same 4.6 m width, same 5.0 m head height, butted against
// the back face of the structure. Sharing the opening's dimensions is what
// makes it read as starting at the boards — anything even slightly off and it
// looks like a separate box parked behind them. The camera flies its whole
// length on entry and stops at the mouth, where the fest ground begins.
const T_HALF_W = openingW / 2;
const T_ROOF_Y = plinthH + pillarH; // the beam's underside = the opening's head
const T_START_Z = -pillarD / 2; // hard against the arch's back face
const T_END_Z = -58;

// once around the section: up one wall, across the roof, down the other
const T_PROFILE_S = 2 * T_ROOF_Y + 2 * T_HALF_W;

export const TUNNEL = {
  halfW: T_HALF_W,
  roofY: T_ROOF_Y,
  startZ: T_START_Z,
  endZ: T_END_Z,
  length: T_START_Z - T_END_Z,
  profileS: T_PROFILE_S,
  // where wall gives way to roof, as a fraction of the profile's arc length.
  // The shell's v runs 0 (left floor) → 1 (right floor), so the graffiti knows
  // which band of the texture is wall and which is ceiling without either file
  // hard-coding the other's numbers.
  wallEndV: T_ROOF_Y / T_PROFILE_S,
  ceilEndV: (T_ROOF_Y + 2 * T_HALF_W) / T_PROFILE_S,
} as const;

export const VAULT = {
  brick: "#241d1a", // soot-darkened brick behind the paint
  mortar: "#332a25",
  ceiling: "#0b0b0e", // the roof, under its black-and-white line-work
  chalk: "#cfd4dc", // the pale ink that line-work is drawn in
  fixture: "#ffe6bd", // the light rods and hoops
  dead: "#2a2b30", // the tubes that gave up years ago
  road: "#191a1f",
} as const;

/**
 * Every word printed on the gate, in one place — sponsors and the fest theme
 * change year to year, so swapping a line here re-skins the whole arch.
 */
export const SIGN = {
  sponsor: "vivo",
  sponsorAlt: "croma",
  product: "V70 · V70 Elite",
  productSub: "Co-engineered with",
  fest: ["BREEZE", "26"] as const,
  leftSpec: ["4K 60fps", "Video with", "Zoom Clarity"] as const,
  rightSpec: ["50 MP", "ZEISS Night", "Telephoto Camera"] as const,
  // the plinths carry no copy — they take their colour from the pillar art
  theme: "GULLYVERSE", // the hanging cut-out letters beyond the arch
  // The legible pieces sprayed along the tunnel, in the order you pass them.
  // Everything else on those walls is abstract or pictorial, so this list is
  // the only copy anyone actually reads on the way in — the theme is Indian
  // street hip-hop, so it runs bilingual. `deva` is used wherever the device
  // can render the script and the Latin is the transliteration, not a
  // translation, so the fallback still says the same word out loud.
  tunnel: [
    { text: "GULLYVERSE" },
    { text: "GALI", deva: "गली" },
    { text: "BREEZE" },
    { text: "APNA SHOR", deva: "अपना शोर" },
    { text: "SNU" },
    { text: "HAWA", deva: "हवा" },
    { text: "BOL", deva: "बोल" },
    { text: "27" },
    { text: "TAAL", deva: "ताल" },
    { text: "SHEHAR", deva: "शहर" },
    { text: "BRZ" },
    { text: "2027" },
  ] as const,
} as const;
