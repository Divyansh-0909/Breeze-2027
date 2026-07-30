"use client";
import React, { Suspense, useEffect, useRef } from "react";
import { Canvas, advance, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";

import { PALETTE } from "../../../components/landing-page/stage3d/palette";
import Stage from "../../../components/landing-page/stage3d/Stage";
import Trusses from "../../../components/landing-page/stage3d/Trusses";
import LEDScreens from "../../../components/landing-page/stage3d/LEDScreens";
import Speakers from "../../../components/landing-page/stage3d/Speakers";
import Lights from "../../../components/landing-page/stage3d/Lights";
import Particles from "../../../components/landing-page/stage3d/Particles";
import Crowd from "../../../components/landing-page/stage3d/Crowd";
import Barricades from "../../../components/landing-page/stage3d/Barricades";
import Effects from "../../../components/landing-page/stage3d/Effects";

/**
 * DEV TOOL — records the travel video the aftermovie page's loading screen
 * plays. Not linked from anywhere; the frame sink it posts to (`/api/rec`)
 * refuses to exist in production.
 *
 * Renders the concert scene with `frameloop="never"` and steps it manually:
 * for each output frame the camera is placed on the scripted crowd-walk path,
 * `advance(t)` renders exactly that instant (driving every clock-based
 * animation — beams, LED shader, particles — deterministically), and the
 * canvas is posted to the sink as a PNG. Render speed is irrelevant, which is
 * the whole point: a software-rendered headless browser can take a second per
 * frame and the output is still a smooth 24 fps.
 *
 * `?mode=sample` renders one frame per second of the path instead, for
 * checking the walk doesn't clip through anyone before paying for a full run.
 *
 * The path: eight seconds at eye height. It opens on open ground BEHIND the
 * crowd (its back row ends at z≈22.5), strides forward into the mass, and
 * covers fifteen metres toward the stage — the walk is a walk, not a sway —
 * settling exactly on the pov composition `CameraRig` rests at, so the
 * recording's last frame IS the live scene's first and the loading screen
 * hands over invisibly.
 */

// 60, not 24: the walk is handheld bob and weave, and 24 fps of that on a
// 60 Hz screen judders no matter how clean the encode is. Recording time
// scales with it — this is the whole-hour run — but it only ever runs here.
const FPS = 60;
const DUR = 8;
const W = 1280;
const H = 720;

/** Where the walk ends — must match CameraRig's pov rest exactly. */
const END = { x: 1.5, y: 1.72, z: 16.8, tx: 0, ty: 5.3, tz: -1, fov: 54 };
/** Where it starts: on the empty ground behind the crowd's back row. */
const START_Z = 32;

function path(t: number): {
  pos: [number, number, number];
  tgt: [number, number, number];
  roll: number;
} {
  const p = THREE.MathUtils.clamp(t / DUR, 0, 1);
  const e = p * p * (3 - 2 * p); // smoothstep: pushes off, settles soft
  const drift = 1 - e; // everything hand-held decays as the walk lands

  return {
    pos: [
      // a light weave — enough to thread shoulders, never enough to read as
      // strafing; the forward stride is the shot. Phases are tuned against
      // the crowd's fixed seed — retune them if the walk ever slices through
      // someone (sample pass shows it as a black blob)
      END.x + 0.9 * drift * Math.cos(t * 1.05 + 0.8) + 0.25 * drift * Math.sin(t * 2.6 + 0.9),
      // walking bob, two beats a second, plus the tiny settle at the end
      END.y - 0.02 * drift + 0.05 * Math.sin(t * 10.5) * (1 - 0.5 * e),
      START_Z - (START_Z - END.z) * e,
    ],
    tgt: [
      // gaze wanders with the weave early, locks to the stage centre late
      END.tx + 0.7 * drift * Math.sin(t * 1.1 + 1.2),
      // eyes come up off the crowd ahead and onto the stage
      2.3 + (END.ty - 2.3) * e,
      END.tz,
    ],
    roll: 0.02 * Math.sin(t * 5.2) * drift,
  };
}

/** Neutral PBR environment, as ConcertStageHero builds it. */
function Env(): null {
  const gl = useThree((s) => s.gl);
  const scene = useThree((s) => s.scene);
  useEffect(() => {
    const pmrem = new THREE.PMREMGenerator(gl);
    const env = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
    scene.environment = env;
    scene.environmentIntensity = 0.1;
    return () => {
      scene.environment = null;
      env.dispose();
      pmrem.dispose();
    };
  }, [gl, scene]);
  return null;
}

/** Steps the scene through the path once everything above it has resolved. */
function Recorder(): null {
  const gl = useThree((s) => s.gl);
  const camera = useThree((s) => s.camera) as THREE.PerspectiveCamera;
  const clock = useThree((s) => s.clock);
  const started = useRef(false);

  useEffect(() => {
    if (started.current) return;
    started.current = true;

    const mode = new URLSearchParams(window.location.search).get("mode");
    const total = FPS * DUR + 1; // inclusive last frame = the exact pov rest
    // sample: one frame per second, to eyeball the path
    // burst: three ADJACENT frames, to prove the show is smooth frame-to-frame
    const indices =
      mode === "sample"
        ? Array.from({ length: DUR + 1 }, (_, k) => k * FPS)
        : mode === "burst"
          ? [2 * FPS, 2 * FPS + 1, 2 * FPS + 2]
          : Array.from({ length: total }, (_, k) => k);

    void (async () => {
      camera.fov = END.fov;
      camera.near = 0.3;
      camera.updateProjectionMatrix();

      // Defensive only — in `frameloop="never"` r3f's render overrides both
      // anyway (see below); this just keeps any stray real-time getDelta
      // call from injecting wall time.
      clock.getDelta = () => 1 / FPS;

      // a dropped POST cost a frame (and truncated the video) once — retry,
      // and only give up on a frame after genuinely trying
      const post = async (body: object) => {
        for (let attempt = 0; attempt < 4; attempt++) {
          try {
            const res = await fetch("/api/rec", {
              method: "POST",
              headers: { "content-type": "application/json" },
              body: JSON.stringify(body),
            });
            if (res.ok) return;
          } catch {
            /* retry */
          }
          await new Promise((r) => setTimeout(r, 300));
        }
      };

      let out = 0;
      for (const i of indices) {
        const t = i / FPS;
        const { pos, tgt, roll } = path(t);
        camera.position.set(...pos);
        camera.lookAt(...tgt);
        camera.rotation.z += roll;
        // SECONDS, not milliseconds: in `frameloop="never"` r3f assigns this
        // timestamp straight into `clock.elapsedTime`, which every animation
        // reads as seconds. Passing ms here put sin(2000·ω) into the beam
        // sweeps — ~15 radians of drift per frame — and the show strobed.
        advance(t);
        const data = gl.domElement.toDataURL("image/png");
        await post({ i: out++, data });
      }
      await post({ done: true });
    })();
  }, [gl, camera, clock]);

  return null;
}

export default function FlythroughRecPage(): React.ReactElement {
  return (
    <main className="min-h-screen bg-black">
      <div style={{ width: W, height: H }}>
        <Canvas
          frameloop="never"
          dpr={1}
          camera={{ fov: END.fov, near: 0.3, far: 150, position: [3.2, 1.7, 26] }}
          // the readback crosses tasks between render and toDataURL, so the
          // buffer must survive compositing
          gl={{ antialias: false, preserveDrawingBuffer: true }}
        >
          <color attach="background" args={[PALETTE.void]} />
          <fog attach="fog" args={[PALETTE.void, 24, 62]} />
          <Suspense fallback={null}>
            <Env />
            <Stage />
            <Barricades />
            {/* immediate: the recorder needs the FULL crowd before its first
                frame — a chunked bake would record people popping in */}
            <Crowd immediate />
            <Trusses />
            {/* prompt VISIBLE, exactly as the live idle stage shows it: the
                recording must match what the visitor lands on — wall
                luminance included — or the crossfade reads as a light change */}
            <LEDScreens videoTexture={null} loading={false} onPlay={() => {}} />
            <Speakers />
            <Lights motion dimmed={false} />
            <Particles />
            <Effects />
            {/* last inside Suspense: must not start stepping frames until
                every model above has actually resolved */}
            <Recorder />
          </Suspense>
        </Canvas>
      </div>
    </main>
  );
}
