"use client";
import React, { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

/**
 * Front-facing cinematic camera: locked head-on to the stage with gentle
 * mouse parallax and a slow vertical breathe, frame-rate-independent damping.
 * With `motion` false (prefers-reduced-motion) the camera holds a fixed
 * composition and only eases to it once.
 * With `focus` true (aftermovie playing) it glides in toward the LED wall
 * and calms the parallax so the video is the frame.
 * With `pov` true the resting shot is IN the crowd instead of above it:
 * eye height, just off the runway with people on every side, looking up at
 * the stage — the composition the travel overlay's push-through-the-crowd
 * footage hands over to. A wider lens here on purpose: close quarters read
 * as close quarters only when the perspective stretches like a phone camera.
 * `focus` still wins — pressing play dollies out of the crowd to the wall.
 */
export default function CameraRig({
  motion,
  focus,
  pov = false,
}: {
  motion: boolean;
  focus: boolean;
  pov?: boolean;
}): React.ReactElement | null {
  const target = useMemo(() => new THREE.Vector3(0, 5.6, -1), []);
  const desiredTarget = useMemo(() => new THREE.Vector3(), []);
  const desired = useMemo(() => new THREE.Vector3(), []);
  const snapped = useRef(false);

  useFrame((state, dt) => {
    const t = motion ? state.clock.elapsedTime : 0;
    const px = motion ? state.pointer.x : 0;
    const py = motion ? state.pointer.y : 0;
    const cam = state.camera as THREE.PerspectiveCamera;

    // pov starts AT the rest pose, not easing down into it: the Canvas's
    // initial camera is the wide shot, and lerping from there reads as a
    // crane move from above right after the travel video ends. First frame
    // snaps, every frame after damps as usual.
    if (pov && !snapped.current) {
      snapped.current = true;
      cam.position.set(1.5, 1.72, 16.8);
      target.set(0, 5.3, -1);
      cam.fov = 54;
      cam.updateProjectionMatrix();
      cam.lookAt(target);
      return;
    }

    if (focus) {
      // zoomed composition: closer to the LED wall, parallax nearly frozen
      const azimuth = px * 0.015;
      const radius = 17;
      desired.set(Math.sin(azimuth) * radius, 5.9 + py * 0.25, Math.cos(azimuth) * radius);
      desiredTarget.set(0, 5.9, -2.5);
    } else if (pov) {
      // standing in the crowd, a step right of the runway (the corridor the
      // Crowd generator keeps clear), heads all around, stage up ahead.
      // Parallax is a head-turn, not a dolly — you're shoulder to shoulder.
      desired.set(
        1.5 + px * 0.35,
        1.72 + py * 0.18 + Math.sin(t * 0.5) * 0.05,
        16.8 + Math.sin(t * 0.13) * 0.15
      );
      desiredTarget.set(px * 1.6, 5.3 + py * 0.8, -1);
    } else {
      // front-facing composition: no orbit, gentle mouse parallax + breathing
      const azimuth = Math.sin(t * 0.08) * 0.02 + px * 0.05;
      const radius = 26.5;
      desired.set(
        Math.sin(azimuth) * radius,
        6.0 + py * 0.9 + Math.sin(t * 0.11) * 0.18,
        Math.cos(azimuth) * radius
      );
      desiredTarget.set(0, 5.6, -1);
    }

    // exp damping: identical feel at any frame rate; the target eases too,
    // so entering/leaving focus is one smooth dolly move
    const k = 1 - Math.exp(-2.2 * dt);
    state.camera.position.lerp(desired, k);
    target.lerp(desiredTarget, k);
    state.camera.lookAt(target);

    // the lens eases with the move, so pov ↔ focus is one continuous shot
    const wantFov = focus ? 42 : pov ? 54 : 42;
    if (Math.abs(cam.fov - wantFov) > 0.05) {
      cam.fov += (wantFov - cam.fov) * k;
      cam.updateProjectionMatrix();
    }
  });

  return null;
}
