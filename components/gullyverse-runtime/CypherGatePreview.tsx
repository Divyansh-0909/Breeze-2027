"use client";

import React, { useEffect, useRef, useState, useSyncExternalStore } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { AgXToneMapping, Color, Euler, PerspectiveCamera } from "three";
import { useImmersiveInput } from "../immersive/input";
import { ReadinessGate, SceneRenderer } from "../immersive/rendering";
import { ImmersiveRuntime } from "../immersive/runtime";
import { BakedAssetPool, type BakedAsset } from "./baked-assets";
import { createCypherSpace } from "./cypher-space";
import { mountSponsorDisplay } from "./sponsor-display";
import walkSpace from "./cypher-walk-space.json";

const gate = createCypherSpace({ start: 1.5, end: 21.5, halfWidth: 5.5, spawnY: 2.2, spawnPitch: 0.27 });
const assetRoot = "/models/gullyverse/locked-rev15z-cypher-";
const zoneAt = (z: number) => z < -15.65 ? "Cypher forecourt" : z < -11.4 ? "Cypher gate" : "Navigation approach";

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
  const [pool] = useState(() => new BakedAssetPool(gl));
  const [assets, setAssets] = useState<BakedAsset[]>();
  const display = useRef<Awaited<ReturnType<typeof mountSponsorDisplay>> | undefined>(undefined);
  const state = useSyncExternalStore(runtime.subscribe, runtime.getSnapshot, runtime.getSnapshot);
  const euler = useRef(new Euler(0, 0, 0, "YXZ"));
  const zone = useRef(zoneAt(runtime.pose.z));

  useEffect(() => {
    const abort = new AbortController();
    const releases = new Set<() => void>();
    const releaseAll = () => {
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
      const [gateAsset, approach] = await Promise.all([
        loadChunk(assetRoot + "gate/"),
        loadChunk(assetRoot + "approach/"),
      ]);
      abort.signal.throwIfAborted();
      const led = await mountSponsorDisplay(approach.scene, assetRoot + "approach/sponsor-led.png", abort.signal);
      if (abort.signal.aborted) { led.dispose(); return; }
      display.current = led;
      setAssets([gateAsset, approach]);
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

function GateWalk() {
  const [runtime] = useState(() => new ImmersiveRuntime("hub", undefined, false, undefined, gate.space));
  const [zone, setZone] = useState(() => zoneAt(runtime.pose.z));
  const state = useSyncExternalStore(runtime.subscribe, runtime.getSnapshot, runtime.getSnapshot);
  const curtain = useRef<HTMLDivElement>(null);
  useImmersiveInput(runtime);
  const ready = state.phase === "local";
  return <>
    <div className="native-canvas">
      <Canvas dpr={1} gl={{ antialias: true, powerPreference: "high-performance" }}
        camera={{ near: 0.05, far: 120 }} fallback={<p>3D is unavailable in this browser.</p>}>
        <GateScene runtime={runtime} curtain={curtain} reportZone={setZone} />
      </Canvas>
    </div>
    <div className="native-curtain" ref={curtain} aria-hidden="true" />
    {ready && <section className="native-controls gate-controls" aria-label="Walk through the cypher gate">
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
    {!ready && <div className="native-loading" role="status">
      <p>{state.error ?? (state.phase === "context-lost" || state.phase === "recovering"
        ? "Restoring 3D…" : "Loading the cypher gate…")}</p>
      {state.error && <a href="/events">Browse events</a>}
    </div>}
  </>;
}

export default function CypherGatePreview() {
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
      <GateWalk />
    </CanvasBoundary>}
    {status === "unavailable" && <div className="native-loading" role="status">
      <p>3D is unavailable in this browser.</p>
      <a href="/events">Browse events</a>
    </div>}
  </div>;
}
