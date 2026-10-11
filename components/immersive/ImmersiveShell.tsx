"use client";
import React, { Component, lazy, Suspense, useEffect, useRef, useState, useSyncExternalStore } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { Canvas } from "@react-three/fiber";
import { point3, world } from "./world";
import { FrameController, SceneRenderer, QUALITY_DPR } from "./rendering";
import { ImmersiveRuntime } from "./runtime";
import { enteredGullyverse, initialNavigation, immersiveHref, rememberGullyverseEntry, locationFromPath, locations } from "./navigation";
import { useImmersiveInput } from "./input";
import WorldOverlays, { MapMarkerProjection, type MapDOM } from "./WorldOverlays";
import { activeDeadline } from "./activeDeadline";
import styles from "./immersive.module.css";

const AftermovieScene = lazy(() => import("./AftermovieScene"));
const infoLinks = [["Events", "/events"], ["Team", "/team"], ["Contact us", "/get-in-touch"], ["Past sponsors", "/sponsors"], ["Merch", "/merch"]];

function InformationLinks() {
  return <nav aria-label="Festival information" className={styles.infoLinks}>{infoLinks.map(([label, href]) => <Link key={href} href={href}>{label}</Link>)}</nav>;
}
function Fallback({ error }: { error?: string }) {
  return <section className={styles.fallback} aria-label="Festival without 3D">
    <p>BREEZE 2027 / GULLYVERSE</p><h1>The festival is still here.</h1>
    <p>{error ? "The immersive view could not load. You can watch the Aftermovie and access festival information here." : "Watch the Aftermovie and explore festival information."}</p>
    <video controls playsInline preload="none" src="/after-movie.mp4" aria-label="Breeze Aftermovie" />
    <InformationLinks /><button onClick={() => window.location.reload()}>Reload immersive experience</button>
  </section>;
}
class SceneBoundary extends Component<{ children: React.ReactNode; onError: (message: string) => void }, { failed: boolean }> {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  componentDidCatch(error: Error) { this.props.onError(error.message); }
  render() { return this.state.failed ? null : this.props.children; }
}

export default function ImmersiveShell() {
  const pathname = usePathname();
  const router = useRouter();
  const [runtime] = useState(() => {
    const entry = initialNavigation(pathname, window.location.search, window.history.state, enteredGullyverse());
    return new ImmersiveRuntime(entry.location, (id, source, entrance) => {
      if (!entrance) rememberGullyverseEntry();
      if (source !== "url" && (locationFromPath(window.location.pathname) !== id || entrance)) {
        const href = immersiveHref(id, entrance);
        const diagnostic = new URLSearchParams(window.location.search).has("diagnostics");
        window.history.pushState({ ...window.history.state, breezeArrival: entrance ? "entrance" : id }, "", href + (diagnostic ? (href.includes("?") ? "&" : "?") + "diagnostics" : ""));
      } else if (id === "hub" && !entrance) {
        window.history.replaceState({ ...window.history.state, breezeArrival: "hub" }, "", window.location.href);
      }
    }, entry.intro, () => performance.now() / 1000);
  });
  const state = useSyncExternalStore(runtime.subscribe, runtime.getSnapshot, runtime.getSnapshot);
  const curtain = useRef<HTMLDivElement>(null);
  const [mapElements] = useState<MapDOM>(() => ({ container: null, nodes: new Map(), dots: new Map(), lines: new Map() }));
  const [flat, setFlat] = useState(false);
  useImmersiveInput(runtime);
  useEffect(() => {
    runtime.onCoveredRoute = href => router.push(href);
    return () => { runtime.onCoveredRoute = null; };
  }, [runtime, router]);
  useEffect(() => {
    const destination = locationFromPath(pathname);
    if (destination && destination !== runtime.getSnapshot().destination) runtime.request(destination, "url");
  }, [pathname, runtime]);
  useEffect(() => {
    // Native popstate can supersede an in-flight journey even before Next rerenders.
    const onPop = () => { const id = locationFromPath(window.location.pathname); if (id) runtime.request(id, "url"); };
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, [runtime]);
  useEffect(() => {
    if (!["boot", "covered", "context-lost", "recovering"].includes(state.phase)) return;
    // A timeout never reveals unfinished content; it offers the 2D fallback.
    const deadline = activeDeadline(45000, () => runtime.fail("Critical scene preparation exceeded 45 seconds."));
    const suspend = () => deadline.pause();
    const resume = () => { if (!document.hidden) deadline.resume(); };
    const visibility = () => document.hidden ? suspend() : resume();
    if (!runtime.suspended && !document.hidden) deadline.resume();
    window.addEventListener("blur", suspend); window.addEventListener("focus", resume);
    document.addEventListener("visibilitychange", visibility); document.addEventListener("freeze", suspend); document.addEventListener("resume", resume);
    return () => {
      deadline.cancel(); window.removeEventListener("blur", suspend); window.removeEventListener("focus", resume);
      document.removeEventListener("visibilitychange", visibility); document.removeEventListener("freeze", suspend); document.removeEventListener("resume", resume);
    };
  }, [state.phase, state.serial, runtime]);
  useEffect(() => {
    if (window.matchMedia("(pointer: coarse)").matches) runtime.setQuality(1);
  }, [runtime]);
  const local = state.phase === "local";
  if (flat || state.phase === "error") return <div className={styles.shell} data-phase={state.phase}><Fallback error={state.error ?? undefined} /></div>;
  return <section className={styles.shell} data-phase={state.phase} data-location={state.scene} data-inspection={state.inspection ?? undefined} data-map-stage={state.mapStage ?? undefined} data-destination-menu={state.destinationMenu || undefined} aria-label="Gullyverse immersive experience">
    <SceneBoundary onError={(message) => runtime.fail(message)}>
      <Canvas dpr={Math.min(window.devicePixelRatio, QUALITY_DPR[state.quality])} camera={{ ...world.camera, position: point3(world.landing.position) }} gl={{ antialias: false, powerPreference: "high-performance" }} fallback={<Fallback error="WebGL2 unavailable" />}>
        <FrameController runtime={runtime} curtain={curtain} />
        <MapMarkerProjection runtime={runtime} elements={mapElements} />
        <SceneRenderer runtime={runtime} />
        <Suspense fallback={null}>
          <AftermovieScene runtime={runtime} serial={state.serial} quality={state.quality} nearStage={state.scene === "aftermovie"} overview={state.map || state.inspection === "overview"} />
        </Suspense>
      </Canvas>
    </SceneBoundary>
    <div ref={curtain} className={styles.curtain} style={{ opacity: 1 }} aria-hidden="true"><div className={styles.occluder} /></div>
    {state.inspection && <aside className={styles.inspection}>STAGE 1 / {state.inspection.toUpperCase()} · 1 unit = 1 m <button onClick={() => runtime.inspect(null)}>Resume view</button></aside>}
    <header className={styles.header}><Link href="/" onClick={(e) => { if (!e.ctrlKey && !e.metaKey && !e.shiftKey && !e.altKey) { e.preventDefault(); if (state.phase === "landing") return; runtime.request("hub", "map"); } }}>BREEZE <span>2027</span></Link><span>GULLYVERSE</span></header>
    {state.phase === "landing" && <div className={styles.landing}><p>FOLLOW THE MUSIC</p><h1>A world<br />beyond the walls.</h1><button aria-label="Enter Gullyverse" onClick={() => runtime.enter()}>Enter Gullyverse <span aria-hidden="true">→</span></button><small>Click, tap, or press Enter</small></div>}
    <p className={styles.status} role="status" aria-live="polite">{["context-lost", "recovering"].includes(state.phase) ? "Restoring your view…" : state.phase === "boot" ? "Preparing your view…" : state.phase === "covered" ? `On the way to ${locations[state.destination].label}…` : state.phase === "entrance" ? "Welcome to Gullyverse" : local ? locations[state.scene].label : "Follow the music"}</p>
    {local && !state.map && !state.destinationMenu && <div className={styles.controls}>
      <p>{state.movie ? "Esc exits the Aftermovie" : state.scene === "hub" ? "WASD / arrows to walk · drag to look · follow a direction" : "WASD / arrows to walk · edge to choose your next stop"}</p>
      <div className={styles.actions}>
        <button onClick={() => runtime.setMap(true)} disabled={state.movie}>Map <kbd>M</kbd></button>
        {state.scene === "aftermovie" && <>
          <button onClick={() => state.movie ? runtime.movieActions?.stop() : runtime.movieActions?.play()}>{state.movie ? "Exit Aftermovie" : "Play Aftermovie"}</button>
          {state.movie && <button onClick={() => runtime.movieActions?.sound()}>Enable sound</button>}
        </>}
      </div>
      {!state.movie && <div className={styles.touchPad} aria-label="Movement controls"><button data-move="forward" aria-label="Walk forward">↑</button><div><button data-move="left" aria-label="Walk left">←</button><button data-move="back" aria-label="Walk backward">↓</button><button data-move="right" aria-label="Walk right">→</button></div><small>Drag the scene to look</small></div>}
    </div>}
    <div className={styles.access}><button onClick={() => { runtime.movieActions?.stop(); runtime.clearInput(); setFlat(true); }}>Use without 3D</button><details onToggle={(e) => { if (e.currentTarget.open) runtime.clearInput(); }}><summary>Festival information</summary><InformationLinks /></details></div>
    <WorldOverlays runtime={runtime} state={state} elements={mapElements} />
  </section>;
}
