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
import { CavernBoundary, WorldSign } from "./HubScene";
import type { ImmersiveRuntime } from "./runtime";

export default function AftermovieScene({ runtime, serial, quality }: { runtime: ImmersiveRuntime; serial: number; quality: number }) {
  const video = useStageVideo();
  const [crowdReady, setCrowdReady] = useState(false);
  const ready = useCallback(() => setCrowdReady(true), []);
  const baked = useCallback((ms: number) => recordPreparation(runtime, "crowd-pose-bake", performance.now() - ms, ms), [runtime]);
  useEffect(() => { runtime.setMovie(video.phase !== "idle"); }, [runtime, video.phase]);
  useEffect(() => {
    runtime.movieActions = { play: video.startMovie, stop: video.stopMovie, sound: video.enableSound, status: video.getStatus };
    return () => { runtime.movieActions = null; };
  }, [runtime, video.startMovie, video.stopMovie, video.enableSound, video.getStatus]);
  return <>
    <color attach="background" args={["#b2bbb9"]} />
    <fog attach="fog" args={["#b2bbb9", 55, 130]} />
    <hemisphereLight args={["#d8e0dd", "#686b59", 0.65]} />
    <CavernBoundary centerZ={-8} />
    <Stage />
    <Trusses /><Speakers /><Barricades />
    <LEDScreens videoTexture={video.phase === "playing" ? video.texture : null} loading={video.phase === "loading"} onPlay={() => { if (runtime.getSnapshot().phase === "local") video.startMovie(); }} />
    <Lights motion={!runtime.reduced} dimmed={video.phase !== "idle"} />
    {/* Already fully covered: yield between poses, without the standalone scene's 150ms pacing gaps. */}
    <Crowd count={quality >= 2 ? 300 : quality === 1 ? 600 : 900} onReady={ready} bakeDelayMs={0} onBake={baked} />
    <Fireworks key={video.pyroKey} active={!runtime.reduced && quality === 0 && video.pyroKey > 0 && video.phase === "playing"} />
    <WorldSign label="GULLYVERSE  →" position={[0, 2.8, 27.8]} rotation={[0, Math.PI, 0]} />
    {crowdReady && ["boot", "covered", "recovering"].includes(runtime.getSnapshot().phase) && <ReadinessGate key={serial} runtime={runtime} serial={serial} />}
  </>;
}
