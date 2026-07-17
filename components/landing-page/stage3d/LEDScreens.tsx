"use client";
import React, { useEffect, useMemo } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { PALETTE, STAGE } from "./palette";

/**
 * The signature element: a 7-panel LED wall — one large vertical center
 * screen flanked by 3 progressively smaller panels per side.
 *
 * Two modes:
 * - idle: shader content (waves + scanlines + glitch bars); the center screen
 *   invites "PLAY THE AFTERMOVIE" and is clickable.
 * - video: all 7 panels become one segmented video wall — each panel samples
 *   its slice of ONE shared VideoTexture (single GPU upload per frame),
 *   width-fit across the combined wall, vertically center-cropped.
 */

const VERT = /* glsl */ `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const FRAG = /* glsl */ `
  varying vec2 vUv;
  uniform float uTime;
  uniform float uSeed;
  uniform vec3 uColorA;
  uniform vec3 uColorB;
  uniform sampler2D uLogo;
  uniform float uHasLogo;
  uniform sampler2D uVideo;
  uniform float uVideoOn;
  uniform vec2 uUvOffset;
  uniform vec2 uUvRepeat;

  float hash(vec2 p) { return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }

  void main() {
    vec2 uv = vUv;

    // panel-edge falloff so each screen reads as a framed unit
    float edge = smoothstep(0.0, 0.05, uv.x) * smoothstep(1.0, 0.95, uv.x)
               * smoothstep(0.0, 0.04, uv.y) * smoothstep(1.0, 0.96, uv.y);

    // ---- video wall mode: sample this panel's slice of the shared video,
    // rendered as a physical LED matrix (pixel cells + grout + shimmer) ----
    if (uVideoOn > 0.5) {
      vec2 wallUv = uUvOffset + uv * uUvRepeat; // continuous across all panels
      const vec2 RES = vec2(368.0, 207.0);      // square LED cells wall-wide
      // sample at LED-cell centers → visible pixelation
      vec2 cellUv = (floor(wallUv * RES) + 0.5) / RES;
      vec3 vcol = texture2D(uVideo, cellUv).rgb;
      // saturation boost — LED walls render punchier color than the source
      float luma = dot(vcol, vec3(0.2126, 0.7152, 0.0722));
      vcol = mix(vec3(luma), vcol, 1.35);
      // round LED dot with dark grout between cells
      vec2 cell = fract(wallUv * RES);
      float led = smoothstep(0.62, 0.25, length(cell - 0.5));
      vcol *= 0.30 + 0.85 * led;
      // faint refresh shimmer rolling down the wall
      vcol *= 1.0 + 0.05 * sin(wallUv.y * 40.0 - uTime * 2.2);
      vcol *= mix(0.55, 1.0, edge);
      gl_FragColor = vec4(vcol * 0.85, 1.0);
      return;
    }

    // ---- idle mode: black panels; center screen carries the play prompt ----
    vec3 col = vec3(0.010, 0.012, 0.016); // barely-there panel tone
    if (uHasLogo > 0.5) {
      vec4 logo = texture2D(uLogo, uv);
      float pulse = 0.85 + 0.15 * sin(uTime * 1.3);
      col += logo.rgb * 1.3 * pulse * logo.a;
    }
    col *= mix(0.35, 1.0, edge);
    gl_FragColor = vec4(col, 1.0);
  }
`;

/** Play prompt for the tall center screen. */
function makePromptTexture(): THREE.CanvasTexture {
  const c = document.createElement("canvas");
  c.width = 512;
  c.height = 768;
  const g = c.getContext("2d")!;
  g.clearRect(0, 0, c.width, c.height);
  g.textAlign = "center";
  g.textBaseline = "middle";

  // one voice: everything in the truss lights' yellowish-white, no colored glow
  const WARM = "#fffbe8";

  // play button — ring + triangle
  g.strokeStyle = WARM;
  g.lineWidth = 9;
  g.shadowColor = WARM;
  g.shadowBlur = 6;
  g.beginPath();
  g.arc(256, 245, 85, 0, Math.PI * 2);
  g.stroke();
  g.fillStyle = WARM;
  g.beginPath();
  g.moveTo(232, 197);
  g.lineTo(232, 293);
  g.lineTo(316, 245);
  g.closePath();
  g.fill();

  // copy
  g.shadowBlur = 4;
  g.font = "600 34px Arial, sans-serif";
  g.fillText("PLAY LAST YEAR'S", 256, 420);
  g.font = "900 76px Arial, sans-serif";
  g.fillText("BREEZE", 256, 498);
  g.font = "800 50px Arial, sans-serif";
  g.fillText("AFTERMOVIE", 256, 572);

  const tex = new THREE.CanvasTexture(c);
  tex.anisotropy = 4;
  return tex;
}

/** Soft radial sprite for the glow halo behind each panel. */
function makeGlowTexture(): THREE.CanvasTexture {
  const c = document.createElement("canvas");
  c.width = c.height = 128;
  const g = c.getContext("2d")!;
  const grad = g.createRadialGradient(64, 64, 12, 64, 64, 64);
  grad.addColorStop(0, "rgba(255,255,255,0.85)");
  grad.addColorStop(0.55, "rgba(255,255,255,0.32)");
  grad.addColorStop(1, "rgba(255,255,255,0)");
  g.fillStyle = grad;
  g.fillRect(0, 0, 128, 128);
  return new THREE.CanvasTexture(c);
}

type Panel = { x: number; w: number; h: number; rotY: number; hasLogo: boolean; seed: number };

type LEDScreensProps = {
  /** when set, all panels switch to segmented-video-wall mode */
  videoTexture: THREE.VideoTexture | null;
  /** click handler for the center screen's play prompt */
  onPlay: () => void;
};

export default function LEDScreens({ videoTexture, onPlay }: LEDScreensProps): React.ReactElement {
  const { topY, screenZ } = STAGE;
  const gl = useThree((s) => s.gl);

  const panels = useMemo<Panel[]>(() => {
    const out: Panel[] = [{ x: 0, w: 6.8, h: 9.2, rotY: 0, hasLogo: true, seed: 0.5 }];
    const widths = [3.2, 2.8, 2.3];
    const heights = [7.2, 5.6, 4.1];
    const gap = 0.4;
    let edge = 3.4; // running outer edge from center (half the center panel width)
    widths.forEach((w, i) => {
      const x = edge + gap + w / 2;
      edge = x + w / 2;
      for (const side of [-1, 1]) {
        out.push({
          x: x * side,
          w,
          h: heights[i],
          rotY: -side * (i + 1) * 0.045, // subtle fan, outer panels turn toward camera
          hasLogo: false,
          seed: (i + 1) * 0.17 + (side + 1) * 0.31,
        });
      }
    });
    return out;
  }, []);

  // per-panel window into the shared video: width-fit across the whole wall,
  // vertically center-cropped (16:9 video on a ~2.8:1 wall)
  const videoWindows = useMemo(() => {
    const minX = Math.min(...panels.map((p) => p.x - p.w / 2));
    const maxX = Math.max(...panels.map((p) => p.x + p.w / 2));
    const wallW = maxX - minX;
    const wallH = Math.max(...panels.map((p) => p.h));
    const displayH = (wallW * 9) / 16; // video height if width-fit
    const vFrac = Math.min(1, wallH / displayH); // visible vertical fraction
    const vBase = (1 - vFrac) / 2;
    return panels.map((p) => ({
      offset: new THREE.Vector2((p.x - p.w / 2 - minX) / wallW, vBase),
      repeat: new THREE.Vector2(p.w / wallW, (p.h / wallH) * vFrac),
    }));
  }, [panels]);

  const materials = useMemo(() => {
    const prompt = makePromptTexture();
    // complete 1x1 transparent texture — an empty THREE.Texture() is an
    // incomplete sampler, which some drivers handle badly
    const blank = new THREE.DataTexture(new Uint8Array([0, 0, 0, 0]), 1, 1);
    blank.needsUpdate = true;
    return panels.map(
      (p, i) =>
        new THREE.ShaderMaterial({
          vertexShader: VERT,
          fragmentShader: FRAG,
          uniforms: {
            uTime: { value: 0 },
            uSeed: { value: p.seed },
            uColorA: { value: new THREE.Color(PALETTE.cyan) },
            uColorB: { value: new THREE.Color(PALETTE.violet) },
            uLogo: { value: p.hasLogo ? prompt : (blank as THREE.Texture) },
            uHasLogo: { value: p.hasLogo ? 1 : 0 },
            uVideo: { value: blank as THREE.Texture },
            uVideoOn: { value: 0 },
            uUvOffset: { value: videoWindows[i].offset },
            uUvRepeat: { value: videoWindows[i].repeat },
          },
        })
    );
  }, [panels, videoWindows]);

  const glowMat = useMemo(() => {
    const m = new THREE.MeshBasicMaterial({
      map: makeGlowTexture(),
      transparent: true,
      opacity: 0.09,
      color: "#fffbe8", // matches the truss heads' yellowish-white
      blending: THREE.AdditiveBlending,
      depthWrite: false,
    });
    m.toneMapped = false;
    return m;
  }, []);

  // flip all panels between idle shader and video wall
  useEffect(() => {
    for (const m of materials) {
      if (videoTexture) m.uniforms.uVideo.value = videoTexture;
      m.uniforms.uVideoOn.value = videoTexture ? 1 : 0;
    }
  }, [videoTexture, materials]);

  useFrame(({ clock }) => {
    const t = clock.elapsedTime;
    for (const m of materials) m.uniforms.uTime.value = t;
  });

  return (
    <group>
      {panels.map((p, i) => (
        <group key={i} position={[p.x, topY + p.h / 2, screenZ]} rotation-y={p.rotY}>
          {/* dark frame behind the panel */}
          <mesh position-z={-0.1}>
            <boxGeometry args={[p.w + 0.16, p.h + 0.16, 0.16]} />
            <meshStandardMaterial color={PALETTE.panel} roughness={0.6} metalness={0.4} />
          </mesh>
          <mesh
            material={materials[i]}
            onClick={p.hasLogo && !videoTexture ? () => onPlay() : undefined}
            onPointerOver={
              p.hasLogo && !videoTexture ? () => (gl.domElement.style.cursor = "pointer") : undefined
            }
            onPointerOut={p.hasLogo ? () => (gl.domElement.style.cursor = "auto") : undefined}
          >
            <planeGeometry args={[p.w, p.h]} />
          </mesh>
          {/* soft light bleed haloing past the panel edges */}
          <mesh position-z={0.05} scale={[1.45, 1.45, 1]} material={glowMat} renderOrder={5}>
            <planeGeometry args={[p.w, p.h]} />
          </mesh>
        </group>
      ))}
    </group>
  );
}
