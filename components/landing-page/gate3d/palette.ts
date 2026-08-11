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
// A flat-roofed brick tunnel butted against the back face of the structure,
// taking its 5.0 m head height straight from the opening's own head. The camera
// flies its whole length on entry and stops at the mouth, where the fest ground
// begins.
//
// Its WIDTH, though, is its own: 6.2 m against the opening's 4.6, so the walls
// stand back off the flight line and the paint on them is read across rather
// than scraped past. The flare is hidden — anything outboard of the opening
// sits behind the pillar boards, which are opaque from x = 2.3 out to the
// facade's 4.27, so no sightline from in front of the arch reaches it. That
// half-width is the ceiling on this number: widen past GATE.halfW and the
// tunnel starts poking out from behind the structure it is supposed to be
// running through.
const T_HALF_W = 3.1;
const T_ROOF_Y = plinthH + pillarH; // the beam's underside = the opening's head
const T_START_Z = -pillarD / 2; // hard against the arch's back face
// 38 m, not 58: the flight covers it in a shade less time than it used to
// cover the longer run, which is what makes the walk slower — the same eased
// curve over two-thirds the distance. Long enough to be a tunnel, short
// enough that you are never just waiting in one.
const T_END_Z = -38;

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

/**
 * The tunnel's surfaces, pulled off the printed boards on the arch itself
 * (`public/gate/*.webp`) so the walls you fly between are the same artwork
 * you just flew through: aged screenprint cream, one heavy ink black, and
 * the three spray colours those posters are built from.
 */
export const VAULT = {
  paper: "#ded4bb", // the posters' aged screenprint stock
  paperDim: "#bfb193", // its shadowed patches and water staining
  // the masonry the whole tunnel is built of. Warm rather than the usual cold
  // red: the arch it runs out of is lit gold and printed on cream stock, and a
  // pink-grey brick under those floods reads as a different building.
  brick: "#8d5b42",
  brickDark: "#6b4130", // the over-fired ones, and everything the soot found
  brickPale: "#ab7a5c", // the under-fired ones — what stops a wall reading as one flat tone
  mortar: "#c8bda6", // lime, close enough to the poster stock to tie the two together
  ink: "#141210", // the tag black everything is lettered in
  red: "#d0342a", // the splats and starbursts
  blue: "#1f4f9c", // the washes and the cooler tags
  yellow: "#e5a81c", // the accent marks and the year blocks
  // the patch of white that goes up before the lettering does. Not #fff: this
  // wall is lit gold and graded through ACES, and pure white clips to a flat
  // hole the moment a travelling lamp passes it
  whitewash: "#ecebe4",
  fixture: "#ffe6bd", // the light rods
  dead: "#2a2b30", // the tubes that gave up years ago
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
  /**
   * Everyone who has played, in the order you pass them — the tunnel is a
   * wall of past headliners, so the walk in is the fest's own history and
   * the far end is this year. Chronological on purpose: add next year's act
   * to the bottom and the walk grows a year longer.
   *
   * These are the only words anyone actually reads on the way in; the rest
   * of the wall is abstract.
   */
  lineup: [
    { act: "NEHA KAKKAR", year: "2017" },
    { act: "TWIN STRINGS", year: "2023" },
    { act: "KHULLAR G", year: "2025" },
    { act: "NIKHITHA GANDHI", year: "2025" },
    { act: "TWIN STRINGS", year: "2026" },
  ] as const,
} as const;
