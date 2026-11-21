"use client";

import React, { lazy, Suspense, useEffect, useRef, useState, useSyncExternalStore } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { AgXToneMapping, Color, Euler, PerspectiveCamera } from "three";
import { useImmersiveInput } from "../immersive/input";
import { ReadinessGate, SceneRenderer } from "../immersive/rendering";
import { ImmersiveRuntime } from "../immersive/runtime";
import { world } from "../immersive/world";
import { BakedAssetPool, type BakedAsset } from "./baked-assets";
import { createCypherSpace } from "./cypher-space";
import { mountSponsorDisplay } from "./sponsor-display";
import { mountMarketLamps } from "./market-lamps";
import walkSpace from "./cypher-walk-space.json";

const routeBounds = { start: -29.5, end: 47.6, halfWidth: 16, plaza: true };
const market = createCypherSpace({ ...routeBounds, spawnY: -27.6 });
const approach = createCypherSpace({ ...routeBounds, spawnY: 2.2, spawnPitch: 0.27 });
const plaza = createCypherSpace({ ...routeBounds, spawnY: 19.3, spawnPitch: 0.08 });
const assetRoot = "/models/gullyverse/locked-rev15z-";
const QuarryArrivalScene = lazy(() => import("./QuarryArrivalScene"));
type Start = "quarry" | "market" | "approach" | "plaza";
const zoneAt = (z: number) => {
  if (z < -22) return "Cypher plaza";
  if (z < -15.65) return "Cypher forecourt";
  if (z < -11.4) return "Cypher gate";
  if (z < -1.5) return "Navigation approach";
  return "Market lane";
};

class CanvasBoundary extends React.Component<{ children: React.ReactNode; onFailure(): void }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidCatch() { this.props.onFailure(); }
  render() { return this.state.failed ? null : this.props.children; }
}

function GateScene({ runtime, curtain, reportZone }: {
  runtime: ImmersiveRuntime;
  curtain: React.RefObject<HTMLDivElement | null>;
  reportZone(zone: ReturnType<typeof zoneAt>): void;
}) {
  const { gl, scene, camera, size } = useThree();
  const [pool] = useState(() => new BakedAssetPool(gl, 1));
  const [assets, setAssets] = useState<BakedAsset[]>();
  const display = useRef<Awaited<ReturnType<typeof mountSponsorDisplay>> | undefined>(undefined);
  const lamps = useRef<ReturnType<typeof mountMarketLamps> | undefined>(undefined);
  const state = useSyncExternalStore(runtime.subscribe, runtime.getSnapshot, runtime.getSnapshot);
  const euler = useRef(new Euler(0, 0, 0, "YXZ"));
  const zone = useRef(zoneAt(runtime.pose.z));

  useEffect(() => {
    const abort = new AbortController();
    const releases = new Set<() => void>();
    const releaseAll = () => {
      lamps.current?.dispose();
      lamps.current = undefined;
      display.current?.dispose();
      display.current = undefined;
      releases.forEach(release => release());
      releases.clear();
    };
    const mobile = window.matchMedia("(max-width: 699px)").matches;
    async function loadChunk(base: string) {
      const response = await fetch(base + "manifest.json", { signal: abort.signal });
      if (!response.ok) throw new Error("The cypher assets are unavailable.");
      const { source, bake } = await response.json();
      if (source?.sha256 !== walkSpace.sourceSHA256 || !Number.isFinite(bake?.range) || bake.range <= 0) {
        throw new Error("The cypher geometry and walking space have different versions.");
      }
      abort.signal.throwIfAborted();
      const lease = pool.acquire(base, mobile, bake);
      releases.add(lease.release);
      try {
        return await lease.promise;
      } catch {
        lease.release();
        releases.delete(lease.release);
        abort.signal.throwIfAborted();
        const fallback = pool.acquire(base, mobile, bake, true);
        releases.add(fallback.release);
        return fallback.promise;
      }
    }
    async function load() {
      const [gateAsset, signAsset, south, north, plazaAsset, audience] = await Promise.all([
        loadChunk(assetRoot + "cypher-gate/"),
        loadChunk(assetRoot + "cypher-approach/"),
        loadChunk(assetRoot + "market-south/"),
        loadChunk(assetRoot + "market-north/"),
        loadChunk(assetRoot + "cypher-plaza/"),
        loadChunk(assetRoot + "cypher-audience/"),
      ]);
      abort.signal.throwIfAborted();
      const led = await mountSponsorDisplay(signAsset.scene, assetRoot + "cypher-approach/sponsor-led.png", abort.signal);
      if (abort.signal.aborted) { led.dispose(); return; }
      display.current = led;
      lamps.current = mountMarketLamps([south.scene, north.scene]);
      setAssets([gateAsset, signAsset, south, north, plazaAsset, audience]);
    }
    void load().catch(() => {
      if (!abort.signal.aborted) runtime.fail("The cypher preview could not load.");
      abort.abort();
      releaseAll();
    });
    return () => { abort.abort(); releaseAll(); };
  }, [pool, runtime]);

  useEffect(() => {
    gl.toneMapping = AgXToneMapping;
    gl.toneMappingExposure = Math.pow(2, 0.25);
    scene.background = new Color("#010303");
    const lost = (event: Event) => { event.preventDefault(); runtime.loseContext(); };
    const restored = () => runtime.restoreContext();
    gl.domElement.addEventListener("webglcontextlost", lost);
    gl.domElement.addEventListener("webglcontextrestored", restored);
    return () => {
      gl.domElement.removeEventListener("webglcontextlost", lost);
      gl.domElement.removeEventListener("webglcontextrestored", restored);
    };
  }, [gl, scene, runtime]);

  useFrame((_, delta) => {
    runtime.tick(delta);
    if (!runtime.reduced) display.current?.advance(runtime.activeFrameDelta);
    lamps.current?.advance(runtime.activeFrameDelta, runtime.reduced);
    const view = runtime.cameraPose(size.width / size.height);
    camera.position.set(view.x, view.y, view.z);
    camera.quaternion.setFromEuler(euler.current.set(view.pitch, view.yaw, 0, "YXZ"));
    if (camera instanceof PerspectiveCamera && camera.fov !== view.fov) {
      camera.fov = view.fov;
      camera.updateProjectionMatrix();
    }
    if (curtain.current) curtain.current.style.opacity = String(runtime.revealOpacity);
    const current = zoneAt(runtime.pose.z);
    if (current !== zone.current) {
      zone.current = current;
      reportZone(current);
    }
  }, -1);

  return <>
    {assets && <>
      {assets.map((asset, index) => <primitive key={index} object={asset.scene} />)}
      <ReadinessGate key={state.serial} runtime={runtime} serial={state.serial} />
    </>}
    <SceneRenderer runtime={runtime} />
  </>;
}

function GateWalk({ start }: { start: Start }) {
  const curtain = useRef<HTMLDivElement>(null);
  const holdCurtain = useRef(false);
  const [atMarket, setAtMarket] = useState(start !== "quarry");
  const [marketRuntime] = useState(() => new ImmersiveRuntime("hub", undefined, false, undefined,
    (start === "approach" ? approach : start === "plaza" ? plaza : market).space));
  const [quarry] = useState(() => start === "quarry" ? new ImmersiveRuntime("hub", () => {
    holdCurtain.current = true;
    setAtMarket(true);
  }, true, () => performance.now() / 1000) : null);
  const activeQuarry = atMarket ? null : quarry;
  const runtime = activeQuarry ?? marketRuntime;
  const [zone, setZone] = useState(() => zoneAt(marketRuntime.pose.z));
  const state = useSyncExternalStore(runtime.subscribe, runtime.getSnapshot, runtime.getSnapshot);
  useImmersiveInput(runtime);
  const walking = atMarket && state.phase === "local";
  const landing = !!activeQuarry && state.phase === "landing";
  return <>
    <div className="native-canvas" data-world={activeQuarry ? "quarry" : "market"} data-phase={state.phase}>
      <Canvas dpr={1} gl={{ antialias: true, powerPreference: "high-performance" }}
        camera={start === "quarry" ? world.camera : { near: 0.05, far: 120 }} fallback={<p>3D is unavailable in this browser.</p>}>
        {activeQuarry ? <Suspense fallback={null}>
          <QuarryArrivalScene runtime={activeQuarry} curtain={curtain} holdCurtain={holdCurtain} />
        </Suspense> : <GateScene runtime={marketRuntime} curtain={curtain} reportZone={setZone} />}
      </Canvas>
    </div>
    <div className="native-curtain" ref={curtain} aria-hidden="true" />
    {landing && <div className="native-controls"><button onClick={() => runtime.enter()}>Enter Gullyverse</button></div>}
    {walking && <section className="native-controls gate-controls" aria-label="Walk through the cypher gate">
      <div className="gate-toolbar">
        <p aria-live="polite">{zone}</p>
        <button onClick={() => runtime.setMap(!state.map)}>{state.map ? "Close map" : "Map"}</button>
      </div>
      {!state.map && <>
        <small>WASD or arrows to walk. Drag to look.</small>
        <div className="native-touch" aria-label="Movement controls">
          <button data-move="forward" aria-label="Walk forward">↑</button>
          <div>
            <button data-move="left" aria-label="Walk left">←</button>
            <button data-move="back" aria-label="Walk backward">↓</button>
            <button data-move="right" aria-label="Walk right">→</button>
          </div>
        </div>
      </>}
    </section>}
    {!walking && !landing && state.phase !== "entrance" && <div className="native-loading" role="status">
      <p>{state.error ?? (state.phase === "context-lost" || state.phase === "recovering"
        ? "Restoring 3D…" : activeQuarry ? "Loading the quarry…" : "Loading the market lane…")}</p>
      {state.error && <a href="/events">Browse events</a>}
    </div>}
  </>;
}

export default function CypherGatePreview({ start = "market" }: { start?: Start }) {
  const [status, setStatus] = useState<"checking" | "ready" | "unavailable">("checking");
  useEffect(() => {
    try {
      const context = document.createElement("canvas").getContext("webgl2");
      setStatus(context ? "ready" : "unavailable");
      context?.getExtension("WEBGL_lose_context")?.loseContext();
    } catch {
      setStatus("unavailable");
    }
  }, []);
  return <div className="native-journey">
    <header className="native-header"><a href="/">BREEZE <span>2027</span></a></header>
    {status === "ready" && <CanvasBoundary onFailure={() => setStatus("unavailable")}>
      <GateWalk start={start} />
    </CanvasBoundary>}
    {status === "unavailable" && <div className="native-loading" role="status">
      <p>3D is unavailable in this browser.</p>
      <a href="/events">Browse events</a>
    </div>}
  </div>;
}
