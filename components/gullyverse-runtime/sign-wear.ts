/**
 * Weathered painted metal for the navigation board (realism pass, 27 Nov): the restyled panels are flat paint on
 * flat geometry, so the wear is procedural in world space (the board faces +z, so world xy is the panel's plane):
 * - sun-faded, uneven paint (low-frequency lightening and grime),
 * - chipped paint showing grey galvanised metal (`paint`) or, on the lettering, the panel underneath (`ink`),
 * - thin rust runs streaking down the face,
 * - slightly shinier bare metal in the chips.
 * Needs the vBreezeWorld varying (fidelity.ts worldVaryings). `material.userData.breezeSignWear` is "paint" or "ink".
 */
export const signWearDeclare = `
float breezeSignHash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
float breezeSignNoise(vec2 p) {
  vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
  return mix(mix(breezeSignHash(i), breezeSignHash(i + vec2(1.0, 0.0)), f.x),
             mix(breezeSignHash(i + vec2(0.0, 1.0)), breezeSignHash(i + 1.0), f.x), f.y);
}
float breezeSignChip = 0.0;`;

export function signWearCode(kind: "paint" | "ink") {
  const chipTo = kind === "paint" ? "vec3(0.16, 0.16, 0.155)" : "diffuseColor.rgb * 0.22";
  return `{
  vec2 p = vBreezeWorld.xy;
  float n1 = breezeSignNoise(p * 3.1), n2 = breezeSignNoise(p * 11.0 + 7.3), n3 = breezeSignNoise(p * 37.0 + 1.7);
  // Fine-grained: small flecks, not camouflage blotches (the low frequency only modulates where wear gathers).
  float fbm = n3 * 0.5 + n2 * 0.35 + n1 * 0.15;
  // Thin rust runs: narrow in x, long in y, patchy.
  float runs = smoothstep(0.8, 0.96, breezeSignNoise(vec2(p.x * 34.0, p.y * 1.1))) * smoothstep(0.35, 0.75, n1);
  breezeSignChip = smoothstep(${kind === "paint" ? "0.74, 0.78" : "0.72, 0.76"}, fbm + 0.12 * (n1 - 0.5));
  vec3 c = diffuseColor.rgb * (0.9 + 0.16 * fbm);
  c = mix(c, c * vec3(1.05, 1.03, 0.97) + 0.03, smoothstep(0.6, 0.9, n1) * 0.3);       // sun-faded patches
  c = mix(c, ${chipTo}, breezeSignChip);
  c = mix(c, vec3(0.2, 0.075, 0.03), runs * ${kind === "paint" ? "0.4" : "0.2"});        // rust runs
  c *= 1.0 - 0.16 * smoothstep(0.55, 0.95, n2);                                            // grime
  diffuseColor.rgb = c;
}`;
}

/** After the roughness map: paint is matte, bare metal in the chips catches a little light. */
export const signWearRoughness = "roughnessFactor = mix(max(roughnessFactor, 0.82), 0.5, breezeSignChip);";
