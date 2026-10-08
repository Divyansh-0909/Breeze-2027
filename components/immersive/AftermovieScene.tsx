"use client";
import { useCallback, useEffect, useState } from "react";
import Stage from "@/components/landing-page/stage3d/Stage";
import Trusses from "@/components/landing-page/stage3d/Trusses";
import Speakers from "@/components/landing-page/stage3d/Speakers";
import LEDScreens from "@/components/landing-page/stage3d/LEDScreens";
import Lights from "@/components/landing-page/stage3d/Lights";
import Crowd from "@/components/landing-page/stage3d/Crowd";
import Barricades from "@/components/landing-page/stage3d/Barricades";
import Fireworks from "@/components/landing-page/stage3d/Fireworks";
import { useStageVideo } from "@/components/landing-page/stage3d/useStageVideo";
import { ReadinessGate } from "./rendering";
import { recordPreparation } from "./diagnostics";
import HubScene from "./HubScene";
import { point3, world } from "./world";
import type { ImmersiveRuntime } from "./runtime";

export default function AftermovieScene({ runtime, serial, quality, nearStage, overview }: { runtime: ImmersiveRuntime; serial: number; quality: number; nearStage: boolean; overview: boolean }) {
  const video = useStageVideo();
  const [crowdReadySerial, setCrowdReadySerial] = useState<number | null>(null);
  const ready = useCallback(() => setCrowdReadySerial(serial), [serial]);
  const baked = useCallback((ms: number) => recordPreparation(runtime, "crowd-pose-bake", performance.now() - ms, ms), [runtime]);
  useEffect(() => { runtime.setMovie(video.phase !== "idle"); }, [runtime, video.phase]);
  useEffect(() => {
    runtime.movieActions = { play: video.startMovie, stop: video.stopMovie, sound: video.enableSound, status: video.getStatus };
    return () => { runtime.movieActions = null; };
  }, [runtime, video.startMovie, video.stopMovie, video.enableSound, video.getStatus]);
  return <>
    <HubScene nearStage={nearStage} quality={quality} overview={overview} />
    {/* One original stage in the shared world. Navigation changes interaction/crowd detail. */}
    <group position={point3(world.stage.origin)} rotation-y={world.stage.yaw}>
    <Stage ground={false} />
    <Trusses /><Speakers /><Barricades />
    <LEDScreens videoTexture={video.phase === "playing" ? video.texture : null} loading={video.phase === "loading"} onPlay={() => { const state = runtime.getSnapshot(); if (nearStage && state.phase === "local" && !state.map && !state.destinationMenu) video.startMovie(); }} />
    <Lights motion={nearStage && !runtime.reduced} dimmed={video.phase !== "idle"} />
    {/* Already fully covered: yield between poses, without the standalone scene's 150ms pacing gaps. */}
    {nearStage && <Crowd clearApproach count={quality >= 2 ? 300 : quality === 1 ? 600 : 900} onReady={ready} bakeDelayMs={0} onBake={baked} />}
    <Fireworks key={video.pyroKey} active={!runtime.reduced && quality === 0 && video.pyroKey > 0 && video.phase === "playing"} />
    </group>
    {(!nearStage || crowdReadySerial === serial) && ["boot", "covered", "recovering"].includes(runtime.getSnapshot().phase) && <ReadinessGate key={serial} runtime={runtime} serial={serial} />}
  </>;
}
