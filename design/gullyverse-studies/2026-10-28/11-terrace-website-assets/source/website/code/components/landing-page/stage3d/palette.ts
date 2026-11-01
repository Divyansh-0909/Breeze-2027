// Shared design tokens for the 3D concert stage.
// Near-black world, two live neon hues (cyan/violet) + magenta reserved
// for the moving-light color cycle. No default Tailwind hues anywhere.
export const PALETTE = {
  void: "#050608", // scene background + fog
  carbon: "#0c0f14", // stage decking / speaker cabinets
  panel: "#14181f", // elevated dark surfaces (roof, frames)
  steel: "#b7bec9", // truss metal
  cyan: "#3ee6ff",
  violet: "#8b5bff",
  magenta: "#ff3ea5",
} as const;

// World layout constants (front of stage faces +z, camera lives at +z)
export const STAGE = {
  topY: 1.3, // stage deck height
  halfW: 12, // platform half width
  frontZ: 4, // platform front edge
  backZ: -5, // platform back edge
  eavesY: 11.4, // roof underside
  screenZ: -4.55, // LED wall plane
} as const;
