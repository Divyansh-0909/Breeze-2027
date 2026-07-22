"use client";
import React, { useEffect, useMemo, useRef } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { PALETTE, STAGE } from "./palette";

/**
 * The signature element: a 7-panel LED wall — one large vertical center
 * screen flanked by 3 progressively smaller panels per side.
 *
 * Three modes:
 * - idle: shader content (waves + scanlines + glitch bars); the center screen
 *   invites "RELIVE THE NIGHT — BREEZE '26" and is clickable.
 * - loading: the center screen swaps the prompt for a "LOADING AFTERMOVIE"
 *   label and a segmented LED progress bar driven by `loadingProgress`.
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
  uniform sampler2D uLoadLabel;
  uniform float uLoad;
  uniform float uProgress;
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

    // ---- idle layer: black panels; center screen carries the play prompt ----
    vec3 idle = vec3(0.010, 0.012, 0.016); // barely-there panel tone
    if (uHasLogo > 0.5) {
      vec4 logo = texture2D(uLogo, uv);
      float pulse = 0.85 + 0.15 * sin(uTime * 1.3);
      // play prompt yields to the loading state as uLoad rises
      idle += logo.rgb * 1.3 * pulse * logo.a * (1.0 - uLoad);

      // ---- loading state: label + segmented LED progress bar, in the same
      // warm truss-light voice as the prompt ----
      vec4 lbl = texture2D(uLoadLabel, uv);
      idle += lbl.rgb * (1.05 + 0.15 * sin(uTime * 1.8)) * lbl.a * uLoad;
      float bx = (uv.x - 0.16) / 0.68; // 0..1 along the bar track
      float inBar = step(0.0, bx) * (1.0 - step(1.0, bx))
                  * smoothstep(0.300, 0.307, uv.y) * (1.0 - smoothstep(0.327, 0.334, uv.y));
      float seg = step(fract(bx * 22.0), 0.78); // tick segments, LED-wall style
      float fill = 1.0 - step(uProgress, bx);
      vec3 warm = vec3(1.0, 0.984, 0.91);
      idle += warm * inBar * seg
            * (0.06 + 1.1 * fill * (0.88 + 0.12 * sin(uTime * 2.6))) * uLoad;
    }
    idle *= mix(0.35, 1.0, edge);

    // ---- video layer: this panel's slice of the shared video, rendered as
    // a physical LED matrix (pixel cells + grout + shimmer) ----
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
    vcol *= 0.85;

    // uVideoOn is a 0→1 fade; ease it so the wall breathes in, not snaps
    gl_FragColor = vec4(mix(idle, vcol, smoothstep(0.0, 1.0, uVideoOn)), 1.0);
  }
`;

/** Play prompt for the tall center screen. */
function makePromptTexture(): THREE.CanvasTexture {
  const c = document.createElement("canvas");
  // matches the center panel's 6.8 : 9.2 aspect so glyphs aren't stretched
  c.width = 568;
  c.height = 768;
  const g = c.getContext("2d")!;
  const cx = c.width / 2;
  g.clearRect(0, 0, c.width, c.height);
  g.textAlign = "center";
  g.textBaseline = "middle";

  // one voice: everything in the truss lights' yellowish-white, no colored glow
  const WARM = "#fffbe8";
  const FONT = "'Segoe UI', Arial, sans-serif";

  // play button — ring + triangle, optically centered
  g.strokeStyle = WARM;
  g.lineWidth = 7;
  g.shadowColor = WARM;
  g.shadowBlur = 5;
  g.beginPath();
  g.arc(cx, 236, 76, 0, Math.PI * 2);
  g.stroke();
  g.fillStyle = WARM;
  g.beginPath();
  g.moveTo(cx - 20, 200);
  g.lineTo(cx - 20, 272);
  g.lineTo(cx + 42, 236);
  g.closePath();
  g.fill();

  // copy — eyebrow / display / subtitle hierarchy with tracking
  g.shadowBlur = 3;
  g.globalAlpha = 0.78;
  (g as CanvasRenderingContext2D & { letterSpacing: string }).letterSpacing = "7px";
  g.font = `600 27px ${FONT}`;
  g.fillText("RELIVE THE NIGHT", cx + 3, 412);

  g.globalAlpha = 1;
  (g as CanvasRenderingContext2D & { letterSpacing: string }).letterSpacing = "3px";
  g.font = `800 76px ${FONT}`;
  g.fillText("BREEZE '26", cx + 1, 486);

  g.globalAlpha = 0.9;
  (g as CanvasRenderingContext2D & { letterSpacing: string }).letterSpacing = "13px";
  g.font = `600 36px ${FONT}`;
  g.fillText("TAP TO WATCH", cx + 6, 556);
  g.globalAlpha = 1;

  const tex = new THREE.CanvasTexture(c);
  tex.anisotropy = 4;
  return tex;
}

/** Label shown above the shader-drawn progress bar while the movie buffers. */
function makeLoadingTexture(): THREE.CanvasTexture {
  const c = document.createElement("canvas");
  // same 6.8 : 9.2 canvas as the prompt so glyphs aren't stretched
  c.width = 568;
  c.height = 768;
  const g = c.getContext("2d")!;
  const cx = c.width / 2;
  g.clearRect(0, 0, c.width, c.height);
  g.textAlign = "center";
  g.textBaseline = "middle";

  const WARM = "#fffbe8";
  const FONT = "'Segoe UI', Arial, sans-serif";
  g.fillStyle = WARM;
  g.shadowColor = WARM;
  g.shadowBlur = 3;
  // sits just above the bar band (shader draws it at uv.y ≈ 0.30–0.33)
  (g as CanvasRenderingContext2D & { letterSpacing: string }).letterSpacing = "9px";
  g.font = `600 30px ${FONT}`;
  g.fillText("LOADING AFTERMOVIE", cx + 4, 468);

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
  /** 0..1 while the aftermovie is buffering, null otherwise */
  loadingProgress: number | null;
  /** click handler for the center screen's play prompt */
  onPlay: () => void;
};

export default function LEDScreens({
  videoTexture,
  loadingProgress,
  onPlay,
}: LEDScreensProps): React.ReactElement {
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
    const loadingLabel = makeLoadingTexture();
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
            uLoadLabel: { value: p.hasLogo ? loadingLabel : (blank as THREE.Texture) },
            uLoad: { value: 0 },
            uProgress: { value: 0 },
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

  // bind the shared video texture; the idle↔video blend animates in useFrame
  useEffect(() => {
    if (!videoTexture) return;
    for (const m of materials) m.uniforms.uVideo.value = videoTexture;
  }, [videoTexture, materials]);

  // fade timing: the texture prop now arrives with the first real playback
  // frame, so the wall breathes up almost immediately; exit is quick
  const FADE_DELAY = 0.15;
  const FADE_IN = 1.0;
  const FADE_OUT = 0.35;
  const fade = useRef(0);
  const fadeStartAt = useRef<number | null>(null);

  // latest loading props, readable from useFrame without re-subscribing
  const loadState = useRef({ on: false, progress: 0 });
  useEffect(() => {
    loadState.current.on = loadingProgress !== null;
    if (loadingProgress !== null) loadState.current.progress = loadingProgress;
  }, [loadingProgress]);
  const loadFade = useRef(0);
  const barFill = useRef(0);

  useFrame(({ clock }, delta) => {
    const t = clock.elapsedTime;
    if (videoTexture) {
      if (fadeStartAt.current === null) fadeStartAt.current = t + FADE_DELAY;
      if (t >= fadeStartAt.current) fade.current = Math.min(1, fade.current + delta / FADE_IN);
    } else {
      fadeStartAt.current = null;
      fade.current = Math.max(0, fade.current - delta / FADE_OUT);
    }
    // loading UI eases in/out; the bar glides toward the buffered fraction so
    // chunky progress events still read as one continuous motion
    const ui = loadState.current;
    loadFade.current += ((ui.on ? 1 : 0) - loadFade.current) * Math.min(1, delta * 6);
    barFill.current += (ui.progress - barFill.current) * Math.min(1, delta * 3);
    for (const m of materials) {
      m.uniforms.uTime.value = t;
      m.uniforms.uVideoOn.value = fade.current;
      m.uniforms.uLoad.value = loadFade.current;
      m.uniforms.uProgress.value = barFill.current;
    }
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
            onClick={
              p.hasLogo && !videoTexture && loadingProgress === null ? () => onPlay() : undefined
            }
            onPointerOver={
              p.hasLogo && !videoTexture && loadingProgress === null
                ? () => (gl.domElement.style.cursor = "pointer")
                : undefined
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
