"use client";
import React from "react";
import { EffectComposer, Bloom, Vignette, SMAA } from "@react-three/postprocessing";

/**
 * Restrained post stack: one mipmap bloom (LED wall, strips and beams sit
 * above the threshold; the dark set stays clean) + a light vignette.
 * AA note: SMAA (post-process) instead of composer MSAA — multisampled
 * half-float framebuffers flicker/black-frame on some Windows ANGLE drivers.
 */
export default function Effects(): React.ReactElement {
  return (
    <EffectComposer multisampling={0}>
      <SMAA />
      <Bloom mipmapBlur intensity={0.68} luminanceThreshold={0.32} luminanceSmoothing={0.35} radius={0.75} />
      <Vignette eskil={false} offset={0.18} darkness={0.55} />
    </EffectComposer>
  );
}
