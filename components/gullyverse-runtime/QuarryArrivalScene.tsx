"use client";

import { useEffect, useState, useSyncExternalStore, type RefObject } from "react";
import AftermovieScene from "../immersive/AftermovieScene";
import { CaveEntranceSession } from "../immersive/CaveEntranceSession";
import { FrameController, SceneRenderer } from "../immersive/rendering";
import type { ImmersiveRuntime } from "../immersive/runtime";

export default function QuarryArrivalScene({ runtime, curtain, holdCurtain }: {
  runtime: ImmersiveRuntime;
  curtain: RefObject<HTMLDivElement | null>;
  holdCurtain: RefObject<boolean>;
}) {
  const [session] = useState(() => new CaveEntranceSession(runtime));
  const state = useSyncExternalStore(runtime.subscribe, runtime.getSnapshot, runtime.getSnapshot);
  useEffect(() => {
    session.retainOwner();
    void session.load();
    return () => session.releaseOwner();
  }, [session]);

  return <>
    <FrameController runtime={runtime} curtain={curtain} holdCurtain={holdCurtain} />
    <SceneRenderer runtime={runtime} wallPreview={session} />
    <AftermovieScene runtime={runtime} serial={state.serial} quality={state.quality}
      nearStage={false} overview={false} wallPreview={session} />
  </>;
}
