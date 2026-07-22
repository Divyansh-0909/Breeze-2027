"use client";
import React, { useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

/**
 * Front-facing cinematic camera: locked head-on to the stage with gentle
 * mouse parallax and a slow vertical breathe, frame-rate-independent damping.
 * With `motion` false (prefers-reduced-motion) the camera holds a fixed
 * composition and only eases to it once.
 * With `focus` true (aftermovie playing) it glides in toward the LED wall
 * and calms the parallax so the video is the frame.
 */
export default function CameraRig({
  motion,
  focus,
}: {
  motion: boolean;
  focus: boolean;
}): React.ReactElement | null {
  const target = useMemo(() => new THREE.Vector3(0, 5.6, -1), []);
  const desiredTarget = useMemo(() => new THREE.Vector3(), []);
  const desired = useMemo(() => new THREE.Vector3(), []);

  useFrame((state, dt) => {
    const t = motion ? state.clock.elapsedTime : 0;
    const px = motion ? state.pointer.x : 0;
    const py = motion ? state.pointer.y : 0;

    if (focus) {
      // zoomed composition: closer to the LED wall, parallax nearly frozen
      const azimuth = px * 0.015;
      const radius = 17;
      desired.set(Math.sin(azimuth) * radius, 5.9 + py * 0.25, Math.cos(azimuth) * radius);
      desiredTarget.set(0, 5.9, -2.5);
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
  });

  return null;
}
