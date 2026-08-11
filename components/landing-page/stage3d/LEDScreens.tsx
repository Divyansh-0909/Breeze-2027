"use client";
import React, { useEffect, useMemo, useRef } from "react";
import { useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { PALETTE, STAGE } from "./palette";

/**
 * The signature element: a 3-panel LED wall — one wide center screen
 * flanked by a single smaller panel per side.
 *
 * Three modes:
 * - idle: shader content (waves + scanlines + glitch bars); the center screen
 *   invites "RELIVE THE NIGHT — BREEZE '26" and is clickable.
 * - loading: the center screen swaps the prompt for a "LOADING..." label
 *   with a spinner above it (download progress isn't reliably measurable,
 *   so the treatment is indeterminate on purpose).
 * - video: all 3 panels become one segmented video wall — each panel samples
 *   its slice of ONE shared VideoTexture (single GPU upload per frame),
 *   width-fit across the combined wall, vertically center-cropped.
 */

/** Panel geometry, in world units. The center screen carries the prompt. */
const CENTER_W = 13.6;
const CENTER_H = 9.2;
const SIDE_W = 4.0;
const SIDE_H = 7.2;
const GAP = 0.4;

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
  uniform sampler2D uVideo;
  uniform float uVideoOn;
  uniform vec2 uUvOffset;
  uniform vec2 uUvRepeat;
  uniform vec2 uPanelSize;

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

      // ---- loading state: "LOADING..." label with a spinner above it, in
      // the same warm truss-light voice as the prompt ----
      vec4 lbl = texture2D(uLoadLabel, uv);
      idle += lbl.rgb * (1.05 + 0.15 * sin(uTime * 1.8)) * lbl.a * uLoad;
      // spinner: rotating arc with a fading tail; uv scaled by the panel's
      // world size so the ring is a true circle
      vec2 sp = (uv - vec2(0.5, 0.49)) * uPanelSize;
      float ring = smoothstep(0.10, 0.05, abs(length(sp) - 0.45));
      float ang = atan(sp.y, sp.x) / 6.2831853; // -0.5..0.5 around the ring
      float sweep = fract(ang - uTime * 0.7);
      float arc = smoothstep(0.0, 0.35, sweep) * step(sweep, 0.8); // 20% gap
      vec3 warm = vec3(1.0, 0.984, 0.91);
      idle += warm * ring * arc * uLoad;
    }
    idle *= mix(0.35, 1.0, edge);

    // ---- video layer: this panel's slice of the shared video, rendered as
    // a physical LED matrix (pixel cells + grout + shimmer) ----
    vec2 wallUv = uUvOffset + uv * uUvRepeat; // continuous across all panels
    const vec2 RES = vec2(336.0, 189.0);      // square LED cells wall-wide
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
  // matches the center panel's aspect so glyphs aren't stretched
  c.height = 768;
  c.width = Math.round((768 * CENTER_W) / CENTER_H);
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

/** Label shown under the shader-drawn spinner while the movie buffers. */
function makeLoadingTexture(): THREE.CanvasTexture {
  const c = document.createElement("canvas");
  // same aspect as the prompt canvas so glyphs aren't stretched
  c.height = 768;
  c.width = Math.round((768 * CENTER_W) / CENTER_H);
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
  // sits just below the spinner (shader draws it centered at uv.y ≈ 0.49)
  (g as CanvasRenderingContext2D & { letterSpacing: string }).letterSpacing = "9px";
  g.font = `600 30px ${FONT}`;
  g.fillText("LOADING...", cx + 4, 468);

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
  /** true while the aftermovie is buffering — center screen shows the spinner */
  loading: boolean;
  /** click handler for the center screen's play prompt */
  onPlay: () => void;
  /** hide the centre panel's play prompt — for shots where the wall is
   *  scenery (the flythrough recording) rather than an invitation */
  promptless?: boolean;
};

export default function LEDScreens({
  videoTexture,
  loading,
  onPlay,
  promptless = false,
}: LEDScreensProps): React.ReactElement {
  const { topY, screenZ } = STAGE;
  const gl = useThree((s) => s.gl);

  const panels = useMemo<Panel[]>(() => {
    const out: Panel[] = [
      { x: 0, w: CENTER_W, h: CENTER_H, rotY: 0, hasLogo: true, seed: 0.5 },
    ];
    const x = CENTER_W / 2 + GAP + SIDE_W / 2;
    for (const side of [-1, 1]) {
      out.push({
        x: x * side,
        w: SIDE_W,
        h: SIDE_H,
        rotY: -side * 0.06, // subtle fan, flanks turn toward camera
        hasLogo: false,
        seed: 0.17 + (side + 1) * 0.31,
      });
    }
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
            uHasLogo: { value: p.hasLogo && !promptless ? 1 : 0 },
            uLoadLabel: { value: p.hasLogo ? loadingLabel : (blank as THREE.Texture) },
            uLoad: { value: 0 },
            uVideo: { value: blank as THREE.Texture },
            uVideoOn: { value: 0 },
            uUvOffset: { value: videoWindows[i].offset },
            uUvRepeat: { value: videoWindows[i].repeat },
            uPanelSize: { value: new THREE.Vector2(p.w, p.h) },
          },
        })
    );
  }, [panels, videoWindows, promptless]);

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

  // latest loading prop, readable from useFrame without re-subscribing
  const loadingRef = useRef(loading);
  useEffect(() => {
    loadingRef.current = loading;
  }, [loading]);
  const loadFade = useRef(0);

  useFrame(({ clock }, delta) => {
    const t = clock.elapsedTime;
    if (videoTexture) {
      if (fadeStartAt.current === null) fadeStartAt.current = t + FADE_DELAY;
      if (t >= fadeStartAt.current) fade.current = Math.min(1, fade.current + delta / FADE_IN);
    } else {
      fadeStartAt.current = null;
      fade.current = Math.max(0, fade.current - delta / FADE_OUT);
    }
    // loading UI (spinner + label) eases in/out; the spin itself runs on uTime
    loadFade.current += ((loadingRef.current ? 1 : 0) - loadFade.current) * Math.min(1, delta * 6);
    for (const m of materials) {
      m.uniforms.uTime.value = t;
      m.uniforms.uVideoOn.value = fade.current;
      m.uniforms.uLoad.value = loadFade.current;
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
            onClick={p.hasLogo && !videoTexture && !loading ? () => onPlay() : undefined}
            onPointerOver={
              p.hasLogo && !videoTexture && !loading
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
